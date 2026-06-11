# Mappings and lookup tables for biological domains
import re

# Common organism name to NCBI Taxonomy ID map
TAXONOMY = {
    "human": "9606",
    "humans": "9606",
    "homo sapiens": "9606",
    "mouse": "10090",
    "mice": "10090",
    "mus musculus": "10090",
    "rat": "10116",
    "zebrafish": "7955"
}

# Common protein family keywords used for routing queries to UniProt
PROTEIN_FAMILIES = ["kinase", "receptor", "channel", "transporter", "enzyme", "polymerase"]

class EntityExtractor:
    def __init__(self):
        # Regex for UniProt accession IDs (e.g. P12345)
        self.accession_pattern = re.compile(r'[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9]([A-Z][A-Z0-9]{2}[0-9]){1,2}')
        
    def extract_entities(self, query: str) -> dict:
        entities = {
            "taxonomy_id": None,
            "taxonomy_name": None,
            "genes": [],
            "proteins": [],
            "diseases": [],
            "accessions": []
        }
        
        q_lower = query.lower()
        
        # Taxonomy extraction
        for org, tax_id in TAXONOMY.items():
            if org in q_lower:
                entities["taxonomy_id"] = tax_id
                entities["taxonomy_name"] = org
                break
                
        # Accession extraction (e.g. P12345)
        words = query.split()
        for w in words:
            if self.accession_pattern.match(w.upper()):
                entities["accessions"].append(w.upper())
                
        # Check for common disease markers
        if "cancer" in q_lower or "tumor" in q_lower:
            entities["diseases"].append("cancer")
        if "diabetes" in q_lower:
            entities["diseases"].append("diabetes")
            
        # Check if any known protein families are mentioned
        for family in PROTEIN_FAMILIES:
            if family in q_lower:
                entities["proteins"].append(family)
                
        return entities
