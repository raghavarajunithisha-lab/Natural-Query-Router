from mcp.server.fastmcp import FastMCP
import asyncio
import os
import sys

# Add project root to sys.path so we can import from app
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.clients.uniprot import uniprot_client
from app.clients.europe_pmc import europe_pmc_client
from app.clients.ensembl import ensembl_client
from app.clients.blast import blast_client
from app.clients.ebi_search import ebi_search_client
from app.nlq.parser import NLQParser

mcp = FastMCP("EMBL-EBI SearchBot")
nlq_parser = NLQParser()

@mcp.tool()
async def search_proteins(query: str, size: int = 5) -> str:
    """Search UniProt for protein information by gene, name, or organism."""
    results = await uniprot_client.search_proteins(query, size)
    return str(results)

@mcp.tool()
async def search_publications(query: str, size: int = 5) -> str:
    """Search Europe PMC for scientific papers."""
    results = await europe_pmc_client.search_publications(query, size)
    return str(results)

@mcp.tool()
async def search_genes(species: str, symbol: str) -> str:
    """Look up gene information via Ensembl."""
    result = await ensembl_client.lookup_symbol(species, symbol)
    return str(result)

@mcp.tool()
async def run_blast(sequence: str, program: str = "blastp", database: str = "uniprotkb") -> str:
    """Submit a BLAST sequence search."""
    job_id = await blast_client.submit_job(sequence, program, database)
    return f"Job submitted successfully. Job ID: {job_id}"

@mcp.tool()
async def get_blast_results(job_id: str) -> str:
    """Retrieve BLAST job results given a Job ID."""
    status = await blast_client.get_status(job_id)
    if status == "RUNNING":
        return "Job is still running. Try again later."
    results = await blast_client.get_results(job_id)
    return str(results)

@mcp.tool()
async def search_ebi(query: str, domain: str = "ebi") -> str:
    """General EBI Search across domains."""
    results = await ebi_search_client.search(domain, query)
    return str(results)

@mcp.tool()
async def natural_language_search(query: str) -> str:
    """Accept a plain-text question and return structured search results."""
    parsed_intent = nlq_parser.parse(query)
    api_query = parsed_intent["api_query_string"]
    target = parsed_intent["target_api"]
    
    if target == "uniprot":
        res = await uniprot_client.search_proteins(api_query)
    elif target == "europe_pmc":
        res = await europe_pmc_client.search_publications(api_query)
    elif target == "blast":
        res = await blast_client.submit_job(api_query)
        return f"BLAST job submitted for sequence. Job ID: {res}"
    else:
        res = await ebi_search_client.search("ebi", api_query)
        
    return str(res)

@mcp.resource("embl://databases")
def get_databases() -> str:
    """List of available EMBL-EBI databases."""
    return "Available databases: uniprot, europe_pmc, ensembl, pdbe, ebi_search."

@mcp.resource("embl://search-help")
def get_search_help() -> str:
    """Search syntax help and examples."""
    return "Examples: 'human kinases', 'recent CRISPR papers', 'TP53 structure'."

@mcp.prompt()
def biological_query(query: str) -> str:
    """Template for asking biological questions."""
    return f"Please analyze the following biological query using the available EMBL tools: {query}"

if __name__ == "__main__":
    mcp.run()
