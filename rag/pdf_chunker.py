
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(extracted_data):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )

    all_chunks = []

    for item in extracted_data:

        chunks = splitter.split_text(item["text"])

        for chunk in chunks:

            all_chunks.append({
                "text": chunk,
                "page": item["page"],
                "source": item["source"]
            })

    return all_chunks
