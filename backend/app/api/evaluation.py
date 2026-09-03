import json
import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException

logger = logging.getLogger("ventureos.api.evaluation")

router = APIRouter(tags=["AI System Evaluation"])


@router.get("/api/evaluation/latest")
@router.get("/evaluation/latest")
async def get_latest_evaluation():
    """
    Returns the most recent saved automated evaluation summary.
    This is an informational inspection endpoint; expensive evaluation runs are executed via CLI.
    """
    report_file = Path(__file__).parent.parent / "evaluation" / "reports" / "latest_evaluation.json"
    if not report_file.exists():
        raise HTTPException(
            status_code=404,
            detail="No evaluation run report found. Execute 'python -m app.evaluation.run_evaluation' first.",
        )

    try:
        with open(report_file, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return {
            "success": True,
            "evaluation": data,
        }
    except Exception as e:
        logger.error("Failed to read evaluation report: %s", e)
        raise HTTPException(status_code=500, detail="Failed to load evaluation report.")
