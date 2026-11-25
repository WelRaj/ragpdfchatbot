from rag.embedding import get_embedding_model

embeddings = get_embedding_model()

text = "Python is a programming language."

vector = embeddings.embed_query(text)

print("Vector length:", len(vector))
print("First 5 values:", vector[:5])