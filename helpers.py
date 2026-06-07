def format_file_size(size_in_bytes):
   
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    else:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"


def clean_text(text):
   
    import re
   
    text = re.sub(r' +', ' ', text)
   
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

def validate_pdf(file):
    """
    Check if uploaded file is a valid PDF.
    Returns (is_valid, error_message)
    """
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if file.size > max_size:
        return False, "File too large. Maximum size is 10MB."

    # Check file extension
    if not file.name.lower().endswith('.pdf'):
        return False, "Only PDF files are supported."

    # Check PDF magic bytes (every PDF starts with %PDF)
    header = file.read(4)
    file.seek(0)  # Reset file pointer back to start
    if header != b'%PDF':
        return False, "File does not appear to be a valid PDF."

    return True, None