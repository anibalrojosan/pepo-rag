from fastapi import FastAPI
from app.core.agent_factory import get_rag_agent

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "ok, PepoRAG backend is running"}
