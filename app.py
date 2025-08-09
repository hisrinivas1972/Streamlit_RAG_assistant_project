import streamlit as st
from utils.document_handler import extract_text_from_file
from utils.youtube_transcriber import download_audio, transcribe_audio
from utils.embedder import embed_chunks, create_faiss_index
from utils.rag_pipeline import get_rag_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter

st.set_page_config(page_title="Local RAG Assistant", layout="wide")

# Sidebar Inputs
st.sidebar.title("Upload & Settings")

uploaded_files = st.sidebar.file_uploader(
    "Upload documents/images (PDF, DOCX, TXT, XLSX, PNG, JPG)", 
    accept_multiple_files=True,
    type=["pdf", "docx", "txt", "xlsx", "png", "jpg", "jpeg"]
)

doc_chunk_size = st.sidebar.selectbox(
    "Chunk size for Documents (chars)",
    options=list(range(100, 2001, 100)),
    index=19
)

st.sidebar.markdown("---")

youtube_url = st.sidebar.text_input("YouTube Video URL")

yt_chunk_size = st.sidebar.selectbox(
    "Chunk size for YouTube (chars)",
    options=list(range(100, 3001, 100)),
    index=19
)

st.sidebar.markdown("---")

process_btn = st.sidebar.button("Process Content")

# State holders for extracted text
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""

if "yt_text" not in st.session_state:
    st.session_state.yt_text = ""

if process_btn:
    # Process documents
    doc_text_accum = ""
    if uploaded_files:
        for file in uploaded_files:
            file_type = file.name.split('.')[-1].lower()
            text = extract_text_from_file(file, file_type)
            doc_text_accum += text + "\n\n"
    st.session_state.doc_text = doc_text_accum

    # Process YouTube
    if youtube_url.strip():
        audio_path = download_audio(youtube_url)
        transcript = transcribe_audio(audio_path)
        st.session_state.yt_text = transcript

    st.success("Processing completed!")

# Main layout with tabs
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
    st.header("Chat with Your Content")

    question = st.text_input("Ask a question about your content here:")
    if question:
        # Combine texts
        combined_text = (st.session_state.doc_text or "") + "\n" + (st.session_state.yt_text or "")
        if not combined_text.strip():
            st.warning("Please upload or transcribe content first.")
        else:
            # Chunk and limit by chunk sizes (choose min of two chunk sizes here for example)
            from langchain.text_splitter import RecursiveCharacterTextSplitter

            chunk_limit = min(doc_chunk_size, yt_chunk_size)
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            chunks = splitter.split_text(combined_text)

            def get_context_up_to_limit(chunks, max_chars):
                context = ""
                for chunk in chunks:
                    remaining = max_chars - len(context)
                    if remaining <= 0:
                        break
                    if len(chunk) > remaining:
                        context += chunk[:remaining]
                        break
                    else:
                        context += chunk
                return context

            limited_context = get_context_up_to_limit(chunks, chunk_limit)

            embeddings = embed_chunks([limited_context])
            index = create_faiss_index([limited_context], embeddings)
            qa = get_rag_chain(index, [limited_context])

            answer = qa.run(question)
            st.markdown("### Answer:")
            st.write(answer)
