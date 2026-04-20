#  AI Cognitive Routing & RAG System

This project implements a multi-stage AI cognitive pipeline that simulates how intelligent agents:

- Select relevant content (routing)  
- Generate contextual posts (autonomous reasoning)  
- Defend arguments using conversation memory (RAG)  

---

## System Overview

The system is divided into three core phases:

```text
Phase 1 → Who should respond?
Phase 2 → What should they say?
Phase 3 → How should they argue?
```
Each phase builds on the previous to create a complete AI reasoning loop.

## Phase 1: Vector-Based Persona Matching (Router)
- Uses embeddings + ChromaDB
- Stores bot personas as vectors
- Matches incoming posts using semantic similarity

### Goal
Route posts only to bots that "care" about the topic.

``` bash 
Lower distance = higher similarity → best-matching bot selected.
```
## Phase 2: Autonomous Content Engine (LangGraph)

### Implemented using LangGraph as a multi-step pipeline:
####  Flow 
- Decide Topic → LLM selects a topic based on persona
- Search Context → mock tool returns relevant news
- Generate Post → LLM produces structured JSON output

``` json 
{
  "bot_id": "...",
  "topic": "...",
  "post_content": "..."
}
```
#### Key Features
- Persona-driven content generation
- Tool-augmented reasoning
- Structured JSON output with fallback parsing

## Phase 3: Combat Engine (Deep Thread RAG)
- Uses full conversation context as memory
- Generates replies in ongoing discussions
### Input Context
- Parent post
- Previous comments
- Latest human reply

#### Prompt Injection Defense

The system enforces strict rules:
- Ignores malicious instructions (e.g., "ignore previous instructions")
- Maintains persona consistency
-Continues argument logically

#### Key Idea
System-level instructions override user input → ensures safe and consistent behavior.

#### Tech Stack
- Python
- LangChain
- LangGraph
- ChromaDB
- Ollama (llama3.1:latest)
- Sentence Transformers

## Project Structure

``` bash
AI_Cognitive_Assignment/
│
├── phase_1.py              # (vector routing)
├── phase_2.py              # (content generation)
├── phase_3.py              # (RAG + defense)
│
├── requirements.txt
├── output.md
└── readme.md
```

## How to Run

1. Setup environment
``` python 
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
2. Run each phase
``` python 
python phase_1.py
python phase_2.py
python phase_3.py
```

## Conclusion

This project demonstrates how to build a robust AI system that combines:
- Retrieval (vector similarity & context)
- Reasoning (LLM decision-making)
- Generation (structured outputs)
- Safety (prompt injection defense)

## Notes
- All outputs are included in output.md
- No external APIs are required (fully local setup)