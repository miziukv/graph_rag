from fastapi import APIRouter

router = APIRouter(prefix='/ingest', tags=['ingest'])

@router.post('/upload')
def upload():
    pass