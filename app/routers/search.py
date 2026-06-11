from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class SearchQuery(BaseModel):
    query: str

@router.post("")
async def perform_search(search_query: SearchQuery):
    """
    Accepts a natural language query, parses it, and executes the search
    across appropriate EMBL-EBI endpoints or local Elasticsearch cache.
    """
    logger.info(f"Received query: {search_query.query}")
    try:
        from app.nlq.parser import NLQParser
        from app.search.elasticsearch_service import es_service
        
        parser = NLQParser()
        parsed_intent = parser.parse(search_query.query)
        
        # In a real flow, we'd check ES cache first, or execute external query
        results = await es_service.execute_search(parsed_intent)
        
        return {
            "query": search_query.query,
            "parsed_intent": parsed_intent,
            "results": results
        }
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/suggest")
async def suggest(q: str):
    """Autocomplete suggestions for search box."""
    return {"suggestions": [f"{q} cancer", f"{q} protein", f"{q} structure"]}

@router.get("/domains")
async def domains():
    """List available domains to search."""
    return {"domains": ["uniprot", "europe_pmc", "ensembl", "ebi_search"]}
