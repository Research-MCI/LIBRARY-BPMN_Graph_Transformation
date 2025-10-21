# Evaluation Testing Suite

This directory contains comprehensive evaluation tests for the BPMN Graph Transformation library. These tests are designed to thoroughly evaluate the quality, performance, and reliability of the BPMN parsing and Neo4j transformation pipeline.

## Test Modules Overview

### 1. End-to-End Evaluation (`test_evaluation_e2e.py`)

**Purpose**: Tests the complete transformation pipeline from BPMN files to Neo4j Cypher queries.

**Test Classes**:
- `TestEndToEndTransformation`: Full pipeline tests for different formats (BPMN, XPDL, XML)
- `TestTransformationQuality`: Quality checks for node-edge relationships, pool/lane structures
- `TestErrorHandling`: Edge cases and error handling scenarios

**Key Tests**:
- BPMN to Cypher full pipeline
- XPDL to Cypher full pipeline
- XML to Cypher full pipeline
- Multiple sample files processing
- Node-edge relationship preservation
- Pool and lane structure preservation
- Flow element type coverage
- Process ID uniqueness
- Batch output functionality
- Empty BPMN handling
- Malformed JSON handling

**Run Command**:
```bash
pytest tests/test_evaluation_e2e.py -v
```

---

### 2. Validation Evaluation (`test_evaluation_validation.py`)

**Purpose**: Tests the validation components including schema validation, semantic validation, and auto-fix functionality.

**Test Classes**:
- `TestSchemaValidation`: JSON schema validation tests
- `TestSemanticValidation`: BPMN semantic rule validation
- `TestValidationWithRealData`: Validation using real sample files
- `TestEdgeCases`: Edge cases and boundary conditions

**Key Tests**:
- Valid structured JSON validation
- Missing elements key handling
- Missing required arrays handling
- Auto-fix for missing IDs
- Auto-fix for duplicate IDs
- Cycle detection in flows
- Event semantics validation
- Gateway semantics validation
- Flow semantics validation
- Pool semantics validation
- Real BPMN output validation
- Empty data validation
- Deeply nested structures
- Special characters in IDs
- Large dataset handling (1000+ elements)

**Run Command**:
```bash
pytest tests/test_evaluation_validation.py -v
```

---

### 3. Graph Transformation Quality (`test_evaluation_transformation.py`)

**Purpose**: Tests the quality and correctness of BPMN to Neo4j graph transformations.

**Test Classes**:
- `TestCypherQueryGeneration`: Cypher syntax and format validation
- `TestNodeTransformation`: Node generation accuracy
- `TestEdgeTransformation`: Edge/relationship generation accuracy
- `TestPoolLaneTransformation`: Pool and lane transformation
- `TestInputNormalization`: Input normalization tests
- `TestTransformationConsistency`: Consistency across formats

**Key Tests**:
- Cypher syntax validity
- Node creation format
- Relationship creation format
- Property inclusion in nodes
- Process ID in queries
- Activity node generation
- Event node generation
- Gateway node generation
- Sequence flow generation
- Flow properties preservation
- Pool generation
- Lane generation
- Raw flow element normalization
- Property preservation during normalization
- Consistent output structure across files
- Deterministic transformation

**Run Command**:
```bash
pytest tests/test_evaluation_transformation.py -v
```

---

### 4. Performance Benchmarks (`test_evaluation_performance.py`)

**Purpose**: Performance testing for parsing, transformation, and the complete pipeline.

**Test Classes**:
- `TestParsingPerformance`: Parsing speed benchmarks
- `TestTransformationPerformance`: Transformation speed benchmarks
- `TestEndToEndPerformance`: Complete pipeline performance
- `TestScalability`: Scalability with different data sizes
- `TestMemoryEfficiency`: Memory efficiency tests

**Key Tests**:
- BPMN parsing speed
- XPDL parsing speed
- XML parsing speed
- Large file parsing (12MB VDX file)
- Transformation speed
- Batch processing performance
- Full pipeline performance
- Repeated transformation performance
- Scalability with element count (10, 50, 100, 500 elements)
- Query generation count
- Batch output memory efficiency
- File output functionality

**Run Command**:
```bash
# Run all performance tests
pytest tests/test_evaluation_performance.py -v -s

# Skip slow tests (large file parsing)
pytest tests/test_evaluation_performance.py -v -s -m "not slow"
```

**Performance Baselines**:
- BPMN parsing: < 10 seconds
- XPDL parsing: < 10 seconds
- XML parsing: < 10 seconds
- Large file parsing: < 120 seconds
- Transformation: < 5 seconds
- Full pipeline: < 15 seconds

---

### 5. Regression Testing (`test_evaluation_regression.py`)

**Purpose**: Ensures changes don't break existing functionality by comparing against known good outputs.

**Test Classes**:
- `TestParserRegressions`: Parser output structure regression tests
- `TestElementCountRegression`: Element count comparison tests
- `TestTransformationRegression`: Transformation output stability tests
- `TestCrossFormatConsistency`: Cross-format consistency verification
- `TestKnownGoodOutputs`: Comparison against all pre-computed outputs
- `TestBackwardCompatibility`: Backward compatibility with old outputs

**Key Tests**:
- BPMN parser output structure
- XML parser output structure
- XPDL parser output structure
- Element count consistency
- Transformation query count stability
- Cypher query format stability
- Same diagram in different formats
- Parser output against all known good outputs
- Old output JSON still processable

**Run Command**:
```bash
pytest tests/test_evaluation_regression.py -v -s
```

---

## Running All Evaluation Tests

### Run All Tests
```bash
pytest tests/test_evaluation_*.py -v
```

### Run with Coverage
```bash
pytest tests/test_evaluation_*.py -v --cov=src/bpmn_mp --cov=src/bpmn_neo4j --cov-report=html
```

### Run Specific Test Class
```bash
pytest tests/test_evaluation_e2e.py::TestEndToEndTransformation -v
```

### Run Specific Test
```bash
pytest tests/test_evaluation_e2e.py::TestEndToEndTransformation::test_bpmn_to_cypher_full_pipeline -v
```

### Run with Print Output (for performance tests)
```bash
pytest tests/test_evaluation_performance.py -v -s
```

---

## Test Data

All tests use sample files from `tests/test_parsers/samples/`:

**Input Files**:
- `Diagram 1.bpmn` (231 KB) - Large BPMN diagram
- `Diagram 1.xpdl` (110 KB) - Same diagram in XPDL format
- `MyDiagram1.bpmn` (8.6 KB) - Small BPMN diagram
- `diagram_3.bpmn` (13 KB) - Medium BPMN diagram
- `diagram_3.xml` (13 KB) - Same diagram in XML format
- `diagram4.bpmn` (16 KB) - Another medium diagram
- `diagram_2.xml` (6 KB) - Small XML diagram
- `Model2.xml` (15 KB) - Medium XML diagram
- `Model2.bpm` (63 KB) - Bizagi native format
- `Model2.vdx` (12 MB) - Large Visio VDX file

**Expected Output Files**:
- `output_bpmn.json` - Expected output for Diagram 1.bpmn
- `output_bpmn2.json` - Expected output for Diagram_1.bpmn
- `output_bpmn3.json` - Expected output for diagram_3.bpmn
- `output_bpmn4.json` - Expected output for diagram4.bpmn
- `output_bpmn5.json` - Expected output for MyDiagram1.bpmn
- `output_xml.json` - Expected output for Model2.xml
- `output_xpdl.json` - Expected output for Diagram 1.xpdl
- `output_vdx.json` - Expected output for Model2.vdx
- `output_bpm.json` - Expected output for Model2.bpm

---

## Test Coverage

The evaluation test suite covers:

1. **Functionality Coverage**:
   - ✅ File parsing (5 formats)
   - ✅ Format auto-detection
   - ✅ Schema validation
   - ✅ Semantic validation
   - ✅ Auto-fix functionality
   - ✅ Graph transformation
   - ✅ Cypher query generation
   - ✅ Batch processing
   - ✅ File output

2. **Quality Attributes**:
   - ✅ Correctness (regression tests)
   - ✅ Performance (benchmarks)
   - ✅ Reliability (error handling)
   - ✅ Scalability (large datasets)
   - ✅ Consistency (cross-format)
   - ✅ Backward compatibility

3. **Edge Cases**:
   - ✅ Empty/minimal BPMN files
   - ✅ Malformed structures
   - ✅ Missing IDs
   - ✅ Duplicate IDs
   - ✅ Cyclic flows
   - ✅ Special characters
   - ✅ Large datasets (1000+ elements)
   - ✅ Very large files (12 MB)

---

## Test Statistics

**Total Test Files**: 5
**Estimated Test Count**: 80+

### Breakdown by Module:
- `test_evaluation_e2e.py`: ~15 tests
- `test_evaluation_validation.py`: ~20 tests
- `test_evaluation_transformation.py`: ~20 tests
- `test_evaluation_performance.py`: ~15 tests
- `test_evaluation_regression.py`: ~15 tests

---

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

### GitHub Actions Example
```yaml
name: Evaluation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -e .
          pip install pytest pytest-cov
      - name: Run evaluation tests
        run: pytest tests/test_evaluation_*.py -v --cov=src
      - name: Run performance benchmarks
        run: pytest tests/test_evaluation_performance.py -v -s -m "not slow"
```

---

## Contributing

When adding new features or making changes:

1. **Run all evaluation tests** to ensure no regressions
2. **Update regression baselines** if output format changes intentionally
3. **Add new tests** for new functionality
4. **Update performance baselines** if performance improvements are made

---

## Troubleshooting

### Test Skips
Some tests may be skipped if:
- Required dependencies are not installed
- Sample files are missing
- Optional parsers are not available

### Performance Test Failures
If performance tests fail:
1. Check system load (other processes may affect timing)
2. Review performance baselines (may need adjustment for slower systems)
3. Run tests multiple times to verify consistency

### Regression Test Failures
If regression tests fail:
1. Check if changes were intentional
2. Update expected output files if format changed
3. Verify backward compatibility is maintained

---

## License

These tests are part of the BPMN Graph Transformation library.

---

## Contact

For questions or issues with the evaluation test suite, please refer to the main project repository.
