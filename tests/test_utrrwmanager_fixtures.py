from importlib import util
from pathlib import Path
import sys

import pytest


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "utrrwmanager"


@pytest.fixture(scope="module")
def mock_client():
    path = ROOT / "tools" / "mock_client_check.py"
    spec = util.spec_from_file_location("mock_client_check_for_utrrwmanager", path)
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_fixture(name: str) -> dict[str, list[str]]:
    entries = {"TX": [], "RX": [], "cmt": []}
    for line in (FIXTURE_DIR / name).read_text(encoding="utf-8").splitlines():
        if line.startswith("TX "):
            entries["TX"].append(line.removeprefix("TX ").strip())
        elif line.startswith("RX "):
            entries["RX"].append(line.removeprefix("RX ").strip())
        elif line.startswith("cmt "):
            entries["cmt"].append(line.removeprefix("cmt ").strip())
    return entries


def test_rom_version_fixture_matches_command_and_response(mock_client):
    fixture = read_fixture("rom_version_2052USM02.txt")

    assert bytes.fromhex(fixture["TX"][0]) == mock_client.COMMANDS["ROM_VERSION_CHECK"]

    frame = mock_client.parse_frame(bytes.fromhex(fixture["RX"][0]))
    assert mock_client.classify_frame(frame) == "ACK ROM_VERSION: 2052USM02"
    assert fixture["cmt"] == ["ROMバージョン: 2052USM02"]


def test_inventory_no_tag_fixture_matches_command_and_done_ack(mock_client):
    fixture = read_fixture("inventory_no_tag.txt")

    assert bytes.fromhex(fixture["TX"][0]) == mock_client.COMMANDS["UHF_INVENTORY"]

    frame = mock_client.parse_frame(bytes.fromhex(fixture["RX"][0]))
    assert mock_client.classify_frame(frame) == "ACK INVENTORY_DONE: count=0, channel=26"


def test_inventory_one_tag_fixture_matches_command_tag_response_and_done_ack(mock_client):
    fixture = read_fixture("inventory_one_tag.txt")

    assert bytes.fromhex(fixture["TX"][0]) == mock_client.COMMANDS["UHF_INVENTORY"]

    tag_frame = mock_client.parse_frame(bytes.fromhex(fixture["RX"][0]))
    assert tag_frame.command == mock_client.RF_TAG_DATA
    assert mock_client.classify_frame(tag_frame).startswith("RF_TAG PC+EPC=")

    done_frame = mock_client.parse_frame(bytes.fromhex(fixture["RX"][1]))
    assert mock_client.classify_frame(done_frame) == "ACK INVENTORY_DONE: count=1, channel=26"
