import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class EuropePMCClient:
    def __init__(self):
        self.base_url = settings.europe_pmc_url
        
    async def search_publications(self, query: str, size: int = 10):
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "resultType": "lite",
            "cursorMark": "*",
            "pageSize": size,
            "format": "json"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                return data.get("resultList", {}).get("result", [])
            except Exception as e:
                logger.error(f"Europe PMC API error: {e}")
                return []

europe_pmc_client = EuropePMCClient()
