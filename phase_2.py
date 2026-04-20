# langgraph_engine.py

from typing import TypedDict
from langgraph.graph import StateGraph
from langchain_ollama import ChatOllama
import json
import re


# -------------------------------
# 1. STATE DEFINITION
# -------------------------------
class GraphState(TypedDict):
    bot_id: str
    persona: str
    topic: str
    search_results: str
    post_content: dict


# -------------------------------
# 2. LLM SETUP (LOCAL)
# -------------------------------
llm = ChatOllama(
    model="llama3.1:latest",
    temperature=0  # ensures stable output
)


# -------------------------------
# 3. MOCK SEARCH TOOL (HARDCODED)
# -------------------------------
def mock_searxng_search(query: str):
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
# 4. SAFE JSON PARSER (CRITICAL)
# -------------------------------
def safe_json_parse(text, state):
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
def decide_topic(state: GraphState):
    prompt = f"""
    You are:
    {state['persona']}

    Decide ONE topic you want to post about today.
    Keep it short (2-5 words).
    Output only the topic.
    """

    topic = llm.invoke(prompt).content.strip()

    return {"topic": topic}


# -------------------------------
# 6. NODE 2: SEARCH TOOL
# -------------------------------
def search_node(state: GraphState):
    results = mock_searxng_search(state["topic"])
    return {"search_results": results}


# -------------------------------
# 7. NODE 3: GENERATE POST
# -------------------------------
def generate_post(state: GraphState):
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
builder = StateGraph(GraphState)

builder.add_node("decide", decide_topic)
builder.add_node("search", search_node)
builder.add_node("generate", generate_post)

builder.set_entry_point("decide")

builder.add_edge("decide", "search")
builder.add_edge("search", "generate")

graph = builder.compile()


# -------------------------------
# 9. RUN TEST
# -------------------------------
if __name__ == "__main__":
    state = {
        "bot_id": "bot_a",
        "persona": "I strongly believe AI and crypto will transform the future. I support OpenAI, innovation, and technology growth.",
        "topic": "",
        "search_results": "",
        "post_content": {}
    }

    result = graph.invoke(state)

    print("\n=== FINAL OUTPUT ===\n")
    print(json.dumps(result["post_content"], indent=2))