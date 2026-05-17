# Clinical Research Agent 🩺

An evidence-based, strict-constraint clinical retrieval engine. This application leverages a high-performance **React (Vite + Tailwind CSS)** frontend paired with a advanced **LangGraph + FastAPI** backend pipeline to search, grade, and synthesize medical literature with absolute zero hallucination tolerance.

---

## 🚀 Key Features

* **Strict Source Anchoring:** Restricts discovery paths exclusively to verified medical domains (`nature.com`, `ahajournals.org`, `ncbi.nlm.nih.gov/pmc`).
* **Zero-Hallucination Guardrails:** Employs an automated multi-agent grading loop. If data is insufficient or unverifiable, the system acts on a strict fallback loop returning *"I don't know"*.
* **Sentence-by-Sentence Citations:** Strips internal agent meta-text thoughts and formats clean inline brackets `[1]`, `[2]` mapping sentences directly to context items.

---

## 🏗️ System Architecture

The application operates as a distributed Multi-Agent workflow built on LangGraph:

1. **Retrieval Node:** Targets clinical constraints via targeted search run executions.
2. **Grading Node:** A strict evaluator bouncer that approves or rejects source contexts using structured JSON scoring.
3. **Generator Node:** Synthesizes the clean final output based on the strict medical prompt parameters.

---

## 🛠️ Tech Stack

### Frontend
* **Framework:** React 18 (Vite template)
* **Styling:** Tailwind CSS
* **Formatting:** React Markdown

### Backend
* **Framework:** FastAPI (Python)
* **Orchestration:** LangGraph & LangCore
* **LLM Integration:** LangChain Core Parsers

---
### 🔑 Environment Configuration

Before running the application, you must configure your environment variables. Create a `.env` file in the root of your **backend** directory:

```env
GROQ_API_KEY=your_openai_api_key_here
```

## 💻 Getting Started

### Prerequisites
* Node.js (v18+ recommended)
* Python 3.10+

### 1. Backend Setup
Navigate to your backend repository, install dependencies, and spin up the Uvicorn engine:
```bash
# Install required packages
pip install langgraph langchain-core langchain-openai fastapi uvicorn

# Start the local server
uvicorn main:app --reload
```

### 2. Frontend Setup
```bash
# Install dependencies
npm install

# Install markdown parser support
npm install react-markdown

# Run the development environment
npm run dev
```