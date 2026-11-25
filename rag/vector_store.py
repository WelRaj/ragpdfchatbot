from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from rag.embedding import get_embedding_model


def create_vector_store(chunks):

    embeddings = get_embedding_model()

    # pdf_chunker returns dictionaries so page/source metadata is preserved.
    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "page": chunk.get("page"),
                "source": chunk.get("source"),
            },
        )
        for chunk in chunks
    ]

    vector_store = FAISS.from_documents(
        documents=documents,
        embedding=embeddings
    )

    vector_store.save_local("faiss_index")

    return vector_store
