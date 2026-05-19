from importlib import util
from pathlib import Path
import sys
from datetime import datetime

import pytest


@pytest.fixture(scope="module")
def real_device_check():
    path = Path(__file__).resolve().parents[1] / "tools" / "real_device_check.py"
    spec = util.spec_from_file_location("real_device_check", path)
    module = util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_host_is_required(real_device_check):
    with pytest.raises(SystemExit):
        real_device_check.parse_args([])


def test_parse_args_defaults(real_device_check):
    args = real_device_check.parse_args(["--host", "192.0.2.10"])

    assert args.host == "192.0.2.10"
    assert args.port == 9004
    assert args.timeout == 3.0
    assert args.log_dir == Path("logs") / "real_device"


def test_yes_option_is_not_available(real_device_check):
    with pytest.raises(SystemExit):
        real_device_check.parse_args(["--host", "192.0.2.10", "--yes"])


def test_only_safe_commands_are_defined(real_device_check):
    assert set(real_device_check.COMMANDS) == {
        "ROM_VERSION_CHECK",
        "COMMAND_MODE_SET_RAM",
        "UHF_INVENTORY",
    }


def test_preflight_text_contains_target_and_forbidden_operations(real_device_check):
    text = real_device_check.build_preflight_text(
        host="192.0.2.10",
        port=9004,
        log_path=Path("logs/real_device/sample.txt"),
    )

    assert "対象IP: 192.0.2.10" in text
    assert "ポート: 9004" in text
    assert "ROMバージョン確認" in text
    assert "UHF_Inventory 1回" in text
    assert "FLASH書き込み" in text
    assert "ブザー制御" in text
    assert "RFタグ書き込み系コマンド" in text


def test_make_log_path(real_device_check):
    path = real_device_check.make_log_path(
        Path("logs/real_device"),
        datetime(2026, 5, 19, 15, 4, 5),
    )

    assert path == Path("logs/real_device/real_device_check_20260519_150405.txt")


def test_log_header_warns_not_to_commit_real_device_logs(real_device_check, monkeypatch, tmp_path):
    captured = {}

    class FakeSocket:
        def settimeout(self, timeout):
            pass

        def sendall(self, command):
            pass

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    def fake_create_connection(target, timeout):
        return FakeSocket()

    def fake_send_and_log(sock, name, command, log_lines):
        log_lines.append(f"TX {name} DUMMY")

    monkeypatch.setattr(real_device_check.socket, "create_connection", fake_create_connection)
    monkeypatch.setattr(real_device_check, "send_and_log", fake_send_and_log)

    log_path = tmp_path / "real_device_check.txt"
    real_device_check.run_check("192.0.2.10", 9004, 3.0, log_path)
    captured["text"] = log_path.read_text(encoding="utf-8")

    assert "Do not commit logs/real_device/ files." in captured["text"]
