from rag.vector_store import create_vector_store

chunks = [
    "Python is a programming language.",
    "Java is used for software development.",
    "Machine learning helps computers learn from data.",
    "Python is used in data science."
]

# Create FAISS database
vector_store = create_vector_store(chunks)

print("FAISS database created!")

# Search relevant chunks
query = "What is Python used for?"

results = vector_store.similarity_search(
    query,
    k=2
)

print("\nRelevant Results:")

for result in results:
    print(result.page_content)
    print("------------------")