from contextlib import contextmanager

from neo4j import GraphDatabase

from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

_driver = None


def get_driver():
    global _driver
    if _driver is None:
        _driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD),
        )
    return _driver


def init_neo4j() -> None:
    driver = get_driver()
    driver.verify_connectivity()
    with driver.session() as session:
        session.run("CREATE CONSTRAINT entity_name_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.name IS UNIQUE")
        session.run("CREATE INDEX entity_type IF NOT EXISTS FOR (e:Entity) ON (e.type)")
    logger.info("Neo4j connected, indexes ready")


@contextmanager
def get_neo4j_session():
    with get_driver().session() as session:
        yield session
