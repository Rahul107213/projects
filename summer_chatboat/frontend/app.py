import streamlit as st
import requests
import os

# Set backend URL (defaults to local docker network, but can be overridden on Railway)
BACKEND_URL = os.environ.get("BACKEND_URL", "http://backend:8000")
st.set_page_config(page_title="PDF AI Chatbot", page_icon="📄", layout="wide")
# Custom CSS for "vibes"
st.markdown("""
<style>
    /* Dark theme & glassmorphism base */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #58a6ff !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: rgba(22, 27, 34, 0.8);
        backdrop-filter: blur(10px);
        border-right: 1px solid #30363d;
    }
    
    /* Upload Box */
    .stFileUploader {
        border-radius: 10px;
        padding: 10px;
        background: rgba(48, 54, 61, 0.3);
        border: 1px dashed #58a6ff;
    }
    
    /* Chat bubbles */
    .stChatMessage {
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        backdrop-filter: blur(5px);
    }
    [data-testid="stChatMessage"]:nth-child(odd) {
        background: rgba(33, 38, 45, 0.8);
        border: 1px solid #30363d;
    }
    [data-testid="stChatMessage"]:nth-child(even) {
        background: rgba(88, 166, 255, 0.1);
        border: 1px solid #58a6ff;
    }
    /* Input Box */
    .stChatInput {
        background: rgba(22, 27, 34, 0.8) !important;
        border: 1px solid #30363d !important;
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)
st.title("✨ AI Document Assistant")
st.markdown("Upload a PDF and instantly ask questions or get a quick summary.")
# Sidebar for Upload
with st.sidebar:
    st.header("📄 Upload Document")
    uploaded_files = st.file_uploader("Choose PDF files", type=["pdf"], accept_multiple_files=True)
    
    if uploaded_files:
        if st.button("Process PDFs", use_container_width=True):
            with st.spinner("Processing documents..."):
                files = []
                for f in uploaded_files:
                    files.append(("files", (f.name, f.getvalue(), "application/pdf")))
                    
                try:
                    response = requests.post(f"{BACKEND_URL}/upload", files=files)
                    if response.status_code == 200:
                        st.success("PDFs processed successfully!")
                        st.session_state["pdf_processed"] = True
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Failed to connect to backend: {str(e)}")
                    
    st.markdown("---")
    if st.button("🗑️ Clear Memory", use_container_width=True):
        try:
            requests.post(f"{BACKEND_URL}/clear")
            st.session_state["pdf_processed"] = False
            st.session_state.messages = []
            st.success("Memory cleared!")
        except:
            st.error("Failed to clear memory.")
# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
# React to user input
if prompt := st.chat_input("Ask a question about your PDF or type 'summarize'..."):
    if not st.session_state.get("pdf_processed", False):
        st.warning("Please upload and process a PDF first.")
    else:
        # Display user message in chat message container
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        # Send request to backend
        with st.chat_message("assistant"):
            try:
                payload = {
                    "query": prompt,
                    "history": st.session_state.messages[:-1] 
                }
                
                # We use iter_lines to stream the response chunks
                res = requests.post(f"{BACKEND_URL}/chat_stream", json=payload, stream=True)
                
                if res.status_code == 200:
                    # Streamlit's write_stream expects a generator of strings
                    def stream_generator():
                        for chunk in res.iter_content(chunk_size=None, decode_unicode=True):
                            if chunk:
                                yield chunk
                                
                    answer = st.write_stream(stream_generator())
                else:
                    answer = f"Error: {res.text}"
                    st.error(answer)
                    
            except Exception as e:
                answer = f"Failed to connect to backend: {str(e)}"
                st.error(answer)
                
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": answer})