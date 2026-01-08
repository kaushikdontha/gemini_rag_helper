# Document Q&A Assistant (RAG)

A web-based AI assistant that allows users to upload documents and ask questions that are answered strictly based on the document's content, with proper citations.

## 📸 Screenshots

### Main Interface - Chat View
![Chat Interface](Screenshots/screencapture-localhost-8501-2026-01-08-09_03_59.png)
*The main chat interface showing document upload area, chat history, and the "Ask" feature. Upload documents using the sidebar and ask questions in the main area.*

### Document Successfully Indexed
![Document Indexed](Screenshots/screencapture-localhost-8502-2026-01-08-09_46_03.png)
*After uploading and processing a document, it appears in the "Indexed Documents" section. The app shows helpful getting started tips for new users.*

### Q&A with Source Citations
![Q&A with Citations](Screenshots/screencapture-localhost-8502-2026-01-08-09_50_39.png)
*The assistant answers questions based on the uploaded document content and provides source citations. Click "View Sources" to see the exact document chunks used.*

---

## ✨ Features

- **Multi-Format Support**: Upload PDF, DOCX, TXT, and Markdown files
- **Smart Chunking**: Documents are split into 500-1000 token chunks with overlap for better context
- **Vector Search**: MongoDB Atlas Vector Search for efficient similarity matching
- **AI-Powered Answers**: Google Gemini generates accurate, grounded responses
- **Citations**: Every answer includes source citations with document name and page/section
- **Knowledge Base Management**: Add, view, and remove documents from the knowledge base
- **Configurable Retrieval**: Adjust top-K parameter for retrieval (default: 5)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Streamlit Frontend                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │
│  │ File Upload │  │ Chat UI     │  │ Citation Display        │ │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     Processing Layer                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Document        │  │ Embedding       │  │ RAG Engine      │ │
│  │ Processor       │  │ Generator       │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────────┐
│                     External Services                           │
│  ┌─────────────────────────┐  ┌───────────────────────────────┐│
│  │ MongoDB Atlas           │  │ Google Gemini API             ││
│  │ (Vector Store)          │  │ (Embeddings + LLM)            ││
│  └─────────────────────────┘  └───────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Python 3.9+
- MongoDB Atlas account (with Vector Search enabled)
- Google Cloud account with Gemini API access

## Setup Instructions

### 1. Clone the Repository

```bash
git clone <repository-url>
cd gemini_rag_helper
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
```

### 5. Set Up MongoDB Atlas Vector Search

1. Log in to [MongoDB Atlas](https://cloud.mongodb.com)
2. Create a new cluster (or use existing)
3. Create a database named `rag_assistant`
4. Create a collection named `document_chunks`
5. Create a Vector Search Index with the following configuration:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 768,
      "similarity": "cosine"
    }
  ]
}
```

Name the index: `vector_index`

### 6. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Usage Guide

### Uploading Documents

1. Click the **file upload** area in the sidebar
2. Select one or more documents (PDF, DOCX, TXT, or MD)
3. Click **"Process & Index"** to extract and store document content
4. Wait for the processing to complete (status will show progress)

### Asking Questions

1. Type your question in the input field at the bottom
2. Click **"Ask"** or press Enter
3. The assistant will search your documents and generate an answer
4. Expand **"View Sources"** to see the retrieved chunks

### Managing Knowledge Base

- **View Documents**: See all indexed documents in the sidebar
- **Delete Document**: Click the 🗑️ button next to any document
- **Clear Chat**: Reset the conversation history
- **Reset KB**: Remove all documents from the knowledge base

### Adjusting Settings

- **Top-K Retrieval**: Slider in sidebar (1-10) controls how many chunks are retrieved

## Project Structure

```
gemini_rag_helper/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (create this)
├── screenshots/                # Application screenshots
├── utils/
│   ├── __init__.py
│   ├── document_processor.py   # Multi-format document loader & chunker
│   ├── mongo_store.py          # MongoDB vector store implementation
│   └── rag_engine.py           # RAG query engine with citations
├── docs/
│   ├── architecture.md         # Architecture diagram
│   └── test_questions.md       # Test questions and expected answers
└── README.md                   # This file
```

## Technical Details

### Document Processing

- **Chunk Size**: 750 tokens (target range: 500-1000)
- **Chunk Overlap**: 100 tokens for context continuity
- **Tokenizer**: tiktoken (cl100k_base encoding)

### Embedding Model

- **Model**: Google Generative AI Embeddings (`models/text-embedding-004`)
- **Dimensions**: 768

### LLM

- **Model**: Google Gemini 2.0 Flash Lite (`gemini-2.0-flash-lite`)
- **Temperature**: 0.1 (for factual responses)

### Retrieval

- **Method**: Cosine similarity
- **Default Top-K**: 5 chunks

## Troubleshooting

### "Database Connection Failed"

- Check your `MONGODB_URI` in the `.env` file
- Ensure your IP address is whitelisted in MongoDB Atlas
- Verify the cluster is running

### "Error generating answer"

- Check your `GOOGLE_API_KEY` in the `.env` file
- Ensure you have Gemini API access enabled

### "No content extracted"

- Ensure the document contains readable text (not just images)
- Try a different document format

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
