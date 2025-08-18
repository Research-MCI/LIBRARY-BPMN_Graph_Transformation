import sys
from pathlib import Path
import pytest

SAMPLES = Path(__file__).parent / "samples"

@pytest.mark.parametrize(
    "filename, expected_plugin",
    [
        ("Diagram 1.bpmn", "bpmn"),
        ("Diagram 1.xpdl", "xpdl"),
        ("Model2.xml", "xml"),
    ],
)
def test_dispatcher_auto_detect(filename, expected_plugin):
    try:
        from bpmn_mp.parsers.dispatcher_new import dispatch_parse, list_plugins
    except Exception as e:
        pytest.skip(f"Dispatcher not available or entry points not loaded: {e}")

    # pastikan plugin ter-discover
    plugins = list_plugins()
    assert expected_plugin in plugins, f"Expected plugin '{expected_plugin}' not discovered. Found: {plugins}"

    sample_path = SAMPLES / filename
    assert sample_path.exists(), f"Sample not found: {sample_path}"

    data, fmt = dispatch_parse(sample_path, filename=sample_path.name)
    assert fmt == expected_plugin, f"Dispatcher chose '{fmt}' but expected '{expected_plugin}'"
    assert isinstance(data, dict), "Parser must return a dict payload"

    # sanity check minimal keys
    if expected_plugin in ("bpmn", "xpdl"):
        for key in ("metadata", "flowElements", "messageFlows", "pools", "lanes"):
            assert key in data, f"Missing key '{key}' in parsed result for {expected_plugin}"
    elif expected_plugin == "xml":
        assert "metadata" in data and "definitions" in data, "XML parser should return metadata + definitions"


def test_dispatcher_with_hint_bpmn():
    try:
        from bpmn_mp.parsers.dispatcher_new import dispatch_parse
    except Exception as e:
        pytest.skip(f"Dispatcher not available: {e}")

    p = SAMPLES / "Diagram 1.bpmn"
    data, fmt = dispatch_parse(p, filename=p.name, hint="bpmn")
    assert fmt == "bpmn"
    assert "metadata" in data


def test_dispatcher_with_hint_xpdl():
    try:
        from bpmn_mp.parsers.dispatcher_new import dispatch_parse
    except Exception as e:
        pytest.skip(f"Dispatcher not available: {e}")

    p = SAMPLES / "Diagram 1.xpdl"
    data, fmt = dispatch_parse(p, filename=p.name, hint="xpdl")
    assert fmt == "xpdl"
    assert "metadata" in data
