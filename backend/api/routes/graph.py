from fastapi import APIRouter, Query
from graph.neo4j_client import get_neo4j_session

router = APIRouter()

@router.get("/graph")
async def get_graph(
    doc_id: str = Query(None, description="Filter by document"),
    entity_type: str = Query(None, description="Filter by entity type"),
    limit: int = Query(100, description="Max nodes to return")
):
    """Get graph data for visualization"""
    with get_neo4j_session() as session:
        query = """
            MATCH (n:Entity)
            WHERE ($doc_id IS NULL OR n.doc_id = $doc_id)
            AND ($entity_type IS NULL OR n.type = $entity_type)
            WITH n LIMIT $limit
            OPTIONAL MATCH (n)-[r]->(m:Entity)
            RETURN
                collect(DISTINCT {id: id(n), name: n.name, type: n.type}) as nodes,
                collect(DISTINCT {source: id(n), target: id(m), type: type(r)}) as edges
        """
        result = session.run(query, doc_id=doc_id,
                           entity_type=entity_type, limit=limit).single()

        return {
            "nodes": result["nodes"],
            "edges": [e for e in result["edges"] if e["target"] is not None]
        }