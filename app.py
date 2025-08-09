import streamlit as st
from utils.document_handler import extract_text_from_file
from utils.youtube_api import get_transcript_from_youtube_url
from utils.embedder import embed_chunks, search_similar_chunks
from utils.vertex_ai import generate_answer_google_api

st.set_page_config(page_title="Google-RAG Assistant", layout="wide")
st.sidebar.title("RAG Assistant Settings")

api_key = st.sidebar.text_input("Google API Key", type="password")
chunk_size = st.sidebar.slider("Chunk size (chars)", 100, 3000, 1000, 100)
source = st.sidebar.radio("Input Source", ["Document", "YouTube"])

text_chunks = []
if source == "Document":
    file = st.sidebar.file_uploader("Upload file (PDF/DOCX/TXT/XLSX/PNG/JPG)", type=["pdf","docx","txt","xlsx","png","jpg","jpeg"])
    if file:
        raw = extract_text_from_file(file, file.name.split(".")[-1].lower())
        text_chunks = [raw[i:i+chunk_size] for i in range(0, len(raw), chunk_size)]
elif source == "YouTube":
    url = st.sidebar.text_input("YouTube URL")
    if url and api_key:
        tx = get_transcript_from_youtube_url(url, api_key)
        text_chunks = [tx[i:i+chunk_size] for i in range(0, len(tx), chunk_size)]

if text_chunks:
    st.success(f"Chunks created: {len(text_chunks)}")
    idx, embs = embed_chunks(text_chunks)
    st.title("Ask your content:")
    query = st.text_input("Question")
    if query and api_key:
        rel = search_similar_chunks(query, text_chunks, idx, embs)
        context = "\n\n".join(rel)
        prompt = f"{context}\n\nQ: {query}\nA:"
        answer = generate_answer_google_api(prompt, api_key)
        st.markdown("## Answer")
        st.write(answer)

st.info("Upload or link content and enter your Google API key to get started.")
