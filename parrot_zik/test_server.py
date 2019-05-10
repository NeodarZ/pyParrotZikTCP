from .interface.version1 import ParrotZikVersion1Interface
from .interface.version2 import ParrotZikVersion2Interface
from . import resource_manager
from . import bluetooth_paired_devices

from . import bluezutils

import sys
import time
import json

from twisted.internet import reactor, protocol

from threading import Thread


REFRESH_FREQUENCY = 60
RECONNECT_FREQUENCY = 5

def toBool(data):
    return data.lower() == "true"

def toBytes(data):
    return str(data).encode('utf-8')

def convert(val):
    constructors = [int, float, str]
    if val.lower() == "true":
        return True
    elif val.lower() == "false":
        return False
    for c in constructors:
        try:
            return c(val)
        except ValueError:
            pass


class TCPParrotZik(protocol.Protocol):
    def api_func_not_found_msg(self, data, setter_functions, getter_functions):
        if data:
            error_msg = "Not implemented yet: " + ' '.join(data) + "\n"
        else:
            error_msg = ""
        error_msg += "Setter implemented:"
        for function in setter_functions:
            error_msg += "\n - " + function
        error_msg += "\nGetter implemented:"
        for function in getter_functions:
            error_msg += "\n - " + function

        return error_msg

    def dataReceived(self, data):
        setter_functions = {
            'auto_connection':
            self.factory.active_interface.toggle_auto_connection,
            'sound_effect_room':
            self.factory.active_interface.toggle_sound_effect_room,
            'flight_mode':
            self.factory.active_interface.toggle_flight_mode,
            'sound_effect_room_status':
            self.factory.active_interface.toggle_sound_effect_room_enabled,
            'sound_effect_angle':
            self.factory.active_interface.toggle_sound_effect_angle,
            'noise_control':
            self.factory.active_interface.toggle_noise_control,
            'head_detection':
            self.factory.active_interface.toggle_head_detection,
        }

        getter_functions = {
            'auto_connection':
            self.factory.active_interface.read_auto_connection,
            'read_battery':
            self.factory.active_interface.read_battery,
            'flight_mode':
            self.factory.active_interface.read_flight_mode,
            'sound_effect_room':
            self.factory.active_interface.read_sound_effect_room,
            'sound_effect_room_status':
            self.factory.active_interface.read_sound_effect_room_enabled,
            'sound_effect_angle':
            self.factory.active_interface.read_sound_effect_angle,
            'noise_control':
            self.factory.active_interface.read_noise_control,
            'head_detection':
            self.factory.active_interface.read_head_detection,

        }
        data = list(data.decode('utf-8').split())
        if len(data) >= 2:
            try:
                setter = setter_functions[data[0]]
                self.transport.write(toBytes(setter(convert(data[1]))))
            except KeyError:
                self.transport.write(toBytes(self.api_func_not_found_msg(data, setter_functions, getter_functions)))
        else:
            if data[0] == "help":
                self.transport.write(toBytes(self.api_func_not_found_msg(None, setter_functions, getter_functions)))
            else:
                try:
                    getter = getter_functions[data[0]]
                    self.transport.write(toBytes(getter()))
                except KeyError:
                    self.transport.write(toBytes(self.api_func_not_found_msg(data, setter_functions, getter_functions)))

class TCPParrotZikFactory(protocol.ServerFactory):
    protocol = TCPParrotZik

    def __init__(self, active_interface=None):
        self.active_interface = active_interface

class ParrotZik(protocol.Protocol):
    def __init__(self):
        self.version_1_interface = ParrotZikVersion1Interface(self)
        self.version_2_interface = ParrotZikVersion2Interface(self)
        self.active_interface = None

    def reconnect(self, frequency):
        while True:
            self.info({'info': 'Trying to connect'})
            try:
                manager = bluetooth_paired_devices.connect()
            except bluetooth_paired_devices.BluetoothIsNotOn:
                self.sinfo({'error': 'Bluetooth is turned off'})
            except bluetooth_paired_devices.DeviceNotFound:
                self.sinfo({'error': 'Parrot Zik not found'})
            except bluetooth_paired_devices.DeviceNotPaired:
                self.sinfo({'error': 'Parrot Zik not paired'})
            except bluetooth_paired_devices.DeviceNotConnected:
                self.sinfo({'error': 'Parrot Zik not connected'})
            except bluetooth_paired_devices.ConnectionFailure:
                self.sinfo({'error': 'Failed to connect'})
            except bluezutils.BluetoothAdaptaterNotFound:
                self.sinfo({'error': 'Adaptateur not found'})
            else:
                if manager.api_version.startswith('1'):
                    interface = self.version_1_interface
                else:
                    interface = self.version_2_interface
                try:
                    interface.activate(manager)
                    reactor.listenTCP(8000, TCPParrotZikFactory(self.active_interface))
                    Thread(target=reactor.run, args=(False,)).start()
                except resource_manager.DeviceDisconnected:
                    interface.deactivate()
                    pass
                else:
                    self.autorefresh(REFRESH_FREQUENCY)
                    sys.exit()
            time.sleep(frequency)

    def info(self, message):
        print(message)

    def sinfo(self, message):
        self.info(message)
        with open("/tmp/parrotZikBattery", "w") as file:
            file.write(json.dumps(message))

    def autorefresh(self, frequency):
        while True:
            if self.active_interface:
                self.sinfo(self.active_interface.read_battery())
                #self.active_interface.toggle_sound_effect_room('silent')
                #self.active_interface._read_sound_effect_room_enabled()
                #self.active_interface.toggle_sound_effect_room_enabled(True)
                #self.active_interface._read_sound_effect_angle()
                #self.active_interface._read_noise_cancelation()
                #self.active_interface.toggle_head_detection(True)
                #self.active_interface._read_head_detection()
                #mode  = self.active_interface.noise_control_types['STREET_MODE_MAX']
                #self.active_interface.toggle_noise_cancelation(mode)
                #print(self.active_interface._read_sound_effect_room())
            else:
                self.reconnect(RECONNECT_FREQUENCY)
            time.sleep(frequency)

    @classmethod
    def main(cls):
        try:
            indicator = cls()
            cls.reconnect(indicator, RECONNECT_FREQUENCY)
        except KeyboardInterrupt:
            pass

parrot = ParrotZik()
parrot.main()
