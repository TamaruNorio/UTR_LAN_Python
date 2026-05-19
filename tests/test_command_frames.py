import pytest


def test_rom_version_check_frame_matches_protocol_example(utr_sample):
    assert utr_sample.COMMANDS["ROM_VERSION_CHECK"] == bytes.fromhex(
        "02 00 4F 01 90 03 E5 0D"
    )


def test_uhf_inventory_frame_matches_protocol_example(utr_sample):
    assert utr_sample.COMMANDS["UHF_INVENTORY"] == bytes.fromhex(
        "02 00 55 01 10 03 6B 0D"
    )


def test_command_mode_set_frame_has_valid_shape_and_sum(utr_sample):
    frame = utr_sample.COMMANDS["COMMAND_MODE_SET"]

    assert frame[0] == utr_sample.STX[0]
    assert frame[2] == 0x4E
    assert frame[3] == 0x07
    assert frame[4] == 0x00
    assert frame[-1] == utr_sample.CR[0]
    assert len(frame) == frame[3] + 7
    assert utr_sample.verify_sum_value(frame) is True


@pytest.mark.parametrize(
    "command_name",
    [
        "ROM_VERSION_CHECK",
        "COMMAND_MODE_SET",
        "UHF_INVENTORY",
    ],
)
def test_priority_command_frames_have_valid_sum(utr_sample, command_name):
    assert utr_sample.verify_sum_value(utr_sample.COMMANDS[command_name]) is True


# TODO: Tighten COMMAND_MODE_SET field-by-field expectations after confirming
# every byte of the 7-byte data section against docs/protocol/command_list.md.
