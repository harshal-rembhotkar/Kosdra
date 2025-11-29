import pypdf
from io import BytesIO

def extract_text_from_file(uploaded_file) -> str:
    try:
        if uploaded_file.type == "application/pdf":
            reader = pypdf.PdfReader(uploaded_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            # Assume text/plain
            return uploaded_file.getvalue().decode("utf-8")
    except Exception as e:
        return f"Error parsing file: {str(e)}"
