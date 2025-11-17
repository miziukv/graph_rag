from services.neo4j_client import neo4j_client
from services.embeddings import chunk, embed
from services.ie_extract import extract
from typing import List, Dict
import re


def normalize(name: str) -> str:
    """Normalize entity names for consistent IDs."""
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')


def create_workspace(workspace_id: str) -> None:
    """Create or ensure workspace exists."""
    neo4j_client.write("""
        MERGE (w:Workspace {id: $workspace_id})
    """, {"workspace_id": workspace_id})


def create_collection(workspace_id: str, collection_id: str, name: str) -> None:
    """Create or ensure collection exists and link to workspace."""
    neo4j_client.write("""
        MERGE (w:Workspace {id: $workspace_id})
        MERGE (c:Collection {id: $collection_id, name: $name})
        MERGE (w)-[:HAS_COLLECTION]->(c)
    """, {
        "workspace_id": workspace_id,
        "collection_id": collection_id,
        "name": name
    })


def write_document(
    text: str,
    workspace_id: str,
    collection_id: str,
    source_doc_id: str,
    metadata: Dict = None
) -> Dict:
    """
    Complete ingestion pipeline for a document.
    
    1. Create Document node
    2. Chunk text
    3. Extract entities from each chunk
    4. Create Chunk nodes with embeddings
    5. Create Entity nodes
    6. Create all relationships
    
    Args:
        text: Document text
        workspace_id: User/project workspace
        collection_id: Collection this document belongs to
        source_doc_id: Original document ID
        metadata: Optional metadata (title, author, etc.)
        
    Returns:
        Summary of created nodes
    """
    metadata = metadata or {}
    doc_id = f"{workspace_id}:{collection_id}:{source_doc_id}"
    
    # Create document node
    neo4j_client.write("""
        MERGE (c:Collection {id: $collection_id})
        MERGE (d:Document {id: $doc_id})
        SET d += $metadata
        MERGE (c)-[:HAS_DOC]->(d)
    """, {
        "collection_id": collection_id,
        "doc_id": doc_id,
        "metadata": metadata
    })
    
    # Chunk text
    chunks = chunk(text)
    
    stats = {
        "document_id": doc_id,
        "chunks": 0,
        "entities": 0,
        "relationships": 0
    }
    
    # Process each chunk
    for i, chunk_text in enumerate(chunks):
        chunk_id = f"{doc_id}:chunk:{i}"
        
        # Generate embedding
        embedding = embed(chunk_text)
        
        # Extract entities and relationships
        extraction = extract(chunk_text)
        
        # Create chunk node
        neo4j_client.write("""
            MATCH (d:Document {id: $doc_id})
            MERGE (ch:Chunk {id: $chunk_id})
            SET ch.content = $content,
                ch.embedding = $embedding,
                ch.index = $index
            MERGE (ch)-[:SECTION_OF]->(d)
        """, {
            "doc_id": doc_id,
            "chunk_id": chunk_id,
            "content": chunk_text,
            "embedding": embedding,
            "index": i
        })
        stats["chunks"] += 1
        
        # Create entities and relationships
        entity_ids = {}
        for entity in extraction.entities:
            entity_id = f"{workspace_id}:{collection_id}:{normalize(entity.name)}:{normalize(entity.type)}"
            entity_ids[entity.name] = entity_id
            
            neo4j_client.write("""
                MATCH (ch:Chunk {id: $chunk_id})
                MERGE (e:Entity {id: $entity_id})
                SET e.name = $name,
                    e.type = $type
                MERGE (ch)-[:MENTIONS]->(e)
                MERGE (e)-[:IN_COLLECTION]->(:Collection {id: $collection_id})
            """, {
                "chunk_id": chunk_id,
                "entity_id": entity_id,
                "name": entity.name,
                "type": entity.type,
                "collection_id": collection_id
            })
            stats["entities"] += 1
        
        # Create entity relationships
        for rel in extraction.relationships:
            source_id = entity_ids.get(rel.source)
            target_id = entity_ids.get(rel.target)
            
            if source_id and target_id:
                neo4j_client.write("""
                    MATCH (source:Entity {id: $source_id})
                    MATCH (target:Entity {id: $target_id})
                    MERGE (source)-[r:RELATES_TO {kind: $kind}]->(target)
                """, {
                    "source_id": source_id,
                    "target_id": target_id,
                    "kind": rel.type
                })
                stats["relationships"] += 1
    
    return stats


def create_vector_index_if_needed() -> None:
    """Create vector index on Chunk nodes if it doesn't exist."""
    neo4j_client.create_vector_index(
        index_name="chunk_embeddings",
        label="Chunk",
        property_name="embedding",
        dimensions=1536
    )

