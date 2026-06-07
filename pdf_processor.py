# components/pdf_processor.py

import fitz  # PyMuPDF
import io
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from utils.helpers import clean_text


def extract_text_from_pdf(uploaded_file):
    """
    Extract raw text from an uploaded PDF file.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        tuple: (full_text, list_of_Documents, page_count)
    """

    # Read the uploaded file into bytes
    # Streamlit gives us a file-like object, fitz needs bytes
    pdf_bytes = uploaded_file.read()

    # Reset the file pointer so it can be read again later if needed
    uploaded_file.seek(0)

    # Open PDF from bytes using PyMuPDF
    # fitz.open() can open from a file path OR from bytes in memory
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")

    page_count = len(pdf_document)
    full_text = ""
    documents = []

    # Loop through every page
    for page_num in range(page_count):
        # Get the page object
        page = pdf_document[page_num]

        # Extract text from this page
        page_text = page.get_text()

        # Clean the extracted text
        page_text = clean_text(page_text)

        # Add to full text
        full_text += f"\n\n--- Page {page_num + 1} ---\n\n{page_text}"

        # Create a LangChain Document object for this page
        # This is the standard format LangChain expects
        doc = Document(
            page_content=page_text,
            metadata={
                "source": uploaded_file.name,
                "page": page_num + 1,
                "total_pages": page_count
            }
        )
        documents.append(doc)

    # Close the PDF to free memory
    pdf_document.close()

    return full_text, documents, page_count


def split_documents(documents, chunk_size=1000, chunk_overlap=200):
    """
    Split LangChain Documents into smaller chunks for embedding.

    Why RecursiveCharacterTextSplitter?
    It tries to split on natural boundaries in this order:
    1. Paragraphs (\n\n)
    2. Lines (\n)
    3. Sentences (. )
    4. Words ( )
    5. Characters (last resort)
    
    This is smarter than splitting at a fixed character count
    because it tries to keep sentences and paragraphs intact.

    Args:
        documents: list of LangChain Document objects
        chunk_size: max characters per chunk (default 1000)
        chunk_overlap: overlap between chunks (default 200)
        
    Returns:
        list of smaller Document chunks
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # These are the boundaries it tries to split on, in order
        separators=["\n\n", "\n", ". ", " ", ""],
        length_function=len
    )

    # split_documents takes a list of Documents
    # and returns a larger list of smaller Documents
    chunks = splitter.split_documents(documents)

    return chunks


def process_pdf(uploaded_file):
    """
    Main function that runs the full PDF processing pipeline.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        
    Returns:
        dict with all processed data
    """

    # Step 1: Extract text
    full_text, documents, page_count = extract_text_from_pdf(uploaded_file)

    # Basic validation: did we actually extract text?
    if not full_text or not full_text.strip():
        raise ValueError("Extracted PDF text is empty — the file may be scanned or unreadable.")

    # Step 2: Split into chunks
    chunks = split_documents(documents)

    # Validate chunks
    if not chunks:
        raise ValueError("No text chunks were produced from the PDF. Check the splitter settings or the extracted text.")

    return {
        "full_text": full_text,
        "documents": documents,
        "chunks": chunks,
        "page_count": page_count,
        "chunk_count": len(chunks),
        "file_name": uploaded_file.name
    }