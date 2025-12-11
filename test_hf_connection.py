import os
# Set Hugging Face Mirror for China
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from langchain_huggingface import HuggingFaceEmbeddings
import time

def test_connection():
    model_name = "sentence-transformers/all-mpnet-base-v2"
    print(f"Testing connection to Hugging Face mirror ({os.environ['HF_ENDPOINT']})...")
    print(f"Attempting to load model: {model_name}")
    
    try:
        start_time = time.time()
        embeddings = HuggingFaceEmbeddings(model_name=model_name)
        end_time = time.time()
        
        print(f"Success! Model loaded in {end_time - start_time:.2f} seconds.")
        
        # Test a simple embedding
        text = "This is a test sentence."
        vector = embeddings.embed_query(text)
        print(f"Embedding generation successful. Vector length: {len(vector)}")
        
    except Exception as e:
        print(f"Connection failed or error occurred: {e}")

if __name__ == "__main__":
    test_connection()
