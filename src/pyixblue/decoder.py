"""Streaming parser for iXblue stdbin output frames."""

import struct
from collections.abc import Iterable

from pyixblue.blocks import EXTENDED_BLOCKS, EXTERNAL_BLOCKS, NAVIGATION_BLOCKS, Block
from pyixblue.errors import StdBinError
from pyixblue.models import MessageType, NavData, NavHeader

_NAV_HEADER_SIZE = {2: 21, 3: 25, 4: 27, 5: 27}
_ANSWER_HEADER_SIZE = 5
_CHECKSUM_SIZE = 4
_IX = b"IX"
_AN = b"AN"


class StdBinDecoder:
    """Reassemble and decode stdbin frames from an arbitrary byte stream.

    Feed whatever arrives from the socket or serial port. ``parse_next_frame``
    returns true once a whole frame is available. A bad protocol version drops
    one byte and raises; a bad checksum drops that frame and raises. The next
    call continues with whatever is still buffered.
    """

    def __init__(self) -> None:
        self._buffer = bytearray()
        self.last_header: NavHeader | None = None
        self.last_nav = NavData()
        self.last_answer = b""

    @property
    def buffered_size(self) -> int:
        """Bytes still waiting to be parsed."""
        return len(self._buffer)

    def add_new_data(self, data: bytes | bytearray | memoryview) -> None:
        """Append bytes. ``data`` may be only part of a frame."""
        if isinstance(data, str):
            raise TypeError("stdbin data must be bytes, not str")
        self._buffer.extend(data)

    def parse_next_frame(self) -> bool:
        """Parse one frame from the internal buffer.

        Returns false when more bytes are needed. Raises ``StdBinError`` when
        a frame header is recognized but the version or checksum is invalid.
        """
        if not self._find_header():
            return False

        header = self._parse_header()
        if len(self._buffer) < header.telegram_size:
            return False
        self._compare_checksum(header.telegram_size)

        if header.message_type is MessageType.NAV:
            self.last_nav = self._parse_nav(header)
            self.last_answer = b""
        else:
            payload_end = header.telegram_size - _CHECKSUM_SIZE
            self.last_answer = bytes(self._buffer[_ANSWER_HEADER_SIZE:payload_end])

        self.last_header = header
        del self._buffer[: header.telegram_size]
        return True

    def _find_header(self) -> bool:
        """Drop leading junk until a supported header is buffered, or wait."""
        while len(self._buffer) > 3:
            version = self._buffer[2]
            magic = bytes(self._buffer[0:2])
            if magic == _IX:
                header_size = _NAV_HEADER_SIZE.get(version)
                if header_size is None:
                    del self._buffer[0]
                    raise StdBinError("Unhandled protocol version")
                return len(self._buffer) >= header_size
            if magic == _AN:
                if 3 <= version <= 5:
                    return len(self._buffer) >= _ANSWER_HEADER_SIZE
                del self._buffer[0]
                raise StdBinError("Unhandled protocol version for an answer")
            del self._buffer[0]
        return False

    def _parse_header(self) -> NavHeader:
        magic = bytes(self._buffer[0:2])
        version = self._buffer[2]
        if magic == _IX:
            if version not in _NAV_HEADER_SIZE:
                raise StdBinError(
                    "Unknown protocol version. Supported protocol are version 2->5"
                )
            if version == 2:
                nav_mask, external_mask, telegram_size, validity, counter = struct.unpack_from(
                    ">IIHII", self._buffer, 3
                )
                extended_mask = None
                navigation_size = None
            elif version == 3:
                (
                    nav_mask,
                    extended_mask,
                    external_mask,
                    telegram_size,
                    validity,
                    counter,
                ) = struct.unpack_from(">IIIHII", self._buffer, 3)
                navigation_size = None
            else:
                (
                    nav_mask,
                    extended_mask,
                    external_mask,
                    navigation_size,
                    telegram_size,
                    validity,
                    counter,
                ) = struct.unpack_from(">IIIHHII", self._buffer, 3)
            return NavHeader(
                message_type=MessageType.NAV,
                protocol_version=version,
                telegram_size=telegram_size,
                navigation_bit_mask=nav_mask,
                extended_navigation_bit_mask=extended_mask,
                external_sensor_bit_mask=external_mask,
                navigation_size=navigation_size,
                validity_time_100us=validity,
                counter=counter,
            )

        if magic == _AN:
            telegram_size = struct.unpack_from(">H", self._buffer, 3)[0]
            return NavHeader(
                message_type=MessageType.ANSWER,
                protocol_version=version,
                telegram_size=telegram_size,
            )

        raise StdBinError("Incorrect frame header, expected 'I', 'X' or 'A', 'N'")

    def _compare_checksum(self, telegram_size: int) -> None:
        if telegram_size < _CHECKSUM_SIZE:
            del self._buffer[0]
            raise StdBinError("Telegram is smaller than a checksum")
        checksum_at = telegram_size - _CHECKSUM_SIZE
        received = struct.unpack_from(">I", self._buffer, checksum_at)[0]
        computed = sum(self._buffer[:checksum_at]) & 0xFFFFFFFF
        if received != computed:
            del self._buffer[:telegram_size]
            raise StdBinError(
                f"Bad checksum. Received: 0x{received:x}, computed: 0x{computed:x}"
            )

    def _parse_nav(self, header: NavHeader) -> NavData:
        if header.navigation_bit_mask is None or header.external_sensor_bit_mask is None:
            raise StdBinError("Navigation frame is missing its bit masks")
        present: dict[str, object] = {}
        offset = _NAV_HEADER_SIZE[header.protocol_version]
        offset = self._apply_blocks(offset, header.navigation_bit_mask, NAVIGATION_BLOCKS, present)
        if header.extended_navigation_bit_mask is not None:
            offset = self._apply_blocks(
                offset,
                header.extended_navigation_bit_mask,
                EXTENDED_BLOCKS,
                present,
            )
        self._apply_blocks(offset, header.external_sensor_bit_mask, EXTERNAL_BLOCKS, present)
        return NavData(**present)

    def _apply_blocks(
        self,
        offset: int,
        mask: int,
        blocks: Iterable[Block],
        present: dict[str, object],
    ) -> int:
        buffer = self._buffer
        buffer_size = len(buffer)
        for block in blocks:
            if (mask >> block.bit) & 1 == 0:
                continue
            if buffer_size - offset < block.size:
                raise StdBinError("Not enough bytes in buffer to parse this memory block")
            present[block.field] = block.build(*block.struct.unpack_from(buffer, offset))
            offset += block.size
        return offset
