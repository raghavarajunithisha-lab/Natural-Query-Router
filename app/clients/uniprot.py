import httpx
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class UniProtClient:
    def __init__(self):
        self.base_url = settings.uniprot_url
        
    async def search_proteins(self, query: str, size: int = 10):
        url = f"{self.base_url}/uniprotkb/search"
        params = {
            "query": query,
            "size": size,
            "format": "json",
            "fields": "accession,id,protein_name,gene_names,organism_name,length"
        }
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, params=params, timeout=10.0)
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
            except Exception as e:
                logger.error(f"UniProt API error: {e}")
                return []
                
    async def get_protein(self, accession: str):
        url = f"{self.base_url}/uniprotkb/{accession}"
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, timeout=10.0)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                logger.error(f"UniProt get protein error: {e}")
                return None

uniprot_client = UniProtClient()
