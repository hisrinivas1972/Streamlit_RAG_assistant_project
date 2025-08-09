from langchain.vectorstores.faiss import FAISS
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.llms import Ollama

def get_rag_chain(index, chunks):
    retriever = FAISS(embedding_function=HuggingFaceEmbeddings(), index=index, texts=chunks).as_retriever()
    llm = Ollama(model="mistral")  # replace with your local model name
    qa = RetrievalQA.from_chain_type(llm=llm, retriever=retriever)
    return qa
