from pathlib import Path
import pytest

SAMPLES = Path(__file__).parent / "samples"

def test_xpdl_plugin_direct():
    try:
        from bpmn_mp.parsers.xpdl_parser.plugin import Plugin
    except Exception as e:
        pytest.skip(f"XPDL plugin not available: {e}")

    plugin = Plugin()
    p = SAMPLES / "Diagram 1.xpdl"
    assert p.exists(), f"Sample not found: {p}"

    score = plugin.detect(p, filename=p.name)
    assert score > 0.5, f"Detect score too low: {score}"

    data = plugin.parse(p, filename=p.name)
    assert isinstance(data, dict)
    for key in ("metadata", "flowElements", "messageFlows", "pools", "lanes"):
        assert key in data

def test_xpdl_dispatcher_roundtrip():
    try:
        from bpmn_mp.parsers.dispatcher_new import dispatch_parse
    except Exception as e:
        pytest.skip(f"Dispatcher not available: {e}")

    p = SAMPLES / "Diagram 1.xpdl"
    data, fmt = dispatch_parse(p, filename=p.name)
    assert fmt == "xpdl"
    assert isinstance(data.get("flowElements", []), list)
