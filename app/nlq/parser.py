from app.nlq.intent import IntentClassifier
from app.nlq.entities import EntityExtractor
import logging

logger = logging.getLogger(__name__)

class NLQParser:
    def __init__(self):
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        
    def parse(self, query: str) -> dict:
        """
        Extracts the intent and core entities from a raw text query, 
        then formats them into the exact search syntax required by the target API.
        """
        intent = self.intent_classifier.classify_intent(query)
        entities = self.entity_extractor.extract_entities(query)
        
        parsed = {
            "original_query": query,
            "intent": intent,
            "entities": entities,
            "target_api": "ebi_search",
            "api_query_string": ""
        }
        
        # Build API specific query strings
        if intent == "protein_search":
            parsed["target_api"] = "uniprot"
            q_parts = []
            if entities["proteins"]:
                q_parts.append(f"protein_name:{entities['proteins'][0]}")
            if entities["taxonomy_id"]:
                q_parts.append(f"organism_id:{entities['taxonomy_id']}")
            if entities["diseases"]:
                q_parts.append(f"keyword:{entities['diseases'][0]}")
            if not q_parts:
                # Fallback to general keyword search
                parsed["api_query_string"] = query
            else:
                parsed["api_query_string"] = " AND ".join(q_parts)
                
        elif intent == "publication_search":
            parsed["target_api"] = "europe_pmc"
            # Strip conversational filler words before sending to Europe PMC
            q_parts = [word for word in query.split() if word.lower() not in ["show", "me", "recent", "papers", "on", "by", "publication", "publications", "find", "search"]]
            parsed["api_query_string"] = " ".join(q_parts)
            
        elif intent == "sequence_search":
            parsed["target_api"] = "blast"
            parsed["api_query_string"] = query.strip()
            
        elif intent == "gene_search":
            parsed["target_api"] = "ensembl_gene"
            if entities.get("genes"):
                parsed["api_query_string"] = entities["genes"][0]
            else:
                q_parts = [word for word in query.split() if word.lower() not in ["show", "me", "find", "search", "for", "the", "gene", "genes", "of"]]
                parsed["api_query_string"] = " ".join(q_parts)
            
        else:
            # general_search, structure_search
            parsed["target_api"] = "ebi_search"
            parsed["api_query_string"] = query
            
        return parsed
