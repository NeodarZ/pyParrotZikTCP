from parrot_zik import resource_manager
from parrot_zik.model.base import BatteryStates

RECONNECT_FREQUENCY = 5


class ParrotZikBaseInterface(object):
    def __init__(self, indicator):
        self.indicator = indicator
        self.parrot = None
        self.battery_level = ""
        self.battery_state = ""

    def activate(self, manager):
        self.parrot = self.parrot_class(manager)
        self.indicator.info({"info": "Connected to: " + self.parrot.friendly_name})
        self.firmware_version = self.parrot.version
        self.auto_connection = self.parrot.auto_connect
        self.indicator.active_interface = self

    @property
    def parrot_class(self):
        raise NotImplementedError

    def deactivate(self):
        self.parrot = None
        self.battery_level = ""
        self.battery_mode = ""
        self.firmware_version = ""
        self.indicator.active_interface = None
        self.indicator.info({"error": "Lost Connection"})
        self.indicator.reconnect(RECONNECT_FREQUENCY)

    def read_auto_connection(self):
        """
        Return auto connection status.
        """
        try:
            data = {"data": {"auto_connection": self.parrot.auto_connect}}
            self.indicator.info(data)
            return data
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def toggle_auto_connection(self, auto_connection):
        """
        Set auto connection mode. Must be 'true' or 'false'.
        """
        try:
            self.parrot.auto_connect = auto_connection
            return self.read_auto_connection()
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def read_battery(self):
        """
        Return battery level and battery state
        """
        try:
            self.parrot.refresh_battery()
            battery_level = self.parrot.battery_level
            battery_state = self.parrot.battery_state
        except AssertionError as e:
            print(e)
        except resource_manager.DeviceDisconnected:
            self.deactivate()
        else:
            return {"data": {"state": BatteryStates.representation[battery_state], "level": battery_level}}
