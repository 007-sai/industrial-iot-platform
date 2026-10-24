import snap7
from snap7.util import get_int, get_bool, get_real, set_int, set_bool, set_real

class PLCClient:
    def __init__(self, ip: str, rack: int = 0, slot: int = 1):
        self.ip = ip
        self.rack = rack
        self.slot = slot
        self.client = snap7.client.Client()

    def connect(self) -> bool:
        try:
            self.client.connect(self.ip, self.rack, self.slot)
            return self.client.get_connected()
        except Exception:
            return False

    def disconnect(self):
        try:
            if self.client.get_connected():
                self.client.disconnect()
        except Exception:
            pass

    def read_int(self, db_number: int, start: int) -> int:
        data = self.client.db_read(db_number, start, 2)
        return get_int(data, 0)

    def read_bool(self, db_number: int, start: int, bit_index: int = 0) -> bool:
        data = self.client.db_read(db_number, start, 1)
        return get_bool(data, 0, bit_index)

    def read_float(self, db_number: int, start: int) -> float:
        data = self.client.db_read(db_number, start, 4)
        return get_real(data, 0)

    def write_int(self, db_number: int, start: int, value: int):
        data = bytearray(2)
        set_int(data, 0, value)
        self.client.db_write(db_number, start, data)

    def write_bool(self, db_number: int, start: int, bit_index: int, value: bool):
        data = self.client.db_read(db_number, start, 1)
        set_bool(data, 0, bit_index, value)
        self.client.db_write(db_number, start, data)

    def write_float(self, db_number: int, start: int, value: float):
        data = bytearray(4)
        set_real(data, 0, value)
        self.client.db_write(db_number, start, data)