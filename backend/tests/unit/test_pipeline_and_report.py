import os
import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch, MagicMock

from app.models.analysis import Analysis
from app.services.pipeline import run_analysis_pipeline
from app.services.report_generator import generate_pdf_report

@pytest.mark.asyncio
async def test_async_pipeline_and_pdf_generation():
    """
    Simulates the async pipeline execution on a mock job description
    by patching Beanie database methods, verifying correct scoring,
    status updates, and PDF report creation.
    """
    # 1. Create a mock Analysis instance
    mock_analysis = MagicMock(spec=Analysis)
    mock_analysis.id = "6a451d8bf0bcb4c5037b9987"
    mock_analysis.user_id = "507f1f77bcf86cd799439011"
    mock_analysis.input_type = "text"
    mock_analysis.original_content = (
        "We are looking for a remote data entry assistant. "
        "Earn ₹2 lakh/month. Guaranteed job with direct selection. "
        "Please pay the registration fee of ₹2500 within 2 hours. "
        "To apply, send bank details to hr-recruiter@gmail.com."
    )
    mock_analysis.status = "processing"
    mock_analysis.pdf_file_path = None
    mock_analysis.created_at = datetime.utcnow()
    mock_analysis.ocr_performed = False
    
    # Version 2.0 Extended Fields
    mock_analysis.confidence_score = None
    mock_analysis.agreement_score = None
    mock_analysis.contradictions = []
    mock_analysis.missing_information = []
    mock_analysis.positive_findings = []
    
    mock_analysis.evidence = []
    mock_analysis.red_flags = []
    mock_analysis.ai_summary = ""
    mock_analysis.risk_explanation = ""
    mock_analysis.recommendations = []
    mock_analysis.website_data = None
    mock_analysis.email_data = None
    
    # Mock async save method
    mock_analysis.save = AsyncMock()

    # 2. Patch database queries and notifications
    with patch("app.models.analysis.Analysis.get", new_callable=AsyncMock) as mock_get, \
         patch("app.services.pipeline.Notification") as mock_notif_class:
         
        # Mock Notification instance returned on creation
        mock_notif_instance = MagicMock()
        mock_notif_instance.save = AsyncMock()
        mock_notif_class.return_value = mock_notif_instance

        mock_get.return_value = mock_analysis

        # Run the pipeline
        await run_analysis_pipeline(mock_analysis.id)

        # 3. Verify status was updated to completed and saved
        assert mock_analysis.status == "completed"
        assert mock_analysis.trust_score is not None
        assert mock_analysis.trust_score < 50  # Multiple rules matched
        assert mock_analysis.risk_category in ["High Risk", "Suspicious"]
        assert len(mock_analysis.evidence) >= 3
        assert len(mock_analysis.recommendations) >= 3
        assert mock_analysis.ai_summary != ""
        assert mock_analysis.risk_explanation != ""
        
        # Verify db get and save were called
        mock_get.assert_called_once_with(mock_analysis.id)
        mock_analysis.save.assert_called()
        mock_notif_class.assert_called()
        mock_notif_instance.save.assert_called()

    # 4. Generate PDF report using the updated mock analysis details
    pdf_dir = "tests_reports"
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_path = os.path.join(pdf_dir, f"test_{mock_analysis.id}.pdf")
    
    try:
        generate_pdf_report(mock_analysis, pdf_path)
        
        # Verify file exists on disk and is non-empty
        assert os.path.exists(pdf_path)
        assert os.path.getsize(pdf_path) > 1024  # > 1KB
        
    finally:
        # Clean up generated test report file
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
        if os.path.exists(pdf_dir):
            os.rmdir(pdf_dir)
