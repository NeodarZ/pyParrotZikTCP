from parrot_zik import resource_manager
from parrot_zik.interface.base import ParrotZikBaseInterface
from parrot_zik.model.version1 import ParrotZikVersion1


class ParrotZikVersion1Interface(ParrotZikBaseInterface):
    parrot_class = ParrotZikVersion1

    def __init__(self, indicator):
        super(ParrotZikVersion1Interface, self).__init__(indicator)

    def activate(self, manager):
        super(ParrotZikVersion1Interface, self).activate(manager)

    def deactivate(self):
        super(ParrotZikVersion1Interface, self).deactivate()

    def toggle_noise_cancelation(self, noise_cancelation):
        """
        Define noise cancelation mode.
        """
        try:
            self.parrot.cancel_noise = noise_cancelation
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def toggle_lou_reed_mode(self, lou_reed_mode):
        """
        Define lou reed mode.
        """
        try:
            self.parrot.lou_reed_mode = lou_reed_mode
        except resource_manager.DeviceDisconnected:
            self.deactivate()

    def toggle_parrot_concert_hall(self, parrot_concert_hall):
        """
        Define parrot concert hall
        """
        try:
            self.parrot.concert_hall = parrot_concert_hall
        except resource_manager.DeviceDisconnected:
            self.deactivate()
