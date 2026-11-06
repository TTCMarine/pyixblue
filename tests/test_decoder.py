"""Golden frames transcribed from ixblue_stdbin_decoder's stdbin_decoder.test.cc.

Sample logs were converted from that project's MIT-licensed test vectors.
See tests/fixtures/ATTRIBUTION.txt.
"""

from pathlib import Path

import pytest

from pyixblue import StdBinDecoder
from pyixblue.errors import StdBinError
from pyixblue.models import InsAlgorithmStatus1

FIXTURES = Path(__file__).parent / "fixtures"

MINIMAL_V2_NAV = bytes(
    [
        0x49, 0x58, 0x02,
        0x00, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x25,
        0x00, 0x00, 0x00, 0x05,
        0x00, 0x00, 0x01, 0x23,
        0x00, 0x00, 0xA0, 0x3F,
        0x00, 0x00, 0xC0, 0xBF,
        0xCD, 0xCC, 0x48, 0x41,
        0x00, 0x00, 0x05, 0x72,
    ]
)
TRUNCATED_V2_NAV = bytes(
    [
        0x49, 0x58, 0x02,
        0x00, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x21,
        0x00, 0x00, 0x00, 0x05,
        0x00, 0x00, 0x01, 0x23,
        0x00, 0x00, 0xA0, 0x3F,
        0x00, 0x00, 0xC0, 0xBF,
        0xCD, 0xCC, 0x48, 0x41,
    ]
)
BAD_CHECKSUM = bytes(
    [
        0x49, 0x58, 0x02,
        0x00, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x25,
        0x00, 0x00, 0x00, 0x05,
        0x00, 0x00, 0x01, 0x23,
        0x00, 0x00, 0xA0, 0x3F,
        0x00, 0x00, 0xC0, 0xBF,
        0xCD, 0xCC, 0x48, 0x41,
        0x00, 0x00, 0x00, 0x00,
    ]
)
BAD_NAV_VERSION = bytes(
    [
        0x49, 0x58, 0x00,
        0x00, 0x00, 0x00, 0x01,
        0x00, 0x00, 0x00, 0x00,
        0x00, 0x25,
        0x00, 0x00, 0x00, 0x05,
        0x00, 0x00, 0x01, 0x23,
        0x00, 0x00, 0xA0, 0x3F,
        0x00, 0x00, 0xC0, 0xBF,
        0xCD, 0xCC, 0x48, 0x41,
        0x00, 0x00, 0x05, 0x70,
    ]
)
BAD_ANSWER_VERSION = bytes(
    [
        0x41, 0x4E, 0x00,
        0x00, 0x0D,
        0xDE, 0xAD, 0xBE, 0xEF,
        0x00, 0x00, 0x03, 0xD4,
    ]
)
MINIMAL_V3_ANSWER = bytes(
    [
        0x41, 0x4E, 0x03,
        0x00, 0x0D,
        0xDE, 0xAD, 0xBE, 0xEF,
        0x00, 0x00, 0x03, 0xD7,
    ]
)


def load(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def close(actual: float, expected: float) -> None:
    assert actual == pytest.approx(expected, rel=1e-5, abs=1e-8)


def parse(payload: bytes) -> StdBinDecoder:
    decoder = StdBinDecoder()
    decoder.add_new_data(payload)
    assert decoder.parse_next_frame()
    return decoder


def assert_absent(nav, *names: str) -> None:
    for name in names:
        assert getattr(nav, name) is None, name


def assert_recovered(decoder: StdBinDecoder) -> None:
    decoder.add_new_data(MINIMAL_V2_NAV)
    assert decoder.parse_next_frame()
    assert decoder.buffered_size == 0
    assert decoder.last_nav.attitude_heading is not None
    decoder.add_new_data(MINIMAL_V3_ANSWER)
    assert decoder.parse_next_frame()
    assert decoder.buffered_size == 0
    assert decoder.last_answer == bytes([0xDE, 0xAD, 0xBE, 0xEF])


def test_truncated_frame_raises():
    decoder = StdBinDecoder()
    decoder.add_new_data(TRUNCATED_V2_NAV)
    with pytest.raises(StdBinError):
        decoder.parse_next_frame()


def test_minimal_v2_frame():
    decoder = parse(MINIMAL_V2_NAV)
    header = decoder.last_header
    assert header is not None
    assert header.message_type == "nav"
    assert header.protocol_version == 2
    assert header.telegram_size == 0x25
    assert header.validity_time_100us == 5
    assert header.counter == 0x123
    assert header.extended_navigation_bit_mask is None
    nav = decoder.last_nav
    assert nav.attitude_heading is not None
    assert nav.attitude_heading_deviation is None
    assert decoder.buffered_size == 0
    assert decoder.parse_next_frame() is False


def test_recovery_from_bad_checksum():
    decoder = StdBinDecoder()
    decoder.add_new_data(BAD_CHECKSUM)
    with pytest.raises(StdBinError, match="checksum"):
        decoder.parse_next_frame()
    assert decoder.buffered_size == 0
    assert_recovered(decoder)


def test_recovery_from_bad_nav_protocol_version():
    decoder = StdBinDecoder()
    decoder.add_new_data(BAD_NAV_VERSION)
    with pytest.raises(StdBinError, match="protocol version"):
        decoder.parse_next_frame()
    assert decoder.buffered_size == len(BAD_NAV_VERSION) - 1
    assert_recovered(decoder)


def test_recovery_from_bad_answer_protocol_version():
    decoder = StdBinDecoder()
    decoder.add_new_data(BAD_ANSWER_VERSION)
    with pytest.raises(StdBinError, match="protocol version"):
        decoder.parse_next_frame()
    assert decoder.buffered_size == len(BAD_ANSWER_VERSION) - 1
    assert_recovered(decoder)


def test_v2_protocol():
    decoder = parse(load("stdbin_v2.bin"))
    nav = decoder.last_nav
    assert nav.attitude_heading is not None
    close(nav.attitude_heading.heading_deg, 209.982)
    close(nav.attitude_heading.roll_deg, 0.016)
    close(nav.attitude_heading.pitch_deg, 0.206)

    assert nav.attitude_heading_deviation is not None
    close(nav.attitude_heading_deviation.heading_stddev_deg, 2.4517534)
    close(nav.attitude_heading_deviation.roll_stddev_deg, 0.004243818)
    close(nav.attitude_heading_deviation.pitch_stddev_deg, 0.004769328)

    assert nav.rt_heave_surge_sway is not None
    close(nav.rt_heave_surge_sway.rt_heave_without_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_heave_at_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_surge_at_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_sway_at_bdl, 0.0)

    assert nav.smart_heave is not None
    assert nav.smart_heave.validity_time_100us == 9215311
    close(nav.smart_heave.smart_heave_m, 0.0)

    assert nav.heading_roll_pitch_rate is not None
    close(nav.heading_roll_pitch_rate.heading_rate, 0.0)
    close(nav.heading_roll_pitch_rate.roll_rate, 0.0)
    close(nav.heading_roll_pitch_rate.pitch_rate, -0.002)

    assert nav.rotation_rate_vessel_frame is not None
    close(nav.rotation_rate_vessel_frame.xv1_degsec, 0.001287996)
    close(nav.rotation_rate_vessel_frame.xv2_degsec, 0.0010229985)
    close(nav.rotation_rate_vessel_frame.xv3_degsec, 0.0026694948)

    assert nav.acceleration_vessel_frame is not None
    close(nav.acceleration_vessel_frame.xv1_msec2, -0.00034000012)
    close(nav.acceleration_vessel_frame.xv2_msec2, 0.000035000077)
    close(nav.acceleration_vessel_frame.xv3_msec2, 0.000055000033)

    assert nav.position is not None
    close(nav.position.latitude_deg, 2.1332412116407853)
    close(nav.position.longitude_deg, 48.000037178805215)
    assert nav.position.altitude_ref == 0
    close(nav.position.altitude_m, 1.0547082)

    assert nav.position_deviation is not None
    close(nav.position_deviation.north_stddev_m, 14.192304)
    close(nav.position_deviation.east_stddev_m, 14.168153)
    close(nav.position_deviation.north_east_corr, 0.58203787)
    close(nav.position_deviation.altitude_stddev_m, 7.6183596)

    assert nav.speed_geographic_frame is not None
    close(nav.speed_geographic_frame.north_msec, -0.0015761498)
    close(nav.speed_geographic_frame.east_msec, -0.027757198)
    close(nav.speed_geographic_frame.up_msec, 0.045121633)

    assert nav.speed_geographic_frame_deviation is not None
    close(nav.speed_geographic_frame_deviation.north_stddev_msec, 0.0114673115)
    close(nav.speed_geographic_frame_deviation.east_stddev_msec, 0.009463781)
    close(nav.speed_geographic_frame_deviation.up_stddev_msec, 0.029867083)

    assert nav.current_geographic_frame is not None
    close(nav.current_geographic_frame.north_msec, 0.0)
    close(nav.current_geographic_frame.east_msec, -0.0)

    assert nav.current_geographic_frame_deviation is not None
    close(nav.current_geographic_frame_deviation.north_stddev_msec, 0.0)
    close(nav.current_geographic_frame_deviation.east_stddev_msec, 0.0)

    assert nav.system_date is not None
    assert (nav.system_date.day, nav.system_date.month, nav.system_date.year) == (1, 1, 2006)

    assert nav.sensor_status is not None
    assert (nav.sensor_status.status1, nav.sensor_status.status2) == (0, 0)

    assert nav.ins_algorithm_status is not None
    status = nav.ins_algorithm_status
    assert status.status1 == 0x12
    assert InsAlgorithmStatus1.ALIGNMENT in status.status1
    assert InsAlgorithmStatus1.GPS_ALTITUDE in status.status1
    assert status.status2 == 0x30000
    assert status.status3 == 0x4000000
    assert status.status4 == 0x200

    assert nav.ins_system_status is not None
    assert nav.ins_system_status.status1 == 0x200
    assert nav.ins_system_status.status2 == 0x1000
    assert nav.ins_system_status.status3 == 0x0

    assert nav.ins_user_status is not None
    assert nav.ins_user_status.status == 0x4C000000

    assert_absent(nav, "ahrs_algorithm_status", "ahrs_system_status", "ahrs_user_status")

    assert nav.heave_surge_sway_speed is not None
    close(nav.heave_surge_sway_speed.realtime_heave_speed, 0.0)
    close(nav.heave_surge_sway_speed.surge_speed, 0.0)
    close(nav.heave_surge_sway_speed.sway_speed, 0.0)

    assert nav.speed_vessel_frame is not None
    close(nav.speed_vessel_frame.xv1_msec, 0.014972644)
    close(nav.speed_vessel_frame.xv2_msec, -0.023280365)
    close(nav.speed_vessel_frame.xv3_msec, 0.0449414)

    assert nav.acceleration_geographic_frame is not None
    close(nav.acceleration_geographic_frame.north_msec2, 0.0)
    close(nav.acceleration_geographic_frame.east_msec2, 0.0)
    close(nav.acceleration_geographic_frame.up_msec2, 9.809999)

    assert nav.course_speed_over_ground is not None
    close(nav.course_speed_over_ground.course_over_ground, 266.96848)
    close(nav.course_speed_over_ground.speed_over_ground, 0.027778123)

    assert nav.temperatures is not None
    close(nav.temperatures.mean_temp_fog, 26.158884)
    close(nav.temperatures.mean_temp_acc, 26.158884)
    close(nav.temperatures.board_temperature, 158.65643)

    assert_absent(
        nav,
        "attitude_quaternion",
        "attitude_quaternion_deviation",
        "raw_acceleration_vessel_frame",
        "acceleration_vessel_frame_deviation",
        "rotation_rate_vessel_frame_deviation",
    )


def test_v2_frame_split_at_every_offset():
    payload = load("stdbin_v2.bin")
    decoder = StdBinDecoder()
    for cut in range(1, len(payload)):
        decoder.add_new_data(payload[:cut])
        assert decoder.parse_next_frame() is False
        decoder.add_new_data(payload[cut:])
        assert decoder.parse_next_frame()
        assert decoder.last_nav.attitude_heading is not None
        close(decoder.last_nav.attitude_heading.heading_deg, 209.982)


def test_v2_with_garbage_prefix():
    payload = load("stdbin_v2.bin")
    decoder = parse(payload[len(payload) // 2 :] + payload)
    assert decoder.last_nav.attitude_heading is not None
    close(decoder.last_nav.attitude_heading.heading_deg, 209.982)
    close(decoder.last_nav.attitude_heading.roll_deg, 0.016)
    close(decoder.last_nav.attitude_heading.pitch_deg, 0.206)


def test_two_frames_with_garbage_prefix():
    v2 = load("stdbin_v2.bin")
    v4 = load("stdbin_v4.bin")
    decoder = StdBinDecoder()
    decoder.add_new_data(v2[len(v2) // 2 :] + v2 + v4)
    assert decoder.parse_next_frame()
    assert decoder.last_header is not None
    assert decoder.last_header.protocol_version == 2
    assert decoder.parse_next_frame()
    assert decoder.last_header.protocol_version == 4
    assert decoder.parse_next_frame() is False


def test_v3_protocol():
    nav = parse(load("stdbin_v3.bin")).last_nav
    assert nav.attitude_heading is not None
    close(nav.attitude_heading.heading_deg, 0.0)
    close(nav.attitude_heading.roll_deg, 0.809)
    close(nav.attitude_heading.pitch_deg, -0.521)

    assert nav.attitude_heading_deviation is not None
    close(nav.attitude_heading_deviation.heading_stddev_deg, 60.0)
    close(nav.attitude_heading_deviation.roll_stddev_deg, 4.9997573)
    close(nav.attitude_heading_deviation.pitch_stddev_deg, 4.999801)

    assert nav.rt_heave_surge_sway is not None
    close(nav.rt_heave_surge_sway.rt_heave_without_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_heave_at_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_surge_at_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_sway_at_bdl, 0.0)

    assert nav.smart_heave is not None
    assert nav.smart_heave.validity_time_100us == 565983535
    close(nav.smart_heave.smart_heave_m, 0.0)

    assert nav.heading_roll_pitch_rate is not None
    close(nav.heading_roll_pitch_rate.heading_rate, 0.0)
    close(nav.heading_roll_pitch_rate.roll_rate, 0.0)
    close(nav.heading_roll_pitch_rate.pitch_rate, -0.0029999998)

    assert nav.rotation_rate_vessel_frame is not None
    close(nav.rotation_rate_vessel_frame.xv1_degsec, -0.0013599998)
    close(nav.rotation_rate_vessel_frame.xv2_degsec, -0.0021450005)
    close(nav.rotation_rate_vessel_frame.xv3_degsec, -0.000024999996)

    assert nav.acceleration_vessel_frame is not None
    close(nav.acceleration_vessel_frame.xv1_msec2, -0.0004)
    close(nav.acceleration_vessel_frame.xv2_msec2, -0.00059999997)
    close(nav.acceleration_vessel_frame.xv3_msec2, -0.07685006)

    assert nav.position is not None
    close(nav.position.latitude_deg, 48.899099791755994)
    close(nav.position.longitude_deg, 2.061999802664471)
    assert nav.position.altitude_ref == 0
    close(nav.position.altitude_m, 3004.5398)

    assert nav.position_deviation is not None
    close(nav.position_deviation.north_stddev_m, 50.0)
    close(nav.position_deviation.east_stddev_m, 50.0)
    close(nav.position_deviation.north_east_corr, -0.00005929864)
    close(nav.position_deviation.altitude_stddev_m, 1.1056086)

    assert nav.speed_geographic_frame is not None
    close(nav.speed_geographic_frame.north_msec, -0.018215187)
    close(nav.speed_geographic_frame.east_msec, -0.012175002)
    close(nav.speed_geographic_frame.up_msec, 0.10336427)

    assert nav.speed_geographic_frame_deviation is not None
    close(nav.speed_geographic_frame_deviation.north_stddev_msec, 12.129728)
    close(nav.speed_geographic_frame_deviation.east_stddev_msec, 12.129744)
    close(nav.speed_geographic_frame_deviation.up_stddev_msec, 0.78773665)

    assert nav.current_geographic_frame is not None
    close(nav.current_geographic_frame.north_msec, 1.919778 * 1e-14)
    close(nav.current_geographic_frame.east_msec, 4.5171327 * 1e-15)

    assert nav.current_geographic_frame_deviation is not None
    close(nav.current_geographic_frame_deviation.north_stddev_msec, 0.50110954)
    close(nav.current_geographic_frame_deviation.east_stddev_msec, 0.5011094)

    assert nav.system_date is not None
    assert (nav.system_date.day, nav.system_date.month, nav.system_date.year) == (14, 3, 2019)

    assert nav.sensor_status is not None
    assert nav.sensor_status.status1 == 0x0
    assert nav.sensor_status.status2 == 0x100

    assert nav.ins_algorithm_status is not None
    assert nav.ins_algorithm_status.status1 == 0x81013112
    assert nav.ins_algorithm_status.status2 == 0x1003011
    assert nav.ins_algorithm_status.status3 == 0x4000100
    assert nav.ins_algorithm_status.status4 == 0x200

    assert nav.ins_system_status is not None
    assert nav.ins_system_status.status1 == 0x08011E00
    assert nav.ins_system_status.status2 == 0x8EFF
    assert nav.ins_system_status.status3 == 0x0

    assert nav.ins_user_status is not None
    assert nav.ins_user_status.status == 0x4C001102

    assert_absent(nav, "ahrs_algorithm_status", "ahrs_system_status", "ahrs_user_status")

    assert nav.heave_surge_sway_speed is not None
    close(nav.heave_surge_sway_speed.realtime_heave_speed, 0.0)
    close(nav.heave_surge_sway_speed.surge_speed, 0.0)
    close(nav.heave_surge_sway_speed.sway_speed, 0.0)

    assert nav.speed_vessel_frame is not None
    close(nav.speed_vessel_frame.xv1_msec, -0.017242743)
    close(nav.speed_vessel_frame.xv2_msec, 0.013600622)
    close(nav.speed_vessel_frame.xv3_msec, 0.10299126)

    assert nav.acceleration_geographic_frame is not None
    close(nav.acceleration_geographic_frame.north_msec2, 0.0)
    close(nav.acceleration_geographic_frame.east_msec2, 0.0)
    close(nav.acceleration_geographic_frame.up_msec2, 9.83)

    assert nav.course_speed_over_ground is not None
    close(nav.course_speed_over_ground.course_over_ground, 213.74023)
    close(nav.course_speed_over_ground.speed_over_ground, 0.021863433)

    assert nav.temperatures is not None
    close(nav.temperatures.mean_temp_fog, 28.700487)
    close(nav.temperatures.mean_temp_acc, 37.533264)
    close(nav.temperatures.board_temperature, 47.899994)

    assert nav.attitude_quaternion is not None
    close(nav.attitude_quaternion.q0, 0.9999646544456482)
    close(nav.attitude_quaternion.q1, -0.00706720445305109)
    close(nav.attitude_quaternion.q2, 0.00454969797283411)
    close(nav.attitude_quaternion.q3, -0.00003185356399626471)

    assert nav.attitude_quaternion_deviation is not None
    close(nav.attitude_quaternion_deviation.quat_stddev_xi1, 0.08726222813129425)
    close(nav.attitude_quaternion_deviation.quat_stddev_xi2, 0.08726298809051514)
    close(nav.attitude_quaternion_deviation.quat_stddev_xi3, 1.0471975803375244)

    assert nav.raw_acceleration_vessel_frame is not None
    close(nav.raw_acceleration_vessel_frame.xv1_msec2, 0.0)
    close(nav.raw_acceleration_vessel_frame.xv2_msec2, 0.0)
    close(nav.raw_acceleration_vessel_frame.xv3_msec2, 7.999994)

    assert nav.acceleration_vessel_frame_deviation is not None
    close(nav.acceleration_vessel_frame_deviation.xv1_stddev_msec2, 16.82827)
    close(nav.acceleration_vessel_frame_deviation.xv2_stddev_msec2, 16.827307)
    close(nav.acceleration_vessel_frame_deviation.xv3_stddev_msec2, 1.1194783)

    assert nav.rotation_rate_vessel_frame_deviation is not None
    close(nav.rotation_rate_vessel_frame_deviation.xv1_stddev_degsec, 0.00008998095)
    close(nav.rotation_rate_vessel_frame_deviation.xv2_stddev_degsec, 0.0029352242)
    close(nav.rotation_rate_vessel_frame_deviation.xv3_stddev_degsec, 0.0032638267)

    assert nav.rotation_acceleration_vessel_frame is not None
    close(nav.rotation_acceleration_vessel_frame.xv1_degsec2, 0.0003888396)
    close(nav.rotation_acceleration_vessel_frame.xv2_degsec2, 0.0017579537)
    close(nav.rotation_acceleration_vessel_frame.xv3_degsec2, 0.0013762031)

    assert nav.rotation_acceleration_vessel_frame_deviation is not None
    close(nav.rotation_acceleration_vessel_frame_deviation.xv1_stddev_degsec2, 0.0000141353985)
    close(nav.rotation_acceleration_vessel_frame_deviation.xv2_stddev_degsec2, 0.000014134977)
    close(nav.rotation_acceleration_vessel_frame_deviation.xv3_stddev_degsec2, 0.000014134976)

    assert nav.raw_rotation_rate_vessel_frame is not None
    close(nav.raw_rotation_rate_vessel_frame.xv1_degsec, 0.0)
    close(nav.raw_rotation_rate_vessel_frame.xv2_degsec, 0.0)
    close(nav.raw_rotation_rate_vessel_frame.xv3_degsec, 0.0)

    assert_absent(
        nav,
        "vehicle_attitude_heading",
        "vehicle_attitude_heading_deviation",
        "vehicle_position",
        "vehicle_position_deviation",
        "gnss_manual",
        "emlog2",
        "usbl3",
        "dmi",
        "lbl2",
        "lbl3",
        "lbl4",
        "event_marker_a",
        "event_marker_b",
        "event_marker_c",
        "dvl_ground_speed2",
        "dvl_water_speed2",
        "turret_angles",
        "vtg1",
        "vtg2",
        "log_book",
    )

    assert nav.utc is not None
    assert nav.utc.validity_time_100us == 566980000
    assert nav.utc.source == 0

    assert nav.gnss1 is not None
    assert nav.gnss1.validity_time_100us == 566981130
    assert nav.gnss1.gnss_id == 0
    assert nav.gnss1.gnss_quality == 4
    close(nav.gnss1.latitude_deg, 48.89909998575846)
    close(nav.gnss1.longitude_deg, 2.062000000476837)
    close(nav.gnss1.altitude_m, 3004.5)
    close(nav.gnss1.latitude_stddev_m, 0.1)
    close(nav.gnss1.longitude_stddev_m, 0.1)
    close(nav.gnss1.altitude_stddev_m, 0.1)
    close(nav.gnss1.lat_lon_stddev_m2, 0.0)
    close(nav.gnss1.geoidal_separation_m, 0.0)

    assert nav.gnss2 is not None
    assert nav.gnss2.validity_time_100us == 566981130
    assert nav.gnss2.gnss_id == 1
    assert nav.gnss2.gnss_quality == 4
    close(nav.gnss2.latitude_deg, 48.89909998575846)
    close(nav.gnss2.longitude_deg, 2.062000000476837)
    close(nav.gnss2.altitude_m, 3004.5)
    close(nav.gnss2.latitude_stddev_m, 0.1)
    close(nav.gnss2.longitude_stddev_m, 0.2)
    close(nav.gnss2.altitude_stddev_m, 0.3)
    close(nav.gnss2.lat_lon_stddev_m2, -0.0)
    close(nav.gnss2.geoidal_separation_m, 0.0)

    assert nav.emlog1 is not None
    assert nav.emlog1.validity_time_100us == 566980110
    assert nav.emlog1.emlog_id == 0
    close(nav.emlog1.xv1_water_speed_ms, 60.0)
    close(nav.emlog1.xv1_speed_stddev_ms, 0.01)

    assert nav.usbl1 is not None
    assert nav.usbl1.validity_time_100us == 566980558
    assert nav.usbl1.usbl_id == 0
    assert nav.usbl1.beacon_id == b"ABC\x00\x00\x00\x00\x00"
    assert nav.usbl1.latitude_deg == 48.9
    close(nav.usbl1.longitude_deg, 2.0639999985694883)
    close(nav.usbl1.altitude_m, 0.0)
    close(nav.usbl1.north_stddev_m, 2.0)
    close(nav.usbl1.east_stddev_m, 2.0)
    close(nav.usbl1.lat_lon_cov_m2, 0.0)
    close(nav.usbl1.altitude_stddev_m, 2.0)

    assert nav.usbl2 is not None
    assert nav.usbl2.validity_time_100us == 566980110
    assert nav.usbl2.usbl_id == 1
    assert nav.usbl2.beacon_id == b"DEF\x00\x00\x00\x00\x00"
    assert nav.usbl2.latitude_deg == -48.898
    close(nav.usbl2.longitude_deg, 289.5933)
    close(nav.usbl2.altitude_m, 0.0)
    close(nav.usbl2.north_stddev_m, 10.0)
    close(nav.usbl2.east_stddev_m, 10.0)
    close(nav.usbl2.lat_lon_cov_m2, 0.0)
    close(nav.usbl2.altitude_stddev_m, 10.0)

    assert nav.depth is not None
    assert nav.depth.validity_time_100us == 566980110
    assert nav.depth.depth_m == -102.0
    assert nav.depth.depth_stddev_m == 100.0

    assert nav.dvl_ground_speed1 is not None
    assert nav.dvl_ground_speed1.validity_time_100us == 566980110
    assert nav.dvl_ground_speed1.dvl_id == 0
    close(nav.dvl_ground_speed1.xv1_ground_speed_ms, 39.0)
    close(nav.dvl_ground_speed1.xv2_ground_speed_ms, 39.0)
    close(nav.dvl_ground_speed1.xv3_ground_speed_ms, 39.0)
    close(nav.dvl_ground_speed1.dvl_speed_of_sound_ms, 1400.0)
    close(nav.dvl_ground_speed1.dvl_altitude_m, 20.0)
    close(nav.dvl_ground_speed1.xv1_stddev_ms, 3.0)
    close(nav.dvl_ground_speed1.xv2_stddev_ms, 3.0)
    close(nav.dvl_ground_speed1.xv3_stddev_ms, 3.0)

    assert nav.dvl_water_speed1 is not None
    assert nav.dvl_water_speed1.validity_time_100us == 566980110
    assert nav.dvl_water_speed1.dvl_id == 0
    close(nav.dvl_water_speed1.xv1_water_speed_ms, 18.571428)
    close(nav.dvl_water_speed1.xv2_water_speed_ms, 18.571428)
    close(nav.dvl_water_speed1.xv3_water_speed_ms, 18.571428)
    close(nav.dvl_water_speed1.dvl_speed_of_sound_ms, 1400.0)
    close(nav.dvl_water_speed1.xv1_stddev_ms, 3.0)
    close(nav.dvl_water_speed1.xv2_stddev_ms, 3.0)
    close(nav.dvl_water_speed1.xv3_stddev_ms, 3.0)

    assert nav.sound_velocity is not None
    assert nav.sound_velocity.ext_speed_of_sound_ms == 1300.0

    assert nav.lbl1 is not None
    assert nav.lbl1.validity_time_100us == 566980558
    assert nav.lbl1.rfu == 0
    assert nav.lbl1.beacon_id == b"0\x00\x00\x00\x00\x00\x00\x01"
    close(nav.lbl1.beacon_latitude_deg, -48.89800001780192)
    close(nav.lbl1.beacon_longitude_deg, 289.5960000038147)
    close(nav.lbl1.beacon_altitude_m, 0.0)
    close(nav.lbl1.range_m, 238.0)
    close(nav.lbl1.range_stddev_m, 10.0)


def _assert_v4_v5_common_absent(nav) -> None:
    assert_absent(
        nav,
        "ahrs_algorithm_status",
        "ahrs_system_status",
        "ahrs_user_status",
        "vehicle_attitude_heading",
        "vehicle_attitude_heading_deviation",
        "vehicle_position",
        "vehicle_position_deviation",
        "utc",
        "gnss1",
        "gnss2",
        "emlog1",
        "emlog2",
        "usbl1",
        "usbl2",
        "usbl3",
        "depth",
        "dvl_ground_speed1",
        "dvl_water_speed1",
        "sound_velocity",
        "dmi",
        "lbl1",
        "lbl2",
        "lbl3",
        "lbl4",
        "event_marker_a",
        "event_marker_b",
        "event_marker_c",
        "dvl_ground_speed2",
        "dvl_water_speed2",
        "turret_angles",
        "vtg1",
        "vtg2",
        "log_book",
    )


def test_v4_protocol():
    nav = parse(load("stdbin_v4.bin")).last_nav
    assert nav.attitude_heading is not None
    close(nav.attitude_heading.heading_deg, 357.428)
    close(nav.attitude_heading.roll_deg, -0.04)
    close(nav.attitude_heading.pitch_deg, 0.178)

    assert nav.attitude_heading_deviation is not None
    close(nav.attitude_heading_deviation.heading_stddev_deg, 54.47794)
    close(nav.attitude_heading_deviation.roll_stddev_deg, 0.010677356)
    close(nav.attitude_heading_deviation.pitch_stddev_deg, 0.016798064)

    assert nav.rt_heave_surge_sway is not None
    close(nav.rt_heave_surge_sway.rt_heave_without_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_heave_at_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_surge_at_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_sway_at_bdl, 0.0)

    assert nav.smart_heave is not None
    assert nav.smart_heave.validity_time_100us == 8715306
    close(nav.smart_heave.smart_heave_m, 0.0)

    assert nav.heading_roll_pitch_rate is not None
    close(nav.heading_roll_pitch_rate.heading_rate, -0.002)
    close(nav.heading_roll_pitch_rate.roll_rate, -0.005)
    close(nav.heading_roll_pitch_rate.pitch_rate, 0.0)

    assert nav.rotation_rate_vessel_frame is not None
    close(nav.rotation_rate_vessel_frame.xv1_degsec, -0.0061404924)
    close(nav.rotation_rate_vessel_frame.xv2_degsec, -0.00091849366)
    close(nav.rotation_rate_vessel_frame.xv3_degsec, 0.0024884976)

    assert nav.acceleration_vessel_frame is not None
    close(nav.acceleration_vessel_frame.xv1_msec2, 0.00004)
    close(nav.acceleration_vessel_frame.xv2_msec2, 0.00040999975)
    close(nav.acceleration_vessel_frame.xv3_msec2, 0.0007599999)

    assert nav.position is not None
    close(nav.position.latitude_deg, 2.133332706885363)
    close(nav.position.longitude_deg, 47.999999832595385)
    assert nav.position.altitude_ref == 0
    close(nav.position.altitude_m, 0.15949036)

    assert nav.position_deviation is not None
    close(nav.position_deviation.north_stddev_m, 14.204068)
    close(nav.position_deviation.east_stddev_m, 14.156303)
    close(nav.position_deviation.north_east_corr, 0.03173876)
    close(nav.position_deviation.altitude_stddev_m, 2.828566)

    assert nav.speed_geographic_frame is not None
    close(nav.speed_geographic_frame.north_msec, -0.0003105167)
    close(nav.speed_geographic_frame.east_msec, -0.011570915)
    close(nav.speed_geographic_frame.up_msec, 0.04521207)

    assert nav.speed_geographic_frame_deviation is not None
    close(nav.speed_geographic_frame_deviation.north_stddev_msec, 0.006963054)
    close(nav.speed_geographic_frame_deviation.east_stddev_msec, 0.0066441046)
    close(nav.speed_geographic_frame_deviation.up_stddev_msec, 0.009995009)

    assert nav.current_geographic_frame is not None
    close(nav.current_geographic_frame.north_msec, 0.0)
    close(nav.current_geographic_frame.east_msec, 0.0)

    assert nav.current_geographic_frame_deviation is not None
    close(nav.current_geographic_frame_deviation.north_stddev_msec, 0.0)
    close(nav.current_geographic_frame_deviation.east_stddev_msec, 0.0)

    assert nav.system_date is not None
    assert (nav.system_date.day, nav.system_date.month, nav.system_date.year) == (1, 1, 2006)

    assert nav.sensor_status is not None
    assert (nav.sensor_status.status1, nav.sensor_status.status2) == (0, 0)

    assert nav.ins_algorithm_status is not None
    assert nav.ins_algorithm_status.status1 == 0x00000012
    assert nav.ins_algorithm_status.status2 == 0x00030000
    assert nav.ins_algorithm_status.status3 == 0x04000000
    assert nav.ins_algorithm_status.status4 == 0x00000200

    assert nav.ins_system_status is not None
    assert nav.ins_system_status.status1 == 0x00000200
    assert nav.ins_system_status.status2 == 0x00001000
    assert nav.ins_system_status.status3 == 0x0

    assert nav.ins_user_status is not None
    assert nav.ins_user_status.status == 0x4C000000

    assert nav.heave_surge_sway_speed is not None
    close(nav.heave_surge_sway_speed.realtime_heave_speed, 0.0)
    close(nav.heave_surge_sway_speed.surge_speed, 0.0)
    close(nav.heave_surge_sway_speed.sway_speed, 0.0)

    assert nav.speed_vessel_frame is not None
    close(nav.speed_vessel_frame.xv1_msec, 0.000061522915)
    close(nav.speed_vessel_frame.xv2_msec, 0.011496336)
    close(nav.speed_vessel_frame.xv3_msec, 0.04489224)

    assert nav.acceleration_geographic_frame is not None
    close(nav.acceleration_geographic_frame.north_msec2, 0.0)
    close(nav.acceleration_geographic_frame.east_msec2, 0.0)
    close(nav.acceleration_geographic_frame.up_msec2, 9.809999)

    assert nav.course_speed_over_ground is not None
    close(nav.course_speed_over_ground.course_over_ground, 268.42966)
    close(nav.course_speed_over_ground.speed_over_ground, 0.011529781)

    assert nav.temperatures is not None
    close(nav.temperatures.mean_temp_fog, 25.993078)
    close(nav.temperatures.mean_temp_acc, 25.993078)
    close(nav.temperatures.board_temperature, 158.65643)

    assert nav.attitude_quaternion is not None
    close(nav.attitude_quaternion.q0, 0.9997469186782837)
    close(nav.attitude_quaternion.q1, 0.00038782256888225675)
    close(nav.attitude_quaternion.q2, -0.0015508179785683751)
    close(nav.attitude_quaternion.q3, -0.02244032360613346)

    assert nav.attitude_quaternion_deviation is not None
    close(nav.attitude_quaternion_deviation.quat_stddev_xi1, 0.00018635205924510956)
    close(nav.attitude_quaternion_deviation.quat_stddev_xi2, 0.00029318343149498105)
    close(nav.attitude_quaternion_deviation.quat_stddev_xi3, 0.9508194327354431)

    assert nav.raw_acceleration_vessel_frame is not None
    close(nav.raw_acceleration_vessel_frame.xv1_msec2, 0.0)
    close(nav.raw_acceleration_vessel_frame.xv2_msec2, 0.0)
    close(nav.raw_acceleration_vessel_frame.xv3_msec2, 8.000145)

    assert nav.acceleration_vessel_frame_deviation is not None
    close(nav.acceleration_vessel_frame_deviation.xv1_stddev_msec2, 0.009960833)
    close(nav.acceleration_vessel_frame_deviation.xv2_stddev_msec2, 0.009610326)
    close(nav.acceleration_vessel_frame_deviation.xv3_stddev_msec2, 0.01413504)

    assert nav.rotation_rate_vessel_frame_deviation is not None
    close(nav.rotation_rate_vessel_frame_deviation.xv1_stddev_degsec, 0.0005122008)
    close(nav.rotation_rate_vessel_frame_deviation.xv2_stddev_degsec, 0.004000983)
    close(nav.rotation_rate_vessel_frame_deviation.xv3_stddev_degsec, 0.00051041954)

    assert nav.rotation_acceleration_vessel_frame is not None
    close(nav.rotation_acceleration_vessel_frame.xv1_degsec2, 0.000536854)
    close(nav.rotation_acceleration_vessel_frame.xv2_degsec2, 0.002185823)
    close(nav.rotation_acceleration_vessel_frame.xv3_degsec2, -0.00046422562)

    assert nav.rotation_acceleration_vessel_frame_deviation is not None
    close(nav.rotation_acceleration_vessel_frame_deviation.xv1_stddev_degsec2, 0.000706749)
    close(nav.rotation_acceleration_vessel_frame_deviation.xv2_stddev_degsec2, 0.0007067489)
    close(nav.rotation_acceleration_vessel_frame_deviation.xv3_stddev_degsec2, 0.000706749)

    assert nav.raw_rotation_rate_vessel_frame is not None
    close(nav.raw_rotation_rate_vessel_frame.xv1_degsec, 0.0)
    close(nav.raw_rotation_rate_vessel_frame.xv2_degsec, 0.0)
    close(nav.raw_rotation_rate_vessel_frame.xv3_degsec, 0.0)

    _assert_v4_v5_common_absent(nav)


def test_v5_protocol():
    nav = parse(load("stdbin_v5.bin")).last_nav
    assert nav.attitude_heading is not None
    close(nav.attitude_heading.heading_deg, 357.404)
    close(nav.attitude_heading.roll_deg, -0.04)
    close(nav.attitude_heading.pitch_deg, 0.178)

    assert nav.attitude_heading_deviation is not None
    close(nav.attitude_heading_deviation.heading_stddev_deg, 54.47794)
    close(nav.attitude_heading_deviation.roll_stddev_deg, 0.010677356)
    close(nav.attitude_heading_deviation.pitch_stddev_deg, 0.016798064)

    assert nav.rt_heave_surge_sway is not None
    close(nav.rt_heave_surge_sway.rt_heave_without_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_heave_at_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_surge_at_bdl, 0.0)
    close(nav.rt_heave_surge_sway.rt_sway_at_bdl, 0.0)

    assert nav.smart_heave is not None
    assert nav.smart_heave.validity_time_100us == 8715456
    close(nav.smart_heave.smart_heave_m, 0.0)

    assert nav.heading_roll_pitch_rate is not None
    close(nav.heading_roll_pitch_rate.heading_rate, -0.002)
    close(nav.heading_roll_pitch_rate.roll_rate, -0.005)
    close(nav.heading_roll_pitch_rate.pitch_rate, -0.001)

    assert nav.rotation_rate_vessel_frame is not None
    close(nav.rotation_rate_vessel_frame.xv1_degsec, -0.006139992)
    close(nav.rotation_rate_vessel_frame.xv2_degsec, -0.0009184938)
    close(nav.rotation_rate_vessel_frame.xv3_degsec, 0.0024874974)

    assert nav.acceleration_vessel_frame is not None
    close(nav.acceleration_vessel_frame.xv1_msec2, 0.000034999997)
    close(nav.acceleration_vessel_frame.xv2_msec2, 0.00041499975)
    close(nav.acceleration_vessel_frame.xv3_msec2, 0.000715)

    assert nav.position is not None
    close(nav.position.latitude_deg, 2.133332701513265)
    close(nav.position.longitude_deg, 47.99999983221664)
    assert nav.position.altitude_ref == 0
    close(nav.position.altitude_m, 0.16032125)

    assert nav.position_deviation is not None
    close(nav.position_deviation.north_stddev_m, 14.204068)
    close(nav.position_deviation.east_stddev_m, 14.156303)
    close(nav.position_deviation.north_east_corr, 0.03173876)
    close(nav.position_deviation.altitude_stddev_m, 2.828566)

    assert nav.speed_geographic_frame is not None
    close(nav.speed_geographic_frame.north_msec, -0.00031041596)
    close(nav.speed_geographic_frame.east_msec, -0.011805205)
    close(nav.speed_geographic_frame.up_msec, 0.045028113)

    assert nav.speed_geographic_frame_deviation is not None
    close(nav.speed_geographic_frame_deviation.north_stddev_msec, 0.0069630453)
    close(nav.speed_geographic_frame_deviation.east_stddev_msec, 0.006644114)
    close(nav.speed_geographic_frame_deviation.up_stddev_msec, 0.009995009)

    assert nav.current_geographic_frame is not None
    close(nav.current_geographic_frame.north_msec, 0.0)
    close(nav.current_geographic_frame.east_msec, 0.0)

    assert nav.current_geographic_frame_deviation is not None
    close(nav.current_geographic_frame_deviation.north_stddev_msec, 0.0)
    close(nav.current_geographic_frame_deviation.east_stddev_msec, 0.0)

    assert nav.system_date is not None
    assert (nav.system_date.day, nav.system_date.month, nav.system_date.year) == (1, 1, 2006)

    assert nav.sensor_status is not None
    assert (nav.sensor_status.status1, nav.sensor_status.status2) == (0, 0)

    assert nav.ins_algorithm_status is not None
    assert nav.ins_algorithm_status.status1 == 0x00000012
    assert nav.ins_algorithm_status.status2 == 0x00030000
    assert nav.ins_algorithm_status.status3 == 0x04000000
    assert nav.ins_algorithm_status.status4 == 0x00000200

    assert nav.ins_system_status is not None
    assert nav.ins_system_status.status1 == 0x00000200
    assert nav.ins_system_status.status2 == 0x00001000
    assert nav.ins_system_status.status3 == 0x0

    assert nav.ins_user_status is not None
    assert nav.ins_user_status.status == 0x4C000000

    assert nav.heave_surge_sway_speed is not None
    close(nav.heave_surge_sway_speed.realtime_heave_speed, 0.0)
    close(nav.heave_surge_sway_speed.surge_speed, 0.0)
    close(nav.heave_surge_sway_speed.sway_speed, 0.0)

    assert nav.speed_vessel_frame is not None
    close(nav.speed_vessel_frame.xv1_msec, 0.00010496828)
    close(nav.speed_vessel_frame.xv2_msec, 0.011636287)
    close(nav.speed_vessel_frame.xv3_msec, 0.04487192)

    assert nav.acceleration_geographic_frame is not None
    close(nav.acceleration_geographic_frame.north_msec2, 0.0)
    close(nav.acceleration_geographic_frame.east_msec2, -0.01)
    close(nav.acceleration_geographic_frame.up_msec2, 9.809999)

    assert nav.course_speed_over_ground is not None
    close(nav.course_speed_over_ground.course_over_ground, 268.6071)
    close(nav.course_speed_over_ground.speed_over_ground, 0.011670535)

    assert nav.temperatures is not None
    close(nav.temperatures.mean_temp_fog, 25.993126)
    close(nav.temperatures.mean_temp_acc, 25.993126)
    close(nav.temperatures.board_temperature, 158.65643)

    assert nav.attitude_quaternion is not None
    close(nav.attitude_quaternion.q0, 0.999742329120636)
    close(nav.attitude_quaternion.q1, 0.00038825065712444484)
    close(nav.attitude_quaternion.q2, -0.0015505076153203845)
    close(nav.attitude_quaternion.q3, -0.022644637152552605)

    assert nav.attitude_quaternion_deviation is not None
    close(nav.attitude_quaternion_deviation.quat_stddev_xi1, 0.00018635205924510956)
    close(nav.attitude_quaternion_deviation.quat_stddev_xi2, 0.00029318343149498105)
    close(nav.attitude_quaternion_deviation.quat_stddev_xi3, 0.9508194327354431)

    assert nav.raw_acceleration_vessel_frame is not None
    close(nav.raw_acceleration_vessel_frame.xv1_msec2, 0.0)
    close(nav.raw_acceleration_vessel_frame.xv2_msec2, 0.0)
    close(nav.raw_acceleration_vessel_frame.xv3_msec2, 8.000145)

    assert nav.acceleration_vessel_frame_deviation is not None
    close(nav.acceleration_vessel_frame_deviation.xv1_stddev_msec2, 0.009960833)
    close(nav.acceleration_vessel_frame_deviation.xv2_stddev_msec2, 0.009610326)
    close(nav.acceleration_vessel_frame_deviation.xv3_stddev_msec2, 0.01413504)

    assert nav.rotation_rate_vessel_frame_deviation is not None
    close(nav.rotation_rate_vessel_frame_deviation.xv1_stddev_degsec, 0.0005122008)
    close(nav.rotation_rate_vessel_frame_deviation.xv2_stddev_degsec, 0.004000983)
    close(nav.rotation_rate_vessel_frame_deviation.xv3_stddev_degsec, 0.00051041954)

    assert nav.rotation_acceleration_vessel_frame is not None
    close(nav.rotation_acceleration_vessel_frame.xv1_degsec2, 0.00032014688)
    close(nav.rotation_acceleration_vessel_frame.xv2_degsec2, 0.001597333)
    close(nav.rotation_acceleration_vessel_frame.xv3_degsec2, -0.00042017436)

    assert nav.rotation_acceleration_vessel_frame_deviation is not None
    close(nav.rotation_acceleration_vessel_frame_deviation.xv1_stddev_degsec2, 0.000706749)
    close(nav.rotation_acceleration_vessel_frame_deviation.xv2_stddev_degsec2, 0.0007067489)
    close(nav.rotation_acceleration_vessel_frame_deviation.xv3_stddev_degsec2, 0.000706749)

    assert nav.raw_rotation_rate_vessel_frame is not None
    close(nav.raw_rotation_rate_vessel_frame.xv1_degsec, 0.0)
    close(nav.raw_rotation_rate_vessel_frame.xv2_degsec, 0.0)
    close(nav.raw_rotation_rate_vessel_frame.xv3_degsec, 0.0)

    _assert_v4_v5_common_absent(nav)


def test_answer_frame():
    decoder = parse(MINIMAL_V3_ANSWER)
    header = decoder.last_header
    assert header is not None
    assert header.message_type == "answer"
    assert header.protocol_version == 3
    assert decoder.last_nav.attitude_heading is None
    assert decoder.last_answer == bytes([0xDE, 0xAD, 0xBE, 0xEF])
