from pathlib import Path
import pytest

SAMPLES = Path(__file__).parent / "samples"

def test_xml_plugin_direct():
    try:
        from bpmn_mp.parsers.xml_parser.plugin import Plugin
    except Exception as e:
        pytest.skip(f"XML plugin not available: {e}")

    plugin = Plugin()
    p = SAMPLES / "Model2.xml"
    assert p.exists(), f"Sample not found: {p}"

    score = plugin.detect(p, filename=p.name)
    assert score >= 0.5, f"Detect score too low: {score}"

    data = plugin.parse(p, filename=p.name)
    assert isinstance(data, dict)
    assert "metadata" in data and "definitions" in data

def test_xml_dispatcher_roundtrip():
    try:
        from bpmn_mp.parsers.dispatcher_new import dispatch_parse
    except Exception as e:
        pytest.skip(f"Dispatcher not available: {e}")

    p = SAMPLES / "Model2.xml"
    data, fmt = dispatch_parse(p, filename=p.name)
    # Bisa 'xml' atau bisa dikalahkan plugin lain jika file khusus — tapi untuk file test ini diasumsikan 'xml'
    assert fmt in ("xml",), f"Dispatcher returned '{fmt}', expected 'xml'"
    assert isinstance(data.get("definitions", []), list)
