from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def embed_chunks(chunks):
    embs = model.encode(chunks)
    index = faiss.IndexFlatL2(embs.shape[1])
    index.add(embs)
    return index, embs

def search_similar_chunks(query, chunks, index, embs, top_k=3):
    q_emb = model.encode([query])
    _, idxs = index.search(q_emb, top_k)
    return [chunks[i] for i in idxs[0] if i < len(chunks)]
