"""Decoded stdbin header and navigation blocks.

Status enums follow the bit indexes in the reference decoder. Each member is
``1 << index``, so a parsed word compares equal to the raw integer.
"""

from dataclasses import dataclass
from enum import FlagBoundary, IntFlag, StrEnum


def _flag(name: str, members: dict[str, int]) -> type[IntFlag]:
    """Build an IntFlag that keeps unnamed bits from the wire word."""
    return IntFlag(name, members, boundary=FlagBoundary.KEEP)  # type: ignore[call-overload]


class MessageType(StrEnum):
    """Kind of stdbin frame."""

    NAV = "nav"
    ANSWER = "answer"


InsAlgorithmStatus1 = _flag(
    "InsAlgorithmStatus1",
    {
        "NAVIGATION": 1 << 0,
        "ALIGNMENT": 1 << 1,
        "FINE_ALIGNMENT": 1 << 2,
        "DEAD_RECKONING": 1 << 3,
        "GPS_ALTITUDE": 1 << 4,
        "DEPTHSENSOR_ALTITUDE": 1 << 5,
        "ZERO_ALTITUDE": 1 << 6,
        "HYDRO_ALTITUDE": 1 << 7,
        "LOG_RECEIVED": 1 << 8,
        "LOG_VALID": 1 << 9,
        "LOG_WAITING": 1 << 10,
        "LOG_REJECTED": 1 << 11,
        "GPS_RECEIVED": 1 << 12,
        "GPS_VALID": 1 << 13,
        "GPS_WAITING": 1 << 14,
        "GPS_REJECTED": 1 << 15,
        "USBL_RECEIVED": 1 << 16,
        "USBL_VALID": 1 << 17,
        "USBL_REJECTED": 1 << 18,
        "DEPTH_RECEIVED": 1 << 19,
        "DEPTH_VALID": 1 << 20,
        "DEPTH_WAITING": 1 << 21,
        "DEPTH_REJECTED": 1 << 22,
        "LBL_RECEIVED": 1 << 23,
        "LBL_VALID": 1 << 24,
        "LBL_WAITING": 1 << 25,
        "LBL_REJECTED": 1 << 26,
        "ALTITUDE_SATURATION": 1 << 27,
        "SPEED_SATURATION": 1 << 28,
        "INTERPOLATION_MISSED": 1 << 29,
        "HEAVE_INITIALISATION": 1 << 30,
    },
)

InsAlgorithmStatus2 = _flag(
    "InsAlgorithmStatus2",
    {
        "WATERTRACK_RECEIVED": 1 << 0,
        "WATERTRACK_VALID": 1 << 1,
        "WATERTRACK_WAITING": 1 << 2,
        "WATERTRACK_REJECTED": 1 << 3,
        "GPS2_RECEIVED": 1 << 4,
        "GPS2_VALID": 1 << 5,
        "GPS2_WAITING": 1 << 6,
        "GPS2_REJECTED": 1 << 7,
        "ALTITUDE_RECEIVED": 1 << 12,
        "ALTITUDE_VALID": 1 << 13,
        "ALTITUDE_WAITING": 1 << 14,
        "ALTITUDE_REJECTED": 1 << 15,
        "ZUPT_ACTIVATED": 1 << 16,
        "ZUPT_VALID": 1 << 17,
        "RO_ZUPT_ACTIVATED": 1 << 18,
        "RO_ZUPT_VALID": 1 << 19,
        "FAST_ALIGNEMENT": 1 << 22,
        "EMULATION_MODE": 1 << 23,
        "EMLOG_RECEIVED": 1 << 24,
        "EMLOG_VALID": 1 << 25,
        "EMLOG_WAITING": 1 << 26,
        "EMLOG_REJECTED": 1 << 27,
        "MANUALGPS_RECEIVED": 1 << 28,
        "MANUALGPS_VALID": 1 << 29,
        "MANUALGPS_WAITING": 1 << 30,
        "MANUALGPS_REJECTED": 1 << 31,
    },
)

InsAlgorithmStatus3 = _flag(
    "InsAlgorithmStatus3",
    {
        "SVL_RECEIVED": 1 << 0,
        "SVL_VALID": 1 << 1,
        "SVL_WAITING": 1 << 2,
        "SVL_REJECTED": 1 << 3,
        "EMLOG2_RECEIVED": 1 << 4,
        "EMLOG2_VALID": 1 << 5,
        "EMLOG2_WAITING": 1 << 6,
        "EMLOG2_REJECTED": 1 << 7,
        "USBL2_RECEIVED": 1 << 8,
        "USBL2_VALID": 1 << 9,
        "USBL2_WAITING": 1 << 10,
        "USBL2_REJECTED": 1 << 11,
        "USBL3_RECEIVED": 1 << 12,
        "USBL3_VALID": 1 << 13,
        "USBL3_WAITING": 1 << 14,
        "USBL3_REJECTED": 1 << 15,
        "CALCHK": 1 << 17,
        "RESTORE_ATTITUDE_FAILED": 1 << 18,
        "REL_SPD_ZUPT_ACTIVATED": 1 << 19,
        "REL_SPD_ZUPT_VALID": 1 << 20,
        "EXT_SENSOR_OUTDATED": 1 << 21,
        "SENSOR_USED_BEFORE_CALIB": 1 << 22,
        "RESTORE_ATTITUDE_REJECTED": 1 << 23,
        "POLAR_VALIDITY": 1 << 27,
        "FIRM_INCOMPATIBLES": 1 << 28,
        "IMO_ALIGNMENT": 1 << 29,
        "OPTIMAL_ALIGNMENT": 1 << 30,
        "STRATEGIC_ALIGNMENT": 1 << 31,
    },
)

InsAlgorithmStatus4 = _flag(
    "InsAlgorithmStatus4",
    {
        "LOG2_RECEIVED": 1 << 0,
        "LOG2_VALID": 1 << 1,
        "LOG2_WAITING": 1 << 2,
        "LOG2_REJECTED": 1 << 3,
        "WATERTRACK2_RECEIVED": 1 << 4,
        "WATERTRACK2_VALID": 1 << 5,
        "WATERTRACK2_WAITING": 1 << 6,
        "WATERTRACK2_REJECTED": 1 << 7,
        "DVL_DIST_TRAVELLED_VALID": 1 << 8,
        "DVL_CALIBRATION_NONE": 1 << 9,
        "DVL_ROUGH_CALIBRATION": 1 << 10,
        "DVL_FINE_CALIBRATION": 1 << 11,
        "DVL_CHECK_CALIBRATION": 1 << 12,
        "MANUAL_ATT_RECEIVED": 1 << 13,
        "MANUAL_ATT_VALID": 1 << 14,
        "MANUAL_ATT_WAITING": 1 << 15,
        "MANUAL_ATT_REJECTED": 1 << 16,
        "FIXED_HEADING": 1 << 17,
        "DEGRADED_MODE": 1 << 18,
        "VTG_RECEIVED": 1 << 19,
        "VTG_VALID": 1 << 20,
        "VTG_WAITING": 1 << 21,
        "VTG_REJECTED": 1 << 22,
        "VTG2_RECEIVED": 1 << 23,
        "VTG2_VALID": 1 << 24,
        "VTG2_WAITING": 1 << 25,
        "VTG2_REJECTED": 1 << 26,
        "ALIX_SYST_SATURATION": 1 << 27,
        "CINT_FLASH_MEMORY_WRERR": 1 << 28,
        "CINT_FLASH_MEMORY_ERERR": 1 << 29,
        "ODO_CALIBRATION_DONE": 1 << 30,
        "INCONSISTENT_SENSOR_DATA": 1 << 31,
    },
)

# The reference parser reads four status words (16 bytes). Status5 and status6
# are named in the C++ struct but are not part of that block.
InsAlgorithmStatus5 = _flag(
    "InsAlgorithmStatus5",
    {
        "NAV_MODE_NONE": 1 << 0,
        "TRAVELING_MODE": 1 << 1,
        "FIRING_MODE": 1 << 2,
        "FIRING_ON_MOVE": 1 << 3,
        "AERO_TRANSPORTATION": 1 << 4,
        "MANUAL_ALTITUD_VALID": 1 << 16,
        "MANUAL_ALTITUDE_REJECTED": 1 << 17,
        "SHOCK_ACTIVATED": 1 << 18,
        "SHOCK_DETECTED": 1 << 19,
        "TR_ZUPT_ACTIVATED": 1 << 20,
        "TR_ZUPT_VALID": 1 << 21,
        "PO_ZUPT_ACTIVATED": 1 << 22,
        "PO_ZUPT_VALID": 1 << 23,
        "RELATIVE_ATTITUDE_DEGRADED": 1 << 24,
        "CDSP_FLASH_MEMORY_WRERR": 1 << 25,
        "CDSP_FLASH_MEMORY_ERERR": 1 << 26,
        "CINT_FLASH_MEMORY_VIRGIN": 1 << 27,
        "CDSP_FLASH_MEMORY_VIRGIN": 1 << 28,
        "CINT_FLASH_MEMORY_ERROR": 1 << 29,
        "CDSP_FLASH_MEMORY_ERROR": 1 << 30,
    },
)

InsSystemStatus1 = _flag(
    "InsSystemStatus1",
    {
        "SERIAL_IN_R_ERR": 1 << 0,
        "INPUT_A_ERR": 1 << 1,
        "INPUT_B_ERR": 1 << 2,
        "INPUT_C_ERR": 1 << 3,
        "INPUT_D_ERR": 1 << 4,
        "INPUT_E_ERR": 1 << 5,
        "INPUT_R_ACTIVITY": 1 << 8,
        "INPUT_A_ACTIVITY": 1 << 9,
        "INPUT_B_ACTIVITY": 1 << 10,
        "INPUT_C_ACTIVITY": 1 << 11,
        "INPUT_D_ACTIVITY": 1 << 12,
        "INPUT_E_ACTIVITY": 1 << 13,
        "OUTPUT_R_FULL": 1 << 16,
        "OUTPUT_A_FULL": 1 << 17,
        "OUTPUT_B_FULL": 1 << 18,
        "OUTPUT_C_FULL": 1 << 19,
        "OUTPUT_D_FULL": 1 << 20,
        "OUTPUT_E_FULL": 1 << 21,
        "ETHERNET_PORT_FULL": 1 << 22,
        "INTERNAL_TIME_USED": 1 << 24,
        "ETHERNET_PORT_ACTIVITY": 1 << 26,
        "PULSE_IN_A_ACTIVITY": 1 << 27,
        "PULSE_IN_B_ACTIVITY": 1 << 28,
    },
)

InsSystemStatus2 = _flag(
    "InsSystemStatus2",
    {
        "GPS_DETECTED": 1 << 2,
        "DMI_DETECTED": 1 << 8,
        "UTC_DETECTED": 1 << 9,
        "ALTITUDE_DETECTED": 1 << 10,
        "PPS_DETECTED": 1 << 11,
        "ZUPT_MODE_ACTIVATED": 1 << 12,
        "MANUAL_GPS_DETECTED": 1 << 14,
        "WAIT_FOR_POSITION": 1 << 21,
        "INTERNAL_LOG": 1 << 24,
        "MPC_OVERLOAD": 1 << 27,
        "POWER_SUPPLY_FAILURE": 1 << 28,
        "RD_MODE": 1 << 29,
        "CONFIGURATION_SAVED": 1 << 30,
    },
)

InsSystemStatus3 = _flag(
    "InsSystemStatus3",
    {
        "VTG1_DETECTED": 1 << 13,
        "MANUAL_ATT_DETECTED": 1 << 15,
        "INPUT_CAN_ERR": 1 << 16,
        "INPUT_CAN_ACTIVITY": 1 << 17,
    },
)


@dataclass(frozen=True, slots=True)
class AttitudeHeading:
    heading_deg: float
    roll_deg: float
    pitch_deg: float


@dataclass(frozen=True, slots=True)
class AttitudeHeadingDeviation:
    heading_stddev_deg: float
    roll_stddev_deg: float
    pitch_stddev_deg: float


@dataclass(frozen=True, slots=True)
class RealTimeHeaveSurgeSway:
    rt_heave_without_bdl: float
    rt_heave_at_bdl: float
    rt_surge_at_bdl: float
    rt_sway_at_bdl: float


@dataclass(frozen=True, slots=True)
class SmartHeave:
    validity_time_100us: int
    smart_heave_m: float


@dataclass(frozen=True, slots=True)
class HeadingRollPitchRate:
    heading_rate: float
    roll_rate: float
    pitch_rate: float


@dataclass(frozen=True, slots=True)
class RotationRateVesselFrame:
    xv1_degsec: float
    xv2_degsec: float
    xv3_degsec: float


@dataclass(frozen=True, slots=True)
class AccelerationVesselFrame:
    xv1_msec2: float
    xv2_msec2: float
    xv3_msec2: float


@dataclass(frozen=True, slots=True)
class Position:
    """WGS84 position at the selected lever arm."""

    latitude_deg: float
    longitude_deg: float
    altitude_ref: int  # 0: geoid (mean sea level), 1: ellipsoid
    altitude_m: float


@dataclass(frozen=True, slots=True)
class PositionDeviation:
    north_stddev_m: float
    east_stddev_m: float
    north_east_corr: float
    altitude_stddev_m: float


@dataclass(frozen=True, slots=True)
class SpeedGeographicFrame:
    north_msec: float
    east_msec: float
    up_msec: float


@dataclass(frozen=True, slots=True)
class SpeedGeographicFrameDeviation:
    north_stddev_msec: float
    east_stddev_msec: float
    up_stddev_msec: float


@dataclass(frozen=True, slots=True)
class CurrentGeographicFrame:
    north_msec: float
    east_msec: float


@dataclass(frozen=True, slots=True)
class CurrentGeographicFrameDeviation:
    north_stddev_msec: float
    east_stddev_msec: float


@dataclass(frozen=True, slots=True)
class SystemDate:
    day: int
    month: int
    year: int


@dataclass(frozen=True, slots=True)
class SensorStatus:
    status1: int
    status2: int


@dataclass(frozen=True, slots=True)
class InsAlgorithmStatus:
    status1: InsAlgorithmStatus1
    status2: InsAlgorithmStatus2
    status3: InsAlgorithmStatus3
    status4: InsAlgorithmStatus4


@dataclass(frozen=True, slots=True)
class InsSystemStatus:
    status1: InsSystemStatus1
    status2: InsSystemStatus2
    status3: InsSystemStatus3


@dataclass(frozen=True, slots=True)
class InsUserStatus:
    status: int


@dataclass(frozen=True, slots=True)
class AhrsAlgorithmStatus:
    status: int


@dataclass(frozen=True, slots=True)
class AhrsSystemStatus:
    status1: int
    status2: int
    status3: int


@dataclass(frozen=True, slots=True)
class AhrsUserStatus:
    status: int


@dataclass(frozen=True, slots=True)
class HeaveSurgeSwaySpeed:
    realtime_heave_speed: float
    surge_speed: float
    sway_speed: float


@dataclass(frozen=True, slots=True)
class SpeedVesselFrame:
    xv1_msec: float
    xv2_msec: float
    xv3_msec: float


@dataclass(frozen=True, slots=True)
class AccelerationGeographicFrame:
    north_msec2: float
    east_msec2: float
    up_msec2: float


@dataclass(frozen=True, slots=True)
class CourseSpeedOverGround:
    course_over_ground: float
    speed_over_ground: float


@dataclass(frozen=True, slots=True)
class Temperatures:
    mean_temp_fog: float
    mean_temp_acc: float
    board_temperature: float


@dataclass(frozen=True, slots=True)
class AttitudeQuaternion:
    q0: float
    q1: float
    q2: float
    q3: float


@dataclass(frozen=True, slots=True)
class AttitudeQuaternionDeviation:
    quat_stddev_xi1: float
    quat_stddev_xi2: float
    quat_stddev_xi3: float


@dataclass(frozen=True, slots=True)
class RawAccelerationVesselFrame:
    xv1_msec2: float
    xv2_msec2: float
    xv3_msec2: float


@dataclass(frozen=True, slots=True)
class AccelerationVesselFrameDeviation:
    xv1_stddev_msec2: float
    xv2_stddev_msec2: float
    xv3_stddev_msec2: float


@dataclass(frozen=True, slots=True)
class RotationRateVesselFrameDeviation:
    xv1_stddev_degsec: float
    xv2_stddev_degsec: float
    xv3_stddev_degsec: float


@dataclass(frozen=True, slots=True)
class RotationAccelerationVesselFrame:
    xv1_degsec2: float
    xv2_degsec2: float
    xv3_degsec2: float


@dataclass(frozen=True, slots=True)
class RotationAccelerationVesselFrameDeviation:
    xv1_stddev_degsec2: float
    xv2_stddev_degsec2: float
    xv3_stddev_degsec2: float


@dataclass(frozen=True, slots=True)
class RawRotationRateVesselFrame:
    xv1_degsec: float
    xv2_degsec: float
    xv3_degsec: float


@dataclass(frozen=True, slots=True)
class VehicleAttitudeHeading:
    heading_deg: float
    roll_deg: float
    pitch_deg: float


@dataclass(frozen=True, slots=True)
class VehicleAttitudeHeadingDeviation:
    heading_stddev_deg: float
    roll_stddev_deg: float
    pitch_stddev_deg: float


@dataclass(frozen=True, slots=True)
class VehiclePosition:
    latitude_deg: float
    longitude_deg: float
    altitude_ref: int
    altitude_m: float


@dataclass(frozen=True, slots=True)
class VehiclePositionDeviation:
    north_stddev_m: float
    east_stddev_m: float
    north_east_corr: float
    altitude_stddev_m: float


@dataclass(frozen=True, slots=True)
class Utc:
    validity_time_100us: int
    source: int


@dataclass(frozen=True, slots=True)
class Gnss:
    validity_time_100us: int
    gnss_id: int
    gnss_quality: int
    latitude_deg: float
    longitude_deg: float
    altitude_m: float
    latitude_stddev_m: float
    longitude_stddev_m: float
    altitude_stddev_m: float
    lat_lon_stddev_m2: float
    geoidal_separation_m: float


@dataclass(frozen=True, slots=True)
class Emlog:
    validity_time_100us: int
    emlog_id: int
    xv1_water_speed_ms: float
    xv1_speed_stddev_ms: float


@dataclass(frozen=True, slots=True)
class Usbl:
    validity_time_100us: int
    usbl_id: int
    beacon_id: bytes
    latitude_deg: float
    longitude_deg: float
    altitude_m: float
    north_stddev_m: float
    east_stddev_m: float
    lat_lon_cov_m2: float
    altitude_stddev_m: float


@dataclass(frozen=True, slots=True)
class Depth:
    validity_time_100us: int
    depth_m: float
    depth_stddev_m: float


@dataclass(frozen=True, slots=True)
class DvlGroundSpeed:
    validity_time_100us: int
    dvl_id: int
    xv1_ground_speed_ms: float
    xv2_ground_speed_ms: float
    xv3_ground_speed_ms: float
    dvl_speed_of_sound_ms: float
    dvl_altitude_m: float
    xv1_stddev_ms: float
    xv2_stddev_ms: float
    xv3_stddev_ms: float


@dataclass(frozen=True, slots=True)
class DvlWaterSpeed:
    validity_time_100us: int
    dvl_id: int
    xv1_water_speed_ms: float
    xv2_water_speed_ms: float
    xv3_water_speed_ms: float
    dvl_speed_of_sound_ms: float
    xv1_stddev_ms: float
    xv2_stddev_ms: float
    xv3_stddev_ms: float


@dataclass(frozen=True, slots=True)
class SoundVelocity:
    validity_time_100us: int
    ext_speed_of_sound_ms: float


@dataclass(frozen=True, slots=True)
class Dmi:
    validity_time_100us: int
    pulse_count: int


@dataclass(frozen=True, slots=True)
class Lbl:
    validity_time_100us: int
    rfu: int
    beacon_id: bytes
    beacon_latitude_deg: float
    beacon_longitude_deg: float
    beacon_altitude_m: float
    range_m: float
    range_stddev_m: float


@dataclass(frozen=True, slots=True)
class EventMarker:
    validity_time_100us: int
    event_id: int
    event_count: int


@dataclass(frozen=True, slots=True)
class TurretAngles:
    validity_time_100us: int
    heading_bearing_drift_angle_deg: float
    roll_deg: float
    elevation_pitch_deg: float


@dataclass(frozen=True, slots=True)
class Vtg:
    validity_time_100us: int
    vtg_id: int
    true_course_deg: float
    magnetic_course_deg: float
    speed_over_ground_ms: float


@dataclass(frozen=True, slots=True)
class LogBook:
    validity_time_100us: int
    log_id: int
    custom_text: bytes


@dataclass(frozen=True, slots=True)
class NavHeader:
    """Parsed stdbin header.

    ``extended_navigation_bit_mask`` is set on protocol versions 3 and later.
    ``navigation_size`` is set on versions 4 and 5. Answer frames leave the
    navigation fields unset. ``counter`` is the frame counter carried in the
    navigation header.
    """

    message_type: MessageType
    protocol_version: int
    telegram_size: int
    navigation_bit_mask: int | None = None
    extended_navigation_bit_mask: int | None = None
    external_sensor_bit_mask: int | None = None
    navigation_size: int | None = None
    validity_time_100us: int | None = None
    counter: int | None = None


@dataclass(frozen=True, slots=True)
class NavData:
    """Navigation, extended-navigation, and external-sensor blocks.

    A field is ``None`` when that block's mask bit was clear in the frame.
    """

    attitude_heading: AttitudeHeading | None = None
    attitude_heading_deviation: AttitudeHeadingDeviation | None = None
    rt_heave_surge_sway: RealTimeHeaveSurgeSway | None = None
    smart_heave: SmartHeave | None = None
    heading_roll_pitch_rate: HeadingRollPitchRate | None = None
    rotation_rate_vessel_frame: RotationRateVesselFrame | None = None
    acceleration_vessel_frame: AccelerationVesselFrame | None = None
    position: Position | None = None
    position_deviation: PositionDeviation | None = None
    speed_geographic_frame: SpeedGeographicFrame | None = None
    speed_geographic_frame_deviation: SpeedGeographicFrameDeviation | None = None
    current_geographic_frame: CurrentGeographicFrame | None = None
    current_geographic_frame_deviation: CurrentGeographicFrameDeviation | None = None
    system_date: SystemDate | None = None
    sensor_status: SensorStatus | None = None
    ins_algorithm_status: InsAlgorithmStatus | None = None
    ins_system_status: InsSystemStatus | None = None
    ins_user_status: InsUserStatus | None = None
    ahrs_algorithm_status: AhrsAlgorithmStatus | None = None
    ahrs_system_status: AhrsSystemStatus | None = None
    ahrs_user_status: AhrsUserStatus | None = None
    heave_surge_sway_speed: HeaveSurgeSwaySpeed | None = None
    speed_vessel_frame: SpeedVesselFrame | None = None
    acceleration_geographic_frame: AccelerationGeographicFrame | None = None
    course_speed_over_ground: CourseSpeedOverGround | None = None
    temperatures: Temperatures | None = None
    attitude_quaternion: AttitudeQuaternion | None = None
    attitude_quaternion_deviation: AttitudeQuaternionDeviation | None = None
    raw_acceleration_vessel_frame: RawAccelerationVesselFrame | None = None
    acceleration_vessel_frame_deviation: AccelerationVesselFrameDeviation | None = None
    rotation_rate_vessel_frame_deviation: RotationRateVesselFrameDeviation | None = None
    rotation_acceleration_vessel_frame: RotationAccelerationVesselFrame | None = None
    rotation_acceleration_vessel_frame_deviation: (
        RotationAccelerationVesselFrameDeviation | None
    ) = None
    raw_rotation_rate_vessel_frame: RawRotationRateVesselFrame | None = None
    vehicle_attitude_heading: VehicleAttitudeHeading | None = None
    vehicle_attitude_heading_deviation: VehicleAttitudeHeadingDeviation | None = None
    vehicle_position: VehiclePosition | None = None
    vehicle_position_deviation: VehiclePositionDeviation | None = None
    utc: Utc | None = None
    gnss1: Gnss | None = None
    gnss2: Gnss | None = None
    gnss_manual: Gnss | None = None
    emlog1: Emlog | None = None
    emlog2: Emlog | None = None
    usbl1: Usbl | None = None
    usbl2: Usbl | None = None
    usbl3: Usbl | None = None
    depth: Depth | None = None
    dvl_ground_speed1: DvlGroundSpeed | None = None
    dvl_water_speed1: DvlWaterSpeed | None = None
    sound_velocity: SoundVelocity | None = None
    dmi: Dmi | None = None
    lbl1: Lbl | None = None
    lbl2: Lbl | None = None
    lbl3: Lbl | None = None
    lbl4: Lbl | None = None
    event_marker_a: EventMarker | None = None
    event_marker_b: EventMarker | None = None
    event_marker_c: EventMarker | None = None
    dvl_ground_speed2: DvlGroundSpeed | None = None
    dvl_water_speed2: DvlWaterSpeed | None = None
    turret_angles: TurretAngles | None = None
    vtg1: Vtg | None = None
    vtg2: Vtg | None = None
    log_book: LogBook | None = None
