
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Step 2: Create vector DB (in-memory)
db = Chroma(
    collection_name="bot_personas",
    embedding_function=embedding
)

# Step 3: Define STRONG personas
personas = [
    ("bot_a", "I strongly support AI, machine learning, OpenAI, crypto, and futuristic technology. I believe AI will replace jobs and improve humanity."),
    
    ("bot_b", "I criticize AI, big tech, capitalism, and billionaires. I believe technology is harming society, reducing privacy, and increasing inequality."),
    
    ("bot_c", "I focus on finance, stock market, trading, ROI, and economic trends. I evaluate everything based on money and profit.")
]

# Step 4: Add personas 
texts = [p[1] for p in personas]
metadatas = [{"bot_id": p[0]} for p in personas]

db.add_texts(texts, metadatas=metadatas)

# Step 5: Routing function
def route_post_to_bots(post_content):
    results = db.similarity_search_with_score(post_content, k=3)

    selected = []
    print("\n--- DEBUG SCORES ---")

    for doc, score in results:
        print(f"{doc.metadata['bot_id']} → score: {score}")

        if score < 1.0:   # relaxed threshold
            selected.append(doc.metadata["bot_id"])

    return selected


# Step 6: Test
if __name__ == "__main__":
    post = "OpenAI released a new AI model that may replace developers"

    bots = route_post_to_bots(post)
    print("\nSelected bots:", bots)