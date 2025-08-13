# ingest.py

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma

print("Starting data ingestion...")
# --- 1. Load Environment Variables ---
load_dotenv()

# --- 2. Define Constants ---
PDF_PATH = "docs/temp.pdf"
CHROMA_PATH = "chroma_db"

def ingest_data():
    """
    Loads data from the PDF, splits it into chunks, creates embeddings using Google's model,
    and stores them in a Chroma vector database.
    """
    # --- 3. Load the Document ---
    print("Loading document...")
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    if not documents:
        print("Could not load any documents. Check the PDF path.")
        return

    # --- 4. Split the Document into Chunks ---
    print("Splitting document into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    print(f"Created {len(chunks)} text chunks.")

    # --- 5. Create Embeddings and Store in Chroma DB ---
    print("Creating Google embeddings and storing in Chroma DB...")

    # The key change: Using Google's embedding model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=CHROMA_PATH
    )
    print("--- Ingestion Complete ---")

# This block needs to be at the very left, with no indentation.
if __name__ == "__main__":
    ingest_data()