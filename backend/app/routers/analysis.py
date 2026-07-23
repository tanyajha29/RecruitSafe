import os
import uuid
import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException, status
import bleach

from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.analysis import AnalysisResponse
from app.middleware.auth import get_current_user, get_current_user_optional
from app.services.document_processor import DocumentProcessor
from app.services.pipeline import run_analysis_pipeline

router = APIRouter(prefix="/api/analyze", tags=["Analysis"])
logger = logging.getLogger("recruitsafe")

# Ensure uploads directory is configured
UPLOAD_DIR = "uploads"

@router.post("", status_code=status.HTTP_201_CREATED)
async def submit_analysis(
    background_tasks: BackgroundTasks,
    input_type: str = Form(...),
    content: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user_optional)
):
    """
    Submits a new job/document for verification.
    - Runs upfront size, type, and MIME validations on uploaded files.
    - Saves the file to a secure temporary location.
    - Immediately registers the analysis in MongoDB as 'processing'.
    - Queues the analysis pipeline using FastAPI BackgroundTasks.
    - Returns the analysis_id and status immediately (non-blocking).
    """
    logger.info(f"Received analysis submission from user: {current_user.email} (Type: {input_type})")
    
    # 1. Validate inputs
    if input_type in ["text", "email", "url"]:
        if not content or content.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Content string is required when input_type is '{input_type}'."
            )
        original_content = bleach.clean(content.strip())
        temp_file_path = None
        
    elif input_type in ["pdf", "image"]:
        if not file:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A file upload is required when input_type is '{input_type}'."
            )
            
        # Run local file validations (extension, size, MIME)
        DocumentProcessor.validate_file(file, input_type)
        
        # Save to temporary uploads/ directory securely
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_ext = file.filename.split(".")[-1] if "." in file.filename else ""
        unique_filename = f"{uuid.uuid4()}.{file_ext}"
        temp_file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        try:
            logger.info(f"Saving temporary upload to: {temp_file_path}")
            with open(temp_file_path, "wb") as buffer:
                # Read chunks to save memory
                while chunk := await file.read(1024 * 1024):
                    buffer.write(chunk)
        except Exception as e:
            logger.error(f"Failed to write temporary file: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save uploaded document. Please try again."
            )
            
        original_content = file.filename
        
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid input_type '{input_type}'. Supported: text, email, url, pdf, image."
        )

    # 2. Create database analysis shell
    analysis = Analysis(
        user_id=current_user.id,
        input_type=input_type,
        original_content=original_content,
        processed_text=None,
        status="processing",
        pdf_file_path=temp_file_path,
        created_at=datetime.utcnow()
    )
    await analysis.save()

    # 3. Schedule async pipeline task
    logger.info(f"Scheduling background task for analysis: {analysis.id}")
    background_tasks.add_task(run_analysis_pipeline, str(analysis.id))

    return {
        "analysis_id": str(analysis.id),
        "status": "processing"
    }

@router.get("/{analysis_id}", response_model=AnalysisResponse, status_code=status.HTTP_200_OK)
async def get_analysis_details(analysis_id: str, current_user: User = Depends(get_current_user_optional)):
    """
    Retrieves the complete results or status of a specific job scan.
    """
    logger.info(f"Fetching analysis details for ID: {analysis_id}")
    
    try:
        analysis = await Analysis.get(analysis_id)
    except Exception:
        analysis = None

    if not analysis or analysis.user_id != current_user.id:
        logger.warning(f"Analysis details requested but not found or unauthorized: {analysis_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested analysis report was not found."
        )
        
    return analysis

@router.delete("/{analysis_id}", status_code=status.HTTP_200_OK)
async def delete_analysis(analysis_id: str, current_user: User = Depends(get_current_user_optional)):
    """
    Permanently deletes a specific job scan from history.
    """
    logger.info(f"Delete requested for analysis report ID: {analysis_id}")
    
    try:
        analysis = await Analysis.get(analysis_id)
    except Exception:
        analysis = None

    if not analysis or analysis.user_id != current_user.id:
        logger.warning(f"Delete rejected: Analysis not found or unauthorized: {analysis_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested analysis report was not found."
        )

    await analysis.delete()
    logger.info(f"Analysis report deleted successfully: {analysis_id}")
    
    return {"message": "Analysis deleted"}
