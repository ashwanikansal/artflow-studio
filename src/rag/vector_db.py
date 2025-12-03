from pathlib import Path
from langchain_chroma import Chroma
from src.rag.embedding_model import get_embedding_model

DB_DIR = Path("D:/Projects/Artflow Studio/src/rag/ingestion.py").parent.parent / "chroma_db"

def get_vector_store():
    embeddings = get_embedding_model()
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=str(DB_DIR)
    )
    return vectordb
