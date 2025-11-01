import PyPDF2
import docx
import os

def parse_resume(file_path: str) -> str:
    """
    Parse resume from file and convert to text
    
    Args:
        file_path: Path to the resume file
        
    Returns:
        Resume content as text
    """
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() == '.pdf':
        return _parse_pdf(file_path)
    elif ext.lower() == '.docx':
        return _parse_docx(file_path)
    elif ext.lower() in ['.md', '.markdown']:
        return _parse_markdown(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def _parse_pdf(file_path: str) -> str:
    """Parse PDF file to text"""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        raise Exception(f"Error parsing PDF: {str(e)}")

def _parse_docx(file_path: str) -> str:
    """Parse DOCX file to text"""
    try:
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error parsing DOCX: {str(e)}")

def _parse_markdown(file_path: str) -> str:
    """Parse markdown file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        raise Exception(f"Error parsing markdown: {str(e)}")