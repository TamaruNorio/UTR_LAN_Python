#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import importlib.util
import socket
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional


DEFAULT_PORT = 9004
DEFAULT_TIMEOUT = 3.0
DEFAULT_LOG_DIR = Path("logs") / "real_device"
LOCALHOSTS = {"127.0.0.1", "localhost"}

ALLOWED_OPERATIONS = [
    "TCP接続確認",
    "ROMバージョン確認",
    "RAM指定のコマンドモード設定",
    "UHF_Inventory 1回",
    "ログ保存",
]

FORBIDDEN_OPERATIONS = [
    "FLASH書き込み",
    "FLASH初期化",
    "FLASH設定復元",
    "RF出力設定変更",
    "周波数設定変更",
    "ブザー制御",
    "LED&ブザー制御",
    "連続Inventory",
    "リスタート",
    "RFタグ書き込み系コマンド",
    "ファームウェア更新",
]


def load_mock_client_module():
    path = Path(__file__).resolve().parent / "mock_client_check.py"
    spec = importlib.util.spec_from_file_location("mock_client_check_for_real_device", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load mock_client_check.py from {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


mock_client = load_mock_client_module()

COMMANDS = {
    "ROM_VERSION_CHECK": mock_client.COMMANDS["ROM_VERSION_CHECK"],
    "COMMAND_MODE_SET_RAM": mock_client.COMMANDS["COMMAND_MODE_SET_RAM"],
    "UHF_INVENTORY": mock_client.COMMANDS["UHF_INVENTORY"],
}


def build_preflight_text(host: str, port: int, log_path: Path) -> str:
    allowed = "\n".join(f"- {item}" for item in ALLOWED_OPERATIONS)
    forbidden = "\n".join(f"- {item}" for item in FORBIDDEN_OPERATIONS)
    return (
        "実機LAN確認を開始する前に、以下を確認してください。\n\n"
        f"対象IP: {host}\n"
        f"ポート: {port}\n"
        "実行コマンド: ROMバージョン確認 -> RAM指定コマンドモード設定 -> UHF_Inventory 1回\n"
        "期待結果: ACK応答、ROM文字列、Inventory完了ACKまたはRFタグ応答を受信できること\n"
        f"ログ保存先: {log_path}\n\n"
        "実行する処理:\n"
        f"{allowed}\n\n"
        "禁止操作:\n"
        f"{forbidden}\n"
    )


def make_log_path(log_dir: Path, now: Optional[datetime] = None) -> Path:
    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    return log_dir / f"real_device_check_{timestamp}.txt"


def append_lines(lines: list[str], *items: str) -> None:
    lines.extend(items)
    for item in items:
        print(item)


def send_and_log(sock: socket.socket, name: str, command: bytes, log_lines: list[str]) -> list:
    append_lines(log_lines, f"TX {name} {mock_client.format_hex(command)}")
    sock.sendall(command)
    frames = [mock_client.recv_frame(sock)]
    while name == "UHF_INVENTORY" and frames[-1].command not in (mock_client.ACK, mock_client.NACK):
        frames.append(mock_client.recv_frame(sock))
    for frame in frames:
        append_lines(log_lines, f"RX {mock_client.format_hex(frame.raw)}")
        append_lines(log_lines, f"RESULT {mock_client.classify_frame(frame)}")
    return frames


def run_check(host: str, port: int, timeout: float, log_path: Path) -> None:
    log_lines = [
        "# This log may contain real device IP/network information. Do not commit logs/real_device/ files.",
        f"target_host: {host}",
        f"target_port: {port}",
        f"started_at: {datetime.now().isoformat(timespec='seconds')}",
        "",
    ]
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        send_and_log(sock, "ROM_VERSION_CHECK", COMMANDS["ROM_VERSION_CHECK"], log_lines)
        send_and_log(sock, "COMMAND_MODE_SET_RAM", COMMANDS["COMMAND_MODE_SET_RAM"], log_lines)
        send_and_log(sock, "UHF_INVENTORY", COMMANDS["UHF_INVENTORY"], log_lines)

    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print(f"LOG {log_path}")


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Safely check minimum TX/RX flow with a real UTR LAN device")
    parser.add_argument("--host", required=True, help="Target reader/writer IP address. No default is provided.")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    # TODO: Consider an explicit non-interactive option only after the safety flow is established.
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    log_path = make_log_path(args.log_dir)
    print(build_preflight_text(args.host, args.port, log_path))

    if args.host not in LOCALHOSTS:
        answer = input("実行する場合は YES と入力してください: ")
        if answer != "YES":
            print("Canceled.")
            return

    run_check(args.host, args.port, args.timeout, log_path)


if __name__ == "__main__":
    main()
