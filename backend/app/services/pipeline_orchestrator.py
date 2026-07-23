import re
import time
import logging
from typing import Dict, Any, List, Tuple, Optional

from app.services.scam_detector import ScamRuleEngine
from app.services.salary_analyzer import SalaryAnalyzer
from app.services.psych_manipulation import PsychologicalDetector
from app.services.identity_theft import IdentityTheftDetector
from app.services.email_verifier import EmailVerifier
from app.services.website_verifier import WebsiteVerifier
from app.services.hiring_workflow_analyzer import HiringWorkflowAnalyzer
from app.services.company_verifier import CompanyVerifier
from app.services.confidence_calculator import ConfidenceCalculator
from app.services.risk_scorer import RiskScorer
from app.services.recommendation_engine import RecommendationEngine
from app.services.ai.ai_provider import ai_service

logger = logging.getLogger("recruitsafe")

class PipelineOrchestrator:
    """
    Modular coordinator that executes EmailVerifier, WebsiteVerifier,
    HiringWorkflowAnalyzer, and scoring engines in a clean pipeline.
    """

    @staticmethod
    def enrich_evidence_item(item: Dict[str, Any], is_positive: bool, default_source: str = "Rule Engine") -> Dict[str, Any]:
        """
        Enriches evidence objects to guarantee presence of the 10 V2.2 attributes
        while maintaining backward compatibility.
        """
        enriched = dict(item)
        
        # 1. id
        if "id" not in enriched:
            title_slug = re.sub(r'[^a-z0-9]', '_', enriched.get("title", enriched.get("factor_name", "generic")).lower())
            enriched["id"] = f"ev_{title_slug}"
            
        # 2. title
        if "title" not in enriched:
            enriched["title"] = enriched.get("factor_name", enriched.get("id", "Evidence Item")).replace("_", " ").title()
            
        # 3. category
        if "category" not in enriched:
            enriched["category"] = "general"
            
        # 4. severity
        if "severity" not in enriched:
            enriched["severity"] = "low" if is_positive else "medium"
            
        # 5. score
        if "score" not in enriched:
            pts = enriched.get("points_deducted", 0)
            if is_positive:
                enriched["score"] = pts if pts > 0 else 5
            else:
                enriched["score"] = -abs(pts) if pts != 0 else -10
                
        # 6. matched_text (Evidence)
        if "matched_text" not in enriched or not enriched["matched_text"] or enriched["matched_text"] == "Extracted context text":
            enriched["matched_text"] = enriched.get("matched_text") or f"Extracted details for {enriched['title']}"
            
        # 7. reason (Reason)
        if "reason" not in enriched or not enriched["reason"] or enriched["reason"] == "No explicit reasoning provided.":
            enriched["reason"] = enriched.get("reason") or enriched.get("description") or f"Legitimacy or threat validation matching rule {enriched['id']}"
            
        # 8. evidence_type
        if "evidence_type" not in enriched:
            score_val = enriched.get("score", 0)
            if enriched.get("id") == "website_unverified" or score_val == 0:
                enriched["evidence_type"] = "unknown"
            elif is_positive or score_val > 0:
                enriched["evidence_type"] = "positive"
            else:
                enriched["evidence_type"] = "negative"
                
        # 9. confidence impact
        if "confidence" not in enriched:
            sev = enriched.get("severity", "medium").lower()
            if sev == "high":
                enriched["confidence"] = 15
            elif sev == "medium":
                enriched["confidence"] = 10
            else:
                enriched["confidence"] = 5
                
        # 10. description (legacy map)
        enriched["description"] = enriched["reason"]
        
        # rule_id compatibility (Rule ID)
        if "rule_id" not in enriched:
            enriched["rule_id"] = enriched["id"]
        
        # weight mapping (Weight)
        enriched["weight"] = enriched["score"]
        
        # Backwards compatible mapping
        enriched["factor_name"] = enriched["title"]
        enriched["points_deducted"] = abs(enriched["score"])
        
        # 11. source
        if "source" not in enriched:
            enriched["source"] = default_source
            
        return enriched

    @classmethod
    async def process_analysis(
        cls,
        input_type: str,
        original_content: str,
        processed_text: Optional[str] = None,
        ocr_performed: bool = False,
        structured_evidence: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Runs the sequential assessment logic flow deterministically."""
        start_time = time.time()
        decision_trace = []
        decision_trace.append("Pipeline orchestration started.")

        scam_text = processed_text or original_content or ""

        # 1. Website Verification Check
        website_data = None
        detected_url = None
        if input_type == "url":
            detected_url = original_content
        else:
            detected_url = WebsiteVerifier.extract_url(scam_text)

        if detected_url:
            careers_url_entity = (structured_evidence or {}).get("careers_url", {})
            careers_url_val = careers_url_entity.get("value") if isinstance(careers_url_entity, dict) else getattr(careers_url_entity, "value", None)
            careers_url_exists = (
                careers_url_val is not None 
                and str(careers_url_val).strip() != "" 
                and str(careers_url_val).strip().lower() not in ["unknown", "none", "not found", "not_found"]
            )
            decision_trace.append(f"Extracting and verifying website presence: {detected_url} (Careers pre-extracted: {careers_url_exists})")
            website_data = await WebsiteVerifier.verify_website(detected_url, careers_url_exists=careers_url_exists)
            decision_trace.append("Website presence crawled successfully.")

        # 2. Email Verification Check
        email_data = None
        detected_email = None
        if input_type == "email":
            # Match email pattern
            match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', original_content)
            if match:
                detected_email = match.group(0)
        else:
            match = re.search(r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b', scam_text)
            if match:
                detected_email = match.group(0)

        if detected_email:
            company_domain = WebsiteVerifier.parse_domain(detected_url) if detected_url else None
            decision_trace.append(f"Verifying recruiter email address: {detected_email}")
            email_data = await EmailVerifier.verify_recruiter_email(detected_email, company_domain)
            decision_trace.append("Recruiter email verifications checked.")

        # 3. Hiring Process Workflow Check
        decision_trace.append("Running Hiring Workflow checks...")
        workflow_data = HiringWorkflowAnalyzer.analyze_workflow(scam_text)
        decision_trace.append(f"Workflow sequence evaluated: Type {workflow_data['type']}, Score {workflow_data['score']}")

        # 4. Rules evidence scan
        all_evidence = []
        all_positives = []

        # Technical scan matches
        rule_evidence, red_flags, _ = ScamRuleEngine.analyze_text(scam_text, structured_evidence)
        all_evidence.extend(rule_evidence)

        # Salary check
        salary_res = SalaryAnalyzer.analyze_salary(scam_text)
        all_evidence.extend(salary_res["evidence"])
        all_positives.extend(salary_res["positive_findings"])

        # Psych checks
        psych_res = PsychologicalDetector.analyze_manipulation(scam_text)
        all_evidence.extend(psych_res["evidence"])

        # Identity checks
        id_res = IdentityTheftDetector.analyze_identity_requests(scam_text)
        all_evidence.extend(id_res["evidence"])

        # 5. Extract verification statuses from Web & Email Verifiers
        overall_verdict, verification_panel = CompanyVerifier.verify_company(
            email_data=email_data,
            website_data=website_data
        )
        is_verified_employer = (overall_verdict == "Verified")

        # Map Web Verifier findings to technical evidence
        if website_data:
            dns_info = website_data.get("dns", {})
            ssl_info = website_data.get("ssl", {})
            whois_info = website_data.get("whois", {})

            if not dns_info.get("resolves", False):
                all_evidence.append({
                    "id": "website_unreachable",
                    "title": "Website Unreachable",
                    "category": "website_security",
                    "severity": "medium",
                    "score": 0,  # Unknown, does not reduce trust
                    "matched_text": "DNS Lookup Failed",
                    "reason": "The domain resolved to no IP addresses, showing it is unresolvable.",
                    "evidence_type": "unknown"
                })
            else:
                # SSL certification check
                if ssl_info.get("has_valid_ssl", False):
                    all_positives.append({
                        "id": "valid_ssl_certificate",
                        "title": "HTTPS Enforced",
                        "category": "website_security",
                        "severity": "low",
                        "score": 5,
                        "matched_text": "SSL Valid",
                        "reason": f"Connection on port 443 is encrypted. Certificate issuer: {ssl_info.get('issuer')}",
                        "evidence_type": "positive"
                    })
                else:
                    all_evidence.append({
                        "id": "missing_ssl",
                        "title": "Missing SSL Certificate",
                        "category": "website_security",
                        "severity": "medium",
                        "score": -10,  # Reduces trust
                        "matched_text": "SSL Handshake Failed / HTTP",
                        "reason": "Connection to website does not use SSL/HTTPS encryption, raising security risks.",
                        "evidence_type": "negative"
                    })

                # WHOIS Domain Age
                if whois_info and not whois_info.get("whois_failed", True):
                    age = whois_info.get("domain_age_days")
                    if age is not None:
                        if age >= 1825:
                            all_positives.append({
                                "id": "established_domain",
                                "title": "Established Company Domain",
                                "category": "domain_intelligence",
                                "severity": "low",
                                "score": 10,
                                "matched_text": f"{age} Days Old",
                                "reason": f"Website domain has been registered for over 5 years ({age // 365} years).",
                                "evidence_type": "positive"
                            })
                        elif age < 30:
                            all_evidence.append({
                                "id": "very_young_domain",
                                "title": "Newly Registered Domain",
                                "category": "domain_intelligence",
                                "severity": "high",
                                "score": -25,
                                "matched_text": f"{age} Days Old",
                                "reason": "The website domain was registered within the last 30 days, typical of temporary scam domains.",
                                "evidence_type": "negative"
                            })

                # Crawled links
                if website_data.get("has_privacy_policy"):
                    all_positives.append({
                        "id": "active_privacy_policy",
                        "title": "Privacy Policy Present",
                        "category": "website_trust",
                        "severity": "low",
                        "score": 3,
                        "matched_text": "Privacy Link Found",
                        "reason": "Website contains a standard Privacy Policy or data protection guidelines.",
                        "evidence_type": "positive"
                    })
                if website_data.get("has_careers"):
                    all_positives.append({
                        "id": "active_careers_page",
                        "title": "Careers Page Present",
                        "category": "website_trust",
                        "severity": "low",
                        "score": 5,
                        "matched_text": "Careers Portal Found",
                        "reason": "Website has a dedicated career links portal.",
                        "evidence_type": "positive"
                    })
                if website_data.get("has_linkedin"):
                    all_positives.append({
                        "id": "linkedin_profile_linked",
                        "title": "LinkedIn Company Page Linked",
                        "category": "website_trust",
                        "severity": "low",
                        "score": 5,
                        "matched_text": "LinkedIn Icon Found",
                        "reason": "Website links directly to an official LinkedIn corporate page.",
                        "evidence_type": "positive"
                    })
        else:
            # Website unsupplied/missing
            all_evidence.append({
                "id": "website_unsupplied",
                "title": "Website Not Supplied",
                "category": "website_security",
                "severity": "medium",
                "score": 0,  # Unknown, does not reduce trust
                "matched_text": "None",
                "reason": "No website URL or company website was mentioned in the posting text.",
                "evidence_type": "unknown"
            })

        # Map Email Verifier findings to technical evidence
        if email_data:
            if email_data.get("is_free_email"):
                all_evidence.append({
                    "id": "public_domain_email",
                    "title": "Public Domain Recruiter Email",
                    "category": "email_legitimacy",
                    "severity": "medium",
                    "score": -15,
                    "matched_text": email_data.get("sender_email"),
                    "reason": "Recruiter is contacting candidates from a free public domain (gmail, yahoo, outlook) rather than corporate server.",
                    "evidence_type": "negative"
                })
            elif email_data.get("is_disposable"):
                all_evidence.append({
                    "id": "disposable_email_domain",
                    "title": "Disposable Recruiter Email",
                    "category": "email_legitimacy",
                    "severity": "high",
                    "score": -25,
                    "matched_text": email_data.get("sender_email"),
                    "reason": "Recruiter is routing messages using temporary, disposable email mailboxes.",
                    "evidence_type": "negative"
                })
            elif not email_data.get("domain_exists"):
                all_evidence.append({
                    "id": "email_domain_non_existent",
                    "title": "Non-Existent Recruiter Domain",
                    "category": "email_legitimacy",
                    "severity": "high",
                    "score": -30,
                    "matched_text": email_data.get("domain"),
                    "reason": "The recruiter domain does not resolve to any active DNS records.",
                    "evidence_type": "negative"
                })
            elif email_data.get("verification_status") == "Verified":
                all_positives.append({
                    "id": "verified_corporate_email",
                    "title": "Verified Corporate Recruiter Email",
                    "category": "email_legitimacy",
                    "severity": "low",
                    "score": 5,
                    "matched_text": email_data.get("sender_email"),
                    "reason": "Recruiter uses an official company domain with verified active MX mail server records.",
                    "evidence_type": "positive"
                })

        # 6. Normalize and enrich all evidence
        enriched_evidence = [cls.enrich_evidence_item(item, is_positive=False) for item in all_evidence]
        enriched_positives = [cls.enrich_evidence_item(item, is_positive=True) for item in all_positives]

        # 7. AI Semantic completes checks
        decision_trace.append("Calling AI provider completions...")
        ai_data = await ai_service.analyze_job(scam_text, enriched_evidence)
        decision_trace.append("AI reasoning finished.")

        # 8. Consensus, Agreement, and Trust scoring
        trust_score, scam_prob, risk_cat, agreement_score, agreement_expl = RiskScorer.calculate_risk(
            evidence_list=enriched_evidence,
            positive_findings=enriched_positives,
            ai_classification=ai_data,
            is_verified_employer=is_verified_employer
        )

        # 9. Confidence Score
        input_quality, missing_fields = ConfidenceCalculator.calculate_input_quality(
            scam_text,
            has_email=(email_data is not None and email_data.get("domain") != ""),
            has_url=(website_data is not None)
        )
        
        confidence_score = ConfidenceCalculator.calculate_confidence(
            scam_text,
            email_data=email_data,
            website_data=website_data,
            ocr_performed=ocr_performed,
            missing_info=missing_fields,
            agreement_score=agreement_score
        )

        # 10. Contextual recommendations
        recs = RecommendationEngine.generate_recommendations(
            evidence_list=enriched_evidence,
            positive_findings=enriched_positives,
            verification_status=verification_panel
        )

        # 11. Run Machine Learning Model prediction
        from app.services.ai.ml_service import MLService
        ml_prediction, ml_probability = MLService.predict(scam_text)

        # 12. Run Decision Fusion Engine
        from app.services.fusion.fusion_engine import DecisionFusionEngine
        fusion_result = DecisionFusionEngine.fuse_decision(
            canonical_entities=structured_evidence or {},
            rule_engine_result=enriched_evidence,
            verification_result=verification_panel,
            ml_prediction=ml_prediction,
            ml_probability=ml_probability
        )

        # Override legacy scoring metrics with hybrid decision fusion outputs
        verdict_mapping = {
            "SAFE": "Safe",
            "SUSPICIOUS": "Suspicious",
            "HIGH_RISK": "High Risk",
            "SCAM": "Scam"
        }
        fused_verdict = verdict_mapping.get(fusion_result["final_verdict"], "Suspicious")

        trust_score = 100 - fusion_result["final_risk_score"]
        scam_prob = float(fusion_result["final_risk_score"])
        risk_cat = fused_verdict
        confidence_score = int(fusion_result["confidence"])
        recs = fusion_result["recommended_actions"]

        decision_trace.append(f"Decision Fusion Engine complete: Verdict={risk_cat}, Risk Score={scam_prob}")
        decision_trace.append("Pipeline orchestration completed successfully.")

        # Build Hybrid Decision Summary explanation
        risk_explanation = f"""### Hybrid Decision Summary
* **Final Trust Verdict**: {risk_cat}
* **Scam Probability (Weighted Risk Score)**: {scam_prob}/100
* **Analysis Confidence**: {confidence_score}%

### Decision Breakdown
* **Rule Engine Scam Index**: {fusion_result['decision_breakdown']['rule_engine']['score']}/100
  * Key Indicators: {", ".join(fusion_result['decision_breakdown']['rule_engine']['reasons']) or "None"}
* **Verification Risk Score**: {fusion_result['decision_breakdown']['verification']['score']}/100
  * Failed Verifications: {", ".join(fusion_result['decision_breakdown']['verification']['reasons']) or "None"}
* **Machine Learning Content Scorer**:
  * Scam Probability: {round(fusion_result['decision_breakdown']['machine_learning']['probability'] * 100, 1)}%
  * Classifier Verdict: {fusion_result['decision_breakdown']['machine_learning']['prediction']}
"""

        # Build programmatic, evidence-based executive summary
        summary_parts = [
            f"Hybrid Decision Intelligence evaluated this job listing as {risk_cat} with {confidence_score}% confidence.",
            f"Rule engine scam index is {fusion_result['decision_breakdown']['rule_engine']['score']}/100.",
            f"Verification risk score is {fusion_result['decision_breakdown']['verification']['score']}/100.",
            f"XGBoost content classifier predicted scam probability of {round(fusion_result['decision_breakdown']['machine_learning']['probability'] * 100, 1)}%."
        ]
        evidence_based_summary = " ".join(summary_parts)

        # Compile final dictionary result
        return {
            "trust_score": trust_score,
            "scam_probability": scam_prob,
            "risk_category": risk_cat,
            "confidence_score": confidence_score,
            "agreement_score": agreement_score,
            "agreement_explanation": agreement_expl,
            "input_quality_score": input_quality,
            "verification_status": verification_panel,
            "evidence": enriched_evidence,
            "positive_findings": enriched_positives,
            "recommendations": recs,
            "ai_summary": evidence_based_summary,
            "risk_explanation": risk_explanation,
            "red_flags": ai_data.get("red_flags", []),
            "website_data": website_data,
            "email_data": email_data,
            "hiring_workflow": workflow_data,
            "decision_trace": decision_trace,
            "hybrid_verdict": fusion_result,
            "processing_time_ms": int((time.time() - start_time) * 1000)
        }
