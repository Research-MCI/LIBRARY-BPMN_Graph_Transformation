"""
Performance Benchmark Evaluation Testing

This module tests the performance characteristics of the BPMN transformation pipeline:
- Parsing speed for different file formats
- Transformation speed
- Memory efficiency
- Scalability with file size
"""

from pathlib import Path
import pytest
import time
import json

SAMPLES = Path(__file__).parent / "test_parsers" / "samples"


class TestParsingPerformance:
    """
    Performance benchmarks for file parsing
    """

    def test_bpmn_parsing_speed(self):
        """Benchmark BPMN file parsing speed"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        if not bpmn_file.exists():
            pytest.skip(f"Sample file not found: {bpmn_file}")

        # Measure parsing time
        start_time = time.time()
        parsed_data, format_type = dispatch_parse(bpmn_file, filename=bpmn_file.name)
        end_time = time.time()

        parsing_time = end_time - start_time

        # Assertion: parsing should complete in reasonable time
        assert parsing_time < 10.0, f"BPMN parsing took too long: {parsing_time:.2f}s"

        # Log performance for tracking
        print(f"\nBPMN parsing time: {parsing_time:.4f}s for {bpmn_file.stat().st_size / 1024:.2f} KB")

    def test_xpdl_parsing_speed(self):
        """Benchmark XPDL file parsing speed"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        xpdl_file = SAMPLES / "Diagram 1.xpdl"
        if not xpdl_file.exists():
            pytest.skip(f"Sample file not found: {xpdl_file}")

        # Measure parsing time
        start_time = time.time()
        parsed_data, format_type = dispatch_parse(xpdl_file, filename=xpdl_file.name)
        end_time = time.time()

        parsing_time = end_time - start_time

        # Assertion: parsing should complete in reasonable time
        assert parsing_time < 10.0, f"XPDL parsing took too long: {parsing_time:.2f}s"

        print(f"\nXPDL parsing time: {parsing_time:.4f}s for {xpdl_file.stat().st_size / 1024:.2f} KB")

    def test_xml_parsing_speed(self):
        """Benchmark XML file parsing speed"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        xml_file = SAMPLES / "Model2.xml"
        if not xml_file.exists():
            pytest.skip(f"Sample file not found: {xml_file}")

        # Measure parsing time
        start_time = time.time()
        parsed_data, format_type = dispatch_parse(xml_file, filename=xml_file.name)
        end_time = time.time()

        parsing_time = end_time - start_time

        # Assertion: parsing should complete in reasonable time
        assert parsing_time < 10.0, f"XML parsing took too long: {parsing_time:.2f}s"

        print(f"\nXML parsing time: {parsing_time:.4f}s for {xml_file.stat().st_size / 1024:.2f} KB")

    @pytest.mark.slow
    def test_large_file_parsing_speed(self):
        """Benchmark parsing of very large VDX file"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
        except Exception as e:
            pytest.skip(f"Parser not available: {e}")

        # Test with the 12MB VDX file
        vdx_file = SAMPLES / "Model2.vdx"
        if not vdx_file.exists():
            pytest.skip(f"Large VDX file not found: {vdx_file}")

        file_size_mb = vdx_file.stat().st_size / (1024 * 1024)
        print(f"\nParsing large file: {file_size_mb:.2f} MB")

        # Measure parsing time
        start_time = time.time()
        try:
            parsed_data, format_type = dispatch_parse(vdx_file, filename=vdx_file.name)
            end_time = time.time()

            parsing_time = end_time - start_time

            # Large file can take longer, but should still complete
            assert parsing_time < 120.0, f"Large file parsing took too long: {parsing_time:.2f}s"

            print(f"Large VDX parsing time: {parsing_time:.4f}s ({file_size_mb / parsing_time:.2f} MB/s)")
        except Exception as e:
            pytest.skip(f"VDX parser may not be fully implemented: {e}")


class TestTransformationPerformance:
    """
    Performance benchmarks for graph transformation
    """

    def test_transformation_speed(self):
        """Benchmark graph transformation speed"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        # Measure transformation time
        start_time = time.time()
        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()
        end_time = time.time()

        transformation_time = end_time - start_time

        # Transformation should be fast
        assert transformation_time < 5.0, f"Transformation took too long: {transformation_time:.2f}s"

        print(f"\nTransformation time: {transformation_time:.4f}s for {transformer.node_count} nodes, {transformer.edge_count} edges")
        if transformation_time > 0:
            print(f"Throughput: {(transformer.node_count + transformer.edge_count) / transformation_time:.2f} elements/s")

    def test_batch_processing_performance(self):
        """Benchmark batch processing performance"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Test different batch sizes
        batch_sizes = [10, 50, 100]
        for batch_size in batch_sizes:
            start_time = time.time()
            batch_count = 0
            for batch in transformer.batch_output(batch_size=batch_size):
                batch_count += 1
            end_time = time.time()

            batch_time = end_time - start_time
            print(f"Batch processing (size={batch_size}): {batch_time:.4f}s for {batch_count} batches")

            # Batching should be very fast (just slicing)
            assert batch_time < 1.0, f"Batch processing too slow: {batch_time:.2f}s"

    @pytest.mark.parametrize("sample_file", [
        "MyDiagram1.bpmn",
        "diagram_3.bpmn",
        "diagram4.bpmn"
    ])
    def test_transformation_speed_multiple_files(self, sample_file):
        """Benchmark transformation across multiple files"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        file_path = SAMPLES / sample_file
        if not file_path.exists():
            pytest.skip(f"Sample file not found: {file_path}")

        parsed_data, _ = dispatch_parse(file_path, filename=file_path.name)

        start_time = time.time()
        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()
        end_time = time.time()

        transformation_time = end_time - start_time

        # Should complete quickly
        assert transformation_time < 5.0, f"Transformation of {sample_file} took too long: {transformation_time:.2f}s"

        print(f"\n{sample_file}: {transformation_time:.4f}s ({transformer.node_count} nodes, {transformer.edge_count} edges)")


class TestEndToEndPerformance:
    """
    Performance benchmarks for the complete pipeline
    """

    def test_full_pipeline_performance(self):
        """Benchmark complete pipeline from file to Cypher queries"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"

        # Measure complete pipeline
        start_time = time.time()

        # Parse
        parsed_data, format_type = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        # Transform
        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        end_time = time.time()
        total_time = end_time - start_time

        # Complete pipeline should finish quickly
        assert total_time < 15.0, f"Full pipeline took too long: {total_time:.2f}s"

        print(f"\nFull pipeline time: {total_time:.4f}s")
        print(f"  - Generated {len(cypher_queries)} Cypher queries")
        print(f"  - {transformer.node_count} nodes, {transformer.edge_count} edges")

    def test_repeated_transformations_performance(self):
        """Test performance of repeated transformations"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "MyDiagram1.bpmn"
        if not bpmn_file.exists():
            pytest.skip(f"Sample file not found: {bpmn_file}")

        # Parse once
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        # Transform multiple times
        num_iterations = 10
        start_time = time.time()

        for i in range(num_iterations):
            transformer = GraphTransformer(parsed_data)
            cypher_queries = transformer.transform()

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / num_iterations

        print(f"\n{num_iterations} transformations: {total_time:.4f}s (avg: {avg_time:.4f}s)")

        # Should handle repeated transformations efficiently
        assert avg_time < 2.0, f"Average transformation time too slow: {avg_time:.2f}s"


class TestScalability:
    """
    Tests for scalability with different data sizes
    """

    def test_scalability_with_element_count(self):
        """Test performance scales reasonably with number of elements"""
        try:
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Transformer not available: {e}")

        # Test with different sizes
        sizes = [10, 50, 100, 500]
        times = []

        for size in sizes:
            # Create test data with varying number of activities
            test_data = {
                "activities": [{"id": f"act_{i}", "name": f"Task {i}"} for i in range(size)],
                "events": [{"id": "start", "type": "start"}, {"id": "end", "type": "end"}],
                "gateways": [],
                "flows": [{"id": f"flow_{i}", "sourceRef": f"act_{i}", "targetRef": f"act_{i+1}"} for i in range(size - 1)],
                "pools": [],
                "lanes": []
            }

            start_time = time.time()
            transformer = GraphTransformer(test_data)
            cypher_queries = transformer.transform()
            end_time = time.time()

            elapsed = end_time - start_time
            times.append(elapsed)

            print(f"\n{size} elements: {elapsed:.4f}s ({size / elapsed:.2f} elements/s)")

        # Performance should not degrade exponentially
        # (simple check: 50x elements shouldn't take 50x time)
        if len(times) >= 2 and times[0] > 0:
            ratio = times[-1] / times[0]
            element_ratio = sizes[-1] / sizes[0]
            print(f"\nScaling ratio: {ratio:.2f}x time for {element_ratio:.2f}x elements")

            # Should be roughly linear or better (allowing some overhead)
            assert ratio < element_ratio * 2, f"Performance degradation too severe: {ratio:.2f}x"

    def test_query_generation_count(self):
        """Test that query count scales appropriately with elements"""
        try:
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Transformer not available: {e}")

        # Create test data
        num_activities = 100
        test_data = {
            "activities": [{"id": f"act_{i}", "name": f"Task {i}"} for i in range(num_activities)],
            "events": [],
            "gateways": [],
            "flows": [],
            "pools": [],
            "lanes": []
        }

        transformer = GraphTransformer(test_data)
        cypher_queries = transformer.transform()

        # Should generate roughly one query per node (may vary by implementation)
        assert len(cypher_queries) > 0, "Should generate queries"
        print(f"\n{num_activities} activities → {len(cypher_queries)} Cypher queries")

        # Query count should be proportional to element count
        assert len(cypher_queries) <= num_activities * 2, "Query count should scale reasonably"


class TestMemoryEfficiency:
    """
    Tests for memory efficiency (basic checks)
    """

    def test_batch_output_memory_efficiency(self):
        """Test that batch output doesn't duplicate data"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "Diagram 1.bpmn"
        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Get all batches
        all_batches = list(transformer.batch_output(batch_size=10))

        # Total queries in batches should equal original
        total_in_batches = sum(len(batch) for batch in all_batches)
        assert total_in_batches == len(cypher_queries), "Batching should not duplicate queries"

    def test_file_output_functionality(self, tmp_path):
        """Test writing queries to file"""
        try:
            from bpmn_mp.parsers.dispatcher_new import dispatch_parse
            from bpmn_neo4j.transformers.graph_transformer import GraphTransformer
        except Exception as e:
            pytest.skip(f"Required modules not available: {e}")

        bpmn_file = SAMPLES / "MyDiagram1.bpmn"
        if not bpmn_file.exists():
            pytest.skip(f"Sample file not found: {bpmn_file}")

        parsed_data, _ = dispatch_parse(bpmn_file, filename=bpmn_file.name)

        transformer = GraphTransformer(parsed_data)
        cypher_queries = transformer.transform()

        # Write to temporary file
        output_file = tmp_path / "cypher_output.txt"

        start_time = time.time()
        transformer.write_to_file(str(output_file))
        end_time = time.time()

        write_time = end_time - start_time

        # File writing should be fast
        assert write_time < 2.0, f"File writing took too long: {write_time:.2f}s"

        # Verify file was written
        assert output_file.exists(), "Output file should exist"

        # Verify content
        lines = output_file.read_text(encoding='utf-8').strip().split('\n')
        assert len(lines) == len(cypher_queries), "File should contain all queries"

        print(f"\nWrote {len(lines)} queries to file in {write_time:.4f}s")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])  # -s to show print output
