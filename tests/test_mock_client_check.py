from importlib import util
from pathlib import Path
import sys

import pytest


@pytest.fixture(scope="module")
def mock_client():
    path = Path(__file__).resolve().parents[1] / "tools" / "mock_client_check.py"
    spec = util.spec_from_file_location("mock_client_check", path)
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_frame(mock_client, command: int, data: bytes = b"") -> bytes:
    body = bytes([0x02, 0x00, command, len(data)]) + data + bytes([0x03])
    return body + bytes([sum(body) & 0xFF, 0x0D])


def test_format_hex(mock_client):
    assert mock_client.format_hex(bytes.fromhex("02 00 4F")) == "02 00 4F"


def test_parse_frame_accepts_valid_ack(mock_client):
    raw = build_frame(mock_client, 0x30, b"\x90" + b"1100USM01")
    frame = mock_client.parse_frame(raw)

    assert frame.command == mock_client.ACK
    assert frame.data == b"\x90" + b"1100USM01"


def test_parse_frame_rejects_sum_mismatch(mock_client):
    raw = build_frame(mock_client, 0x30, b"\x90")
    bad = raw[:-2] + bytes([raw[-2] ^ 0xFF]) + raw[-1:]

    with pytest.raises(ValueError, match="SUM mismatch"):
        mock_client.parse_frame(bad)


def test_parse_frame_rejects_etx_and_cr_mismatch(mock_client):
    raw = bytearray(build_frame(mock_client, 0x30, b"\x90"))
    raw[5] = 0x00
    with pytest.raises(ValueError, match="ETX mismatch"):
        mock_client.parse_frame(bytes(raw))

    raw = bytearray(build_frame(mock_client, 0x30, b"\x90"))
    raw[-1] = 0x00
    with pytest.raises(ValueError, match="CR mismatch"):
        mock_client.parse_frame(bytes(raw))


def test_classify_rom_ack(mock_client):
    frame = mock_client.parse_frame(build_frame(mock_client, 0x30, b"\x90" + b"1100USM01"))

    assert mock_client.classify_frame(frame) == "ACK ROM_VERSION: 1100USM01"


def test_classify_inventory_done_ack(mock_client):
    frame = mock_client.parse_frame(build_frame(mock_client, 0x30, b"\x10\x00\x01\x00\x1A"))

    assert mock_client.classify_frame(frame) == "ACK INVENTORY_DONE: count=1, channel=26"


def test_classify_rf_tag_response(mock_client):
    frame = mock_client.parse_frame(build_frame(mock_client, 0x6C, b"\x09\xFF\x12\x30\x02\x30\x00"))

    assert mock_client.classify_frame(frame) == "RF_TAG PC+EPC=30 00"


def test_classify_nack(mock_client):
    frame = mock_client.parse_frame(build_frame(mock_client, 0x31, b"\x90\x42" + b"\x00" * 8))

    assert mock_client.classify_frame(frame) == "NACK detail=0x90, error=SUM_ERROR"


def test_parse_args_defaults_to_localhost(mock_client):
    args = mock_client.parse_args([])

    assert args.host == "127.0.0.1"
    assert args.port == 9004
    assert args.timeout == 3.0
