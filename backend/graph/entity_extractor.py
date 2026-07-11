import json
from openai import OpenAI
from models.graph import Entity, Relationship, ExtractionResult
from utils.config import get_settings
from utils.logger import get_logger

logger = get_logger(__name__)
settings = get_settings()

EXTRACTION_SYSTEM_PROMPT = """You are an expert knowledge graph extractor for technical and research documents.

Your task is to extract named entities and their relationships from the provided text.

ENTITY TYPES (use exactly these):
- Person: Individual people (researchers, authors, scientists)
- Organization: Companies, universities, research labs, institutes
- Technology: Software, algorithms, frameworks, models, tools
- Concept: Abstract ideas, techniques, theories, methods
- Location: Places, countries, cities

RELATIONSHIP TYPES (use exactly these):
- USES: Entity uses/employs another entity
- CREATED_BY: Entity was created by another entity
- DEPENDS_ON: Entity depends on another entity technically
- RELATED_TO: General semantic relationship
- PART_OF: Entity is a component of another
- AUTHORED_BY: Document authored by person
- AFFILIATED_WITH: Person/tech affiliated with organization
- INTRODUCED: Entity introduced a concept/technology

RULES:
1. Only extract entities clearly mentioned in the text
2. Relationships must be explicitly or strongly implied in the text
3. Entity names should be in their canonical form (e.g., "BERT" not "bert")
4. Minimum 2 entities needed to create a relationship
5. Return ONLY valid JSON — no preamble, no markdown
"""

EXTRACTION_USER_TEMPLATE = """Extract entities and relationships from this text:

{text}

Return ONLY this JSON structure:
{{
  "entities": [
    {{"name": "EntityName", "type": "Person|Organization|Technology|Concept|Location"}}
  ],
  "relationships": [
    {{"source": "Entity1", "target": "Entity2", "type": "RELATIONSHIP_TYPE"}}
  ]
}}"""

VALID_ENTITY_TYPES = {"Person", "Organization", "Technology", "Concept", "Location"}
VALID_REL_TYPES = {
    "USES", "CREATED_BY", "DEPENDS_ON", "RELATED_TO",
    "PART_OF", "AUTHORED_BY", "AFFILIATED_WITH", "INTRODUCED"
}

class EntityExtractor:

    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.EXTRACTION_MODEL

    def extract(self, text: str, chunk_id: str) -> ExtractionResult:
        text = text[:3000]   # Save tokens, focus extraction

        try:
            raw_result = self._call_llm(text)
            return self._validate_and_clean(raw_result, chunk_id)
        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse failed for chunk {chunk_id}: {e}")
            return ExtractionResult(entities=[], relationships=[], chunk_id=chunk_id)
        except Exception as e:
            logger.error(f"Extraction failed for chunk {chunk_id}: {e}")
            return ExtractionResult(entities=[], relationships=[], chunk_id=chunk_id)

    def _call_llm(self, text: str) -> dict:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": EXTRACTION_SYSTEM_PROMPT},
                {"role": "user", "content": EXTRACTION_USER_TEMPLATE.format(text=text)}
            ],
            response_format={"type": "json_object"},
            temperature=0.0,
            max_tokens=1000
        )
        return json.loads(response.choices[0].message.content)

    def _validate_and_clean(self, raw: dict, chunk_id: str) -> ExtractionResult:
        """Validate LLM output — never trust it blindly"""
        entities = []
        for e in raw.get("entities", []):
            if not isinstance(e, dict):
                continue
            if "name" not in e or "type" not in e:
                continue
            if e["type"] not in VALID_ENTITY_TYPES:
                logger.debug(f"Invalid entity type: {e['type']}, skipping")
                continue
            if len(e["name"]) < 2 or len(e["name"]) > 100:
                continue
            entities.append(Entity(name=e["name"].strip(), type=e["type"]))

        entity_names = {e.name for e in entities}

        relationships = []
        for r in raw.get("relationships", []):
            if not isinstance(r, dict):
                continue
            if not all(k in r for k in ["source", "target", "type"]):
                continue
            if r["type"] not in VALID_REL_TYPES:
                logger.debug(f"Invalid rel type: {r['type']}, skipping")
                continue
            if r["source"] not in entity_names or r["target"] not in entity_names:
                continue
            if r["source"] == r["target"]:
                continue
            relationships.append(Relationship(source=r["source"], target=r["target"], type=r["type"]))

        return ExtractionResult(entities=entities, relationships=relationships, chunk_id=chunk_id)