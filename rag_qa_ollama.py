import os
import argparse
import pandas as pd
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Set Hugging Face Mirror for China
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

CHROMA_DIR = "rag_resource/chroma_db"
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
URLS_CSV = "rag_resource/urls.csv"
MODEL_NAME = "qwen3:8b"  # Updated to match installed model

def load_urls(csv_path: str) -> list[str]:
    if not os.path.exists(csv_path):
        return []
    try:
        df = pd.read_csv(csv_path)
    except Exception:
        return []
    # Flatten non-empty url column values into a list of strings
    urls = []
    for _, row in df.iterrows():
        url = str(row.get(" url", "")).strip()  # column name appears with leading space
        if not url:
            url = str(row.get("url", "")).strip()
        if url:
            urls.append(url)
    return urls

def format_docs(docs: list[Document]) -> str:
    parts = []
    for d in docs:
        meta = d.metadata
        label = f"Law={meta.get('law_name','')}, Section={meta.get('section','')}, Subsection={meta.get('subsection','')}"
        parts.append(f"{label}: {d.page_content}")
    return "\n\n".join(parts)

def build_chain():
    if not os.path.exists(CHROMA_DIR):
        raise FileNotFoundError(f"Chroma directory not found at {CHROMA_DIR}. Please run build_vector_db.py first.")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectordb = Chroma(persist_directory=CHROMA_DIR, embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 6})

    urls = load_urls(URLS_CSV)
    urls_text = "\n".join(f"- {u}" for u in urls) if urls else "(no extra URLs found)"

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a helpful legal assistant for migration and refugee topics. "
                "Use the provided context to answer briefly and cite the most relevant law section identifiers when possible. "
                "If unsure, say so and suggest consulting official sources."
            ),
            (
                "user",
                "Question: {question}\n\nContext:\n{context}\n\nReference URLs:\n{urls}\n\nAnswer succinctly and include URLs if helpful."
            ),
        ]
    )

    llm = ChatOllama(model=MODEL_NAME, temperature=0.1)

    chain = (
        RunnableParallel({
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
            "urls": RunnablePassthrough(lambda _: urls_text),
        })
        | prompt
        | llm
    )
    return chain

def run_cli(question: str):
    chain = build_chain()
    print("Running RAG query...\n")
    answer = chain.invoke(question)
    print(answer.content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG Q&A with Ollama Qwen3")
    parser.add_argument("question", type=str, help="User question about migration/refugee laws")
    args = parser.parse_args()
    run_cli(args.question)
