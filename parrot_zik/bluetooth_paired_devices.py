import sys
import re
from subprocess import Popen, PIPE, STDOUT

from .resource_manager import GenericResourceManager

import dbus
from . import bluezutils

if sys.platform == "darwin":
    from binplist import binplist
    import lightblue
else:
    import bluetooth
    if sys.platform in ['linux', 'linux2']:
        import dbus
    if sys.platform == "win32":
        import _winreg


p = re.compile('90:03:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}|'
               'A0:14:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}:[0-9A-Fa-f]{2}')


class BluetoothDeviceManager(object):
    def is_bluetooth_on(self):
        raise NotImplementedError

    def get_mac(self):
        raise NotImplementedError


class BluezBluetoothDeviceManager(BluetoothDeviceManager):
    def is_bluetooth_on(self):
        bus = dbus.SystemBus()
        adapter_path = bluezutils.find_adapter().object_path
        adapter = dbus.Interface(bus.get_object("org.bluez", adapter_path), "org.freedesktop.DBus.Properties")

        return adapter.Get("org.bluez.Adapter1", "Powered")


    def get_mac(self):
        addresses = []
        try:
            bus = dbus.SystemBus()
            adapter = bluezutils.find_adapter()
            adapter_path = adapter.object_path

            om = dbus.Interface(bus.get_object("org.bluez", "/"),
                    "org.freedesktop.DBus.ObjectManager")
            objects = om.GetManagedObjects()

            for path, interfaces in objects.items():
                if "org.bluez.Device1" not in interfaces:
                    continue
                properties = interfaces["org.bluez.Device1"]
                if properties["Adapter"] != adapter_path:
                    continue;
                addresses.append(properties)
        except dbus.exceptions.DBusException:
            pass
        else:
            try:
                res = next(item for item in addresses if re.search(p, item["Address"]))
            except StopIteration:
                raise DeviceNotFound
            if res['Connected']:
                return res['Address']
            elif not res['Paired']:
                raise DeviceNotPaired
            else:
                raise DeviceNotConnected


class BluetoothCmdDeviceManager(BluetoothDeviceManager):
    def is_bluetooth_on(self):
        return True

    def get_mac(self):
        pipe = Popen(['bluetoothctl'], stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        res = str(pipe.communicate("exit".encode("UTF-8")))
        if len(res) > 0 and res[0]:
            match = p.search(res[0])
            if match:
                return match.group(0)
        raise DeviceNotConnected


def get_parrot_zik_mac_linux():
    bluez_manager = BluezBluetoothDeviceManager()
    try:
        if bluez_manager.is_bluetooth_on():
            return bluez_manager.get_mac()
        else:
            raise BluetoothIsNotOn
    except dbus.exceptions.DBusException:
        raise BluetoothIsNotOn
    except OSError as e:
        if e.errno == 2:
            bluetoothcmd_manager = BluetoothCmdDeviceManager()
            return bluetoothcmd_manager.get_mac()


def get_parrot_zik_mac_darwin():
    fd = open("/Library/Preferences/com.apple.Bluetooth.plist", "rb")
    plist = binplist.BinaryPlist(file_obj=fd)
    parsed_plist = plist.Parse()
    try:
        for mac in parsed_plist['PairedDevices']:
            if p.match(mac.replace("-", ":")):
                return mac.replace("-", ":")
        else:
            raise DeviceNotConnected
    except Exception:
        pass


def get_parrot_zik_mac_windows():
    aReg = _winreg.ConnectRegistry(None, _winreg.HKEY_LOCAL_MACHINE)
    aKey = _winreg.OpenKey(
        aReg, 'SYSTEM\CurrentControlSet\Services\
        BTHPORT\Parameters\Devices')
    for i in range(10):
        try:
            asubkey_name = _winreg.EnumKey(aKey, i)
            mac = ':'.join(asubkey_name[i:i+2] for i in range(0, 12, 2))
            res = p.findall(mac)
            if len(res) > 0:
                return res[0]
            else:
                raise DeviceNotConnected
        except EnvironmentError:
            pass


if sys.platform in ['linux', 'linux2']:
    get_parrot_zik_mac = get_parrot_zik_mac_linux
elif sys.platform == 'darwin':
    get_parrot_zik_mac = get_parrot_zik_mac_darwin
elif sys.platform == 'win32':
    get_parrot_zik_mac = get_parrot_zik_mac_windows
else:
    raise AssertionError('Platform not supported')


def connect():
    mac = get_parrot_zik_mac()
    if sys.platform == "darwin":
        service_matches = lightblue.findservices(
            name="Parrot RFcomm service", addr=mac)
    else:
        uuids = ["0ef0f502-f0ee-46c9-986c-54ed027807fb",
                 "8B6814D3-6CE7-4498-9700-9312C1711F63",
                 "8B6814D3-6CE7-4498-9700-9312C1711F64"]
        service_matches = []
        for uuid in uuids:
            try:
                service_matches = bluetooth.find_service(uuid=uuid, address=mac)
            except bluetooth.btcommon.BluetoothError:
                pass
            if service_matches:
                break

    if len(service_matches) == 0:
        raise ConnectionFailure
    first_match = service_matches[0]

    if sys.platform == "darwin":
        host = first_match[0]
        port = first_match[1]
        sock = lightblue.socket()
    else:
        port = first_match["port"]
        host = first_match["host"]
        sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    try:
        sock.connect((host, port))
    except bluetooth.btcommon.BluetoothError:
        raise ConnectionFailure

    sock.send('\x00\x03\x00')
    sock.recv(1024)
    return GenericResourceManager(sock)


class DeviceNotConnected(Exception):
    pass


class DeviceNotPaired(Exception):
    pass


class DeviceNotFound(Exception):
    pass

class ConnectionFailure(Exception):
    pass


class BluetoothIsNotOn(Exception):
    pass
