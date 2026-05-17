import os
from typing import List, TypedDict
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field  # Using standard Pydantic (Fix applied)
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from langchain_groq import ChatGroq
# ==========================================
# 1. SETUP & STATE
# ==========================================
# The API key is loaded in main.py via dotenv before this file is executed.
# We are using ChatOpenAI but pointing it to OpenRouter's servers.

llm = ChatGroq(
    api_key=os.environ.get("GROQ_API_KEY"),
    model="llama-3.3-70b-versatile", # Meta's massive 70B model, permanently free here
    temperature=0
)

class GraphState(TypedDict):
    question: str
    documents: List[Document]
    generation: str

# ==========================================
# 2. AGENT NODES
# ==========================================

def retrieve_node(state: GraphState):
    """Agent 1: The Web Researcher. Searches ONLY trusted medical sites."""
    print("---NODE: LIVE WEB RETRIEVAL---")
    question = state["question"]
    
    # 1. Initialize the free search wrapper
    wrapper = DuckDuckGoSearchAPIWrapper()
    
    # 2. The Strict Domain Filter
    # PubMed Central (PMC) is included because it hosts open-access Nature/AHA papers
    trusted_domains = "site:nature.com OR site:ahajournals.org OR site:ncbi.nlm.nih.gov/pmc"
    
    # Combine the user's question with our strict filters
    search_query = f"{question} {trusted_domains}"
    print(f"   -> Executing Search: {search_query}")
    
    try:
        # 3. Fetch the top 4 results from the web
        raw_results = wrapper.results(search_query, max_results=4)
        
        # 4. Convert the web results into Document objects for the Grader Agent
        documents = []
        for result in raw_results:
            doc = Document(
                page_content=result.get("snippet", ""),
                metadata={
                    "source": result.get("link", "Unknown Web Source"),
                    "title": result.get("title", "No Title")
                }
            )
            documents.append(doc)
            print(f"   -> Found source: {result.get('link')}")
            
    except Exception as e:
        print(f"   -> Search Failed: {e}")
        documents = [] # If search fails, pass empty docs to trigger the fallback

    return {"documents": documents, "question": question}


def grade_documents_node(state: GraphState):
    """Agent 2: The Bouncer. Evaluates relevance to prevent hallucination."""
    print("---NODE: GRADE DOCUMENTS---")
    question = state["question"]
    documents = state["documents"]

    class GradeDocuments(BaseModel):
        binary_score: str = Field(description="Documents are relevant to the question, 'yes' or 'no'")

    structured_llm_grader = llm.with_structured_output(GradeDocuments)

    system_prompt = """You are a strict medical evaluator assessing relevance of a retrieved document to a user question. \n 
    If the document contains specific facts, mechanisms, or data that directly answer the user question, grade it as 'yes'. \n
    If the document is too vague, does not contain the specific answer, or you are unsure, grade it as 'no'. Do not guess."""
    
    grade_prompt = PromptTemplate(
        template=system_prompt + "\n\nRetrieved document: \n\n {document} \n\n User question: {question}",
        input_variables=["document", "question"],
    )
    
    retrieval_grader = grade_prompt | structured_llm_grader

    filtered_docs = []
    for d in documents:
        score = retrieval_grader.invoke({"question": question, "document": d.page_content})
        if score.binary_score.lower() == "yes":
            print("   -> Grader: Document Approved")
            filtered_docs.append(d)
        else:
            print("   -> Grader: Document Rejected (Potential Hallucination Blocked)")

    return {"documents": filtered_docs, "question": question}


def generate_node(state: GraphState):
    """Agent 3: The Writer. Drafts the response using ONLY approved context."""
    print("---NODE: GENERATE---")
    question = state["question"]
    documents = state["documents"]
    
    context = "\n\n".join([f"Content: {d.page_content} \nCitation: [{d.metadata.get('source', 'Unknown')}]" for d in documents])

    system_prompt = """You are a medical research assistant. 
    Use the following pieces of retrieved context to answer the question. 
    If the context does not contain the answer, say "I don't know". Do not use outside knowledge.
    You MUST append the exact Citation provided in the context to the end of your answer.
    
    Context: {context}"""
    
    prompt = PromptTemplate(
        template=system_prompt + "\n\nQuestion: {question} \nAnswer:",
        input_variables=["context", "question"],
    )
    
    rag_chain = prompt | llm
    generation = rag_chain.invoke({"context": context, "question": question})
    
    return {"documents": documents, "question": question, "generation": generation.content}


def fallback_node(state: GraphState):
    """Agent 4: The Safety Net. Triggers when no relevant docs are found."""
    print("---NODE: FALLBACK---")
    return {
        "documents": state["documents"], 
        "question": state["question"], 
        "generation": "I don't know. Reliable information regarding this specific query was not found in the trusted medical journals."
    }

# ==========================================
# 3. ROUTING LOGIC
# ==========================================

def decide_to_generate(state: GraphState):
    """Determines next step based on document grading."""
    filtered_documents = state["documents"]
    
    if not filtered_documents:
        print("---ROUTING: ALL DOCS REJECTED -> GO TO FALLBACK---")
        return "fallback"
    else:
        print("---ROUTING: DOCS APPROVED -> GO TO GENERATE---")
        return "generate"

# ==========================================
# 4. BUILD THE GRAPH
# ==========================================

workflow = StateGraph(GraphState)

workflow.add_node("retrieve", retrieve_node)
workflow.add_node("grade_documents", grade_documents_node)
workflow.add_node("generate", generate_node)
workflow.add_node("fallback", fallback_node)

workflow.set_entry_point("retrieve")
workflow.add_edge("retrieve", "grade_documents")

workflow.add_conditional_edges(
    "grade_documents",
    decide_to_generate,
    {
        "generate": "generate",
        "fallback": "fallback",
    },
)

workflow.add_edge("generate", END)
workflow.add_edge("fallback", END)

# Compile the final application
rag_app = workflow.compile()