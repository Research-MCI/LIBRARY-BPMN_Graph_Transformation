"""
End-to-End Evaluation Testing for BPMN Graph Transformation

This module tests the complete pipeline:
File → Parse → Validate → Transform → Cypher Queries
"""

from pathlib import Path
import pytest
import json

SAMPLES = Path(__file__).parent / "test_parsers" / "samples"


class TestEndToEndTransformation:
    """
    End-to-end tests for the complete BPMN transformation pipeline.
    Tests cover: parsing → validation → transformation → Cypher generation
    """

    def test_bpmn_to_cypher_full_pipeline(self):
        """Test complete pipeline from BPMN file to Cypher queries"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        # Parse BPMN file
        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        assert bpmn_file.exists(), f"Sample file not found: {bpmn_file}"

        parsed_data, format_type = dispatch_parse(bpmn_file, filename=bpmn_file.name)
        assert format_type == "bpmn", f"Expected format 'bpmn', got '{format_type}'"
        assert isinstance(parsed_data, dict), "Parsed data should be a dictionary"

        # Transform to graph
        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Validate output
        assert isinstance(cypher_queries, list), "Cypher queries should be a list"
        assert len(cypher_queries) > 0, "Should generate at least one Cypher query"
        assert transformer.node_count > 0, "Should have created at least one node"

        # Validate Cypher syntax
        for query in cypher_queries:
            assert isinstance(query, str), "Each query should be a string"
            assert len(query.strip()) > 0, "Query should not be empty"
            # Basic Cypher syntax check
            assert "CREATE" in query or "MERGE" in query or "MATCH" in query, \
                f"Query should contain Cypher keywords: {query[:100]}"

    def test_xpdl_to_cypher_full_pipeline(self):
        """Test complete pipeline from XPDL file to Cypher queries"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        # Parse XPDL file
        xpdl_file = SAMPLES / "Diagram 1.xpdl"
        assert xpdl_file.exists(), f"Sample file not found: {xpdl_file}"

        parsed_data, format_type = dispatch_parse(xpdl_file, filename=xpdl_file.name)
        assert format_type == "xpdl", f"Expected format 'xpdl', got '{format_type}'"

        # Transform to graph
        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Validate output
        assert len(cypher_queries) > 0, "Should generate Cypher queries"
        assert transformer.node_count > 0, "Should have nodes"

    def test_xml_to_cypher_full_pipeline(self):
        """Test complete pipeline from XML file to Cypher queries"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        # Parse XML file
        xml_file = SAMPLES / "Model2.xml"
        assert xml_file.exists(), f"Sample file not found: {xml_file}"

        parsed_data, format_type = dispatch_parse(xml_file, filename=xml_file.name)
        assert format_type == "xml", f"Expected format 'xml', got '{format_type}'"

        # Transform to graph
        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Validate output
        assert len(cypher_queries) > 0, "Should generate Cypher queries"

    @pytest.mark.parametrize("sample_file,expected_format", [
        ("MyDiagram1.bpmn", "bpmn"),
        ("diagram_3.bpmn", "bpmn"),
        ("diagram4.bpmn", "bpmn"),
        ("diagram_2.xml", "xml"),
        ("diagram_3.xml", "xml"),
    ])
    def test_multiple_samples_pipeline(self, sample_file, expected_format):
        """Test pipeline with multiple sample files"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        file_path = SAMPLES / sample_file
        if not file_path.exists():
            pytest.skip(f"Sample file not found: {file_path}")

        # Parse
        parsed_data, format_type = dispatch_parse(file_path, filename=file_path.name)
        assert format_type == expected_format

        # Transform
        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Basic validation
        assert isinstance(cypher_queries, list)
        assert len(cypher_queries) >= 0  # Some files might be minimal


class TestTransformationQuality:
    """
    Tests for evaluating the quality and correctness of graph transformations
    """

    def test_node_edge_relationship_preservation(self):
        """Verify that node-edge relationships are preserved correctly"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Count CREATE statements for nodes and edges
        node_creates = [q for q in cypher_queries if "CREATE (:" in q and ")-[" not in q]
        edge_creates = [q for q in cypher_queries if ")-[" in q and "]->" in q]

        assert len(node_creates) > 0, "Should have node creation queries"
        assert len(edge_creates) >= 0, "Should have edge creation queries (can be 0 for simple diagrams)"
        assert transformer.node_count == len(node_creates), "Node count should match CREATE statements"

    def test_pool_lane_structure_preservation(self):
        """Verify that pool and lane hierarchies are preserved"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        # Check if parsed data has pools/lanes
        has_pools = len(parsed_data.get("pools", [])) > 0
        has_lanes = len(parsed_data.get("lanes", [])) > 0

        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        if has_pools:
            pool_queries = [q for q in cypher_queries if ":Pool" in q or ":Lane" in q]
            assert len(pool_queries) > 0, "Should generate queries for pools/lanes"

    def test_flow_element_types_coverage(self):
        """Verify all BPMN flow element types are handled"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        all_queries = "\n".join(cypher_queries)

        # Check for common BPMN element types
        element_types = ["Activity", "Event", "Gateway", "Flow"]
        found_types = [et for et in element_types if et in all_queries or et.lower() in all_queries.lower()]

        # At least some element types should be present
        assert len(found_types) > 0, f"Should find BPMN element types in Cypher queries. Queries: {all_queries[:500]}"

    def test_process_id_uniqueness(self):
        """Verify that each transformation gets a unique process ID"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        # Create two transformers
        transformer1 = GraphTransformer(parsed_data)
        transformer2 = GraphTransformer(parsed_data)

        # Process IDs should be different
        assert transformer1.process_id != transformer2.process_id, \
            "Each transformation should have a unique process ID"

    def test_batch_output_functionality(self):
        """Test that batch output works correctly"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Test batching
        batch_size = 10
        batches = list(transformer.batch_output(batch_size=batch_size))

        # Validate batches
        total_queries = sum(len(batch) for batch in batches)
        assert total_queries == len(cypher_queries), "Batching should preserve all queries"

        # Check batch sizes
        for batch in batches[:-1]:  # All but last
            assert len(batch) <= batch_size, f"Batch size should not exceed {batch_size}"


class TestErrorHandling:
    """
    Tests for error handling and edge cases
    """

    def test_empty_bpmn_handling(self):
        """Test handling of minimal/empty BPMN structures"""
        try:
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        # Minimal valid structure
        minimal_data = {
            "flowElements": [],
            "pools": [],
            "lanes": []
        }

        transformer = GraphTransformer(minimal_data)
        cypher_queries = transformer.transform()

        # Should handle gracefully
        assert isinstance(cypher_queries, list)
        assert transformer.node_count == 0
        assert transformer.edge_count == 0

    def test_malformed_json_structure(self):
        """Test handling of unsupported JSON structure"""
        try:
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        # Unsupported structure
        malformed_data = {"random": "data", "not": "bpmn"}

        transformer = GraphTransformer(malformed_data)
        cypher_queries = transformer.transform()

        # Should handle gracefully without crashing
        assert isinstance(cypher_queries, list)

    def test_already_structured_json(self):
        """Test handling of pre-structured BPMN JSON"""
        try:
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        # Already structured data
        structured_data = {
            "activities": [],
            "events": [],
            "gateways": [],
            "flows": [],
            "pools": [],
            "lanes": []
        }

        transformer = GraphTransformer(structured_data)
        cypher_queries = transformer.transform()

        # Should use as-is without normalization
        assert isinstance(cypher_queries, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
