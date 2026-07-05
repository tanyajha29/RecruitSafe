import os
import logging
from PIL import Image
import pytesseract
from pdf2image import convert_from_path

from app.config import settings

logger = logging.getLogger("recruitsafe")

# Initialize and verify Tesseract availability on module load
TESSERACT_AVAILABLE = False
try:
    # Set tesseract command path if specified
    if settings.TESSERACT_CMD and settings.TESSERACT_CMD != "tesseract":
        pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
    
    # Try fetching tesseract version to check if it's available in PATH
    version = pytesseract.get_tesseract_version()
    logger.info(f"Tesseract OCR is available. Version: {version}")
    TESSERACT_AVAILABLE = True
except Exception as e:
    logger.warning(
        f"Tesseract OCR is NOT available on this system. Image OCR will fail. "
        f"Error details: {e}. (To enable OCR, install Tesseract and configure TESSERACT_CMD)"
    )
    TESSERACT_AVAILABLE = False

class OCREngineUnavailableException(Exception):
    """Custom exception raised when OCR processing is requested but Tesseract is missing."""
    pass

class OCREngine:
    @staticmethod
    def is_available() -> bool:
        """Returns whether Tesseract OCR is installed and available."""
        return TESSERACT_AVAILABLE

    @classmethod
    def extract_from_image(cls, image_path: str) -> str:
        """
        Extracts normalized text from an image file using Tesseract.
        Raises OCREngineUnavailableException if Tesseract is missing.
        """
        if not TESSERACT_AVAILABLE:
            raise OCREngineUnavailableException(
                "OCR service is currently unavailable on this server. "
                "Image uploads cannot be processed. Please copy/paste the text instead."
            )

        try:
            logger.info(f"Running Tesseract OCR on image: {image_path}")
            # Preprocess image internally or open directly
            with Image.open(image_path) as img:
                # Convert to grayscale to improve Tesseract accuracy
                img_gray = img.convert('L')
                extracted_text = pytesseract.image_to_string(img_gray, lang=settings.TESSERACT_LANG)
                return extracted_text.strip()
        except Exception as e:
            logger.error(f"Failed to perform OCR on image {image_path}: {e}", exc_info=True)
            raise Exception(f"OCR text extraction failed: {str(e)}")

    @classmethod
    def extract_from_pdf_pages(cls, pdf_path: str) -> str:
        """
        Converts all PDF pages into images and runs OCR on each page.
        Raises OCREngineUnavailableException if Tesseract is missing.
        """
        if not TESSERACT_AVAILABLE:
            raise OCREngineUnavailableException(
                "OCR service is currently unavailable on this server. "
                "Scanned PDF uploads cannot be processed. Please copy/paste the text instead."
            )

        try:
            logger.info(f"Converting PDF to images for OCR: {pdf_path}")
            # Convert PDF pages to list of PIL Images
            pages = convert_from_path(pdf_path, dpi=200)
            
            logger.info(f"PDF converted to {len(pages)} page images. Commencing OCR...")
            extracted_pages_text = []
            
            for i, page in enumerate(pages):
                logger.info(f"Running OCR on page {i+1}/{len(pages)}")
                page_gray = page.convert('L')
                page_text = pytesseract.image_to_string(page_gray, lang=settings.TESSERACT_LANG)
                extracted_pages_text.append(page_text)
                
            return "\n\n".join(extracted_pages_text).strip()
        except Exception as e:
            logger.error(f"Failed to perform PDF OCR on {pdf_path}: {e}", exc_info=True)
            raise Exception(f"PDF OCR text extraction failed: {str(e)}")
