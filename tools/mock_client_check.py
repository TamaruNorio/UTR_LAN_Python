#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import socket
from dataclasses import dataclass
from typing import Iterable, Optional


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 9004
DEFAULT_TIMEOUT = 3.0

STX = 0x02
ETX = 0x03
CR = 0x0D
ACK = 0x30
NACK = 0x31
RF_TAG_DATA = 0x6C

COMMANDS = {
    "ROM_VERSION_CHECK": bytes.fromhex("02 00 4F 01 90 03 E5 0D"),
    "COMMAND_MODE_SET_RAM": bytes.fromhex("02 00 4E 07 00 00 00 10 00 00 00 03 6A 0D"),
    "UHF_INVENTORY": bytes.fromhex("02 00 55 01 10 03 6B 0D"),
}

NACK_ERRORS = {
    0x42: "SUM_ERROR",
    0x44: "FORMAT_ERROR",
}


@dataclass(frozen=True)
class Frame:
    raw: bytes
    address: int
    command: int
    data: bytes


def format_hex(data: bytes) -> str:
    return data.hex(" ").upper()


def calculate_sum(data: bytes) -> int:
    return sum(data) & 0xFF


def parse_frame(raw: bytes) -> Frame:
    if len(raw) < 7:
        raise ValueError("frame too short")
    data_length = raw[3]
    expected_length = data_length + 7
    if len(raw) != expected_length:
        raise ValueError("frame length mismatch")
    if raw[0] != STX:
        raise ValueError("STX mismatch")
    if raw[4 + data_length] != ETX:
        raise ValueError("ETX mismatch")
    if raw[-1] != CR:
        raise ValueError("CR mismatch")
    if raw[-2] != calculate_sum(raw[:-2]):
        raise ValueError("SUM mismatch")
    return Frame(raw=raw, address=raw[1], command=raw[2], data=raw[4 : 4 + data_length])


def classify_frame(frame: Frame) -> str:
    if frame.command == ACK:
        if frame.data[:1] == b"\x90":
            rom = frame.data[1:].decode("ascii", errors="replace")
            return f"ACK ROM_VERSION: {rom}"
        if frame.data[:1] == b"\x10":
            count = int.from_bytes(frame.data[2:4], "little") if len(frame.data) >= 4 else 0
            channel = frame.data[4] if len(frame.data) >= 5 else None
            if channel is None:
                return f"ACK INVENTORY_DONE: count={count}"
            return f"ACK INVENTORY_DONE: count={count}, channel={channel}"
        return "ACK"
    if frame.command == NACK:
        detail = frame.data[0] if len(frame.data) >= 1 else 0
        error = frame.data[1] if len(frame.data) >= 2 else 0
        name = NACK_ERRORS.get(error, f"UNKNOWN_ERROR_0x{error:02X}")
        return f"NACK detail=0x{detail:02X}, error={name}"
    if frame.command == RF_TAG_DATA:
        pc_epc_len = frame.data[4] if len(frame.data) >= 5 else 0
        pc_epc = frame.data[5 : 5 + pc_epc_len]
        return f"RF_TAG PC+EPC={format_hex(pc_epc)}"
    return f"UNKNOWN command=0x{frame.command:02X}"


def recv_exact(sock: socket.socket, size: int) -> bytes:
    chunks = bytearray()
    while len(chunks) < size:
        chunk = sock.recv(size - len(chunks))
        if not chunk:
            raise ConnectionError("connection closed")
        chunks.extend(chunk)
    return bytes(chunks)


def recv_frame(sock: socket.socket) -> Frame:
    header = recv_exact(sock, 4)
    if header[0] != STX:
        raise ValueError("STX mismatch")
    data_length = header[3]
    rest = recv_exact(sock, data_length + 3)
    return parse_frame(header + rest)


def send_and_print(sock: socket.socket, name: str, command: bytes) -> list[Frame]:
    print(f"TX {name}: {format_hex(command)}")
    sock.sendall(command)
    frames = [recv_frame(sock)]
    while name == "UHF_INVENTORY" and frames[-1].command != ACK and frames[-1].command != NACK:
        frames.append(recv_frame(sock))
    for frame in frames:
        print(f"RX: {format_hex(frame.raw)}")
        print(f"  {classify_frame(frame)}")
    return frames


def run_check(host: str, port: int, timeout: float) -> None:
    print(f"CONNECT {host}:{port}")
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        send_and_print(sock, "ROM_VERSION_CHECK", COMMANDS["ROM_VERSION_CHECK"])
        send_and_print(sock, "COMMAND_MODE_SET_RAM", COMMANDS["COMMAND_MODE_SET_RAM"])
        send_and_print(sock, "UHF_INVENTORY", COMMANDS["UHF_INVENTORY"])


def parse_args(argv: Optional[Iterable[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check TX/RX with the UTR mock TCP server")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    run_check(args.host, args.port, args.timeout)


if __name__ == "__main__":
    main()
