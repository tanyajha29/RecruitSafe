import os
import time
import logging
from datetime import datetime, timezone

from app.models.analysis import Analysis
from app.models.notification import Notification
from app.services.document_processor import DocumentProcessor
from app.services.pipeline_orchestrator import PipelineOrchestrator

logger = logging.getLogger("recruitsafe")

async def run_analysis_pipeline(analysis_id: str) -> None:
    """
    Background worker task that executes the RecruitSafe Version 2.2
    Contextual Explainable Risk Assessment Engine.
    """
    start_time = time.time()
    logger.info(f"Starting async analysis pipeline V2.2 for job ID: {analysis_id}")
    
    # 1. Fetch analysis document from database
    analysis = await Analysis.get(analysis_id)
    if not analysis:
        logger.error(f"Pipeline failed: Analysis record {analysis_id} not found.")
        return

    temp_file_path = analysis.pdf_file_path
    
    try:
        scam_text = ""
        ocr_performed = False

        # 2. Extract text if PDF or Image
        if analysis.input_type in ["pdf", "image"] and temp_file_path:
            if not os.path.exists(temp_file_path):
                raise FileNotFoundError(f"Uploaded temp file not found at path: {temp_file_path}")
                
            logger.info(f"Extracting text from uploaded file: {temp_file_path}")
            extracted_text, ocr_ran = DocumentProcessor.process_file_extraction(temp_file_path, analysis.input_type)
            
            analysis.processed_text = extracted_text
            analysis.ocr_performed = ocr_ran
            scam_text = extracted_text
            logger.info(f"Extraction successful. Text length: {len(extracted_text)} characters.")
        else:
            # Standard Text Paste or URL
            scam_text = analysis.original_content or ""

        # Phase 1 & Phase 2: Ingest and compile the structured evidence model
        from app.services.structured_extractor import StructuredExtractor
        from app.services.ai.ai_provider import ai_service
        analysis.structured_evidence = StructuredExtractor.extract_all(scam_text, analysis.original_content)

        missing_fields = [k for k, v in analysis.structured_evidence.items() if v["extraction_status"] == "not_found"]
        if missing_fields and ai_service.enabled:
            try:
                ai_extracted = await ai_service.extract_missing_fields(scam_text, missing_fields)
                for field, val in ai_extracted.items():
                    if val and str(val).strip() != "" and str(val).strip().lower() not in ["unknown", "none", "not found"]:
                        analysis.structured_evidence[field] = {
                            "value": str(val).strip(),
                            "source": "AI Fallback",
                            "extraction_status": "extracted",
                            "confidence": 80
                        }
            except Exception as e:
                logger.error(f"Fallback AI information extraction failed: {e}")

        # Validate structured evidence before scoring
        from app.services.extraction_validator import ExtractionValidator
        analysis.structured_evidence = ExtractionValidator.validate_all(analysis.structured_evidence)

        # 3. Delegate to modular PipelineOrchestrator
        orchestration_result = await PipelineOrchestrator.process_analysis(
            input_type=analysis.input_type,
            original_content=analysis.original_content or "",
            processed_text=scam_text,
            ocr_performed=ocr_performed,
            structured_evidence=analysis.structured_evidence
        )

        # 4. Save results to Beanie model
        analysis.trust_score = orchestration_result["trust_score"]
        analysis.scam_probability = orchestration_result["scam_probability"]
        analysis.risk_category = orchestration_result["risk_category"]
        analysis.confidence_score = orchestration_result["confidence_score"]
        analysis.agreement_score = orchestration_result["agreement_score"]
        analysis.agreement_explanation = orchestration_result["agreement_explanation"]
        analysis.input_quality_score = orchestration_result["input_quality_score"]
        analysis.verification_status = orchestration_result["verification_status"]
        analysis.evidence = orchestration_result["evidence"]
        analysis.positive_findings = orchestration_result["positive_findings"]
        analysis.recommendations = orchestration_result["recommendations"]
        analysis.ai_summary = orchestration_result["ai_summary"]
        analysis.risk_explanation = orchestration_result["risk_explanation"]
        analysis.red_flags = orchestration_result["red_flags"]
        analysis.website_data = orchestration_result["website_data"]
        analysis.email_data = orchestration_result["email_data"]
        analysis.hiring_workflow = orchestration_result["hiring_workflow"]
        analysis.decision_trace = orchestration_result["decision_trace"]
        analysis.hybrid_verdict = orchestration_result.get("hybrid_verdict")

        # Parse detected email info if email_data is present
        if orchestration_result["email_data"]:
            analysis.email_detected = True
            analysis.email_type = orchestration_result["email_data"].get("is_free_email")
            if orchestration_result["email_data"].get("is_disposable"):
                analysis.email_type = "disposable"
            elif orchestration_result["email_data"].get("is_free_email"):
                analysis.email_type = "public"
            else:
                analysis.email_type = "corporate"
        else:
            analysis.email_detected = False
            analysis.email_type = None

        analysis.status = "completed"
        analysis.processing_time_ms = int((time.time() - start_time) * 1000)
        
        await analysis.save()

        # 5. Create completion notification
        notif = Notification(
            user_id=analysis.user_id,
            type="analysis_complete",
            title="Analysis Completed",
            message=f"Your job check is complete. Verdict: {analysis.risk_category} (Score: {analysis.trust_score}/100)",
            analysis_id=analysis.id
        )
        await notif.save()
        logger.info(f"Async pipeline V2.2 completed successfully for job ID: {analysis_id}")
        
    except Exception as e:
        logger.error(f"Error in async analysis pipeline for job ID {analysis_id}: {e}", exc_info=True)
        analysis.status = "failed"
        analysis.error_message = str(e)
        analysis.processing_time_ms = int((time.time() - start_time) * 1000)
        await analysis.save()
        
        notif = Notification(
            user_id=analysis.user_id,
            type="upload_error",
            title="Analysis Failed",
            message=f"An error occurred while evaluating this job check: {str(e)}",
            analysis_id=analysis.id
        )
        await notif.save()
        
    finally:
        # Cleanup uploaded temporary files
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Successfully cleaned up temporary upload file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to delete temporary file {temp_file_path}: {e}")
