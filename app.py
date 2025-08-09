import streamlit as st
import os
from utils.document_handler import extract_text_from_file
from utils.youtube_api import get_youtube_captions
from utils.embedder import embed_chunks, create_faiss_index, semantic_search
from utils.vertex_ai import generate_answer
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(page_title="Google API RAG Assistant", layout="wide")

# Sidebar Inputs
st.sidebar.title("Settings & Inputs")

uploaded_files = st.sidebar.file_uploader(
    "Upload documents (PDF, DOCX, TXT, XLSX, PNG, JPG)", accept_multiple_files=True,
    type=["pdf", "docx", "txt", "xlsx", "png", "jpg", "jpeg"]
)

doc_chunk_size = st.sidebar.selectbox(
    "Chunk size for Documents (chars)",
    options=list(range(100, 2001, 100)),
    index=19
)

youtube_url = st.sidebar.text_input("YouTube Video URL")

yt_chunk_size = st.sidebar.selectbox(
    "Chunk size for YouTube (chars)",
    options=list(range(100, 3001, 100)),
    index=19
)

google_api_key = st.sidebar.text_input("Google API Key", type="password")

process_btn = st.sidebar.button("Process Content")

if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if "yt_text" not in st.session_state:
    st.session_state.yt_text = ""

if "faiss_index" not in st.session_state:
    st.session_state.faiss_index = None

if "chunks" not in st.session_state:
    st.session_state.chunks = []

if process_btn:
    if not google_api_key:
        st.sidebar.error("Please enter your Google API Key!")
    else:
        # Process documents locally
        combined_doc_text = ""
        if uploaded_files:
            for file in uploaded_files:
                file_type = file.name.split('.')[-1].lower()
                combined_doc_text += extract_text_from_file(file, file_type) + "\n\n"
        st.session_state.doc_text = combined_doc_text

        # Process YouTube captions via API
        if youtube_url.strip():
            captions = get_youtube_captions(youtube_url, google_api_key)
            st.session_state.yt_text = captions or "No captions found."

        # Combine text
        combined_text = (st.session_state.doc_text or "") + "\n" + (st.session_state.yt_text or "")

        # Chunk text (use min chunk size for safety)
        chunk_size = min(doc_chunk_size, yt_chunk_size)
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=100)
        chunks = splitter.split_text(combined_text)
        st.session_state.chunks = chunks

        # Embed chunks and create FAISS index
        embeddings = embed_chunks(chunks)
        faiss_index = create_faiss_index(chunks, embeddings)
        st.session_state.faiss_index = faiss_index

        st.success("Content processed successfully!")

# Main tabs
tabs = st.tabs(["Documents", "YouTube Transcript", "Chat"])

with tabs[0]:
    st.header("Documents Content")
    if st.session_state.doc_text:
        st.text_area("Extracted Text", st.session_state.doc_text, height=300)
    else:
        st.info("Upload documents and click Process.")

with tabs[1]:
    st.header("YouTube Transcript")
    if st.session_state.yt_text:
        st.text_area("Transcript", st.session_state.yt_text, height=300)
    else:
        st.info("Paste YouTube URL and click Process.")

with tabs[2]:
    st.header("Chat with your content")

    question = st.text_input("Ask a question about your content here:")

    if question:
        if not st.session_state.faiss_index or not st.session_state.chunks:
            st.warning("Please upload/process content first.")
        elif not google_api_key:
            st.warning("Please enter your Google API Key in the sidebar.")
        else:
            results = semantic_search(st.session_state.faiss_index, st.session_state.chunks, question)
            answer = generate_answer(question, results, google_api_key)
            st.markdown("### Answer:")
            st.write(answer)
