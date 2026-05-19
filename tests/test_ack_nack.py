def build_frame(command: int, data: bytes) -> bytes:
    body = bytes([0x02, 0x00, command, len(data)]) + data + bytes([0x03])
    return body + bytes([sum(body) & 0xFF, 0x0D])


def test_ack_command_code_is_30h(utr_sample):
    frame = build_frame(0x30, bytes([0x90]))

    assert frame[utr_sample.CMD_LOCATION] == utr_sample.ACK[0]


def test_nack_command_code_is_31h_and_data_length_is_0ah(utr_sample):
    frame = build_frame(
        0x31,
        bytes([0x90, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    )

    assert frame[utr_sample.CMD_LOCATION] == utr_sample.NACK[0]
    assert frame[3] == 0x0A
    assert utr_sample.verify_sum_value(frame) is True


def test_parse_nack_response_sum_error_42h(utr_sample):
    frame = build_frame(
        0x31,
        bytes([0x90, 0x42, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    )

    message = utr_sample.parse_nack_response(frame)

    assert "SUM_ERROR" in message
    assert "SUM値" in message


def test_parse_nack_response_unknown_error_code(utr_sample):
    frame = build_frame(
        0x31,
        bytes([0x90, 0x99, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]),
    )

    assert utr_sample.parse_nack_response(frame) == "Unknown NACK error (0x99)"


# TODO: Error code 2 through 4 are present in the NACK frame format, but the
# current parser only maps error code 1. Add tests after parser behavior is
# designed against docs/protocol/frame_format.md and command_list.md.
