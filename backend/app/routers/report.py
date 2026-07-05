import os
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse

from app.models.user import User
from app.models.analysis import Analysis
from app.middleware.auth import get_current_user
from app.services.report_generator import generate_pdf_report

router = APIRouter(prefix="/api/report", tags=["Report"])
logger = logging.getLogger("recruitsafe")

REPORTS_DIR = "reports"

@router.get("/{analysis_id}", status_code=status.HTTP_200_OK)
async def download_analysis_report(analysis_id: str, current_user: User = Depends(get_current_user)):
    """
    Generates and returns the downloadable PDF report for a completed job scan.
    """
    logger.info(f"PDF report download requested for ID: {analysis_id} by user {current_user.email}")
    
    try:
        analysis = await Analysis.get(analysis_id)
    except Exception:
        analysis = None

    if not analysis or analysis.user_id != current_user.id:
        logger.warning(f"Report download rejected: Analysis not found or unauthorized: {analysis_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested analysis report was not found."
        )

    if analysis.status != "completed":
        logger.warning(f"Report download rejected: Analysis is in state '{analysis.status}': {analysis_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The analysis report is not ready. Current status: '{analysis.status}'."
        )

    # Ensure output directory exists
    os.makedirs(REPORTS_DIR, exist_ok=True)
    pdf_filename = f"RecruitSafe_Report_{analysis_id}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)

    # Generate PDF if it does not already exist
    if not os.path.exists(pdf_path):
        try:
            generate_pdf_report(analysis, pdf_path)
        except Exception as e:
            logger.error(f"Failed to generate PDF report on-the-fly for {analysis_id}: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate the PDF report document. Please try again."
            )

    return FileResponse(
        path=pdf_path,
        media_type="application/pdf",
        filename=pdf_filename
    )
