import json
from pathlib import Path
from langchain_chroma import Chroma
from src.rag.embedding_model import get_embedding_model
from langchain_classic.schema import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

DATA_DIR = Path("D:/Projects/Artflow Studio/src/rag/ingestion.py").parent.parent / "data"
DB_DIR = Path("D:/Projects/Artflow Studio/src/rag/ingestion.py").parent.parent / "chroma_db"

# Creating a Text Splitter
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=600, 
    chunk_overlap=100,   
)

# loading the older posts
def load_posts():
    posts_path = DATA_DIR / "posts.json"
    with open(posts_path, "r", encoding="utf-8") as f:
        posts = json.load(f)
    docs = []
    for p in posts:
        text = f"Caption: {p['caption']}\nHashtags: {' '.join(p['hashtags'])}\nCreated at: {p['created_at']}\nLikes: {p['likes']}, Comments: {p['comments']}"
        docs.append(
            Document(
                page_content=text,
                metadata={"source": "instagram_post", "id": p["id"], "type": p["type"]}
            )
        )
    print("posts loaded.")
    return docs

# Loading user/artist notes
def load_style_notes():
    style_path = DATA_DIR / "style_notes.md"
    text = style_path.read_text(encoding="utf-8")
    base_doc = Document(
            page_content=text,
            metadata={"source": "style_notes"}
        )
    # Chunking style notes because it may be large
    chunks = text_splitter.split_documents([base_doc])
    print("notes chukning done.")
    return chunks

# Creating vector store
def build_vector_store():
    # Load all the docs
    docs = load_posts() + load_style_notes()

    # Create the embedding model
    print("creating embeddings...")
    embeddings = get_embedding_model()

    # Create a vector store
    print("Creating store...")

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=str(DB_DIR)
    )
    # vectordb.persist()
    print("✅ Vector store built and persisted.")

if __name__ == "__main__":
    build_vector_store()
