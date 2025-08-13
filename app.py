# app.py

import nest_asyncio
nest_asyncio.apply()

import streamlit as st
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

# --- 1. Load Environment Variables and Setup ---
load_dotenv()
CHROMA_PATH = "chroma_db"

# --- 2. User Interface Setup ---
st.set_page_config(page_title="Gemini-Powered Docs Helper", layout="wide")
st.title("📄 Gemini-Powered Docs Helper")
st.info("Ask a question about the 'Attention Is All You Need' paper.")

# --- 3. Main Application Logic ---
if not os.path.exists(CHROMA_PATH):
    st.error("Chroma DB not found. Please run ingest.py first.")
else:
    user_question = st.text_input("What is your question?")

    if user_question:
        try:
            st.spinner("Searching the document with Gemini...")

            embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
            
            # Use the correct, stable Gemini model name from your available models
            llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash", temperature=0)

            db = Chroma(
                persist_directory=CHROMA_PATH,
                embedding_function=embeddings
            )

            qa_chain = RetrievalQA.from_chain_type(
                llm=llm,
                chain_type="stuff",
                retriever=db.as_retriever(search_kwargs={"k": 3}),
                return_source_documents=True
            )

            # Use the modern .invoke() method
            result = qa_chain.invoke({"query": user_question})

            st.success("Answer:")
            st.write(result["result"])

            with st.expander("Show Sources"):
                st.write("Gemini used the following snippets from the document to generate the answer:")
                for document in result["source_documents"]:
                    st.info(document.page_content)

        except Exception as e:
            st.error(f"An error occurred: {e}")