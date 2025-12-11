import pandas as pd
import os
# Set Hugging Face Mirror for China BEFORE importing other modules that might use it
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import shutil
import time

# Configuration
CSV_PATH = "rag_resource/combined_laws.csv"
DB_DIR = "rag_resource/chroma_db"
# Using a high quality model suitable for semantic search
EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"

def main():
    # Check if CSV exists
    if not os.path.exists(CSV_PATH):
        print(f"Error: File not found at {CSV_PATH}")
        return

    print(f"Loading data from {CSV_PATH}...")
    try:
        df = pd.read_csv(CSV_PATH)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return
    
    # Fill NaN values with empty strings to avoid errors in metadata
    df = df.fillna("")
    
    documents = []
    print("Processing rows into documents...")
    for index, row in df.iterrows():
        text = str(row['Text']).strip()
        if not text:
            continue
            
        # Construct metadata dictionary
        # Converting all metadata to strings to ensure compatibility with Chroma
        metadata = {
            "source": "combined_laws.csv",
            "law_name": str(row['law_name']),
            "chapter": str(row['Chapter']),
            "chapter_title": str(row['ChapterTitle']),
            "sub_chapter": str(row['SubChapter']),
            "sub_chapter_title": str(row['SubChapterTitle']),
            "section": str(row['Section']),
            "section_title": str(row['SectionTitle']),
            "subsection": str(row['Subsection']),
            "point": str(row['Point']),
            "subpoint": str(row['Subpoint']),
            "global_index": int(row['global_index']) if row['global_index'] != "" else -1
        }
        
        # Create Document object
        doc = Document(page_content=text, metadata=metadata)
        documents.append(doc)
        
    print(f"Created {len(documents)} documents.")
    
    print(f"Initializing embedding model: {EMBEDDING_MODEL}...")
    try:
        embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    except Exception as e:
        print(f"Error initializing embeddings: {e}")
        return
    
    # Clear existing DB if you want a fresh start (optional, but good for rebuilding)
    if os.path.exists(DB_DIR):
        print(f"Removing existing database at {DB_DIR} for a fresh build...")
        shutil.rmtree(DB_DIR)
    
    print(f"Creating Vector Database in {DB_DIR}...")
    try:
        # Create vector store from documents
        # This will automatically persist to disk because persist_directory is provided
        vector_store = Chroma.from_documents(
            documents=documents,
            embedding=embeddings,
            persist_directory=DB_DIR
        )
        print(f"Vector database built successfully and persisted to {DB_DIR}")
        
        # Basic verification
        print("Verifying database...")
        count = vector_store._collection.count()
        print(f"Database contains {count} documents.")
        
    except Exception as e:
        print(f"Error creating vector database: {e}")

if __name__ == "__main__":
    main()
