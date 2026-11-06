"""Block layout checks, including blocks the sample logs leave unset."""

import struct

from pyixblue import StdBinDecoder
from pyixblue.blocks import EXTENDED_BLOCKS, EXTERNAL_BLOCKS, NAVIGATION_BLOCKS

# Byte counts from the reference MemoryBlockParser constructors.
# Logbook is the 40 bytes that parser reads, not its 12-byte guard.
NAV_SIZES = {
    "attitude_heading": 12,
    "attitude_heading_deviation": 12,
    "rt_heave_surge_sway": 16,
    "smart_heave": 8,
    "heading_roll_pitch_rate": 12,
    "rotation_rate_vessel_frame": 12,
    "acceleration_vessel_frame": 12,
    "position": 21,
    "position_deviation": 16,
    "speed_geographic_frame": 12,
    "speed_geographic_frame_deviation": 12,
    "current_geographic_frame": 8,
    "current_geographic_frame_deviation": 8,
    "system_date": 4,
    "sensor_status": 8,
    "ins_algorithm_status": 16,
    "ins_system_status": 12,
    "ins_user_status": 4,
    "ahrs_algorithm_status": 4,
    "ahrs_system_status": 12,
    "ahrs_user_status": 4,
    "heave_surge_sway_speed": 12,
    "speed_vessel_frame": 12,
    "acceleration_geographic_frame": 12,
    "course_speed_over_ground": 8,
    "temperatures": 12,
    "attitude_quaternion": 16,
    "attitude_quaternion_deviation": 12,
    "raw_acceleration_vessel_frame": 12,
    "acceleration_vessel_frame_deviation": 12,
    "rotation_rate_vessel_frame_deviation": 12,
}
EXTENDED_SIZES = {
    "rotation_acceleration_vessel_frame": 12,
    "rotation_acceleration_vessel_frame_deviation": 12,
    "raw_rotation_rate_vessel_frame": 12,
    "vehicle_attitude_heading": 12,
    "vehicle_attitude_heading_deviation": 12,
    "vehicle_position": 21,
    "vehicle_position_deviation": 16,
}
EXTERNAL_SIZES = {
    "utc": 5,
    "gnss1": 46,
    "gnss2": 46,
    "gnss_manual": 46,
    "emlog1": 13,
    "emlog2": 13,
    "usbl1": 49,
    "usbl2": 49,
    "usbl3": 49,
    "depth": 12,
    "dvl_ground_speed1": 37,
    "dvl_water_speed1": 33,
    "sound_velocity": 8,
    "dmi": 8,
    "lbl1": 41,
    "lbl2": 41,
    "lbl3": 41,
    "lbl4": 41,
    "event_marker_a": 9,
    "event_marker_b": 9,
    "event_marker_c": 9,
    "dvl_ground_speed2": 37,
    "dvl_water_speed2": 33,
    "turret_angles": 16,
    "vtg1": 17,
    "vtg2": 17,
    "log_book": 40,
}


def test_block_sizes_and_bit_order():
    groups = (
        (NAVIGATION_BLOCKS, NAV_SIZES),
        (EXTENDED_BLOCKS, EXTENDED_SIZES),
        (EXTERNAL_BLOCKS, EXTERNAL_SIZES),
    )
    for blocks, sizes in groups:
        bits = [block.bit for block in blocks]
        assert bits == sorted(bits)
        assert len(bits) == len(set(bits))
        assert {block.field: block.size for block in blocks} == sizes


def test_vehicle_deviation_and_logbook_are_consumed_in_bit_order():
    """Bit 4 of the extended mask is omitted by the reference constructor."""
    payload = struct.pack(">fff", 1.5, 2.5, 3.5)
    payload += struct.pack(">ii", 1000, -7)  # dmi, bit 13
    payload += struct.pack(">iBI", 20, 0, 9)  # event A, bit 18
    payload += struct.pack(">iBfff", 30, 0, 10.0, 11.0, 12.5)  # vtg1, bit 25
    payload += struct.pack(">iI32s", 40, 99, b"HELLO".ljust(32, b"\x00"))  # bit 27
    telegram_size = 25 + len(payload) + 4
    header = struct.pack(
        ">2sBIIIHII",
        b"IX",
        3,
        0,
        1 << 4,
        (1 << 13) | (1 << 18) | (1 << 25) | (1 << 27),
        telegram_size,
        0,
        1,
    )
    body = header + payload
    frame = body + struct.pack(">I", sum(body) & 0xFFFFFFFF)

    decoder = StdBinDecoder()
    decoder.add_new_data(frame)
    assert decoder.parse_next_frame()
    nav = decoder.last_nav
    assert nav.vehicle_attitude_heading is None
    assert nav.vehicle_attitude_heading_deviation is not None
    assert nav.vehicle_attitude_heading_deviation.heading_stddev_deg == 1.5
    assert nav.vehicle_attitude_heading_deviation.roll_stddev_deg == 2.5
    assert nav.vehicle_attitude_heading_deviation.pitch_stddev_deg == 3.5
    assert nav.dmi is not None
    assert nav.dmi.validity_time_100us == 1000
    assert nav.dmi.pulse_count == -7
    assert nav.event_marker_a is not None
    assert nav.event_marker_a.event_count == 9
    assert nav.vtg1 is not None
    assert nav.vtg1.true_course_deg == 10.0
    assert nav.vtg1.speed_over_ground_ms == 12.5
    assert nav.log_book is not None
    assert nav.log_book.log_id == 99
    assert nav.log_book.custom_text.startswith(b"HELLO")
    assert decoder.buffered_size == 0
