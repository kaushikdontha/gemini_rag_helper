# mongo_store.py - MongoDB Vector Store for RAG

import os
from typing import List, Dict, Any, Optional
from dataclasses import asdict
import numpy as np
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

from langchain_google_genai import GoogleGenerativeAIEmbeddings


class MongoVectorStore:
    """
    MongoDB-based vector store for document embeddings.
    Uses MongoDB Atlas Vector Search for similarity queries.
    """
    
    def __init__(self, connection_string: Optional[str] = None, database_name: str = "rag_assistant"):
        """
        Initialize MongoDB connection.
        
        Args:
            connection_string: MongoDB Atlas connection string
            database_name: Name of the database to use
        """
        self.connection_string = connection_string or os.getenv("MONGODB_URI")
        if not self.connection_string:
            raise ValueError("MongoDB connection string not provided. Set MONGODB_URI environment variable.")
        
        self.database_name = database_name
        self.collection_name = "document_chunks"
        self.client = None
        self.db = None
        self.collection = None
        
        # Initialize embeddings model (using newer model with separate quota)
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
        
        self._connect()
    
    def _connect(self):
        """Establish MongoDB connection."""
        try:
            self.client = MongoClient(self.connection_string)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # Create indexes
            self._ensure_indexes()
            
        except ConnectionFailure as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")
    
    def _ensure_indexes(self):
        """Create necessary indexes for efficient querying."""
        # Index for document name queries
        self.collection.create_index("metadata.document_name")
        
        # Note: Vector search index must be created in MongoDB Atlas UI
        # or via Atlas Admin API. Here we just ensure basic indexes exist.
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a text chunk."""
        embedding = self.embeddings.embed_query(text)
        return embedding
    
    def add_chunks(self, chunks: List[Any], progress_callback=None) -> int:
        """
        Add document chunks to the vector store.
        
        Args:
            chunks: List of DocumentChunk objects
            progress_callback: Optional callback function for progress updates
            
        Returns:
            Number of chunks added
        """
        documents = []
        total = len(chunks)
        
        for i, chunk in enumerate(chunks):
            # Generate embedding
            embedding = self.generate_embedding(chunk.content)
            
            doc = {
                "content": chunk.content,
                "embedding": embedding,
                "metadata": chunk.metadata,
                "chunk_id": chunk.chunk_id,
                "token_count": chunk.token_count
            }
            documents.append(doc)
            
            if progress_callback:
                progress_callback(i + 1, total)
        
        if documents:
            self.collection.insert_many(documents)
        
        return len(documents)
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        Perform similarity search using cosine similarity.
        
        Note: For production, use MongoDB Atlas Vector Search.
        This implementation uses a fallback approach for compatibility.
        
        Args:
            query: Query text
            k: Number of top results to return
            
        Returns:
            List of matching documents with scores
        """
        query_embedding = self.generate_embedding(query)
        
        # Try vector search first (Atlas Vector Search)
        try:
            results = self._atlas_vector_search(query_embedding, k)
            if results:
                return results
        except OperationFailure:
            # Fallback to manual cosine similarity
            pass
        
        # Fallback: Manual cosine similarity search
        return self._manual_similarity_search(query_embedding, k)
    
    def _atlas_vector_search(self, query_embedding: List[float], k: int) -> List[Dict[str, Any]]:
        """
        Use MongoDB Atlas Vector Search if available.
        Requires vector search index to be configured in Atlas.
        """
        pipeline = [
            {
                "$vectorSearch": {
                    "index": "vector_index",
                    "path": "embedding",
                    "queryVector": query_embedding,
                    "numCandidates": k * 10,
                    "limit": k
                }
            },
            {
                "$project": {
                    "content": 1,
                    "metadata": 1,
                    "chunk_id": 1,
                    "score": {"$meta": "vectorSearchScore"}
                }
            }
        ]
        
        results = list(self.collection.aggregate(pipeline))
        return results
    
    def _manual_similarity_search(self, query_embedding: List[float], k: int) -> List[Dict[str, Any]]:
        """
        Manual cosine similarity search (fallback for non-Atlas deployments).
        """
        query_vec = np.array(query_embedding)
        
        all_docs = list(self.collection.find({}, {
            "content": 1, 
            "embedding": 1, 
            "metadata": 1, 
            "chunk_id": 1
        }))
        
        if not all_docs:
            return []
        
        # Calculate cosine similarities
        scored_docs = []
        for doc in all_docs:
            doc_vec = np.array(doc["embedding"])
            similarity = np.dot(query_vec, doc_vec) / (
                np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
            )
            scored_docs.append({
                "content": doc["content"],
                "metadata": doc["metadata"],
                "chunk_id": doc["chunk_id"],
                "score": float(similarity)
            })
        
        # Sort by similarity and return top k
        scored_docs.sort(key=lambda x: x["score"], reverse=True)
        return scored_docs[:k]
    
    def get_all_documents(self) -> List[str]:
        """Get list of all unique document names in the store."""
        pipeline = [
            {"$group": {"_id": "$metadata.document_name"}},
            {"$project": {"document_name": "$_id", "_id": 0}}
        ]
        results = list(self.collection.aggregate(pipeline))
        return [r["document_name"] for r in results if r.get("document_name")]
    
    def get_document_count(self) -> int:
        """Get total number of chunks in the store."""
        return self.collection.count_documents({})
    
    def delete_document(self, document_name: str) -> int:
        """
        Delete all chunks from a specific document.
        
        Args:
            document_name: Name of the document to delete
            
        Returns:
            Number of chunks deleted
        """
        result = self.collection.delete_many({"metadata.document_name": document_name})
        return result.deleted_count
    
    def clear_all(self) -> int:
        """
        Clear all documents from the knowledge base.
        
        Returns:
            Number of chunks deleted
        """
        result = self.collection.delete_many({})
        return result.deleted_count
    
    def close(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
