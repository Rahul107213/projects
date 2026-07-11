import os
import tempfile
import shutil


from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from core import state


def process_pdf(file_obj):
    """
    Saves the uploaded file temporarily, extracts text, splits it into chunks,
    generates embeddings, and stores them in the global FAISS vector store.
    """
    # Save file to a temporary location
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        shutil.copyfileobj(file_obj, tmp_file)
        tmp_path = tmp_file.name
        
        
    try:
        # Load PDF
        loader = PyPDFLoader(tmp_path)
        docs = loader.load()
        
        
        # Split into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(docs)
        
        
        # Create embeddings and vector store
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2", google_api_key=api_key)
        
        new_vector_store = FAISS.from_documents(chunks, embeddings)
        if state.vector_store is None:
            state.vector_store = new_vector_store
        else:
            state.vector_store.merge_from(new_vector_store)
        
    finally:
        # Clean up temp file
        os.remove(tmp_path)
