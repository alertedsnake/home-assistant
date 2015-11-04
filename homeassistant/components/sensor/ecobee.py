"""
homeassistant.components.sensors.ecobee
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Adds support for Ecobee thermostat sensors and remote sensors.

In configuration.yaml:

sensor:
    platform: ecobee

"""
import logging

import homeassistant.components.ecobee as ecobee
from homeassistant.const import (TEMP_CELCIUS, TEMP_FAHRENHEIT)
from homeassistant.helpers.entity import Entity

_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Sets up the nest thermostat. """

    _LOGGER.warning("Setting up...")

    eapi = ecobee.CLIENT
    if not eapi:
        _LOGGER.error("No client yet?")
        return False

    devs = []
    for thermostat in eapi.list_thermostats():
        for sensor in thermostat.list_sensors():
            _LOGGER.warning("setting up sensor {}/{}".format(thermostat.id, sensor.id))
            if sensor._get_capability('temperature'):
                devs.append(EcobeeTemperature(sensor))
            if sensor._get_capability('humidity'):
                devs.append(EcobeeHumidity(sensor))
            if sensor._get_capability('occupancy'):
                devs.append(EcobeeOccupancy(sensor))

    add_devices(devs)


class EcobeeSensorBase(Entity):
    """Ecobee sensor base class"""

    def __init__(self, device):
        self.device = device
        _LOGGER.info("Setting up {} {}/{}".format(self.__class__.__name__, self._thermostat.id, self.device.id))

    @property
    def _thermostat(self):
        return self.device.thermostat

    @property
    def unique_id(self):
        """ Returns a unique id. """
        return "{}/{}/{}".format(self.__class__.__name__, self._thermostat.id, self.device.id)

    @property
    def should_poll(self):
        """ False because we will push our own state to HA when changed. """
        return False


class EcobeeTemperature(EcobeeSensorBase):
    """Ecobee temperature sensor"""

    @property
    def name(self):
        """ Returns the name of the device. """
        return "{}: {}".format(self.device.name, 'Temperature')

    @property
    def unit_of_measurement(self):
        if self._thermostat.settings.get('useCelsius', False):
            return TEMP_CELCIUS
        return TEMP_FAHRENHEIT

    @property
    def state(self):
        return self.device.temperature

    @property
    def state_attributes(self):
        """ Returns the state attributes. """
        return {'temperature': self.state}


class EcobeeHumidity(EcobeeSensorBase):
    """Ecobee humidity sensor, usually only on thermostat unit"""

    @property
    def name(self):
        """ Returns the name of the device. """
        return "{}: {}".format(self.device.name, 'Humidity')

    @property
    def unit_of_measurement(self):
        return "%"

    @property
    def state(self):
        return self.device.humidity

    @property
    def state_attributes(self):
        """ Returns the state attributes. """
        return {'humidity': self.state}


class EcobeeOccupancy(EcobeeSensorBase):
    """Ecobee occupancy sensor"""

    @property
    def name(self):
        """ Returns the name of the device. """
        return "{}: {}".format(self.device.name, 'Occupancy')

    @property
    def state(self):
        return str(self.device.occupancy)

    @property
    def unit_of_measurement(self):
        return ""

    @property
    def state_attributes(self):
        """ Returns the state attributes. """
        return {'occupancy': self.state}

