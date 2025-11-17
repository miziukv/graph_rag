from fastapi import APIRouter, UploadFile, File, Form
from services.writer import (
    create_workspace,
    create_collection,
    write_document,
    create_vector_index_if_needed
)
import json

router = APIRouter(prefix='/ingest', tags=['ingest'])


@router.post('/upload')
async def upload(
    file: UploadFile = File(...),
    workspace_id: str = Form(...),
    collection_id: str = Form(...),
    collection_name: str = Form(None),
    metadata: str = Form(None)
):
    """
    Upload and process a document into the knowledge graph.
    
    This endpoint:
    1. Creates workspace and collection if needed
    2. Chunks the document
    3. Generates embeddings
    4. Extracts entities and relationships
    5. Writes everything to Neo4j
    
    Args:
        file: Text file to upload
        workspace_id: User/project workspace ID
        collection_id: Collection ID (e.g., "algorithms", "history")
        collection_name: Human-readable collection name (optional)
        metadata: JSON string with document metadata (optional)
        
    Returns:
        Summary of ingestion (chunks, entities, relationships created)
    """
    # Read file content
    content = await file.read()
    text = content.decode('utf-8')
    
    # Parse metadata
    doc_metadata = json.loads(metadata) if metadata else {}
    doc_metadata['filename'] = file.filename
    
    # Ensure workspace and collection exist
    create_workspace(workspace_id)
    create_collection(
        workspace_id,
        collection_id,
        collection_name or collection_id
    )
    
    # Create vector index if first upload
    create_vector_index_if_needed()
    
    # Process document
    stats = write_document(
        text=text,
        workspace_id=workspace_id,
        collection_id=collection_id,
        source_doc_id=file.filename,
        metadata=doc_metadata
    )
    
    return {
        "status": "success",
        "workspace_id": workspace_id,
        "collection_id": collection_id,
        **stats
    }


@router.post('/collection')
def create_collection_endpoint(
    workspace_id: str = Form(...),
    collection_id: str = Form(...),
    collection_name: str = Form(...)
):
    """
    Create a new collection in a workspace.
    
    Args:
        workspace_id: User/project workspace ID
        collection_id: Unique collection ID (e.g., "col_algorithms")
        collection_name: Human-readable name (e.g., "Algorithm Papers")
        
    Returns:
        Confirmation message
    """
    create_workspace(workspace_id)
    create_collection(workspace_id, collection_id, collection_name)
    
    return {
        "status": "success",
        "workspace_id": workspace_id,
        "collection_id": collection_id,
        "collection_name": collection_name
    }
