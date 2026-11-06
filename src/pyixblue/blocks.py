"""Declarative stdbin memory-block table.

Sizes and bit positions match the reference ``MemoryBlockParser`` constructors.
Blocks are stored in bit order, which is the order they are packed on the wire.
Logbook is the 40 bytes the reference parser actually reads (``int32``,
``uint32``, and 32 text bytes), not the 12-byte guard declared on that parser.
``vehicle_attitude_heading_deviation`` is included even though the reference
decoder constructs no parser for it, so a set extended-mask bit 4 is consumed.
"""

from collections.abc import Callable
from dataclasses import dataclass, fields
from struct import calcsize
from typing import Any

from pyixblue.models import (
    AccelerationGeographicFrame,
    AccelerationVesselFrame,
    AccelerationVesselFrameDeviation,
    AhrsAlgorithmStatus,
    AhrsSystemStatus,
    AhrsUserStatus,
    AttitudeHeading,
    AttitudeHeadingDeviation,
    AttitudeQuaternion,
    AttitudeQuaternionDeviation,
    CourseSpeedOverGround,
    CurrentGeographicFrame,
    CurrentGeographicFrameDeviation,
    Depth,
    Dmi,
    DvlGroundSpeed,
    DvlWaterSpeed,
    Emlog,
    EventMarker,
    Gnss,
    HeadingRollPitchRate,
    HeaveSurgeSwaySpeed,
    InsAlgorithmStatus,
    InsAlgorithmStatus1,
    InsAlgorithmStatus2,
    InsAlgorithmStatus3,
    InsAlgorithmStatus4,
    InsSystemStatus,
    InsSystemStatus1,
    InsSystemStatus2,
    InsSystemStatus3,
    InsUserStatus,
    Lbl,
    LogBook,
    Position,
    PositionDeviation,
    RawAccelerationVesselFrame,
    RawRotationRateVesselFrame,
    RealTimeHeaveSurgeSway,
    RotationAccelerationVesselFrame,
    RotationAccelerationVesselFrameDeviation,
    RotationRateVesselFrame,
    RotationRateVesselFrameDeviation,
    SensorStatus,
    SmartHeave,
    SoundVelocity,
    SpeedGeographicFrame,
    SpeedGeographicFrameDeviation,
    SpeedVesselFrame,
    SystemDate,
    Temperatures,
    TurretAngles,
    Usbl,
    Utc,
    VehicleAttitudeHeading,
    VehicleAttitudeHeadingDeviation,
    VehiclePosition,
    VehiclePositionDeviation,
    Vtg,
)


@dataclass(frozen=True, slots=True)
class Block:
    """One optional memory block identified by a mask bit."""

    field: str
    bit: int
    fmt: str
    build: Callable[[tuple[Any, ...]], Any]

    @property
    def size(self) -> int:
        return calcsize(self.fmt)


def _build(
    cls: type[Any], converters: tuple[Callable[[int], Any] | None, ...] = ()
) -> Callable[[tuple[Any, ...]], Any]:
    names = tuple(item.name for item in fields(cls))

    def build(values: tuple[Any, ...]) -> Any:
        converted: list[Any] = []
        for index, value in enumerate(values):
            converter = converters[index] if index < len(converters) else None
            converted.append(converter(value) if converter is not None else value)
        return cls(**dict(zip(names, converted, strict=True)))

    return build


def _block(
    field: str,
    bit: int,
    fmt: str,
    cls: type[Any],
    converters: tuple[Callable[[int], Any] | None, ...] = (),
) -> Block:
    return Block(field, bit, fmt, _build(cls, converters))


def _sorted(blocks: tuple[Block, ...]) -> tuple[Block, ...]:
    return tuple(sorted(blocks, key=lambda block: block.bit))


NAVIGATION_BLOCKS = _sorted(
    (
        _block("attitude_heading", 0, ">fff", AttitudeHeading),
        _block("attitude_heading_deviation", 1, ">fff", AttitudeHeadingDeviation),
        _block("rt_heave_surge_sway", 2, ">ffff", RealTimeHeaveSurgeSway),
        _block("smart_heave", 3, ">If", SmartHeave),
        _block("heading_roll_pitch_rate", 4, ">fff", HeadingRollPitchRate),
        _block("rotation_rate_vessel_frame", 5, ">fff", RotationRateVesselFrame),
        _block("acceleration_vessel_frame", 6, ">fff", AccelerationVesselFrame),
        _block("position", 7, ">ddBf", Position),
        _block("position_deviation", 8, ">ffff", PositionDeviation),
        _block("speed_geographic_frame", 9, ">fff", SpeedGeographicFrame),
        _block("speed_geographic_frame_deviation", 10, ">fff", SpeedGeographicFrameDeviation),
        _block("current_geographic_frame", 11, ">ff", CurrentGeographicFrame),
        _block("current_geographic_frame_deviation", 12, ">ff", CurrentGeographicFrameDeviation),
        _block("system_date", 13, ">BBH", SystemDate),
        _block("sensor_status", 14, ">II", SensorStatus),
        _block(
            "ins_algorithm_status",
            15,
            ">IIII",
            InsAlgorithmStatus,
            (
                InsAlgorithmStatus1,
                InsAlgorithmStatus2,
                InsAlgorithmStatus3,
                InsAlgorithmStatus4,
            ),
        ),
        _block(
            "ins_system_status",
            16,
            ">III",
            InsSystemStatus,
            (InsSystemStatus1, InsSystemStatus2, InsSystemStatus3),
        ),
        _block("ins_user_status", 17, ">I", InsUserStatus),
        _block("ahrs_algorithm_status", 18, ">I", AhrsAlgorithmStatus),
        _block("ahrs_system_status", 19, ">III", AhrsSystemStatus),
        _block("ahrs_user_status", 20, ">I", AhrsUserStatus),
        _block("heave_surge_sway_speed", 21, ">fff", HeaveSurgeSwaySpeed),
        _block("speed_vessel_frame", 22, ">fff", SpeedVesselFrame),
        _block("acceleration_geographic_frame", 23, ">fff", AccelerationGeographicFrame),
        _block("course_speed_over_ground", 24, ">ff", CourseSpeedOverGround),
        _block("temperatures", 25, ">fff", Temperatures),
        _block("attitude_quaternion", 26, ">ffff", AttitudeQuaternion),
        _block("attitude_quaternion_deviation", 27, ">fff", AttitudeQuaternionDeviation),
        _block("raw_acceleration_vessel_frame", 28, ">fff", RawAccelerationVesselFrame),
        _block(
            "acceleration_vessel_frame_deviation",
            29,
            ">fff",
            AccelerationVesselFrameDeviation,
        ),
        _block(
            "rotation_rate_vessel_frame_deviation",
            30,
            ">fff",
            RotationRateVesselFrameDeviation,
        ),
    )
)

EXTENDED_BLOCKS = _sorted(
    (
        _block(
            "rotation_acceleration_vessel_frame",
            0,
            ">fff",
            RotationAccelerationVesselFrame,
        ),
        _block(
            "rotation_acceleration_vessel_frame_deviation",
            1,
            ">fff",
            RotationAccelerationVesselFrameDeviation,
        ),
        _block("raw_rotation_rate_vessel_frame", 2, ">fff", RawRotationRateVesselFrame),
        _block("vehicle_attitude_heading", 3, ">fff", VehicleAttitudeHeading),
        _block(
            "vehicle_attitude_heading_deviation",
            4,
            ">fff",
            VehicleAttitudeHeadingDeviation,
        ),
        _block("vehicle_position", 5, ">ddBf", VehiclePosition),
        _block("vehicle_position_deviation", 6, ">ffff", VehiclePositionDeviation),
    )
)

EXTERNAL_BLOCKS = _sorted(
    (
        _block("utc", 0, ">IB", Utc),
        _block("gnss1", 1, ">iBBddffffff", Gnss),
        _block("gnss2", 2, ">iBBddffffff", Gnss),
        _block("gnss_manual", 3, ">iBBddffffff", Gnss),
        _block("emlog1", 4, ">iBff", Emlog),
        _block("emlog2", 5, ">iBff", Emlog),
        _block("usbl1", 6, ">iB8sddfffff", Usbl),
        _block("usbl2", 7, ">iB8sddfffff", Usbl),
        _block("usbl3", 8, ">iB8sddfffff", Usbl),
        _block("depth", 9, ">iff", Depth),
        _block("dvl_ground_speed1", 10, ">iBffffffff", DvlGroundSpeed),
        _block("dvl_water_speed1", 11, ">iBfffffff", DvlWaterSpeed),
        _block("sound_velocity", 12, ">if", SoundVelocity),
        _block("dmi", 13, ">ii", Dmi),
        _block("lbl1", 14, ">iB8sddfff", Lbl),
        _block("lbl2", 15, ">iB8sddfff", Lbl),
        _block("lbl3", 16, ">iB8sddfff", Lbl),
        _block("lbl4", 17, ">iB8sddfff", Lbl),
        _block("event_marker_a", 18, ">iBI", EventMarker),
        _block("event_marker_b", 19, ">iBI", EventMarker),
        _block("event_marker_c", 20, ">iBI", EventMarker),
        _block("dvl_ground_speed2", 21, ">iBffffffff", DvlGroundSpeed),
        _block("dvl_water_speed2", 22, ">iBfffffff", DvlWaterSpeed),
        _block("turret_angles", 24, ">ifff", TurretAngles),
        _block("vtg1", 25, ">iBfff", Vtg),
        _block("vtg2", 26, ">iBfff", Vtg),
        _block("log_book", 27, ">iI32s", LogBook),
    )
)
