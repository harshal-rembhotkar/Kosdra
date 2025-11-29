import pypdf
from io import BytesIO

def extract_text_from_file(uploaded_file) -> str:
    try:
        if uploaded_file.type == "application/pdf":
            file_bytes = uploaded_file.read()
            reader = pypdf.PdfReader(BytesIO(file_bytes))
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
        else:
            data = uploaded_file.read()
            return (data or b"").decode("utf-8", errors="ignore")
    except Exception as e:
        return f"Error parsing file: {str(e)}"