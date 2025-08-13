# 📄 Gemini-Powered RAG Document Helper

A Streamlit web application that leverages a Retrieval-Augmented Generation (RAG) pipeline with Google's Gemini models to answer questions about a specific PDF document.



## Overview

This project demonstrates the power of Large Language Models (LLMs) for domain-specific question-answering. It ingests a user-provided PDF, processes it into a searchable vector database using ChromaDB, and uses Google's Gemini Pro via LangChain to provide context-aware answers. This allows the model to answer questions based solely on the knowledge within the document, complete with source references.

## Features ✨

- **PDF Ingestion:** Processes any PDF document into a queryable knowledge base.
- **RAG Pipeline:** Utilizes a Retrieval-Augmented Generation pipeline for accurate, context-aware answers.
- **Interactive UI:** A user-friendly web interface built with Streamlit.
- **Source Verification:** Displays the source text snippets from the document that were used to generate the answer.
- **Secure API Key Handling:** Uses a `.env` file to keep API keys safe and out of version control.

## Tech Stack ⚙️

- **Language:** Python
- **Core Libraries:** LangChain, Google Generative AI, Streamlit
- **Vector Database:** ChromaDB
- **PDF Processing:** PyPDF

---

## Getting Started

Follow these instructions to get a local copy up and running.

### Prerequisites

- Python 3.9+
- Git
