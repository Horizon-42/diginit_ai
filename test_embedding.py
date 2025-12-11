from langchain_ollama import OllamaEmbeddings

try:
    print("Initializing OllamaEmbeddings with nomic-embed-text...")
    embeddings = OllamaEmbeddings(model="nomic-embed-text")
    print("Embedding a test string...")
    vector = embeddings.embed_query("This is a test sentence to check if the model works.")
    print(f"Success! Vector length: {len(vector)}")
except Exception as e:
    print(f"Error: {e}")
