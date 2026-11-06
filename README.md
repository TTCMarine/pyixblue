# pyixblue

[![PyPI version](https://img.shields.io/pypi/v/pyixblue.svg)](https://pypi.org/project/pyixblue/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyixblue.svg)](https://pypi.org/project/pyixblue/)
[![Docs](https://img.shields.io/badge/docs-readthedocs-blue.svg)](https://pyixblue.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/TTCMarine/pyixblue/blob/main/LICENSE)

Python parser for the iXblue stdbin output protocol (versions 2 through 5).

stdbin is the binary navigation output of iXblue inertial systems. This package
reassembles and decodes those frames. It does not open a socket or a serial
port; pass in the bytes you receive over UDP, TCP, or serial.

The block layout and checksum follow the MIT-licensed
[ixblue_stdbin_decoder](https://github.com/ixblue/ixblue_stdbin_decoder).

## Install

From [PyPI](https://pypi.org/project/pyixblue/):

```sh
pip install pyixblue
```

For development, from a checkout (installs the package in editable mode along
with the test dependencies):

```sh
uv sync
```

## Usage

```python
from pyixblue import StdBinDecoder

decoder = StdBinDecoder()
decoder.add_new_data(chunk)  # bytes-like; a chunk may be a partial frame
while decoder.parse_next_frame():  # False when more bytes are needed
    header = decoder.last_header
    if header.message_type == "nav":
        nav = decoder.last_nav  # missing blocks are None
        if nav.position is not None:
            print(nav.position.latitude_deg, nav.position.longitude_deg)
    else:
        payload = decoder.last_answer
```

`parse_next_frame` raises `StdBinError` when a frame is recognized but its
protocol version or checksum is invalid. The decoder drops the bad version
byte, or the whole frame after a bad checksum, so the next call can resync.

Navigation, extended-navigation, and external-sensor blocks are present only
when their mask bit is set. INS algorithm and system status words are `IntFlag`
values (`1 << bit`), so they compare equal to the raw integer:

```python
from pyixblue.models import InsAlgorithmStatus1

if nav.ins_algorithm_status is not None:
    status = nav.ins_algorithm_status.status1
    if InsAlgorithmStatus1.NAVIGATION in status:
        print(hex(status))
```

## Protocol

Supported output frames:

| Kind | Magic | Versions |
| --- | --- | --- |
| Navigation | `IX` | 2, 3, 4, 5 |
| Answer | `AN` | 3, 4, 5 |

Multi-byte fields are big-endian. The checksum is the low 32 bits of the sum of
every preceding byte, stored as a big-endian `uint32`.

Version 3 adds the extended-navigation mask. Versions 4 and 5 add the
navigation-data size. The header also keeps the frame `counter`, which the
reference C++ header discards.

## License

MIT. Sample frames under `tests/fixtures/` were converted from the
ixblue_stdbin_decoder test logs (MIT, Copyright (c) 2019 iXblue SAS).
