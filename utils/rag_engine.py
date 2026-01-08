# rag_engine.py - RAG Query Engine with Citations

import os
from typing import List, Dict, Any, Tuple, Optional
from langchain_google_genai import ChatGoogleGenerativeAI


class RAGEngine:
    """
    RAG Query Engine that retrieves relevant chunks and generates
    grounded answers with citations.
    """
    
    # System prompt for grounded generation
    SYSTEM_PROMPT = """You are a helpful document assistant. Your task is to answer questions based ONLY on the provided context from uploaded documents.

IMPORTANT RULES:
1. ONLY use information from the provided context to answer questions
2. If the answer is not found in the context, respond with: "I couldn't find this information in the uploaded document."
3. Always cite your sources by referencing the document name and section/page
4. Be concise but thorough in your answers
5. If the context contains partial information, acknowledge what you found and what's missing

Format your response as:
- Answer the question directly
- Include citations in [Document: X, Page/Section: Y] format"""

    NOT_FOUND_RESPONSE = "I couldn't find this information in the uploaded document."
    
    def __init__(self, vector_store, model_name: str = "gemini-2.0-flash-lite", top_k: int = 5):
        """
        Initialize the RAG engine.
        
        Args:
            vector_store: MongoVectorStore instance
            model_name: Name of the Gemini model to use
            top_k: Number of chunks to retrieve (default 5)
        """
        self.vector_store = vector_store
        self.top_k = top_k
        
        # Initialize LLM
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.1,  # Low temperature for factual responses
            convert_system_message_to_human=True
        )
    
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for a query.
        
        Args:
            query: User's question
            
        Returns:
            List of relevant chunks with metadata
        """
        results = self.vector_store.similarity_search(query, k=self.top_k)
        return results
    
    def format_context(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Format retrieved chunks into context for the LLM.
        
        Args:
            chunks: List of retrieved chunks
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(chunks, 1):
            metadata = chunk.get("metadata", {})
            doc_name = metadata.get("document_name", "Unknown Document")
            
            # Build location string based on available metadata
            location_parts = []
            if "page" in metadata:
                location_parts.append(f"Page {metadata['page']}")
            if "section" in metadata:
                location_parts.append(f"Section {metadata['section']}")
            if "section_title" in metadata:
                location_parts.append(f"'{metadata['section_title']}'")
            
            location = ", ".join(location_parts) if location_parts else "Full Document"
            
            context_parts.append(
                f"[Source {i}: {doc_name} - {location}]\n{chunk['content']}\n"
            )
        
        return "\n---\n".join(context_parts)
    
    def generate_answer(self, query: str, context: str) -> str:
        """
        Generate an answer using the LLM.
        
        Args:
            query: User's question
            context: Formatted context from retrieved chunks
            
        Returns:
            Generated answer string
        """
        if not context:
            return self.NOT_FOUND_RESPONSE
        
        prompt = f"""{self.SYSTEM_PROMPT}

CONTEXT FROM DOCUMENTS:
{context}

USER QUESTION: {query}

Please provide a comprehensive answer based on the context above, with proper citations."""

        try:
            response = self.llm.invoke(prompt)
            answer = response.content
            
            # Check if the answer indicates no information found
            if self._is_no_info_response(answer):
                return self.NOT_FOUND_RESPONSE
            
            return answer
            
        except Exception as e:
            return f"Error generating answer: {str(e)}"
    
    def _is_no_info_response(self, answer: str) -> bool:
        """Check if the answer indicates no relevant information was found."""
        no_info_phrases = [
            "not found in",
            "no information",
            "cannot find",
            "don't have information",
            "not mentioned",
            "not available in",
            "context does not contain",
            "context doesn't contain"
        ]
        answer_lower = answer.lower()
        return any(phrase in answer_lower for phrase in no_info_phrases)
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        Complete RAG query pipeline.
        
        Args:
            question: User's question
            
        Returns:
            Dictionary with answer, sources, and metadata
        """
        # Check if there are any documents
        if self.vector_store.get_document_count() == 0:
            return {
                "answer": "No documents have been uploaded yet. Please upload a document first.",
                "sources": [],
                "has_sources": False
            }
        
        # Retrieve relevant chunks
        chunks = self.retrieve(question)
        
        if not chunks:
            return {
                "answer": self.NOT_FOUND_RESPONSE,
                "sources": [],
                "has_sources": False
            }
        
        # Format context
        context = self.format_context(chunks)
        
        # Generate answer
        answer = self.generate_answer(question, context)
        
        # Format sources for display
        sources = self._format_sources_for_display(chunks)
        
        return {
            "answer": answer,
            "sources": sources,
            "has_sources": len(sources) > 0 and answer != self.NOT_FOUND_RESPONSE
        }
    
    def _format_sources_for_display(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format chunks as sources for UI display."""
        sources = []
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            source = {
                "document": metadata.get("document_name", "Unknown"),
                "content": chunk.get("content", ""),
                "score": chunk.get("score", 0),
                "location": self._get_location_string(metadata)
            }
            sources.append(source)
        return sources
    
    def _get_location_string(self, metadata: Dict[str, Any]) -> str:
        """Build a human-readable location string from metadata."""
        parts = []
        
        if "page" in metadata:
            total = metadata.get("total_pages", "")
            if total:
                parts.append(f"Page {metadata['page']} of {total}")
            else:
                parts.append(f"Page {metadata['page']}")
        
        if "section" in metadata:
            parts.append(f"Section {metadata['section']}")
        
        if "section_title" in metadata and metadata["section_title"] != "Document Start":
            parts.append(f"'{metadata['section_title']}'")
        
        return ", ".join(parts) if parts else "Full Document"
