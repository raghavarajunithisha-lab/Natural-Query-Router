from elasticsearch import AsyncElasticsearch
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class ElasticsearchService:
    def __init__(self):
        self.es = AsyncElasticsearch(settings.es_hosts)
        self.fallback_mode = False
        self._cache = {} # In-memory cache for fallback
        
    async def initialize(self):
        try:
            info = await self.es.info()
            logger.info(f"Connected to Elasticsearch: {info['version']['number']}")
            # Ensure index exists
            if not await self.es.indices.exists(index="ebi_cache"):
                await self.es.indices.create(index="ebi_cache")
                logger.info("Created ebi_cache index")
        except Exception as e:
            logger.warning(f"Could not connect to Elasticsearch. Enabling fallback mode. Error: {e}")
            self.fallback_mode = True

    async def execute_search(self, parsed_intent: dict):
        """
        Executes search using ES cache if available, else falls back to direct API calls.
        """
        api_query = parsed_intent["api_query_string"]
        target = parsed_intent["target_api"]
        cache_key = f"{target}::{api_query}"
        
        # Check if we have a cached response for this exact query
        if not self.fallback_mode:
            try:
                res = await self.es.get(index="ebi_cache", id=cache_key, ignore=[404])
                if res and "_source" in res:
                    logger.info("Cache hit in Elasticsearch")
                    return res["_source"]["data"]
            except Exception as e:
                logger.error(f"ES cache read error: {e}")
        else:
            if cache_key in self._cache:
                logger.info("Cache hit in memory fallback")
                return self._cache[cache_key]
                
        # If not in cache, route the request to the appropriate EMBL-EBI API client
        logger.info(f"Cache miss. Fetching from {target} for query: {api_query}")
        results = await self._fetch_from_api(target, api_query, parsed_intent)
        
        # Save the successful API response into the cache for next time
        if not self.fallback_mode:
            try:
                await self.es.index(index="ebi_cache", id=cache_key, document={"data": results})
            except Exception as e:
                logger.error(f"ES cache write error: {e}")
        else:
            self._cache[cache_key] = results
            
        return results

    async def _fetch_from_api(self, target: str, query: str, parsed_intent: dict = None):
        if target == "uniprot":
            from app.clients.uniprot import uniprot_client
            return await uniprot_client.search_proteins(query)
        elif target == "europe_pmc":
            from app.clients.europe_pmc import europe_pmc_client
            return await europe_pmc_client.search_publications(query)
        elif target == "ensembl_gene":
            from app.clients.ensembl import ensembl_client
            species = "human"
            if parsed_intent and parsed_intent.get("entities") and parsed_intent["entities"].get("taxonomy_name"):
                species = parsed_intent["entities"]["taxonomy_name"].replace(" ", "_")
            res = await ensembl_client.lookup_symbol(species, query)
            return [res] if res and "id" in res else []
        else:
            from app.clients.ebi_search import ebi_search_client
            return await ebi_search_client.search("europepmc", query)

es_service = ElasticsearchService()
