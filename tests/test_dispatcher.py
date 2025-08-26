import pytest
from unittest.mock import patch, mock_open

from bpnb_mp.parsers.dispatcher import dispatch_parse

@pytest.mark.parametrize("file_ext, func_name, mode, mock_return, expected_type", [
    (".bpmn", "parse_file_bpmn", "r", {"result": "bpmn"}, "bpmn"),
    (".xpdl", "parse_file_xpdl", "r", {"result": "xpdl"}, "xpdl"),
    (".xml", "parse_file_xml", "r", {"attr": 1}, "xml"),
    (".bpm", "parse_file_native", "rb", {"result": "native"}, "native"),
])
def test_dispatch_parse_supported(file_ext, func_name, mode, mock_return, expected_type):
    dummy_path = f"test{file_ext}"
    file_content = "dummy content" if mode == "r" else b"dummy content"

    patch_str = f"bpmn_mp.parsers.dispatcher.{func_name}"
    with patch("builtins.open", mock_open(read_data=file_content)), \
         patch(patch_str, return_value=mock_return) as mock_parser:
        if file_ext == ".xml":
            result, t = dispatch_parse(dummy_path)
            assert t == expected_type
            assert result == {"extendedAttributes": mock_return}
        else:
            result, t = dispatch_parse(dummy_path)
            assert t == expected_type
            assert result == mock_return
        mock_parser.assert_called_once()