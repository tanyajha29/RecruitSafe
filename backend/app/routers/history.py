import logging
from typing import Optional
from fastapi import APIRouter, Depends, status

from app.models.user import User
from app.models.analysis import Analysis
from app.schemas.analysis import HistoryResponse, AnalysisSummary
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["History"])
logger = logging.getLogger("recruitsafe")

@router.get("", response_model=HistoryResponse, status_code=status.HTTP_200_OK)
async def get_history(
    page: int = 1,
    per_page: int = 10,
    q: Optional[str] = None,
    risk_category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieves a paginated list of previous analyses performed by the user.
    Allows filtering by risk category and search terms matching original content/text layers.
    """
    logger.info(f"Retrieving analysis history for user: {current_user.email} (page={page}, per_page={per_page})")
    
    # 1. Base query for user's analyses
    query = Analysis.find({"user_id": current_user.id})
    
    # 2. Apply risk category filter
    if risk_category and risk_category != "":
        query = query.find({"risk_category": risk_category})
        
    # 3. Apply search filter
    if q and q.strip() != "":
        search_pattern = f".*{q.strip()}.*"
        query = query.find({
            "$or": [
                {"original_content": {"$regex": search_pattern, "$options": "i"}},
                {"processed_text": {"$regex": search_pattern, "$options": "i"}}
            ]
        })

    # 4. Count total matching documents
    total = await query.count()
    
    # 5. Retrieve paginated sorted list
    skip_val = (page - 1) * per_page
    docs = await query.sort("-created_at").skip(skip_val).limit(per_page).to_list()
    
    # 6. Format summaries
    summaries = []
    for doc in docs:
        preview = ""
        if doc.original_content:
            preview = doc.original_content[:50]
            if len(doc.original_content) > 50:
                preview += "..."
                
        summaries.append(
            AnalysisSummary(
                id=str(doc.id),
                input_type=doc.input_type,
                original_content=preview,
                trust_score=doc.trust_score,
                risk_category=doc.risk_category or "Processing",
                created_at=doc.created_at
            )
        )

    return HistoryResponse(
        total=total,
        page=page,
        per_page=per_page,
        analyses=summaries
    )
