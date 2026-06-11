from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    es_hosts: str = "http://localhost:9200"
    ebi_email: str = "searchbot-prototype@ebi.ac.uk"
    llm_api_key: str | None = None
    port: int = 8000
    
    # API Base URLs
    ebi_search_url: str = "https://www.ebi.ac.uk/ebisearch/ws/rest"
    uniprot_url: str = "https://rest.uniprot.org"
    europe_pmc_url: str = "https://www.ebi.ac.uk/europepmc/webservices/rest"
    ensembl_url: str = "https://rest.ensembl.org"
    blast_url: str = "https://www.ebi.ac.uk/jdispatcher/rest"

    class Config:
        env_file = ".env"

settings = Settings()
