import pytest
from unittest.mock import patch, MagicMock
from graph.entity_extractor import EntityExtractor
import json

class TestEntityExtractor:

    @patch('graph.entity_extractor.OpenAI')
    def test_successful_extraction(self, mock_openai):
        """Test valid extraction result"""
        mock_response = {
            "entities": [
                {"name": "BERT", "type": "Technology"},
                {"name": "Google", "type": "Organization"}
            ],
            "relationships": [
                {"source": "BERT", "target": "Google", "type": "CREATED_BY"}
            ]
        }

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value.choices[0].message.content = \
            json.dumps(mock_response)
        mock_openai.return_value = mock_client

        # IMPORTANT: instantiate AFTER the patch is active — see explanation below
        extractor = EntityExtractor()
        result = extractor.extract("BERT was created by Google.", "chunk-1")

        assert len(result.entities) == 2
        assert result.entities[0].name == "BERT"
        assert len(result.relationships) == 1

    @patch('graph.entity_extractor.OpenAI')
    def test_invalid_entity_type_filtered(self, mock_openai):
        """Invalid entity types should be rejected — tests _validate_and_clean directly"""
        extractor = EntityExtractor()
        raw = {
            "entities": [
                {"name": "BERT", "type": "InvalidType"},
                {"name": "Google", "type": "Organization"}
            ],
            "relationships": []
        }
        result = extractor._validate_and_clean(raw, "chunk-1")
        assert len(result.entities) == 1   # Only Organization kept
        assert result.entities[0].name == "Google"

    @patch('graph.entity_extractor.OpenAI')
    def test_self_loop_relationship_rejected(self, mock_openai):
        """Entity cannot have a relationship with itself"""
        extractor = EntityExtractor()
        raw = {
            "entities": [{"name": "BERT", "type": "Technology"}],
            "relationships": [
                {"source": "BERT", "target": "BERT", "type": "RELATED_TO"}
            ]
        }
        result = extractor._validate_and_clean(raw, "chunk-1")
        assert len(result.relationships) == 0

        