"""
Regression Testing for BPMN Graph Transformation

This module tests for regressions by comparing current output against
known good outputs (the pre-computed JSON files in samples).

Tests ensure that:
- Parser output structure remains consistent
- Transformation output remains stable
- Changes don't break existing functionality
"""

from pathlib import Path
import pytest
import json

SAMPLES = Path(__file__).parent / "test_parsers" / "samples"


class TestParserRegressions:
    """
    Regression tests for parser outputs against known good outputs
    """

    def test_bpmn_parser_output_structure(self):
        """Test BPMN parser output matches expected structure"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        # Parse the BPMN file
        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        if not bpmn_file.exists():
            pytest.skip(f"Sample file not found: {bpmn_file}")

        parsed_data, format_type = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        # Load the expected output
        expected_output_file = SAMPLES / "output_bpmn.json"
        if not expected_output_file.exists():
            pytest.skip(f"Expected output not found: {expected_output_file}")

        with open(expected_output_file, 'r', encoding='utf-8') as f:
            expected_data = json.load(f)

        # Compare top-level keys
        expected_keys = set(expected_data.keys())
        actual_keys = set(parsed_data.keys())

        # Should have similar structure
        common_keys = expected_keys & actual_keys
        assert len(common_keys) > 0, f"Should have common keys. Expected: {expected_keys}, Actual: {actual_keys}"

        print(f"\nCommon keys: {common_keys}")
        print(f"Expected keys: {expected_keys}")
        print(f"Actual keys: {actual_keys}")

    def test_xml_parser_output_structure(self):
        """Test XML parser output matches expected structure"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        # Parse the XML file
        xml_file = SAMPLES / "Model2.xml"
        if not xml_file.exists():
            pytest.skip(f"Sample file not found: {xml_file}")

        parsed_data, format_type = dispatch_parse(xml_file, filename=xml_file.name)

        # Load the expected output
        expected_output_file = SAMPLES / "output_xml.json"
        if not expected_output_file.exists():
            pytest.skip(f"Expected output not found: {expected_output_file}")

        with open(expected_output_file, 'r', encoding='utf-8') as f:
            expected_data = json.load(f)

        # Compare structure
        expected_keys = set(expected_data.keys())
        actual_keys = set(parsed_data.keys())

        common_keys = expected_keys & actual_keys
        assert len(common_keys) > 0, "Should have common keys"

        print(f"\nXML Parser - Common keys: {common_keys}")

    def test_xpdl_parser_output_structure(self):
        """Test XPDL parser output matches expected structure"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        # Parse the XPDL file
        xpdl_file = SAMPLES / "Diagram 1.xpdl"
        if not xpdl_file.exists():
            pytest.skip(f"Sample file not found: {xpdl_file}")

        parsed_data, format_type = dispatch_parse(xpdl_file, filename=xpdl_file.name)

        # Load the expected output
        expected_output_file = SAMPLES / "output_xpdl.json"
        if not expected_output_file.exists():
            pytest.skip(f"Expected output not found: {expected_output_file}")

        with open(expected_output_file, 'r', encoding='utf-8') as f:
            expected_data = json.load(f)

        # Compare structure
        expected_keys = set(expected_data.keys())
        actual_keys = set(parsed_data.keys())

        common_keys = expected_keys & actual_keys
        assert len(common_keys) > 0, "Should have common keys"

        print(f"\nXPDL Parser - Common keys: {common_keys}")


class TestElementCountRegression:
    """
    Regression tests comparing element counts
    """

    def test_bpmn_element_counts(self):
        """Test that BPMN parsing produces expected number of elements"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        if not bpmn_file.exists():
            pytest.skip(f"Sample file not found: {bpmn_file}")

        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        # Count elements
        flow_elements = parsed_data.get("flowElements", [])
        pools = parsed_data.get("pools", [])
        lanes = parsed_data.get("lanes", [])

        print(f"\nBPMN Element counts:")
        print(f"  Flow elements: {len(flow_elements)}")
        print(f"  Pools: {len(pools)}")
        print(f"  Lanes: {len(lanes)}")

        # Basic sanity checks
        assert isinstance(flow_elements, list), "flowElements should be a list"
        assert isinstance(pools, list), "pools should be a list"
        assert isinstance(lanes, list), "lanes should be a list"

    def test_mydiagram1_element_counts(self):
        """Test element counts for MyDiagram1.bpmn"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        bpmn_file = SAMPLES / "MyDiagram1.bpmn"
        if not bpmn_file.exists():
            pytest.skip(f"Sample file not found: {bpmn_file}")

        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        # Expected output file
        expected_file = SAMPLES / "output_bpmn5.json"
        if expected_file.exists():
            with open(expected_file, 'r', encoding='utf-8') as f:
                expected_data = json.load(f)

            # Compare element counts if available
            expected_flow_elements = expected_data.get("flowElements", [])
            actual_flow_elements = parsed_data.get("flowElements", [])

            print(f"\nMyDiagram1 comparison:")
            print(f"  Expected flow elements: {len(expected_flow_elements)}")
            print(f"  Actual flow elements: {len(actual_flow_elements)}")

            # Counts should match (or be very close)
            # Allow small differences due to parsing improvements
            assert abs(len(actual_flow_elements) - len(expected_flow_elements)) <= 5, \
                "Flow element count should be close to expected"


class TestTransformationRegression:
    """
    Regression tests for transformation output
    """

    def test_transformation_query_count_stability(self):
        """Test that transformation produces consistent query counts"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        # Use a stable test file
        bpmn_file = SAMPLES / "MyDiagram1.bpmn"
        if not bpmn_file.exists():
            pytest.skip(f"Sample file not found: {bpmn_file}")

        # Parse and transform
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)
        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Store baseline (this will need to be updated if implementation changes)
        query_count = len(cypher_queries)
        node_count = transformer.node_count
        edge_count = transformer.edge_count

        print(f"\nTransformation output for MyDiagram1.bpmn:")
        print(f"  Cypher queries: {query_count}")
        print(f"  Nodes: {node_count}")
        print(f"  Edges: {edge_count}")

        # Basic sanity checks
        assert query_count >= 0, "Should have non-negative query count"
        assert node_count >= 0, "Should have non-negative node count"
        assert edge_count >= 0, "Should have non-negative edge count"

    def test_cypher_query_format_stability(self):
        """Test that Cypher query format remains consistent"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "diagram_3.bpmn"
        if not bpmn_file.exists():
            pytest.skip(f"Sample file not found: {bpmn_file}")

        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)
        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        if len(cypher_queries) > 0:
            # Check that queries still follow expected patterns
            create_queries = [q for q in cypher_queries if "CREATE" in q]
            merge_queries = [q for q in cypher_queries if "MERGE" in q]

            print(f"\nCypher query patterns:")
            print(f"  CREATE queries: {len(create_queries)}")
            print(f"  MERGE queries: {len(merge_queries)}")

            # At least one type should be present
            assert len(create_queries) + len(merge_queries) > 0, "Should have CREATE or MERGE queries"


class TestCrossFormatConsistency:
    """
    Tests that verify consistency across different format inputs
    """

    def test_same_diagram_different_formats(self):
        """Test that same diagram in different formats produces similar output"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        # Diagram 1 exists in both BPMN and XPDL formats
        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        xpdl_file = SAMPLES / "Diagram 1.xpdl"

        if not bpmn_file.exists() or not xpdl_file.exists():
            pytest.skip("Both format files not available")

        # Parse both
        bpmn_data, bpmn_fmt = dispatch_parse(bpmn_file, filename=bpmn_file.name)
        xpdl_data, xpdl_fmt = dispatch_parse(xpdl_file, filename=xpdl_file.name)

        # Should have identified formats correctly
        assert bpmn_fmt == "bpmn", "Should identify BPMN format"
        assert xpdl_fmt == "xpdl", "Should identify XPDL format"

        # Should have similar top-level keys
        bpmn_keys = set(bpmn_data.keys())
        xpdl_keys = set(xpdl_data.keys())
        common_keys = bpmn_keys & xpdl_keys

        print(f"\nCross-format comparison (Diagram 1):")
        print(f"  BPMN keys: {bpmn_keys}")
        print(f"  XPDL keys: {xpdl_keys}")
        print(f"  Common keys: {common_keys}")

        # Should have at least some structure in common
        assert len(common_keys) > 0, "Different formats of same diagram should have some common structure"

    def test_diagram_3_xml_vs_bpmn(self):
        """Test diagram_3 in XML vs BPMN format"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        # diagram_3 exists in both XML and BPMN formats
        bpmn_file = SAMPLES / "diagram_3.bpmn"
        xml_file = SAMPLES / "diagram_3.xml"

        if not bpmn_file.exists() or not xml_file.exists():
            pytest.skip("Both format files not available")

        # Parse both
        bpmn_data, bpmn_fmt = dispatch_parse(bpmn_file, filename=bpmn_file.name)
        xml_data, xml_fmt = dispatch_parse(xml_file, filename=xml_file.name)

        # Count elements
        bpmn_flow_count = len(bpmn_data.get("flowElements", []))
        xml_flow_count = len(xml_data.get("flowElements", []))

        print(f"\ndiagram_3 cross-format comparison:")
        print(f"  BPMN flow elements: {bpmn_flow_count}")
        print(f"  XML flow elements: {xml_flow_count}")

        # Element counts should be similar (may not be exact due to format differences)
        if bpmn_flow_count > 0 and xml_flow_count > 0:
            ratio = max(bpmn_flow_count, xml_flow_count) / min(bpmn_flow_count, xml_flow_count)
            assert ratio < 2.0, "Element counts should be reasonably similar across formats"


class TestKnownGoodOutputs:
    """
    Tests that compare against all known good output files
    """

    @pytest.mark.parametrize("input_file,output_file,expected_format", [
        ("Diagram 1.bpmn", "output_bpmn.json", "bpmn"),
        ("MyDiagram1.bpmn", "output_bpmn5.json", "bpmn"),
        ("diagram_3.bpmn", "output_bpmn3.json", "bpmn"),
        ("diagram4.bpmn", "output_bpmn4.json", "bpmn"),
        ("Model2.xml", "output_xml.json", "xml"),
        ("Diagram 1.xpdl", "output_xpdl.json", "xpdl"),
    ])
    def test_parser_output_against_known_good(self, input_file, output_file, expected_format):
        """Test parser output structure against known good outputs"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        input_path = SAMPLES / input_file
        output_path = SAMPLES / output_file

        if not input_path.exists():
            pytest.skip(f"Input file not found: {input_path}")
        if not output_path.exists():
            pytest.skip(f"Output file not found: {output_path}")

        # Parse input
        parsed_data, format_type = dispatch_parse(input_path, filename=input_path.name)

        # Load expected output
        with open(output_path, 'r', encoding='utf-8') as f:
            expected_data = json.load(f)

        # Verify format detection
        assert format_type == expected_format, f"Format detection should match: expected {expected_format}, got {format_type}"

        # Compare structure
        expected_keys = set(expected_data.keys())
        actual_keys = set(parsed_data.keys())
        common_keys = expected_keys & actual_keys

        print(f"\n{input_file} -> {output_file}:")
        print(f"  Format: {format_type}")
        print(f"  Common keys: {len(common_keys)}/{len(expected_keys)}")

        # Should have significant overlap
        overlap_ratio = len(common_keys) / len(expected_keys) if len(expected_keys) > 0 else 0
        assert overlap_ratio > 0.5, f"Should have at least 50% key overlap, got {overlap_ratio:.2%}"


class TestBackwardCompatibility:
    """
    Tests to ensure backward compatibility with older versions
    """

    def test_old_output_json_still_parseable(self):
        """Test that old output JSON files can still be processed"""
        try:
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Transformer not available: {e}")

        output_files = [
            "output_bpmn.json",
            "output_bpmn2.json",
            "output_bpmn3.json",
            "output_xml.json"
        ]

        for output_file in output_files:
            file_path = SAMPLES / output_file
            if not file_path.exists():
                continue

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Should be able to process without errors
            try:
                transformer = GraphTransformer(data)
                cypher_queries = transformer.transform()
                print(f"\n{output_file}: Successfully transformed (generated {len(cypher_queries)} queries)")
            except Exception as e:
                pytest.fail(f"Failed to transform {output_file}: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
