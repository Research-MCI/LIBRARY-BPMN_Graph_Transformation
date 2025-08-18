from pathlib import Path
import pytest

SAMPLES = Path(__file__).parent / "samples"

def test_bpmn_plugin_direct():
    # Uji plugin BPMN langsung (tanpa dispatcher), opsional
    try:
        from bpmn_mp.parsers.bpmn_parser.plugin import Plugin
    except Exception as e:
        pytest.skip(f"BPMN plugin not available: {e}")

    plugin = Plugin()
    p = SAMPLES / "Diagram 1.bpmn"
    assert p.exists(), f"Sample not found: {p}"

    score = plugin.detect(p, filename=p.name)
    assert score > 0.5, f"Detect score too low: {score}"

    data = plugin.parse(p, filename=p.name)
    assert isinstance(data, dict)
    for key in ("metadata", "flowElements", "messageFlows", "pools", "lanes"):
        assert key in data

def test_bpmn_dispatcher_roundtrip():
    try:
        from bpmn_mp.parsers.dispatcher_new import dispatch_parse
    except Exception as e:
        pytest.skip(f"Dispatcher not available: {e}")

    p = SAMPLES / "Diagram 1.bpmn"
    data, fmt = dispatch_parse(p, filename=p.name)
    assert fmt == "bpmn"
    assert isinstance(data.get("flowElements", []), list)
