from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class BlastSubmitReq(BaseModel):
    sequence: str
    program: str = "blastp"
    database: str = "uniprotkb"

@router.post("/submit")
async def submit_blast(req: BlastSubmitReq):
    try:
        from app.clients.blast import blast_client
        job_id = await blast_client.submit_job(req.sequence, req.program, req.database)
        return {"job_id": job_id, "status": "SUBMITTED"}
    except Exception as e:
        logger.error(f"BLAST submission failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}")
async def check_status(job_id: str):
    try:
        from app.clients.blast import blast_client
        status = await blast_client.get_status(job_id)
        return {"job_id": job_id, "status": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/results/{job_id}")
async def get_results(job_id: str):
    try:
        from app.clients.blast import blast_client
        results = await blast_client.get_results(job_id)
        return {"job_id": job_id, "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
