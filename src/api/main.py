from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import rag, ingest
from services.neo4j_client import neo4j_client
from contextlib import asynccontextmanager
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app lifecycle:
    - Connect to Neo4j on startup
    - Close connection on shutdown
    """
    # Startup
    neo4j_client.connect()
    yield
    # Shutdown
    neo4j_client.close()


app = FastAPI(lifespan=lifespan)

# Add CORS middleware to allow frontend to call backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(rag.router)
app.include_router(ingest.router)


@app.get("/")
def read_root():
    return {"message": "Graph RAG API", "status": "running"}


if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
