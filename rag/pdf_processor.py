import fitz


def extract_pdf(uploaded_file):

    pdf_bytes = uploaded_file.getvalue()

    document = fitz.open(
        stream=pdf_bytes,
        filetype="pdf"
    )

    extracted_data = []

    for page_number, page in enumerate(document, start=1):

        text = page.get_text("text")

        if text.strip():

            extracted_data.append({
                "text": text,
                "page": page_number,
                "source": uploaded_file.name
            })

    document.close()

    return extracted_data