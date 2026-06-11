import re
from app.nlq.entities import PROTEIN_FAMILIES

class IntentClassifier:
    def __init__(self):
        self.sequence_pattern = re.compile(r'^[A-Z]{10,}$', re.IGNORECASE)
        
    def classify_intent(self, query: str) -> str:
        q_lower = query.lower()
        # Route to Europe PMC if the user asks for literature
        if "paper" in q_lower or "publication" in q_lower or "author" in q_lower or "article" in q_lower:
            return "publication_search"
            
        # Route to PDBe if the user is looking for structures
        if "structure" in q_lower or "3d" in q_lower or "pdb" in q_lower:
            return "structure_search"
            
        # Route to Ensembl for genetic lookups
        if "gene" in q_lower:
            return "gene_search"
            
        # Route to UniProt if specific protein families are mentioned
        if "protein" in q_lower or any(fam in q_lower for fam in PROTEIN_FAMILIES):
            return "protein_search"
            
        # Check if the query is a raw sequence string (for BLAST alignments)
        words = query.split()
        if len(words) == 1 and self.sequence_pattern.match(words[0]):
            return "sequence_search"
            
        return "general_search"
