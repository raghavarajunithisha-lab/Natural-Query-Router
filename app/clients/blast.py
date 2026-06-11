import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class BlastClient:
    def __init__(self):
        self.base_url = settings.blast_url
        self.email = settings.ebi_email
        
    async def submit_job(self, sequence: str, program: str = "blastp", database: str = "uniprotkb"):
        url = f"{self.base_url}/ncbiblast/run"
        data = {
            "email": self.email,
            "program": program,
            "stype": "protein" if program == "blastp" else "dna",
            "sequence": sequence,
            "database": database
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(url, data=data, timeout=10.0)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"BLAST submission error: {e}")
                raise
                
    async def get_status(self, job_id: str):
        url = f"{self.base_url}/ncbiblast/status/{job_id}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"BLAST status error: {e}")
                return "ERROR"
                
    async def get_results(self, job_id: str):
        url = f"{self.base_url}/ncbiblast/result/{job_id}/out"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=20.0)
                response.raise_for_status()
                return response.text
            except Exception as e:
                logger.error(f"BLAST result error: {e}")
                return None

blast_client = BlastClient()
