from langgraph.graph import StateGraph, START, END
from typing import TypedDict, List, Dict
from openai import OpenAI
from services.embeddings import embed
from services.neo4j_client import neo4j_client
from services.rerank import rerank

client = OpenAI()


class State(TypedDict):
    """State passed between nodes in the RAG workflow."""
    query: str
    workspace_id: str
    collection_id: str
    key_entities: List[str]
    retrieved_chunks: List[Dict]
    context: str
    answer: str


def plan(state: State) -> State:
    """
    Analyze the query and extract key entities/concepts.
    
    This helps focus retrieval on relevant parts of the graph.
    """
    query = state["query"]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "Extract key entities, concepts, and topics from the user's question. Return as a comma-separated list."
            },
            {
                "role": "user",
                "content": f"Question: {query}"
            }
        ],
        temperature=0
    )
    
    key_entities_str = response.choices[0].message.content
    key_entities = [e.strip() for e in key_entities_str.split(",")]
    
    return {
        **state,
        "key_entities": key_entities
    }


def retrieve(state: State) -> State:
    """
    Retrieve relevant chunks and their connected entities from the graph.
    
    Steps:
    1. Vector search for similar chunks
    2. Expand to connected entities and relationships
    3. Rerank by relevance
    """
    query = state["query"]
    workspace_id = state["workspace_id"]
    collection_id = state["collection_id"]
    
    # Generate query embedding
    query_embedding = embed(query)
    
    # Vector search for relevant chunks
    vector_results = neo4j_client.read("""
        CALL db.index.vector.queryNodes('chunk_embeddings', 10, $query_vector)
        YIELD node, score
        
        // Filter by workspace and collection
        MATCH (node)-[:SECTION_OF]->(d:Document)
        MATCH (d)<-[:HAS_DOC]-(c:Collection {id: $collection_id})
        MATCH (c)<-[:HAS_COLLECTION]-(w:Workspace {id: $workspace_id})
        
        // Get connected entities and relationships
        OPTIONAL MATCH (node)-[:MENTIONS]->(e:Entity)
        OPTIONAL MATCH (e)-[r:RELATES_TO]->(related:Entity)
        
        RETURN 
            node.id as chunk_id,
            node.content as content,
            score,
            collect(DISTINCT {name: e.name, type: e.type}) as entities,
            collect(DISTINCT {source: e.name, target: related.name, type: r.kind}) as relationships
        ORDER BY score DESC
    """, {
        "query_vector": query_embedding,
        "workspace_id": workspace_id,
        "collection_id": collection_id
    })
    
    # Rerank results
    reranked = rerank(vector_results, top_k=5)
    
    return {
        **state,
        "retrieved_chunks": reranked
    }


def reason(state: State) -> State:
    """
    Analyze retrieved information and build context for answer generation.
    
    Combines chunks with entity relationships to create rich context.
    """
    chunks = state["retrieved_chunks"]
    key_entities = state["key_entities"]
    
    # Build structured context
    context_parts = []
    
    context_parts.append(f"Key entities mentioned in query: {', '.join(key_entities)}\n")
    context_parts.append("Relevant information from knowledge graph:\n")
    
    for i, chunk in enumerate(chunks, 1):
        context_parts.append(f"\n--- Source {i} (relevance: {chunk.get('rerank_score', 0):.2f}) ---")
        context_parts.append(chunk["content"])
        
        # Add entity information
        entities = chunk.get("entities", [])
        if entities:
            entity_names = [e["name"] for e in entities if e["name"]]
            if entity_names:
                context_parts.append(f"Entities: {', '.join(entity_names)}")
        
        # Add relationships
        relationships = chunk.get("relationships", [])
        if relationships:
            rel_strs = [
                f"{r['source']} {r['type']} {r['target']}" 
                for r in relationships 
                if r.get("source") and r.get("target")
            ]
            if rel_strs:
                context_parts.append(f"Relationships: {'; '.join(rel_strs)}")
    
    context = "\n".join(context_parts)
    
    return {
        **state,
        "context": context
    }


def write(state: State) -> State:
    """
    Generate the final answer using the retrieved context.
    """
    query = state["query"]
    context = state["context"]
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are a helpful assistant that answers questions using the provided context from a knowledge graph.

Instructions:
- Answer the question accurately based on the context
- Cite which sources you use (Source 1, Source 2, etc.)
- If the context doesn't contain enough information, say so
- Use the entity relationships to provide deeper insights
- Be clear and concise"""
            },
            {
                "role": "user",
                "content": f"""Context:
{context}

Question: {query}

Answer:"""
            }
        ],
        temperature=0.7
    )
    
    answer = response.choices[0].message.content
    
    return {
        **state,
        "answer": answer
    }


# Build the graph
workflow = StateGraph(State)

# Add nodes
workflow.add_node("plan", plan)
workflow.add_node("retrieve", retrieve)
workflow.add_node("reason", reason)
workflow.add_node("write", write)

# Add edges
workflow.add_edge(START, "plan")
workflow.add_edge("plan", "retrieve")
workflow.add_edge("retrieve", "reason")
workflow.add_edge("reason", "write")
workflow.add_edge("write", END)

# Compile the graph
graph = workflow.compile()