import os
import time
import logging
import re
from datetime import datetime, timezone
from typing import List, Dict, Any

from app.models.analysis import Analysis
from app.models.notification import Notification
from app.services.document_processor import DocumentProcessor
from app.services.scam_detector import ScamRuleEngine
from app.services.salary_analyzer import SalaryAnalyzer
from app.services.hiring_process import HiringProcessValidator
from app.services.psych_manipulation import PsychologicalDetector
from app.services.identity_theft import IdentityTheftDetector
from app.services.website_intelligence import WebsiteIntelligence
from app.services.email_analyzer import EmailAnalyzer
from app.services.contradiction_detector import ContradictionDetector
from app.services.confidence_calculator import ConfidenceCalculator
from app.services.risk_scorer import RiskScorer
from app.services.recommendation_engine import RecommendationEngine
from app.services.ai.ai_provider import ai_service

logger = logging.getLogger("recruitsafe")

def enrich_evidence_item(item: Dict[str, Any], is_positive: bool, default_source: str = "Rule Engine") -> Dict[str, Any]:
    """
    Enriches evidence findings to guarantee presence of the 11 required attributes.
    Supports backward compatibility for UI.
    """
    enriched = dict(item)
    
    # id
    if "id" not in enriched:
        title_slug = re.sub(r'[^a-z0-9]', '_', enriched.get("title", enriched.get("factor_name", "generic")).lower())
        enriched["id"] = f"ev_{title_slug}"
        
    # title
    if "title" not in enriched:
        enriched["title"] = enriched.get("factor_name", enriched.get("id", "Evidence Item")).replace("_", " ").title()
        
    # rule_id
    if "rule_id" not in enriched:
        prefix = "RULE"
        if default_source == "Website Analyzer":
            prefix = "WEB"
        elif default_source == "Email Analyzer":
            prefix = "EML"
        elif default_source == "AI":
            prefix = "AI"
        elif default_source == "Company Verification":
            prefix = "VER"
        elif default_source == "OCR":
            prefix = "OCR"
        
        hash_val = sum(ord(c) for c in enriched["id"]) % 1000
        enriched["rule_id"] = f"{prefix}_{hash_val:03d}"
        
    # category
    if "category" not in enriched:
        enriched["category"] = "general"
        
    # severity
    if "severity" not in enriched:
        enriched["severity"] = "low" if is_positive else "medium"
        
    # score
    if "score" not in enriched:
        pts = enriched.get("points_deducted", 0)
        if is_positive:
            enriched["score"] = pts if pts > 0 else 5
        else:
            enriched["score"] = -abs(pts) if pts != 0 else -10
            
    # matched_text
    if "matched_text" not in enriched:
        enriched["matched_text"] = "Extracted context text"
        
    # reason
    if "reason" not in enriched:
        enriched["reason"] = enriched.get("description", "No explicit reasoning provided.")
        
    # evidence_type
    if "evidence_type" not in enriched:
        score_val = enriched.get("score", 0)
        if enriched.get("id") == "website_unverified" or score_val == 0:
            enriched["evidence_type"] = "unknown"
        elif is_positive or score_val > 0:
            enriched["evidence_type"] = "positive"
        else:
            enriched["evidence_type"] = "negative"
            
    # confidence impact
    if "confidence" not in enriched:
        sev = enriched.get("severity", "medium").lower()
        if sev == "high":
            enriched["confidence"] = 15
        elif sev == "medium":
            enriched["confidence"] = 10
        else:
            enriched["confidence"] = 5
            
    # source
    if "source" not in enriched:
        enriched["source"] = default_source

    # Backward-compatible fields
    enriched["factor_name"] = enriched["title"]
    enriched["description"] = enriched["reason"]
    enriched["points_deducted"] = abs(enriched["score"])
        
    return enriched

async def run_analysis_pipeline(analysis_id: str) -> None:
    """
    Background worker task that executes the RecruitSafe Version 2.0
    Multi-Layer AI-Assisted Explainable Risk Assessment Engine.
    """
    start_time = time.time()
    logger.info(f"Starting async analysis pipeline V2.0 for job ID: {analysis_id}")
    
    # 1. Fetch analysis document from database
    analysis = await Analysis.get(analysis_id)
    if not analysis:
        logger.error(f"Pipeline failed: Analysis record {analysis_id} not found in database.")
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
            
        elif analysis.input_type == "url" and analysis.original_content:
            url = analysis.original_content
            logger.info(f"Analyzing company website URL: {url}")
            
            # Run URL analysis (Scraping links, meta info)
            url_result = await WebsiteIntelligence.analyze_url(url)
            analysis.website_data = url_result
            
            # Fetch WHOIS & SSL
            domain = WebsiteIntelligence.extract_domain(url)
            if domain:
                whois_info = await WebsiteIntelligence.get_domain_whois(domain)
                ssl_info = await WebsiteIntelligence.check_ssl(domain)
                
                # Format dates to iso string for JSON serialization
                whois_formatted = {
                    "domain_age_days": whois_info["domain_age_days"],
                    "registrar": whois_info["registrar"],
                    "country": whois_info["country"],
                    "registration_date": whois_info["registration_date"].isoformat() if whois_info["registration_date"] else None,
                    "expiration_date": whois_info["expiration_date"].isoformat() if whois_info["expiration_date"] else None,
                    "whois_failed": whois_info["whois_failed"]
                }
                
                ssl_formatted = {
                    "has_valid_ssl": ssl_info["has_valid_ssl"],
                    "issuer": ssl_info["issuer"],
                    "expiration_date": ssl_info["expiration_date"].isoformat() if ssl_info["expiration_date"] else None
                }
                
                analysis.website_data.update({
                    "whois": whois_formatted,
                    "ssl": ssl_formatted
                })

            # Use website meta details for rules scan
            scam_text = f"Company Website: {url_result.get('page_title', '')}. Description: {url_result.get('meta_description', '')}"

        elif analysis.input_type == "email" and analysis.original_content:
            logger.info("Analyzing recruiter email content")
            scam_text = analysis.original_content
            
            # Try to parse sender email from body
            email_matches = re.findall(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', scam_text)
            
            # Extract potential company domain if a website link is mentioned in email body
            company_url = None
            url_matches = re.findall(r'https?://[^\s/$.?#].[^\s]*', scam_text)
            if url_matches:
                company_url = url_matches[0]
                
            if email_matches:
                sender_email = email_matches[0]
                logger.info(f"Detected recruiter email address in body: {sender_email}")
                email_result = await EmailAnalyzer.analyze_recruiter_email(sender_email, company_url)
                analysis.email_data = email_result
            else:
                analysis.email_data = {
                    "sender_email": "Unknown Recruiter",
                    "domain": "",
                    "is_valid_format": False,
                    "domain_exists": False,
                    "is_free_email": False,
                    "is_disposable": False,
                    "dns_records": {"has_mx": False, "has_spf": False, "has_dmarc": False}
                }

        else:
            # Standard Text Paste
            logger.info("Analyzing raw pasted job description text.")
            scam_text = analysis.original_content or ""

        # --- Pipeline Evidence Gathering ---
        all_evidence = []
        all_positives = []

        # 1. Rule Engine Scan
        rule_evidence, red_flags, rule_deductions = ScamRuleEngine.analyze_text(scam_text)
        all_evidence.extend(rule_evidence)

        # 2. Salary Intelligence Analysis
        salary_res = SalaryAnalyzer.analyze_salary(scam_text)
        all_evidence.extend(salary_res["evidence"])
        all_positives.extend(salary_res["positive_findings"])

        # 3. Hiring Process Validation
        hiring_res = HiringProcessValidator.validate_process(scam_text)
        all_evidence.extend(hiring_res["evidence"])
        all_positives.extend(hiring_res["positive_findings"])

        # 4. Psychological Manipulation Detector
        psych_res = PsychologicalDetector.analyze_manipulation(scam_text)
        all_evidence.extend(psych_res["evidence"])

        # 5. Identity Theft Detector
        id_res = IdentityTheftDetector.analyze_identity_requests(scam_text)
        all_evidence.extend(id_res["evidence"])

        # 6. Website / Domain Intelligence (If URL was provided or found)
        # Check if URL was extracted from email text to enrich company intelligence
        extracted_url = None
        if analysis.input_type != "url":
            url_matches = re.findall(r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', scam_text)
            if url_matches:
                extracted_url = "https://" + url_matches[0]
                
        active_url = analysis.original_content if analysis.input_type == "url" else extracted_url
        
        if active_url:
            domain = WebsiteIntelligence.extract_domain(active_url)
            # Run live lookups if not already run in URL stage
            if not analysis.website_data:
                url_res = await WebsiteIntelligence.analyze_url(active_url)
                whois_res = await WebsiteIntelligence.get_domain_whois(domain)
                ssl_res = await WebsiteIntelligence.check_ssl(domain)
                
                whois_formatted = {
                    "domain_age_days": whois_res["domain_age_days"],
                    "registrar": whois_res["registrar"],
                    "country": whois_res["country"],
                    "registration_date": whois_res["registration_date"].isoformat() if whois_res["registration_date"] else None,
                    "expiration_date": whois_res["expiration_date"].isoformat() if whois_res["expiration_date"] else None,
                    "whois_failed": whois_res["whois_failed"]
                }
                
                ssl_formatted = {
                    "has_valid_ssl": ssl_res["has_valid_ssl"],
                    "issuer": ssl_res["issuer"],
                    "expiration_date": ssl_res["expiration_date"].isoformat() if ssl_res["expiration_date"] else None
                }
                url_res.update({"whois": whois_formatted, "ssl": ssl_formatted})
                analysis.website_data = url_res

            web_data = analysis.website_data
            whois_info = web_data.get("whois", {})
            ssl_info = web_data.get("ssl", {})

            # Reachability checks
            whois_failed = whois_info.get("whois_failed", True)
            has_valid_ssl = ssl_info.get("has_valid_ssl", False)
            is_reachable = not whois_failed or has_valid_ssl
            
            if not is_reachable:
                all_evidence.append({
                    "id": "website_unverified",
                    "title": "Website Could Not Be Verified",
                    "category": "website_security",
                    "severity": "medium",
                    "score": 0,  # 0 trust deduction
                    "matched_text": "DNS unresolvable / Connection timeout",
                    "description": "The provided website could not be reached or DNS resolution failed. This makes it impossible to verify SSL or registration details.",
                    "explanation": "No server response was received during SSL or WHOIS lookup verification.",
                    "evidence_type": "unknown",
                    "source": "Website Analyzer"
                })
            else:
                # Domain Age checks
                if not whois_failed:
                    age = whois_info.get("domain_age_days")
                    if age is not None:
                        if age >= 1825:  # 5+ Years
                            all_positives.append({
                                "id": "established_domain",
                                "title": "Established Website Domain",
                                "category": "domain_intelligence",
                                "severity": "low",
                                "score": 10,
                                "description": f"The website domain has been active for over 5 years ({age} days), representing a highly established organization.",
                                "matched_text": f"Age: {age} days",
                                "explanation": f"Domain age of {age/365:.1f} years exceeds the 5-year trust benchmark."
                            })
                        elif age < 30:
                            all_evidence.append({
                                "id": "very_young_domain",
                                "title": "Extremely Young Domain",
                                "category": "domain_intelligence",
                                "severity": "high",
                                "score": -25,
                                "description": "The website domain was registered less than 30 days ago. Temporary domains are frequently registered for short-term scam schemes.",
                                "matched_text": f"Age: {age} days",
                                "explanation": f"Domain age ({age} days) falls under the 30-day high-risk threshold."
                            })
                        elif age < 180:
                            all_evidence.append({
                                "id": "young_domain",
                                "title": "Young Domain",
                                "category": "domain_intelligence",
                                "severity": "medium",
                                "score": -15,
                                "description": f"The website domain is relatively new ({age} days ago), which increases the security risk of it being a temporary recruiting landing page.",
                                "matched_text": f"Age: {age} days",
                                "explanation": f"Domain age ({age} days) falls under the 6-month medium-risk threshold."
                            })

                # SSL checks
                if has_valid_ssl:
                    all_positives.append({
                        "id": "valid_ssl_certificate",
                        "title": "Encrypted Connection (HTTPS)",
                        "category": "website_security",
                        "severity": "low",
                        "score": 5,
                        "description": "The website enforces valid SSL/TLS encryption certificates, securing data submission transmissions.",
                        "matched_text": "SSL Active",
                        "explanation": "Valid SSL certificate verified successfully on port 443."
                    })
                else:
                    all_evidence.append({
                        "id": "missing_ssl",
                        "title": "Missing SSL Encryption",
                        "category": "website_security",
                        "severity": "medium",
                        "score": -15,
                        "description": "The site does not enforce encrypted HTTPS communication. Legitimate employers transmit credentials securely.",
                        "matched_text": "SSL Missing/Invalid",
                        "explanation": "No valid SSL certificate found active on port 443."
                    })

            # Scraped Page Content checks
            if web_data.get("has_privacy_policy"):
                all_positives.append({
                    "id": "active_privacy_policy",
                    "title": "Active Privacy Policy Page",
                    "category": "website_trust",
                    "severity": "low",
                    "score": 3,
                    "description": "Website contains explicit privacy policy compliance documentation, characteristic of standard corporate transparency.",
                    "matched_text": "Privacy Policy match in HTML",
                    "explanation": "Verified active Privacy Policy linkages on domain pages."
                })
            if web_data.get("has_terms_conditions"):
                all_positives.append({
                    "id": "active_terms_page",
                    "title": "Active Terms & Conditions Page",
                    "category": "website_trust",
                    "severity": "low",
                    "score": 3,
                    "description": "Website contains Terms and Conditions of service, showing standard regulatory compliance.",
                    "matched_text": "Terms match in HTML",
                    "explanation": "Verified active Terms linkages on domain pages."
                })
            if web_data.get("has_careers"):
                all_positives.append({
                    "id": "active_careers_page",
                    "title": "Active Careers Portal link",
                    "category": "website_trust",
                    "severity": "low",
                    "score": 4,
                    "description": "Website contains a dedicated careers page link, demonstrating structured hiring transparency.",
                    "matched_text": "Careers match in HTML",
                    "explanation": "Verified active Careers linkages on domain pages."
                })
            if web_data.get("has_linkedin"):
                all_positives.append({
                    "id": "linkedin_profile_linked",
                    "title": "LinkedIn Company Portal Linked",
                    "category": "website_trust",
                    "severity": "low",
                    "score": 5,
                    "description": "The company's website links to an official LinkedIn organization page.",
                    "matched_text": "LinkedIn link match in HTML",
                    "explanation": "Verified active LinkedIn corporate profiles linked in page body."
                })

        # 7. Email Intelligence checks
        if analysis.email_data:
            email_data = analysis.email_data
            
            if email_data.get("is_free_email"):
                all_evidence.append({
                    "id": "public_domain_email",
                    "title": "Public Domain Recruiter Email",
                    "category": "email_legitimacy",
                    "severity": "medium",
                    "score": -15,
                    "description": f"The recruiter is using a free public domain email address ({email_data.get('sender_email')}) instead of an official company email domain.",
                    "matched_text": email_data.get("sender_email"),
                    "explanation": "Sender uses free consumer address domain (Gmail/Yahoo/Outlook) for recruitment communications."
                })
            if email_data.get("is_disposable"):
                all_evidence.append({
                    "id": "disposable_email_domain",
                    "title": "Disposable Recruiter Email",
                    "category": "email_legitimacy",
                    "severity": "high",
                    "score": -25,
                    "description": "The recruiter is using a temporary disposable email mailbox, a significant indicator of spam and malicious operations.",
                    "matched_text": email_data.get("sender_email"),
                    "explanation": "Recruiter is routing messages via anonymous throwaway mailbox servers."
                })
            if email_data.get("domain") and not email_data.get("domain_exists"):
                all_evidence.append({
                    "id": "email_domain_non_existent",
                    "title": "Non-Existent Recruiter Domain",
                    "category": "email_legitimacy",
                    "severity": "high",
                    "score": -30,
                    "description": f"The recruiter domain '{email_data.get('domain')}' does not exist in public DNS databases.",
                    "matched_text": email_data.get("domain"),
                    "explanation": "Recruiter domain failed standard TCP/DNS lookup checks."
                })

        # 8. Contradiction Detection
        contr_res = ContradictionDetector.detect_contradictions(scam_text, analysis.email_data, analysis.website_data)
        contradictions = contr_res["contradictions"]
        all_evidence.extend(contr_res["evidence"])

        # 9. Company Footprint Verification
        from app.services.company_verifier import CompanyVerifier
        overall_verdict, verification_panel = CompanyVerifier.verify_company(
            email_data=analysis.email_data,
            website_data=analysis.website_data
        )
        is_verified_employer = (overall_verdict == "Verified")

        # 10. Input Quality Score & Missing Fields
        input_quality, missing_fields = ConfidenceCalculator.calculate_input_quality(
            scam_text,
            has_email=(analysis.email_data is not None and analysis.email_data.get("domain") != ""),
            has_url=(analysis.website_data is not None)
        )

        # 11. Normalize all Evidence and Positive findings
        enriched_evidence = []
        for item in all_evidence:
            src = "Rule Engine"
            if item.get("id", "").startswith("email_") or item.get("id", "").startswith("brand_vs_free_email") or item.get("id", "").startswith("public_domain") or item.get("id", "").startswith("disposable_email"):
                src = "Email Analyzer"
            elif item.get("id", "").startswith("website_") or item.get("id", "").startswith("young_") or item.get("id", "").startswith("very_young_") or item.get("id", "").startswith("claim_vs_") or item.get("id", "").startswith("https_vs_"):
                src = "Website Analyzer"
            elif item.get("id", "").startswith("history_vs_domain"):
                src = "Website Analyzer"
            enriched_evidence.append(enrich_evidence_item(item, is_positive=False, default_source=src))

        enriched_positives = []
        for item in all_positives:
            src = "Rule Engine"
            if item.get("id") in ["established_domain", "active_privacy_policy", "active_terms_page", "active_careers_page", "linkedin_profile_linked", "valid_ssl_certificate"]:
                src = "Website Analyzer"
            enriched_positives.append(enrich_evidence_item(item, is_positive=True, default_source=src))

        # 12. Chronological decision trace
        decision_trace = []
        decision_trace.append("Input Parsed successfully")
        decision_trace.append(f"Input Quality Calculated: {input_quality}/100")
        decision_trace.append(f"Website Verification DNS: {verification_panel.get('DNS')}, SSL: {verification_panel.get('SSL')}")
        decision_trace.append(f"Email Analysis: {verification_panel.get('Corporate Email')}")
        decision_trace.append(f"Rule Engine Evidence Collected: {len(enriched_evidence)} items")
        decision_trace.append(f"Contradictions Identified: {len(contradictions)} items")
        decision_trace.append(f"Verification Footprint Status: {overall_verdict}")

        # 13. AI Service Semantic Classification call
        ai_data = await ai_service.analyze_job(scam_text, enriched_evidence)
        decision_trace.append("AI Semantic Analysis reasoning complete")

        # Map rule score for consensus agreement check
        temp_trust = 100
        temp_negatives = [item for item in enriched_evidence if item.get("evidence_type") == "negative"]
        temp_trust -= sum(abs(item.get("score", 0)) for item in temp_negatives)
        temp_trust = max(0, min(100, temp_trust))
        
        has_fin = any(item.get("category") == "financial_fraud" for item in temp_negatives)
        has_id = any(item.get("category") == "identity_theft" for item in temp_negatives)
        
        temp_agreement, _ = RiskScorer.calculate_agreement(temp_trust, ai_data, has_fin, has_id)

        # 14. Redesigned Confidence Score calculation
        confidence_score = ConfidenceCalculator.calculate_confidence(
            scam_text,
            email_data=analysis.email_data,
            website_data=analysis.website_data,
            ocr_performed=analysis.ocr_performed,
            missing_info=missing_fields,
            agreement_score=temp_agreement
        )
        decision_trace.append(f"Confidence Score Calculated: {confidence_score}/100")

        # 15. Composite Risk Verdict & Agreement calculations
        trust_score, scam_probability, risk_category, agreement_score, agreement_explanation = RiskScorer.calculate_risk(
            evidence_list=enriched_evidence,
            positive_findings=enriched_positives,
            ai_classification=ai_data,
            is_verified_employer=is_verified_employer
        )
        decision_trace.append(f"Composite Trust Score: {trust_score}/100")
        decision_trace.append(f"Final Verdict: {risk_category}")

        # Merge AI red flags with rule engine flags (ensure unique titles)
        merged_flags = {item["title"]: item for item in red_flags}
        for ai_flag in ai_data.get("red_flags", []):
            title = ai_flag.get("title")
            if title not in merged_flags:
                merged_flags[title] = {
                    "title": title,
                    "description": ai_flag.get("description", ""),
                    "severity": ai_flag.get("severity", "medium")
                }

        # 16. Generate Contextual Safety Recommendations
        dynamic_recs = RecommendationEngine.generate_recommendations(
            evidence_list=enriched_evidence,
            positive_findings=enriched_positives,
            verification_status=verification_panel
        )

        # 17. Save V2.1 metrics and updates to database document
        analysis.trust_score = trust_score
        analysis.scam_probability = scam_probability
        analysis.risk_category = risk_category
        analysis.confidence_score = confidence_score
        analysis.agreement_score = agreement_score
        analysis.contradictions = contradictions
        analysis.missing_information = missing_fields
        analysis.evidence = enriched_evidence
        analysis.positive_findings = enriched_positives
        analysis.red_flags = list(merged_flags.values())
        analysis.ai_summary = ai_data.get("ai_summary", "")
        analysis.risk_explanation = ai_data.get("risk_explanation", "")
        analysis.recommendations = dynamic_recs
        
        # Version 2.1 specific
        analysis.input_quality_score = input_quality
        analysis.verification_status = verification_panel
        analysis.agreement_explanation = agreement_explanation
        analysis.decision_trace = decision_trace
        
        analysis.status = "completed"
        analysis.processing_time_ms = int((time.time() - start_time) * 1000)
        analysis.gemini_api_called = ai_service.enabled
        
        await analysis.save()

        # Create completed notification
        notif = Notification(
            user_id=analysis.user_id,
            type="analysis_complete",
            title="Analysis Completed",
            message=f"Your job check is complete. Verdict: {analysis.risk_category} (Score: {analysis.trust_score}/100)",
            analysis_id=analysis.id
        )
        await notif.save()
        logger.info(f"Async pipeline V2.1 completed successfully for job ID: {analysis_id}")
        
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
        # Cleanup uploaded temporary files immediately
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logger.info(f"Successfully cleaned up temporary upload file: {temp_file_path}")
            except Exception as e:
                logger.error(f"Failed to delete temporary file {temp_file_path}: {e}")
