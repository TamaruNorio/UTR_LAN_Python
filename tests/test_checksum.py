def test_calculate_sum_value_protocol_example_without_overflow(utr_sample):
    # docs/protocol/checksum.md: STX through ETX, lower byte only.
    data = bytes.fromhex("02 00 4F 01 00 03")

    assert utr_sample.calculate_sum_value(data) == 0x55


def test_calculate_sum_value_protocol_example_with_overflow(utr_sample):
    # docs/protocol/checksum.md: 013Fh overflows to SUM 3Fh.
    data = bytes.fromhex("02 00 4E 03 9F 45 05 03")

    assert utr_sample.calculate_sum_value(data) == 0x3F


def test_verify_sum_value_accepts_valid_frame(utr_sample):
    frame = utr_sample.COMMANDS["ROM_VERSION_CHECK"]

    assert utr_sample.verify_sum_value(frame) is True


def test_verify_sum_value_rejects_invalid_sum(utr_sample):
    frame = utr_sample.COMMANDS["ROM_VERSION_CHECK"]
    invalid_frame = frame[:-2] + bytes([frame[-2] ^ 0xFF]) + frame[-1:]

    assert utr_sample.verify_sum_value(invalid_frame) is False


def test_verify_sum_value_rejects_too_short_frame(utr_sample):
    assert utr_sample.verify_sum_value(bytes.fromhex("02 00 30")) is False


# TODO: Decide whether an invalid received SUM should become an exception or a
# return-value status after response parsing is separated from the sample script.
