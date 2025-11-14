from fastapi import FastAPI
from routers import rag, ingest
import uvicorn

app = FastAPI()

app.include_router(rag.router)
app.include_router(ingest.router)

if __name__ == "__main__":
    uvicorn.run(app, host='0.0.0.0', port=8000)
