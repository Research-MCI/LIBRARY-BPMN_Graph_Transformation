"""
Validation Evaluation Testing for BPMN Graph Transformation

This module tests the validation components:
- Schema validation
- Semantic validation
- Auto-fix functionality
- Edge case handling
"""

from pathlib import Path
import pytest
import json
import copy

SAMPLES = Path(__file__).parent / "test_parsers" / "samples"


class TestSchemaValidation:
    """
    Tests for JSON schema validation functionality
    """

    def test_valid_structured_json(self):
        """Test schema validation with valid structured JSON"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        valid_data = {
            "elements": {
                "activities": [],
                "events": [],
                "flows": [],
                "gateways": [],
                "pools": [],
                "lanes": []
            }
        }

        # Should validate successfully
        result = validate_schema(copy.deepcopy(valid_data), auto_fix=False)
        assert result is not None

    def test_missing_elements_key(self):
        """Test validation when 'elements' key is missing"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        invalid_data = {
            "activities": [],
            "events": []
        }

        # Should add 'elements' key
        result = validate_schema(copy.deepcopy(invalid_data), auto_fix=False)
        assert "elements" in result

    def test_missing_required_arrays(self):
        """Test validation when required arrays are missing"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        incomplete_data = {
            "elements": {
                "activities": []
                # Missing events, flows
            }
        }

        # Should add missing arrays
        result = validate_schema(copy.deepcopy(incomplete_data), auto_fix=False)
        assert "events" in result["elements"]
        assert "flows" in result["elements"]

    def test_auto_fix_missing_ids(self):
        """Test auto-fix functionality for missing IDs"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        data_with_missing_ids = {
            "elements": {
                "activities": [
                    {"name": "Task 1"},  # Missing ID
                    {"id": "act_2", "name": "Task 2"}
                ],
                "events": [
                    {"type": "start"}  # Missing ID
                ],
                "flows": []
            }
        }

        # Auto-fix should add IDs
        result = validate_schema(copy.deepcopy(data_with_missing_ids), auto_fix=True)

        # Check that IDs were added
        assert all("id" in act for act in result["elements"]["activities"])
        assert all("id" in evt for evt in result["elements"]["events"])

    def test_auto_fix_duplicate_ids(self):
        """Test auto-fix functionality for duplicate IDs"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        data_with_duplicates = {
            "elements": {
                "activities": [
                    {"id": "task_1", "name": "Task 1"},
                    {"id": "task_1", "name": "Task 2"}  # Duplicate ID
                ],
                "events": [
                    {"id": "event_1", "type": "start"},
                    {"id": "event_1", "type": "end"}  # Duplicate ID
                ],
                "flows": []
            }
        }

        # Auto-fix should resolve duplicates
        result = validate_schema(copy.deepcopy(data_with_duplicates), auto_fix=True)

        # Collect all IDs
        all_ids = [act["id"] for act in result["elements"]["activities"]]
        all_ids += [evt["id"] for evt in result["elements"]["events"]]

        # All IDs should be unique
        assert len(all_ids) == len(set(all_ids)), "All IDs should be unique after auto-fix"

    def test_cycle_detection_in_flows(self):
        """Test cycle detection in sequence flows"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema, detect_cycle
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        # Create a cyclic flow
        cyclic_flows = [
            {"id": "flow1", "sourceRef": "A", "targetRef": "B"},
            {"id": "flow2", "sourceRef": "B", "targetRef": "C"},
            {"id": "flow3", "sourceRef": "C", "targetRef": "A"}  # Creates cycle
        ]

        # Should detect cycle
        has_cycle = detect_cycle(cyclic_flows)
        assert has_cycle, "Should detect cycle in flows"

    def test_no_cycle_in_flows(self):
        """Test that acyclic flows pass validation"""
        try:
            from bpmn_neo4j.validators.schema_validator import detect_cycle
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        # Create an acyclic flow
        acyclic_flows = [
            {"id": "flow1", "sourceRef": "A", "targetRef": "B"},
            {"id": "flow2", "sourceRef": "B", "targetRef": "C"},
            {"id": "flow3", "sourceRef": "C", "targetRef": "D"}
        ]

        # Should not detect cycle
        has_cycle = detect_cycle(acyclic_flows)
        assert not has_cycle, "Should not detect cycle in acyclic flows"


class TestSemanticValidation:
    """
    Tests for BPMN semantic validation
    """

    def test_semantic_validator_import(self):
        """Test that semantic validator can be imported"""
        try:
            from bpmn_neo4j.validators.bpmn_semantic_validator import validate_bpmn_semantics
            assert validate_bpmn_semantics is not None
        except Exception as e:
            pytest.skip(f"Semantic validator not available: {e}")

    def test_validate_events_semantics(self):
        """Test semantic validation for BPMN events"""
        try:
            from bpmn_neo4j.validators.bpmn_semantic_validator import validate_events
        except Exception as e:
            pytest.skip(f"Semantic validator not available: {e}")

        # Valid event structure
        valid_events = [
            {"id": "start_1", "type": "start"},
            {"id": "end_1", "type": "end"}
        ]

        # Should validate without errors
        validate_events(valid_events)

    def test_validate_gateways_semantics(self):
        """Test semantic validation for BPMN gateways"""
        try:
            from bpmn_neo4j.validators.bpmn_semantic_validator import validate_gateways
        except Exception as e:
            pytest.skip(f"Semantic validator not available: {e}")

        # Valid gateway structure
        valid_gateways = [
            {"id": "gateway_1", "type": "exclusive", "gatewayDirection": "diverging"}
        ]

        # Should validate without errors
        validate_gateways(valid_gateways)

    def test_validate_flows_semantics(self):
        """Test semantic validation for sequence flows"""
        try:
            from bpmn_neo4j.validators.bpmn_semantic_validator import validate_flows
        except Exception as e:
            pytest.skip(f"Semantic validator not available: {e}")

        # Valid flow structure
        valid_flows = [
            {"id": "flow_1", "sourceRef": "task_1", "targetRef": "task_2"}
        ]

        # Should validate without errors
        validate_flows(valid_flows)

    def test_validate_pools_semantics(self):
        """Test semantic validation for pools and lanes"""
        try:
            from bpmn_neo4j.validators.bpmn_semantic_validator import validate_pools
        except Exception as e:
            pytest.skip(f"Semantic validator not available: {e}")

        # Valid pool structure
        valid_pools = [
            {"id": "pool_1", "name": "Pool 1"}
        ]

        # Should validate without errors
        validate_pools(valid_pools)


class TestValidationWithRealData:
    """
    Tests validation using real sample files
    """

    def test_validate_parsed_bpmn_output(self):
        """Test validation on actual parsed BPMN output"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        # Load and parse real BPMN
        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        if not bpmn_file.exists():
            pytest.skip(f"Sample file not found: {bpmn_file}")

        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        # Wrap in elements structure if needed
        test_data = {
            "elements": {
                "activities": parsed_data.get("flowElements", []),
                "events": [],
                "flows": [],
                "gateways": [],
                "pools": parsed_data.get("pools", []),
                "lanes": parsed_data.get("lanes", [])
            }
        }

        # Should validate
        result = validate_schema(copy.deepcopy(test_data), auto_fix=True)
        assert result is not None

    def test_validate_output_json_files(self):
        """Test validation on pre-generated output JSON files"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        output_files = [
            "output_bpmn.json",
            "output_bpmn2.json",
            "output_xml.json",
            "output_xpdl.json"
        ]

        for output_file in output_files:
            file_path = SAMPLES / output_file
            if not file_path.exists():
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Wrap in elements if needed
            if "elements" not in data:
                test_data = {"elements": data}
            else:
                test_data = data

            # Should handle the output JSON
            result = validate_schema(copy.deepcopy(test_data), auto_fix=True)
            assert result is not None, f"Failed to validate {output_file}"


class TestEdgeCases:
    """
    Tests for edge cases and error conditions
    """

    def test_empty_data_validation(self):
        """Test validation with empty data"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        empty_data = {}

        # Should handle gracefully
        result = validate_schema(copy.deepcopy(empty_data), auto_fix=False)
        assert "elements" in result

    def test_deeply_nested_structure(self):
        """Test validation with deeply nested structures"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        nested_data = {
            "elements": {
                "activities": [
                    {
                        "id": "act_1",
                        "name": "Task",
                        "extensionElements": {
                            "properties": {
                                "nested": {
                                    "deeply": {
                                        "value": "test"
                                    }
                                }
                            }
                        }
                    }
                ],
                "events": [],
                "flows": []
            }
        }

        # Should handle nested structures
        result = validate_schema(copy.deepcopy(nested_data), auto_fix=True)
        assert result is not None

    def test_special_characters_in_ids(self):
        """Test validation with special characters in IDs"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        data_with_special_chars = {
            "elements": {
                "activities": [
                    {"id": "task-1_with.special:chars", "name": "Task 1"}
                ],
                "events": [],
                "flows": []
            }
        }

        # Should handle special characters
        result = validate_schema(copy.deepcopy(data_with_special_chars), auto_fix=False)
        assert result is not None

    def test_very_large_id_count(self):
        """Test validation with many elements"""
        try:
            from bpmn_neo4j.validators.schema_validator import validate_schema
        except Exception as e:
            pytest.skip(f"Schema validator not available: {e}")

        # Create 1000 activities
        large_data = {
            "elements": {
                "activities": [{"id": f"act_{i}", "name": f"Task {i}"} for i in range(1000)],
                "events": [],
                "flows": []
            }
        }

        # Should handle large datasets
        result = validate_schema(copy.deepcopy(large_data), auto_fix=False)
        assert result is not None
        assert len(result["elements"]["activities"]) == 1000


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
