from graph.neo4j_client import get_neo4j_session
import re

class GraphRetriever:

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        1. Query se entity-like terms nikalo
        2. Unhe Neo4j mein dhoondho
        3. Neighbors traverse karo
        4. Related chunk_ids return karo (text nahi — sirf IDs)
        """
        query_entities = self._extract_query_entities(query)

        if not query_entities:
            return []

        chunk_refs = []
        with get_neo4j_session() as session:
            for entity_name in query_entities:
                results = self._traverse_from_entity(session, entity_name, top_k)
                chunk_refs.extend(results)

        return chunk_refs[:top_k]

    def _extract_query_entities(self, query: str) -> list[str]:
        """Simple heuristic: capitalized words/phrases.
        Advanced alternative: dedicated NER model, ya LLM call."""
        capitalized = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', query)
        return list(set(capitalized))[:5]

    def _traverse_from_entity(self, session, entity_name: str, limit: int) -> list[dict]:
        result = session.run("""
            MATCH (e:Entity)
            WHERE toLower(e.name) CONTAINS toLower($entity_name)
            OPTIONAL MATCH (e)-[r1]->(neighbor1:Entity)
            WITH e, collect(DISTINCT neighbor1) as neighbors1
            UNWIND e.chunk_ids as chunk_id
            RETURN DISTINCT chunk_id, e.name as source_entity
            LIMIT $limit
        """, entity_name=entity_name, limit=limit)

        return [
            {"chunk_id": record["chunk_id"], "source_entity": record["source_entity"]}
            for record in result
            if record["chunk_id"] is not None
        ]