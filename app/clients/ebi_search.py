import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EBISearchClient:
    def __init__(self):
        self.base_url = settings.ebi_search_url
        
    async def search(self, domain: str, query: str, size: int = 10):
        url = f"{self.base_url}/{domain}"
        params = {
            "query": query,
            "size": size,
            "format": "json",
            "fields": "name,description"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                return data.get("entries", [])
            except Exception as e:
                logger.error(f"EBI Search API error: {e}")
                return []

    async def get_domains(self):
        # In a real app we'd fetch this from /domains endpoint
        return ["uniprot", "europe_pmc", "ensembl", "pdbe"]

ebi_search_client = EBISearchClient()
