import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EnsemblClient:
    def __init__(self):
        self.base_url = settings.ensembl_url
        
    async def lookup_symbol(self, species: str, symbol: str):
        url = f"{self.base_url}/lookup/symbol/{species}/{symbol}"
        headers = {"Content-Type": "application/json"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"Ensembl API error: {e}")
                return None

ensembl_client = EnsemblClient()
