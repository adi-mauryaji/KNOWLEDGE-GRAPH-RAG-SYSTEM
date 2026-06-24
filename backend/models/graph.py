from pydantic import BaseModel,field_validator
from typing import Optional

VALID_ENTITY_TYPES=frozenset({"Person","Organization","Technology","Concept","Location","ResearchPaper"})
VALID_RELATIONSHIP_TYPES=frozenset({"USES","CREATED_BY","DEPENDS_ON","RELATED_TO","PARTS_OF","AUTHORED_BY","AFFILIATED_BY","INTRODUCED","MENTIONS","BASED_ON"})

class Entity(BaseModel):
    name:str
    type:str
    confidence:float=1.0

    @field_validator("type")
    @classmethod
    def validate_type(cls,v):
        if v not in VALID_ENTITY_TYPES:
            raise ValueError(f"Invalid entity type '{v} .Must be one of {VALID_ENTITY_TYPES} ")
        return v
    
    @field_validator("name")
    @classmethod
    def validate_name(cls,v):
        v=v.strip()
        if len(v)<2:
            raise ValueError(f"Entity name is too short.Must be more than 2")
        if len(v)>150:
            raise ValueError(f"Entity name mush be less than 150")
        return v
    
class Relationship(BaseModel):
        source: str
        target: str
        type: str
        weight: float=1.0

        @field_validator("type")
        @classmethod
        def validate_type(cls,v):
            if v not in VALID_RELATIONSHIP_TYPES:
                raise ValueError(f"Invalid relationship type '{v}.Must be one of {VALID_RELATIONSHIP_TYPES}")
            return v
        
class ExtractionResult(BaseModel):
    chunk_id:str
    entities: list[Entity]=[]
    relationships: list[Relationship]=[]
    extraction_model: str ="Unknown"
    processing_time_ms: Optional[int]=None

class GraphNode(BaseModel):
    id: int
    name: str
    type: str
    doc_ids: list[str]=[]

class GraphEdge(BaseModel)
    source: str
    target: str
    type: str
    doc_id: Optional[str]=None

class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    source: list[GraphEdge]
    total_nodes: int
    total_edges: int
    
        
    
