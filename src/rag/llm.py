
from dotenv import load_dotenv
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint

load_dotenv()

def get_llm() -> ChatHuggingFace:
    llm = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.2-1B-Instruct", # small model
        # repo_id="meta-llama/Llama-3.2-8B-Instruct", # large model
        task="text-generation",
        max_new_tokens=512,
        temperature=0.7,
        do_sample=False,
        repetition_penalty=1.03,
    )

    return ChatHuggingFace(llm=llm)