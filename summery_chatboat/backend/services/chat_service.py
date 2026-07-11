import os
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_classic.chains import create_retrieval_chain, create_history_aware_retriever
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from core import state


def get_answer(query: str, history: List[Dict[str, str]] = None) -> str:
    """
    Takes a user query and chat history, fetches relevant context from FAISS,
    and asks Google Gemini to answer based on that context.
    """
    if not state.vector_store:
        raise ValueError("Vector store is not initialized. Please upload a PDF first.")
        
    if history is None:
        history = []
        
    # Convert dict history from frontend to LangChain message objects
    chat_history = []
    for msg in history:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))
            
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables.")
        
    models = ["gemini-2.0-flash-lite", "gemini-3.5-flash", "gemini-2.5-pro"]
    warning_msg = None
    
    for i, model_name in enumerate(models):
        try:
            llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.2, google_api_key=api_key)
            
            contextualize_q_system_prompt = (
                "Given a chat history and the latest user question "
                "which might reference context in the chat history, "
                "formulate a standalone question which can be understood "
                "without the chat history. Do NOT answer the question, "
                "just reformulate it if needed and otherwise return it as is."
            )
            
            contextualize_q_prompt = ChatPromptTemplate.from_messages([
                ("system", contextualize_q_system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            retriever = state.vector_store.as_retriever(search_kwargs={"k": 3})
            history_aware_retriever = create_history_aware_retriever(
                llm, retriever, contextualize_q_prompt
            )
            
            system_prompt = (
                "You are a helpful assistant for analyzing documents. "
                "You may be provided with context extracted from MULTIPLE different documents (for example, a resume and a job description). "
                "Use the provided context below to answer the user's question. "
                "If the user asks you to compare, find similarities, or match requirements across the documents, synthesize the information across all the provided context carefully. "
                "If the user asks for a summary, summarize based on the context. "
                "If the answer is not in the context, just say you don't know based on the provided documents. "
                "Context: {context}"
            )
            
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
            
            response = rag_chain.invoke({
                "input": query,
                "chat_history": chat_history
            })
            
            return {"answer": response["answer"], "warning": warning_msg}
            
        except Exception as e:
            if i == len(models) - 1:
                raise e
                
            err_str = str(e).lower()
            if "quota" in err_str or "429" in err_str:
                warning_msg = f"⚠️ Notice: The primary model ({model_name}) exceeded its token quota. Automatically switched to a backup model!"
            elif "503" in err_str or "unavailable" in err_str:
                warning_msg = f"⚠️ Notice: The primary model ({model_name}) is currently overloaded. Automatically switched to a backup model!"
            else:
                warning_msg = f"⚠️ Notice: The primary model ({model_name}) encountered an error. Automatically switched to a backup model!"

async def get_answer_stream(query: str, history: List[Dict[str, str]] = None):
    if not state.vector_store:
        yield "Error: Vector store is not initialized. Please upload a PDF first."
        return
        
    if history is None:
        history = []
        
    chat_history = []
    for msg in history:
        if msg["role"] == "user":
            chat_history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            chat_history.append(AIMessage(content=msg["content"]))
            
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        yield "Error: GOOGLE_API_KEY not found in environment variables."
        return
        
    models = ["gemini-2.0-flash-lite", "gemini-3.5-flash", "gemini-2.5-pro"]
    
    for i, model_name in enumerate(models):
        try:
            llm = ChatGoogleGenerativeAI(model=model_name, temperature=0.2, google_api_key=api_key)
            
            contextualize_q_prompt = ChatPromptTemplate.from_messages([
                ("system", "Given a chat history and the latest user question formulate a standalone question. Do NOT answer the question."),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            retriever = state.vector_store.as_retriever(search_kwargs={"k": 3})
            history_aware_retriever = create_history_aware_retriever(llm, retriever, contextualize_q_prompt)
            
            qa_prompt = ChatPromptTemplate.from_messages([
                ("system", 
                "You are a helpful assistant for analyzing documents. "
                "You may be provided with context extracted from MULTIPLE different documents (for example, a resume and a job description). "
                "Use the provided context below to answer the user's question. "
                "If the user asks you to compare, find similarities, or match requirements across the documents, synthesize the information across all the provided context carefully. "
                "If the user asks for a summary, summarize based on the context. "
                "If the answer is not in the context, just say you don't know based on the provided documents. "
                "Context: {context}"),
                MessagesPlaceholder("chat_history"),
                ("human", "{input}"),
            ])
            
            question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
            rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
            
            stream_started = False
            async for chunk in rag_chain.astream({"input": query, "chat_history": chat_history}):
                if "answer" in chunk:
                    stream_started = True
                    yield chunk["answer"]
                    
            return
            
        except Exception as e:
            if stream_started or i == len(models) - 1:
                yield f"\n\n[Error during generation: {str(e)}]"
                return
            
            err_str = str(e).lower()
            if "quota" in err_str or "429" in err_str:
                yield f"*(⚠️ {model_name} hit quota. Switched to backup. Please wait...)*\n\n"
            else:
                yield f"*(⚠️ {model_name} overloaded. Switched to backup. Please wait...)*\n\n"
