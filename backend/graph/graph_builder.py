from graph.neo4j_client import get_neo4j_session
from models.graph import Entity, Relationship

class GraphBuilder:

    def build_from_extraction(
        self,
        entities: list[Entity],
        relationships: list[Relationship],
        doc_id: str,
        chunk_id: str
    ):
        """Write entities and relationships to Neo4j"""
        with get_neo4j_session() as session:
            self._create_entities(session, entities, doc_id, chunk_id)
            self._create_relationships(session, relationships, doc_id, chunk_id)

    def _create_entities(self, session, entities, doc_id, chunk_id):
        for entity in entities:
            # MERGE = create if not exists, update if exists
            session.run("""
                MERGE (e:Entity {name: $name})
                SET e.type = $type
                SET e.doc_ids = CASE
                    WHEN $doc_id IN coalesce(e.doc_ids, [])
                    THEN e.doc_ids
                    ELSE coalesce(e.doc_ids, []) + $doc_id
                END
                SET e.chunk_ids = CASE
                    WHEN $chunk_id IN coalesce(e.chunk_ids, [])
                    THEN e.chunk_ids
                    ELSE coalesce(e.chunk_ids, []) + $chunk_id
                END
            """,
            name=entity.name, type=entity.type,
            doc_id=doc_id, chunk_id=chunk_id)

    def _create_relationships(self, session, relationships, doc_id, chunk_id):
        for rel in relationships:
            # Relationship type comes from a CLOSED, validated set
            # (models/graph.py's VALID_RELATIONSHIP_TYPES already enforced
            # this at the Pydantic layer before it ever reaches here) —
            # so f-string interpolation here is safe, not arbitrary user input.
            session.run(f"""
                MATCH (a:Entity {{name: $source}})
                MATCH (b:Entity {{name: $target}})
                MERGE (a)-[r:{rel.type}]->(b)
                SET r.doc_id = $doc_id
                SET r.chunk_id = $chunk_id
            """,
            source=rel.source, target=rel.target,
            doc_id=doc_id, chunk_id=chunk_id)

    def delete_document_graph(self, doc_id: str):
        """Remove this document's contribution; delete entities with no
        remaining document references."""
        with get_neo4j_session() as session:
            session.run("""
                MATCH (e:Entity)
                WHERE $doc_id IN e.doc_ids
                SET e.doc_ids = [x IN e.doc_ids WHERE x <> $doc_id]
            """, doc_id=doc_id)

            session.run("""
                MATCH (e:Entity)
                WHERE size(e.doc_ids) = 0
                DETACH DELETE e
            """)