from fastapi import FastAPI

app = FastAPI()

@app.get('/answer')
def answer():
    pass

@app.get('/')
def search():
    pass
