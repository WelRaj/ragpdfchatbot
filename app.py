import html
import streamlit as st

from rag.pdf_processor import extract_pdf
from rag.pdf_chunker import create_chunks
from rag.vector_store import create_vector_store
from rag.llm import generate_answer


st.set_page_config(
    page_title="Chat with PDF files",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --bg: #0d0f18;
            --panel: #272832;
            --card: #11131d;
            --border: #3d3f4d;
            --text: #f5f5f7;
            --muted: #aeb0bd;
            --accent: #ff9800;
            --blue: #1ea7e8;
        }

        .stApp { background: var(--bg); color: var(--text); }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stToolbar"] { visibility: hidden; }
        [data-testid="stDecoration"] { display: none; }

        section[data-testid="stSidebar"] {
            width: 380px !important;
            background: var(--panel);
            border-right: 1px solid #30313d;
        }
        section[data-testid="stSidebar"] > div {
            padding: 135px 26px 24px;
        }
        section[data-testid="stSidebar"] h1 {
            font-size: 34px;
            line-height: 1.1;
            margin-bottom: 24px;
        }
        section[data-testid="stSidebar"] p,
        section[data-testid="stSidebar"] label {
            color: var(--text) !important;
        }

        .brand-row {
            position: fixed;
            top: 26px;
            right: 28px;
            z-index: 2;
            display: flex;
            gap: 24px;
            align-items: center;
            color: var(--text);
            font-size: 18px;
        }
        .brand-row a { color: var(--text); text-decoration: none; font-size: 25px; }
        .hero { max-width: 1040px; margin: 120px auto 0; }
        .hero h1 {
            text-align: center;
            font-size: clamp(34px, 4vw, 60px);
            line-height: 1.12;
            letter-spacing: -1.5px;
            margin: 0 0 34px;
            color: #fafafa;
        }
        .welcome { font-size: 20px; margin-bottom: 52px; }
        .empty-state {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 14px;
            font-size: 21px;
            font-weight: 600;
            margin: 0 auto;
        }
        .bot-icon {
            display: inline-flex;
            width: 48px;
            height: 48px;
            align-items: center;
            justify-content: center;
            border-radius: 13px;
            background: var(--accent);
            font-size: 28px;
        }
        .status-pill {
            display: inline-block;
            margin-top: 12px;
            padding: 5px 11px;
            border-radius: 999px;
            background: #173d2d;
            color: #85e1aa;
            font-size: 13px;
        }
        .upload-note { color: var(--muted); font-size: 16px; margin-top: -8px; }
        .file-count { color: var(--muted); font-size: 14px; margin: 12px 0 4px; }
        .message-wrap {
            max-width: 1040px;
            margin: 32px auto 0;
            padding-bottom: 115px;
        }
        .chat-user, .chat-assistant {
            width: fit-content;
            max-width: 76%;
            padding: 12px 16px;
            border-radius: 16px;
            margin: 12px 0;
            font-size: 16px;
        }
        .chat-user { margin-left: auto; background: #343542; }
        .chat-assistant { background: #1c1f2b; }
        div[data-testid="stChatInput"] {
            max-width: 1040px;
            margin: 0 auto;
        }
        div[data-testid="stChatInput"] > div {
            background: #292a35;
            border: 1px solid #292a35;
            border-radius: 32px;
        }
        div[data-testid="stChatInput"] textarea { color: white; }
        .stButton > button {
            border: 1px solid #555766;
            border-radius: 10px;
            background: transparent;
            color: var(--text);
            font-size: 17px;
            padding: 10px 18px;
            min-height: 50px;
        }
        .stButton > button:hover { border-color: #8f91a0; color: white; }
        section[data-testid="stSidebar"] .stButton > button { width: 100%; }
        section[data-testid="stSidebar"] [data-testid="stFileUploader"] {
            padding: 12px 14px 14px;
            border: 1px solid #30313d;
            border-radius: 14px;
            background: var(--card);
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
            border: none;
            background: transparent;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"] > div:first-child { display: none; }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"]:before {
            content: 'Drag and drop files here';
            display: block;
            color: var(--text);
            font-size: 17px;
            font-weight: 600;
            margin: 4px 0 12px;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzoneInstructions"]:after {
            content: 'Limit 200MB per file';
            display: block;
            color: var(--muted);
            font-size: 15px;
            margin-top: 7px;
        }
        section[data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] button {
            border: 1px solid #555766;
            background: #30313d;
            color: white;
            border-radius: 10px;
        }
        @media (max-width: 760px) {
            section[data-testid="stSidebar"] { width: 300px !important; }
            section[data-testid="stSidebar"] > div { padding: 40px 18px 20px; }
            .hero { margin-top: 65px; padding: 0 20px; }
            .hero h1 { font-size: 35px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("# Menu:")
        st.markdown(
            "Upload your PDF Files and Click on<br>the Submit & Process Button",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        files = st.file_uploader(
            "PDF files",
            type=["pdf"],
            accept_multiple_files=True,
            label_visibility="collapsed",
        )
        if files:
            st.markdown(
                f"<div class='file-count'>{len(files)} PDF file(s) selected</div>",
                unsafe_allow_html=True,
            )
            for file in files:
                st.caption(f"📄 {file.name}")

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        if st.button("Submit & Process", use_container_width=True):
            if files:
                with st.spinner("Processing PDFs..."):
                    all_chunks = []
                    for file in files:
                        extracted_data = extract_pdf(file)
                        chunks = create_chunks(extracted_data)
                        all_chunks.extend(chunks)

                    st.session_state.vector_store = create_vector_store(all_chunks)
                    st.session_state.processed = True
                    st.toast(
                        f"Indexed {len(files)} PDF(s) ({len(all_chunks)} chunks)",
                        icon="✅",
                    )
            else:
                st.warning("Please upload at least one PDF first.")

        if st.button("Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()


def main() -> None:
    inject_styles()
    st.markdown(
        "<div class='brand-row'><span>Fork</span><a href='https://github.com' target='_blank'>◉</a><span>⋮</span></div>",
        unsafe_allow_html=True,
    )
    render_sidebar()

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "processed" not in st.session_state:
        st.session_state.processed = False
    if "vector_store" not in st.session_state:
        st.session_state.vector_store = None

    st.markdown("<div class='hero'>", unsafe_allow_html=True)
    st.markdown("# Chat with PDF files using Gemini🤖", unsafe_allow_html=True)
    st.markdown("<div class='welcome'>Welcome to the chat!</div>", unsafe_allow_html=True)

    if not st.session_state.messages:
        st.markdown(
            "<div class='empty-state'><span class='bot-icon'>🤖</span><span>upload some pdfs and ask me a question</span></div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown("<div class='message-wrap'>", unsafe_allow_html=True)
        for message in st.session_state.messages:
            css_class = "chat-user" if message["role"] == "user" else "chat-assistant"
            content = message["content"]
            if isinstance(content, list):
                content = "\n".join(
                    item.get("text", str(item)) if isinstance(item, dict) else str(item)
                    for item in content
                )
            safe_content = html.escape(str(content)).replace("\n", "<br>")
            st.markdown(
                f"<div class='{css_class}'>{safe_content}</div>",
                unsafe_allow_html=True,
            )
            if message.get("sources"):
                with st.expander("View PDF Sources"):
                    for i, src in enumerate(message["sources"], 1):
                        st.caption(f"**Chunk {i}:** {src}")
        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.processed:
        st.markdown(
            "<div style='text-align:center'><span class='status-pill'>● PDFs uploaded and ready</span></div>",
            unsafe_allow_html=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

    prompt = st.chat_input("Your message")
    if prompt:
        if not st.session_state.processed or st.session_state.vector_store is None:
            st.warning("Please upload and process at least one PDF in the sidebar first.")
        else:
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.spinner("Searching PDFs and generating answer..."):
                docs = st.session_state.vector_store.similarity_search(prompt, k=4)
                try:
                    answer = generate_answer(prompt, docs)
                except Exception as exc:
                    error_text = str(exc)
                    if "503" in error_text or "UNAVAILABLE" in error_text:
                        answer = (
                            "Gemini is temporarily busy. Your PDF was indexed successfully; "
                            "please wait a moment and send the question again."
                        )
                    else:
                        answer = f"I couldn't generate an answer right now: {error_text}"
                sources = [doc.page_content for doc in docs]

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                }
            )
            st.rerun()


if __name__ == "__main__":
    main()
