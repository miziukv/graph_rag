from fastapi import APIRouter

router = APIRouter(prefix='/rag', tags=['rag'])

@router.get('/answer')
def answer():
    pass

@router.get('/search')
def search():
    pass
