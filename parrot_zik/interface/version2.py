import functools

from parrot_zik import resource_manager
from parrot_zik.interface.base import ParrotZikBaseInterface
from parrot_zik.model.version2 import ParrotZikVersion2
from parrot_zik.model.version2 import NoiseControlTypes
from parrot_zik.model.version2 import Rooms
from parrot_zik.model.version2 import Angles


class ParrotZikVersion2Interface(ParrotZikBaseInterface):
    parrot_class = ParrotZikVersion2

    def __init__(self, indicator):
        super(ParrotZikVersion2Interface, self).__init__(indicator)
        self.noise_control_types = NoiseControlTypes.representation
        self.rooms_types = Rooms.representation
        self.angles = Angles.representation

    def activate(self, manager):
        super(ParrotZikVersion2Interface, self).activate(manager)

    def deactivate(self):
        super(ParrotZikVersion2Interface, self).deactivate()

    def toggle_flight_mode(self, flight_mode):
        try:
            #self.parrot.flight_mode = flight_mode
            warning = {'warning': 'Sorry for this moment this function is disable because you need to connect your system on headset with NFC to disable flight mode.'}
            self.indicator.info(warning)
            return warning
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def read_flight_mode(self):
        try:
            data = {'data': {'flight_mode': self.parrot.flight_mode}}
            self.indicator.info(data)
            return data
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def toggle_sound_effect_room(self, room):
        """
        Define ambiance room. Muse be one of the following room:
        'concert', 'jazz', 'living', 'silent'.
        """
        try:
            if room in self.rooms_types:
                self.parrot.room = room
                data = {'data': {'sound_effect_room': self.parrot.room}}
                self.indicator.info(data)
                return data
            else:
                data = {'error': "'" + room + "' is not a correct room name"}
                self.indicator.info(data)
                return data
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def read_sound_effect_room(self):
        """
        Return current ambiance room value.
        """
        try:
            data = {'data': {'sound_effect_type': self.parrot.room}}
            self.indicator.info(data)
            return data
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def toggle_sound_effect_room_enabled(self, sound_effect):
        """
        Enable or disable the ambiance room. Must be 'true' or 'false'.
        """
        try:
            self.parrot.sound_effect = sound_effect
            return self.read_sound_effect_room_enabled()
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def read_sound_effect_room_enabled(self):
        """
        Return current ambiance room status.
        """
        try:
            data = {'data': {'sound_effect_state': self.parrot.sound_effect}}
            self.indicator.info(data)
            return data
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def toggle_sound_effect_angle(self, angle):
        """
        Define angle, must be one of the following interger:
        30, 60, 90, 120, 150, 180
        """
        try:
            if angle in self.angles:
                self.parrot.angle = angle
                return self.read_sound_effect_angle()
            else:
                data = {'error': "'"+str(angle)+"' is not an accepted angle"}
                self.indicator.info(data)
                return data
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def read_sound_effect_angle(self):
        """
        Return current sound angle.
        """
        try:
            data = {'data': {'sound_effec_angle': self.parrot.angle}}
            self.indicator.info(data)
            return data
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def toggle_noise_control(self, noise_control):
        """
        Define noise cancelation mode. Must be one of this value:
        'NOISE_CONTROL_MAX': Noise reduction maximum
        'NOISE_CONTROL_ON': Noise reduction enable
        'NOISE_CONTROL_OFF': Noise reduction disable
        'STREET_MODE': Street mode
        'STREET_MODE_MAX': Street mode maximum
        """
        try:
            for noise_control_type, noise_control_value in self.noise_control_types.items():
                if noise_control == noise_control_type:
                    self.parrot.noise_control = noise_control_value
            return self.read_noise_control()
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def read_noise_control(self):
        """
        Return current noise cancelation mode.
        """
        try:
            active_noise_control = self.parrot.noise_control
            for noise_control_type, noise_control in self.noise_control_types.items():
                if active_noise_control == noise_control:
                    data = {'data': {'noise_control': noise_control_type}}
                    self.indicator.info(data)
                    return data
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def toggle_head_detection(self, head_detection):
        """
        Enable or disable head detection. Must be 'true' or 'false'.
        """
        try:
            self.parrot.head_detection = head_detection
            return self.read_head_detection()
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def read_head_detection(self):
        """
        Return head detector status.
        """
        try:
            data = {'data': {'head_detection': self.parrot.head_detection}}
            self.indicator.info(data)
            return data
        except resource_manager.DeviceDisconnected:
            self.deactivate()
