import pytest


@pytest.mark.parametrize(
    "command_name",
    [
        "ROM_VERSION_CHECK",
        "COMMAND_MODE_SET",
        "UHF_INVENTORY",
    ],
)
def test_command_frame_length_matches_data_length_plus_7(utr_sample, command_name):
    frame = utr_sample.COMMANDS[command_name]
    data_length = frame[3]

    assert len(frame) == data_length + 7


@pytest.mark.parametrize(
    "command_name",
    [
        "ROM_VERSION_CHECK",
        "COMMAND_MODE_SET",
        "UHF_INVENTORY",
    ],
)
def test_command_frame_has_stx_etx_cr_at_expected_positions(utr_sample, command_name):
    frame = utr_sample.COMMANDS[command_name]
    etx_index = utr_sample.HEADER_LENGTH + frame[3]

    assert frame[0] == utr_sample.STX[0]
    assert frame[etx_index] == utr_sample.ETX[0]
    assert frame[-1] == utr_sample.CR[0]


def test_parse_data_frame_returns_complete_frame_and_next_index(utr_sample):
    frame = utr_sample.COMMANDS["UHF_INVENTORY"]
    data = b"\x99" + frame + b"\x88"

    parsed, next_index = utr_sample.parse_data_frame(data, 1)

    assert parsed == frame
    assert next_index == 1 + len(frame)


def test_parse_data_frame_returns_none_for_incomplete_frame(utr_sample):
    frame = utr_sample.COMMANDS["UHF_INVENTORY"]

    parsed, next_index = utr_sample.parse_data_frame(frame[:-1], 0)

    assert parsed is None
    assert next_index == 0


def test_parse_data_frame_returns_none_when_cr_is_invalid(utr_sample):
    frame = utr_sample.COMMANDS["UHF_INVENTORY"]
    invalid_frame = frame[:-1] + b"\x00"

    parsed, next_index = utr_sample.parse_data_frame(invalid_frame, 0)

    assert parsed is None
    assert next_index == 0


# TODO: ETX mismatch handling is currently enforced by communicate(), not
# parse_data_frame(). Keep this test file focused on current pure functions
# until frame parsing is split into a dedicated protocol module.
