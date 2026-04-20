# langgraph_engine.py

"""
Phase 2: Autonomous Content Engine (LangGraph)

This module builds a multi-step AI pipeline where:
1. The LLM decides a topic based on persona
2. A mock search tool provides real-world context
3. The LLM generates a structured post (JSON output)
"""

from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_ollama import ChatOllama
import json
import re


# -------------------------------
# 1. STATE DEFINITION
# -------------------------------
class GraphState(TypedDict):
    """
    Represents the shared state flowing through the LangGraph pipeline.
    """
    bot_id: str
    persona: str
    topic: str
    search_results: str
    post_content: dict


# -------------------------------
# 2. LLM SETUP
# -------------------------------
# Using local LLaMA model via Ollama
# temperature=0 ensures deterministic and structured output
llm = ChatOllama(
    model="llama3.1:latest",
    temperature=0
)


# -------------------------------
# 3. MOCK SEARCH TOOL
# -------------------------------
def mock_searxng_search(query: str) -> str:
    """
    Simulates a search engine by returning hardcoded news
    based on keywords in the query.
    """
    query = query.lower()

    if "ai" in query:
        return "OpenAI releases a powerful new model that may replace developers."
    elif "crypto" in query:
        return "Bitcoin hits all-time high amid institutional adoption."
    elif "market" in query or "finance" in query:
        return "Global stock markets surge due to strong economic signals."
    else:
        return "No major news found."


# -------------------------------
# 4. SAFE JSON PARSER
# -------------------------------
def safe_json_parse(text: str, state: GraphState) -> dict:
    """
    Extracts JSON from LLM output.

    If the model returns invalid JSON, fallback ensures
    the pipeline does not break.
    """
    try:
        json_str = re.search(r"\{.*\}", text, re.DOTALL).group()
        return json.loads(json_str)
    except:
        return {
            "bot_id": state["bot_id"],
            "topic": state["topic"],
            "post_content": text[:200]
        }


# -------------------------------
# 5. NODE 1: DECIDE TOPIC
# -------------------------------
def decide_topic(state: GraphState) -> dict:
    """
    LLM selects a topic based on the bot persona.

    Output is constrained to simple keywords to ensure
    compatibility with the search tool.
    """
    prompt = f"""
    You are:
    {state['persona']}

    Decide ONE topic you want to post about today.

    RULES:
    - Use simple keywords like: AI, crypto, market
    - Keep it 1-2 words only
    - Do NOT use full sentences

    Output only the topic.
    """

    topic = llm.invoke(prompt).content.strip()

    return {"topic": topic.lower()}


# -------------------------------
# 6. NODE 2: SEARCH
# -------------------------------
def search_node(state: GraphState) -> dict:
    """
    Fetches context using the mock search tool.
    """
    results = mock_searxng_search(state["topic"])
    return {"search_results": results}


# -------------------------------
# 7. NODE 3: GENERATE POST
# -------------------------------
def generate_post(state: GraphState) -> dict:
    """
    Generates a persona-driven post using:
    - persona (system behavior)
    - search results (context)
    """

    prompt = f"""
    You are:
    {state['persona']}

    Context:
    {state['search_results']}

    TASK:
    Write a strong, opinionated tweet (max 280 characters).

    RULES:
    - Output ONLY valid JSON
    - No explanation
    - No extra text

    FORMAT:
    {{
      "bot_id": "{state['bot_id']}",
      "topic": "{state['topic']}",
      "post_content": "..."
    }}
    """

    response = llm.invoke(prompt).content.strip()

    parsed = safe_json_parse(response, state)

    return {"post_content": parsed}


# -------------------------------
# 8. BUILD GRAPH
# -------------------------------
# Define workflow pipeline
builder = StateGraph(GraphState)

builder.add_node("decide", decide_topic)
builder.add_node("search", search_node)
builder.add_node("generate", generate_post)

builder.set_entry_point("decide")

builder.add_edge("decide", "search")
builder.add_edge("search", "generate")

graph = builder.compile()


# -------------------------------
# 9. TEST EXECUTION
# -------------------------------
if __name__ == "__main__":
    initial_state = {
        "bot_id": "bot_a",
        "persona": "I strongly believe AI and crypto will transform the future. I support OpenAI, innovation, and technology growth.",
        "topic": "",
        "search_results": "",
        "post_content": {}
    }

    result = graph.invoke(initial_state)

    print("\n=== FINAL OUTPUT ===\n")
    print(json.dumps(result["post_content"], indent=2))