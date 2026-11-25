import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

PROMPT_TEMPLATE = """Answer the question using only the context below.
If the answer is not in the context, say "I couldn't find that in the uploaded PDF."

Context:
{context}

Question:
{question}
"""

def generate_answer(query: str, docs: list):
    context = "\n\n".join(doc.page_content for doc in docs)
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.5-flash-lite",
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        temperature=0.2,
    )

    chain = prompt | llm
    response = chain.invoke({"context": context, "question": query})

    # Gemini may return either plain text or a list of content blocks.
    content = response.content
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                text = item.get("text")
                if text:
                    parts.append(str(text))
            else:
                text = getattr(item, "text", None)
                parts.append(str(text if text is not None else item))
        return "\n".join(parts)
    return str(content)
