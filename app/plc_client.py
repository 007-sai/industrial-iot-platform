import snap7


class PLCClient:
    """Handles communication with a Siemens S7 PLC."""

    def __init__(self, ip_address: str, rack: int = 0, slot: int = 1):
        self.ip_address = ip_address
        self.rack = rack
        self.slot = slot
        self.client = snap7.Client()

    def connect(self) -> bool:
        """Connect to the Siemens PLC."""

        try:
            self.client.connect(
                self.ip_address,
                self.rack,
                self.slot,
            )

            return self.client.get_connected()

        except Exception as error:
            print(f"PLC connection failed: {error}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the PLC."""

        if self.client.get_connected():
            self.client.disconnect()

    def is_connected(self) -> bool:
        """Return the current PLC connection status."""

        return self.client.get_connected()
