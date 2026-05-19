def build_frame(command: int, data: bytes) -> bytes:
    body = bytes([0x02, 0x00, command, len(data)]) + data + bytes([0x03])
    return body + bytes([sum(body) & 0xFF, 0x0D])


def inventory_tag_frame(pc_uii: bytes = b"\x30\x00") -> bytes:
    # Current parser expects RSSI at frame[5:7] and PC+UII length at frame[8].
    data = bytes([0x09, 0xF8, 0x30, 0x00, len(pc_uii)]) + pc_uii
    return build_frame(0x6C, data)


def inventory_done_ack_frame(read_count: int) -> bytes:
    # Current parser reads little-endian count from frame[6:8].
    data = bytes([0x10, 0x00]) + read_count.to_bytes(2, byteorder="little")
    return build_frame(0x30, data)


def test_inventory_tag_response_uses_6ch_command_code(utr_sample):
    frame = inventory_tag_frame()

    assert frame[utr_sample.CMD_LOCATION] == utr_sample.INV[0]
    assert utr_sample.verify_sum_value(frame) is True


def test_handle_inventory_response_collects_pc_uii(utr_sample):
    frame = inventory_tag_frame(pc_uii=b"\x30\x00")
    pc_uii_list = []
    rssi_list = []

    utr_sample.handle_inventory_response(frame, pc_uii_list, rssi_list)

    assert pc_uii_list == [b"\x30\x00"]
    assert len(rssi_list) == 1


def test_inventory_done_ack_is_identified_by_ack_and_detail_inv(utr_sample):
    frame = inventory_done_ack_frame(read_count=1)

    assert frame[utr_sample.CMD_LOCATION] == utr_sample.ACK[0]
    assert frame[utr_sample.DETAIL_LOCATION] == utr_sample.DETAIL_INV[0]
    assert utr_sample.check_inventory_ack_response(frame) == 1


def test_received_data_parse_handles_tag_response_then_inventory_done_ack(utr_sample):
    tag_frame = inventory_tag_frame(pc_uii=b"\x30\x00")
    ack_frame = inventory_done_ack_frame(read_count=1)

    pc_uii_list, rssi_list, expected_read_count = utr_sample.received_data_parse(
        tag_frame + ack_frame
    )

    assert pc_uii_list == [b"\x30\x00"]
    assert len(rssi_list) == 1
    assert expected_read_count == 1


# TODO: Confirm the full 6Ch RF tag response layout, RSSI conversion basis, and
# multiple-tag edge cases before adding stricter response parser expectations.
