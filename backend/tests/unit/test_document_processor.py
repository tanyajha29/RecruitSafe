import pytest
from fastapi import UploadFile, HTTPException
from io import BytesIO

from app.services.document_processor import DocumentProcessor

def test_text_cleaning_and_normalization():
    """
    Verifies that clean_text successfully normalizes excessive spaces,
    tabs, null bytes, and newlines while preserving semantic structure.
    """
    raw_text = "Software   Engineer\n\n\n\nCompany: Tech\x00Corp\r\n\r\nSalary:\t$120k"
    cleaned = DocumentProcessor.clean_text(raw_text)
    
    # 1. Null byte removed
    assert "TechCorp" in cleaned
    # 2. Tabs and double spaces replaced with single spaces
    assert "Software Engineer" in cleaned
    assert "Salary: $120k" in cleaned
    # 3. Multiple newlines normalized
    assert "\n\n" in cleaned
    assert "\n\n\n" not in cleaned
    assert "\r" not in cleaned

def test_file_validation_valid_pdf():
    """
    Verifies that validate_file successfully accepts valid PDF configurations.
    """
    # Mock UploadFile with a small binary body
    file_content = b"%PDF-1.5 mock pdf contents"
    mock_file = UploadFile(
        file=BytesIO(file_content),
        filename="offer_letter.pdf",
        headers={"content-type": "application/pdf"}
    )
    
    # Should compile without exception
    DocumentProcessor.validate_file(mock_file, "pdf")

def test_file_validation_invalid_extension():
    """
    Verifies that validate_file raises HTTPException (400) for mismatched extensions.
    """
    mock_file = UploadFile(
        file=BytesIO(b"some malware exe contents"),
        filename="malware.exe",
        headers={"content-type": "application/pdf"}
    )
    
    with pytest.raises(HTTPException) as exc:
        DocumentProcessor.validate_file(mock_file, "pdf")
    assert exc.value.status_code == 400
    assert "Invalid file extension" in exc.value.detail

def test_file_validation_invalid_mime():
    """
    Verifies that validate_file raises HTTPException (400) for mismatched MIME types.
    """
    mock_file = UploadFile(
        file=BytesIO(b"mock text contents in pdf name"),
        filename="offer.pdf",
        headers={"content-type": "text/plain"}
    )
    
    with pytest.raises(HTTPException) as exc:
        DocumentProcessor.validate_file(mock_file, "pdf")
    assert exc.value.status_code == 400
    assert "Invalid MIME type" in exc.value.detail

def test_file_validation_oversized_file():
    """
    Verifies that validate_file raises HTTPException (413) for files exceeding size limits.
    """
    # Mock a file exceeding 20MB limit (e.g. 21MB)
    size_21mb = 21 * 1024 * 1024
    
    # Instead of allocating a 21MB buffer, we can write a mock stream object that reports 21MB
    class OversizedBytesIO(BytesIO):
        def seek(self, offset, whence=0):
            if whence == 2: # seek to end
                self.position = size_21mb
            else:
                self.position = offset
        def tell(self):
            return size_21mb

    mock_file = UploadFile(
        file=OversizedBytesIO(b"oversized stream"),
        filename="large_offer.pdf",
        headers={"content-type": "application/pdf"}
    )
    
    with pytest.raises(HTTPException) as exc:
        DocumentProcessor.validate_file(mock_file, "pdf")
    assert exc.value.status_code == 413
    assert "File too large" in exc.value.detail
