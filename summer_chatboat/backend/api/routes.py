import os
from typing import List, Dict
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from core import state


from services.pdf_processor import process_pdf
from services.chat_service import get_answer



# Load .env from current directory
load_dotenv(override=True)
app = FastAPI()


class ChatRequest(BaseModel):
    query: str
    history: List[Dict[str, str]] = []
    
    
@app.post("/upload")
async def upload_pdf(files: List[UploadFile] = File(...)):
    for file in files:
        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
    try:
        for file in files:
            process_pdf(file.file)
        return {"message": "PDFs successfully processed and merged into memory."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
@app.post("/clear")
async def clear_memory():
    state.vector_store = None
    return {"message": "Memory cleared."}
    
@app.post("/chat")
async def chat_with_pdf(request: ChatRequest):
    if not state.vector_store:
        raise HTTPException(status_code=400, detail="Please upload a PDF first.")
    try:
        result = get_answer(request.query, request.history)
        if isinstance(result, dict):
            return result
        return {"answer": result}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        error_msg = str(e)
        if "503" in error_msg or "UNAVAILABLE" in error_msg:
            raise HTTPException(status_code=503, detail="Google's AI servers are currently overloaded. Please try again in a few moments!")
        elif "429" in error_msg or "quota" in error_msg.lower():
            raise HTTPException(status_code=429, detail="API token quota exceeded. Please wait a bit or try a different API key.")
        raise HTTPException(status_code=500, detail=error_msg)

from fastapi.responses import StreamingResponse
from services.chat_service import get_answer_stream

@app.post("/chat_stream")
async def chat_stream_endpoint(request: ChatRequest):
    if not state.vector_store:
        raise HTTPException(status_code=400, detail="Please upload a PDF first.")
        
    async def event_generator():
        try:
            async for chunk in get_answer_stream(request.query, request.history):
                yield chunk
        except Exception as e:
            yield f"[Stream Error: {str(e)}]"
            
    return StreamingResponse(event_generator(), media_type="text/plain")
