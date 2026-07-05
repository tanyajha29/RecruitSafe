from fastapi import APIRouter, Depends, status
import logging
from typing import Dict

from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.analysis import DashboardStats, AnalysisSummary
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])
logger = logging.getLogger("recruitsafe")

@router.get("", response_model=DashboardStats, status_code=status.HTTP_200_OK)
async def get_dashboard_stats(current_user: User = Depends(get_current_user)):
    """
    Retrieves aggregated dashboard statistics for the authenticated user,
    including total checks, risk category counts, risk distribution percentages,
    and a list of the 5 most recent analyses.
    """
    logger.info(f"Retrieving dashboard statistics for user: {current_user.email}")
    
    # Query all analyses for the current user
    user_analyses = await Analysis.find(Analysis.user_id == current_user.id).to_list()
    
    total = len(user_analyses)
    safe = 0
    needs_verification = 0
    suspicious = 0
    high_risk = 0
    
    for analysis in user_analyses:
        if analysis.status == "completed":
            cat = analysis.risk_category
            if cat == "Safe":
                safe += 1
            elif cat == "Needs Verification":
                needs_verification += 1
            elif cat == "Suspicious":
                suspicious += 1
            elif cat == "High Risk":
                high_risk += 1

    # Fetch 5 most recent analyses sorted by creation date descending
    recent_docs = await Analysis.find(
        Analysis.user_id == current_user.id
    ).sort(-Analysis.created_at).limit(5).to_list()

    recent_summaries = []
    for doc in recent_docs:
        # Create preview text from original content (first 50 characters)
        preview = ""
        if doc.original_content:
            preview = doc.original_content[:50]
            if len(doc.original_content) > 50:
                preview += "..."
                
        recent_summaries.append(
            AnalysisSummary(
                id=str(doc.id),
                input_type=doc.input_type,
                original_content=preview,
                trust_score=doc.trust_score,
                risk_category=doc.risk_category or "Processing",
                created_at=doc.created_at
            )
        )

    # Calculate risk distribution percentage
    distribution: Dict[str, float] = {
        "Safe": 0.0,
        "Needs Verification": 0.0,
        "Suspicious": 0.0,
        "High Risk": 0.0
    }
    
    if total > 0:
        distribution["Safe"] = round((safe / total) * 100, 1)
        distribution["Needs Verification"] = round((needs_verification / total) * 100, 1)
        distribution["Suspicious"] = round((suspicious / total) * 100, 1)
        distribution["High Risk"] = round((high_risk / total) * 100, 1)

    return DashboardStats(
        total_analyses=total,
        safe_count=safe,
        needs_verification_count=needs_verification,
        suspicious_count=suspicious,
        high_risk_count=high_risk,
        recent_analyses=recent_summaries,
        risk_distribution=distribution
    )
