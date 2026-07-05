import os
import re
import logging
from typing import Tuple
from fastapi import UploadFile, HTTPException, status
from pypdf import PdfReader

from app.config import settings
from app.services.ocr_engine import OCREngine, OCREngineUnavailableException

logger = logging.getLogger("recruitsafe")

# Allowed MIME types and extensions
ALLOWED_EXTENSIONS = {
    "pdf": ["pdf"],
    "image": ["png", "jpg", "jpeg"]
}

ALLOWED_MIME_TYPES = {
    "pdf": ["application/pdf"],
    "image": ["image/png", "image/jpeg", "image/jpg"]
}

MAX_FILE_SIZES = {
    "pdf": 20 * 1024 * 1024,   # 20MB
    "image": 10 * 1024 * 1024  # 10MB
}

class DocumentProcessor:
    @staticmethod
    def validate_file(file: UploadFile, file_type: str) -> None:
        """
        Validates the uploaded file extension, content-type (MIME), and size limits.
        Raises HTTPException if validation fails.
        """
        # 1. Validate file extension
        filename = file.filename or ""
        ext = filename.split(".")[-1].lower() if "." in filename else ""
        
        if file_type not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file category: '{file_type}'"
            )
            
        if ext not in ALLOWED_EXTENSIONS[file_type]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file extension '.{ext}' for category '{file_type}'. Allowed: {ALLOWED_EXTENSIONS[file_type]}"
            )

        # 2. Validate MIME type
        if file.content_type not in ALLOWED_MIME_TYPES[file_type]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid MIME type '{file.content_type}'. Expected one of: {ALLOWED_MIME_TYPES[file_type]}"
            )

        # 3. Validate file size (seek to end to verify size)
        file.file.seek(0, 2)
        size = file.file.tell()
        file.file.seek(0)  # Reset pointer to start
        
        max_size = MAX_FILE_SIZES[file_type]
        if size > max_size:
            max_mb = max_size / (1024 * 1024)
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large ({round(size / (1024*1024), 2)}MB). Maximum allowed size is {int(max_mb)}MB."
            )

    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans and normalizes extracted text:
        - Normalizes line breaks
        - Removes null bytes
        - Normalizes excessive spaces and tabs to single spaces
        - Preserves important punctuation and semantic structures
        """
        if not text:
            return ""
            
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize line breaks to \n
        text = re.sub(r'\r\n|\r', '\n', text)
        
        # Normalize excessive horizontal whitespace (multiple spaces/tabs)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Normalize excessive vertical whitespace (more than two newlines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        return text.strip()

    @classmethod
    def extract_text_directly_from_pdf(cls, pdf_path: str) -> str:
        """
        Attempts direct text extraction from a digital PDF using pypdf.
        Returns empty string if the PDF is scanned (contains no digital text layer).
        """
        try:
            logger.info(f"Attempting direct digital text extraction from PDF: {pdf_path}")
            reader = PdfReader(pdf_path)
            text_content = []
            
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_content.append(page_text)
                    
            return "\n\n".join(text_content).strip()
        except Exception as e:
            logger.warning(f"Direct PDF text extraction failed on {pdf_path}: {e}")
            return ""

    @classmethod
    def process_file_extraction(cls, file_path: str, file_type: str) -> Tuple[str, bool]:
        """
        Orchestrates text extraction based on file type (image or pdf):
        - For images: Runs OCR.
        - For PDFs: Attempts direct digital extraction first. If it yields no text (scanned PDF),
          falls back to image-based OCR if Tesseract is available.
        Returns a tuple of (extracted_text, ocr_performed_bool).
        """
        if file_type == "image":
            text = OCREngine.extract_from_image(file_path)
            return cls.clean_text(text), True
            
        elif file_type == "pdf":
            # 1. Attempt direct text extraction first
            text = cls.extract_text_directly_from_pdf(file_path)
            
            # 2. If text is extracted, return it directly
            if text and len(text.strip()) > 20: # arbitrary minimum character threshold
                logger.info(f"Direct PDF text extraction succeeded for {file_path}")
                return cls.clean_text(text), False
                
            # 3. If direct extraction failed, fall back to OCR if Tesseract is available
            logger.info(f"Direct PDF text extraction yielded insufficient text. Falling back to OCR...")
            if OCREngine.is_available():
                ocr_text = OCREngine.extract_from_pdf_pages(file_path)
                return cls.clean_text(ocr_text), True
            else:
                # Tesseract missing, can't OCR scanned PDF
                logger.error("Scanned PDF detected but OCR engine is unavailable.")
                raise OCREngineUnavailableException(
                    "This PDF appears to be a scanned document (contains only images). "
                    "We cannot parse scanned PDFs because the Tesseract OCR engine is not installed on this server. "
                    "Please upload a text-based PDF or copy/paste the job description instead."
                )
        else:
            raise ValueError(f"Unknown file type: {file_type}")
