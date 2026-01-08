# app.py - Document Q&A Assistant (RAG)
# A web-based AI assistant for document question answering with citations

import nest_asyncio
nest_asyncio.apply()

import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import custom modules
from utils.document_processor import DocumentProcessor
from utils.mongo_store import MongoVectorStore
from utils.rag_engine import RAGEngine

# --- Page Configuration ---
st.set_page_config(
    page_title="Document Q&A Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Custom CSS for Light Theme ---
st.markdown("""
<style>
    /* Main container styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.2rem;
        font-weight: 700;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Chat message styling */
    .chat-message {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        color: #1a1a1a !important;
    }
    
    .user-message {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-left: 4px solid #2196f3;
        color: #1a1a1a !important;
    }
    
    .assistant-message {
        background: white;
        border-left: 4px solid #667eea;
        color: #1a1a1a !important;
    }
    
    /* Citation styling */
    .citation-box {
        background: #f5f5f5;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin-top: 0.5rem;
        font-size: 0.9rem;
    }
    
    .citation-header {
        font-weight: 600;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    
    /* Source box styling */
    .source-box {
        background: #fafafa;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .source-title {
        font-weight: 600;
        color: #333;
        font-size: 0.95rem;
    }
    
    .source-location {
        color: #666;
        font-size: 0.85rem;
        margin-bottom: 0.5rem;
    }
    
    .source-content {
        color: #444;
        font-size: 0.9rem;
        line-height: 1.5;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    
    /* Upload area */
    .upload-area {
        background: white;
        border: 2px dashed #667eea;
        border-radius: 12px;
        padding: 2rem;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    /* Status badges */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 500;
    }
    
    .status-success {
        background: #e8f5e9;
        color: #2e7d32;
    }
    
    .status-processing {
        background: #fff3e0;
        color: #ef6c00;
    }
    
    .status-error {
        background: #ffebee;
        color: #c62828;
    }
    
    /* Document list */
    .doc-item {
        background: white;
        padding: 0.75rem 1rem;
        border-radius: 8px;
        margin-bottom: 0.5rem;
        border: 1px solid #e0e0e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .doc-name {
        font-weight: 500;
        color: #333;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    /* Info boxes */
    .info-box {
        background: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 1rem;
        border-radius: 0 8px 8px 0;
        margin: 1rem 0;
        color: #1a1a1a !important;
    }
    
    .info-box strong {
        color: #1565c0 !important;
    }
    
    .info-box ul, .info-box li {
        color: #333 !important;
    }
    
    /* No documents message */
    .no-docs {
        text-align: center;
        padding: 2rem;
        color: #666;
    }
    
    .no-docs-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    
    /* Text input styling */
    .stTextInput input {
        color: black !important;
    }
    
    /* Labels */
    .stTextInput label {
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)


# --- Session State Initialization ---
def init_session_state():
    """Initialize session state variables."""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    if 'vector_store' not in st.session_state:
        try:
            st.session_state.vector_store = MongoVectorStore()
            st.session_state.db_connected = True
        except Exception as e:
            st.session_state.db_connected = False
            st.session_state.db_error = str(e)
    
    if 'rag_engine' not in st.session_state and st.session_state.get('db_connected'):
        st.session_state.rag_engine = RAGEngine(
            vector_store=st.session_state.vector_store,
            top_k=5
        )
    
    if 'doc_processor' not in st.session_state:
        st.session_state.doc_processor = DocumentProcessor(
            chunk_size=750,  # Target 500-1000 tokens
            chunk_overlap=100
        )
    
    if 'upload_status' not in st.session_state:
        st.session_state.upload_status = None


def clear_chat():
    """Clear chat history."""
    st.session_state.chat_history = []
    st.session_state.upload_status = None


def reset_knowledge_base():
    """Reset the entire knowledge base."""
    if st.session_state.get('db_connected'):
        deleted = st.session_state.vector_store.clear_all()
        st.session_state.chat_history = []
        return deleted
    return 0


def process_uploaded_file(uploaded_file):
    """Process an uploaded file and add to knowledge base."""
    try:
        # Read file content
        file_content = uploaded_file.read()
        filename = uploaded_file.name
        print(f"[DEBUG] Processing file: {filename}, size: {len(file_content)} bytes")
        
        # Check if format is supported
        if not st.session_state.doc_processor.is_supported(filename):
            return False, f"Unsupported file format: {filename}"
        
        # Process document
        print(f"[DEBUG] Extracting text and creating chunks...")
        chunks = st.session_state.doc_processor.process_document(file_content, filename)
        print(f"[DEBUG] Created {len(chunks)} chunks")
        
        if not chunks:
            return False, "No content could be extracted from the document."
        
        # Add to vector store
        print(f"[DEBUG] Adding chunks to vector store...")
        count = st.session_state.vector_store.add_chunks(chunks)
        print(f"[DEBUG] Successfully added {count} chunks")
        
        return True, f"Successfully indexed {count} chunks from {filename}"
        
    except Exception as e:
        import traceback
        error_msg = f"Error processing file: {str(e)}"
        print(f"[ERROR] {error_msg}")
        print(f"[ERROR] Traceback: {traceback.format_exc()}")
        return False, error_msg


# --- Main Application ---
def main():
    init_session_state()
    
    # --- Sidebar ---
    with st.sidebar:
        st.markdown("### 📁 Document Management")
        
        # Check DB connection
        if not st.session_state.get('db_connected'):
            st.error(f"❌ Database Connection Failed")
            st.caption(st.session_state.get('db_error', 'Unknown error'))
            st.info("Please check your MONGODB_URI environment variable.")
            return
        
        st.success("✅ Connected to MongoDB")
        
        # File Upload Section
        st.markdown("#### Upload Documents")
        st.caption("Supported: PDF, DOCX, TXT, Markdown")
        
        uploaded_files = st.file_uploader(
            "Choose files",
            type=['pdf', 'docx', 'txt', 'md'],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        
        if uploaded_files:
            if st.button("📤 Process & Index", use_container_width=True, type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing: {uploaded_file.name}...")
                    success, message = process_uploaded_file(uploaded_file)
                    
                    if success:
                        st.success(f"✅ {uploaded_file.name}")
                    else:
                        st.error(f"❌ {message}")
                    
                    progress_bar.progress((i + 1) / len(uploaded_files))
                
                status_text.text("✅ All files processed!")
                st.rerun()
        
        st.divider()
        
        # Document List
        st.markdown("#### 📚 Indexed Documents")
        
        try:
            documents = st.session_state.vector_store.get_all_documents()
            chunk_count = st.session_state.vector_store.get_document_count()
            
            if documents:
                st.caption(f"Total: {len(documents)} documents, {chunk_count} chunks")
                
                for doc in documents:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.text(f"📄 {doc}")
                    with col2:
                        if st.button("🗑️", key=f"del_{doc}", help=f"Delete {doc}"):
                            st.session_state.vector_store.delete_document(doc)
                            st.rerun()
            else:
                st.markdown("""
                <div class="no-docs">
                    <div class="no-docs-icon">📭</div>
                    <p>No documents indexed yet</p>
                    <p style="font-size: 0.9rem; color: #888;">Upload documents to get started</p>
                </div>
                """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error loading documents: {e}")
        
        st.divider()
        
        # Action Buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🧹 Clear Chat", use_container_width=True):
                clear_chat()
                st.rerun()
        with col2:
            if st.button("🔄 Reset KB", use_container_width=True):
                deleted = reset_knowledge_base()
                st.success(f"Deleted {deleted} chunks")
                st.rerun()
        
        st.divider()
        
        # Settings
        st.markdown("#### ⚙️ Settings")
        top_k = st.slider("Top-K Retrieval", min_value=1, max_value=10, value=5)
        if st.session_state.get('rag_engine'):
            st.session_state.rag_engine.top_k = top_k
    
    # --- Main Content Area ---
    st.markdown("""
    <div class="main-header">
        <h1>📄 Document Q&A Assistant</h1>
        <p>Ask questions about your uploaded documents and get accurate answers with citations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chat Interface
    if not st.session_state.get('db_connected'):
        st.error("Database not connected. Please configure MongoDB.")
        return
    
    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>🧑 You:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong><br>
                {message["content"]}
            </div>
            """, unsafe_allow_html=True)
            
            # Show sources if available
            if message.get("sources") and message.get("has_sources"):
                with st.expander("📚 View Sources", expanded=False):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        <div class="source-box">
                            <div class="source-title">Source {i}: {source['document']}</div>
                            <div class="source-location">📍 {source['location']}</div>
                            <div class="source-content">{source['content'][:500]}{'...' if len(source['content']) > 500 else ''}</div>
                        </div>
                        """, unsafe_allow_html=True)
    
    # User input
    st.markdown("---")
    
    user_question = st.text_input(
        "Ask a question about your documents:",
        placeholder="What is the main topic of the document?",
        key="user_input"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    with col2:
        if st.button("🧹 Clear", use_container_width=True):
            clear_chat()
            st.rerun()
    
    if ask_button and user_question:
        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_question
        })
        
        # Get answer
        with st.spinner("🔍 Searching documents and generating answer..."):
            result = st.session_state.rag_engine.query(user_question)
        
        # Add assistant response to history
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "has_sources": result["has_sources"]
        })
        
        st.rerun()
    
    # Show tips if no chat history
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="info-box">
            <strong>💡 Getting Started</strong>
            <ul>
                <li>Upload documents using the sidebar (PDF, DOCX, TXT, or Markdown)</li>
                <li>Once indexed, ask questions about your documents</li>
                <li>Each answer includes citations to help you verify the information</li>
                <li>Adjust the Top-K setting to control how many chunks are retrieved</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()