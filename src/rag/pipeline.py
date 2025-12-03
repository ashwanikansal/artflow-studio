from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from src.rag.llm import get_llm
from src.rag.vector_db import get_vector_store
from operator import itemgetter

def build_rag_chain():

    vectordb = get_vector_store()    
    
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})

    model = get_llm()

    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You are ArtFlow — an assistant that knows the user's art style, captions, "
         "and past posts. Use ONLY the provided context to answer.\n"
         "If context is missing, say you don't have enough info.\n\n"
         "Context:\n{context}\n"),
        ("human", "{question}")
    ])

    # Combine docs into a single string
    def combine_docs(docs):
        return "\n\n".join([d.page_content for d in docs])
    
    combine_docs_runnable = RunnableLambda(combine_docs)

    chain = {
            "context": itemgetter("question") | retriever | combine_docs_runnable,
            "question": itemgetter("question")
        } | prompt | model

    return chain