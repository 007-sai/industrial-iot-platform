
from unittest.mock import MagicMock

from app.plc_client import PLCClient


def test_read_int_returns_value():
    """Test INT reading without a physical PLC."""

    plc = PLCClient("192.168.100.1")
    plc.client = MagicMock()

    plc.client.db_read.return_value = bytearray([0x00, 0x2A])

    value = plc.read_int(db_number=22, start=0)

    assert value == 42
    plc.client.db_read.assert_called_once_with(22, 0, 2)

def test_read_bool_returns_value():
    """Test BOOL reading without a physical PLC."""

    plc = PLCClient("192.168.100.1")
    plc.client = MagicMock()
    plc.client.db_read.return_value = bytearray([0b00000100])

    value = plc.read_bool(db_number=22, start=0, bit_index=2)

    assert value is True
    plc.client.db_read.assert_called_once_with(22, 0, 1)


def test_read_float_returns_value():
    """Test REAL reading without a physical PLC."""

    import struct

    plc = PLCClient("192.168.100.1")
    plc.client = MagicMock()
    plc.client.db_read.return_value = bytearray(struct.pack(">f", 12.5))

    value = plc.read_float(db_number=22, start=0)

    assert value == 12.5
    plc.client.db_read.assert_called_once_with(22, 0, 4)
