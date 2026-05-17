import os
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# IMPORTANT: Load the .env file BEFORE importing the agent workflow
load_dotenv() 

from agent_workflow import rag_app

app = FastAPI(
    title="Medical Agentic RAG API",
    description="API for querying medical documents with strict hallucination prevention via OpenRouter."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your React app to talk to this API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    question: str
    answer: str
    sources_used: list[str]

@app.post("/api/v1/query", response_model=QueryResponse)
async def ask_medical_question(request: QueryRequest):
    try:
        # Initialize the state for the graph
        inputs = {"question": request.question}
        
        # Invoke the LangGraph workflow
        result = rag_app.invoke(inputs)
        
        # Extract the final generation and the sources of the *approved* documents
        final_answer = result.get("generation", "Error: No generation found.")
        approved_docs = result.get("documents", [])
        sources = [doc.metadata.get("source", "Unknown Source") for doc in approved_docs]
        
        return QueryResponse(
            question=request.question,
            answer=final_answer,
            sources_used=sources
        )
        
    except Exception as e:
        print(f"Error occurred: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error during workflow execution.")

@app.get("/")
async def root():
    return {"status": "Medical RAG API is running safely via OpenRouter."}