# router.py

"""
Phase 1: Vector-Based Persona Routing

This module:
- Stores bot personas as vector embeddings
- Matches incoming posts with relevant bots using semantic similarity
"""

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings


# -------------------------------
# 1. Initialize Embedding Model
# -------------------------------
# We use a lightweight sentence-transformer model
# to convert text into vector representations
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# -------------------------------
# 2. Create Vector Database
# -------------------------------
# In-memory ChromaDB simulates pgvector-like storage
db = Chroma(
    collection_name="bot_personas",
    embedding_function=embedding
)


# -------------------------------
# 3. Define Bot Personas
# -------------------------------
# Each bot has a unique perspective
personas = [
    (
        "bot_a",
        "I strongly support AI, machine learning, OpenAI, crypto, and futuristic technology. "
        "I believe AI will replace jobs and improve humanity."
    ),
    (
        "bot_b",
        "I criticize AI, big tech, capitalism, and billionaires. "
        "I believe technology is harming society, reducing privacy, and increasing inequality."
    ),
    (
        "bot_c",
        "I focus on finance, stock market, trading, ROI, and economic trends. "
        "I evaluate everything based on money and profit."
    )
]


# -------------------------------
# 4. Store Personas in Vector DB
# -------------------------------
texts = [p[1] for p in personas]
metadatas = [{"bot_id": p[0]} for p in personas]

db.add_texts(texts, metadatas=metadatas)


# -------------------------------
# 5. Routing Function
# -------------------------------
def route_post_to_bots(post_content: str, threshold: float = 1.0):
    """
    Routes a post to relevant bots using semantic similarity.

    Args:
        post_content (str): Incoming post text
        threshold (float): Distance threshold (lower = stricter match)

    Returns:
        list: List of selected bot IDs
    """

    results = db.similarity_search_with_score(post_content, k=3)

    selected = []

    print("\n--- DEBUG SCORES ---")

    for doc, score in results:
        bot_id = doc.metadata["bot_id"]
        print(f"{bot_id} → score: {score}")

        # Lower score = more similar
        if score < threshold:
            selected.append(bot_id)

    return selected


# -------------------------------
# 6. Test Execution
# -------------------------------
if __name__ == "__main__":
    test_post = "OpenAI released a new AI model that may replace developers"

    selected_bots = route_post_to_bots(test_post)

    print("\nSelected bots:", selected_bots)