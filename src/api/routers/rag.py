from fastapi import APIRouter, Query
from services.neo4j_client import neo4j_client
from services.embeddings import embed
from services.rerank import rerank
from langgraph.rag_graph import graph

router = APIRouter(prefix='/rag', tags=['rag'])


@router.get('/answer')
def answer(
    query: str,
    workspace_id: str,
    collection_id: str
):
    """
    Generate an answer to a user question using Graph RAG.
    
    This endpoint:
    1. Embeds the query
    2. Retrieves relevant documents from the knowledge graph
    3. Uses graph relationships and context for reasoning
    4. Generates a comprehensive answer using an LLM
    
    Args:
        query: User's natural language question
        workspace_id: User/project workspace ID
        collection_id: Collection to search in
        
    Returns:
        JSON containing the generated answer and supporting context
    """
    # Run the LangGraph RAG workflow
    result = graph.invoke({
        "query": query,
        "workspace_id": workspace_id,
        "collection_id": collection_id
    })
    
    return {
        "query": query,
        "answer": result["answer"],
        "context": result["context"],
        "key_entities": result["key_entities"],
        "sources": result["retrieved_chunks"]
    }


@router.get('/search')
def search(
    query: str,
    workspace_id: str,
    collection_id: str,
    limit: int = Query(default=10, ge=1, le=50)
):
    """
    Perform semantic search over the knowledge graph.
    
    Returns relevant document chunks and their relationships
    without generating a full answer. Useful for:
    - Exploring what information exists
    - Finding related entities
    - Retrieving source documents
    
    Args:
        query: Search query text
        workspace_id: User/project workspace ID
        collection_id: Collection to search in
        limit: Maximum number of results to return (1-50, default: 10)
        
    Returns:
        JSON containing matching documents, entities, and relevance scores
    """
    # Generate query embedding
    query_embedding = embed(query)
    
    # Vector search with entity/relationship expansion
    results = neo4j_client.read("""
        CALL db.index.vector.queryNodes('chunk_embeddings', $limit, $query_vector)
        YIELD node, score
        
        // Filter by collection
        MATCH (node)-[:SECTION_OF]->(d:Document)
        MATCH (d)<-[:HAS_DOC]-(c:Collection {id: $collection_id})
        MATCH (c)<-[:HAS_COLLECTION]-(w:Workspace {id: $workspace_id})
        
        // Get connected entities
        OPTIONAL MATCH (node)-[:MENTIONS]->(e:Entity)
        
        // Get relationships between entities
        OPTIONAL MATCH (e)-[r:RELATES_TO]->(related:Entity)
        
        RETURN 
            node.id as chunk_id,
            node.content as content,
            node.index as chunk_index,
            d.id as document_id,
            d.filename as filename,
            score,
            collect(DISTINCT {name: e.name, type: e.type}) as entities,
            collect(DISTINCT {
                source: e.name, 
                target: related.name, 
                type: r.kind
            }) as relationships
        ORDER BY score DESC
    """, {
        "query_vector": query_embedding,
        "workspace_id": workspace_id,
        "collection_id": collection_id,
        "limit": limit
    })
    
    # Rerank results
    reranked_results = rerank(results, top_k=limit)
    
    return {
        "query": query,
        "results": reranked_results,
        "total": len(reranked_results)
    }
