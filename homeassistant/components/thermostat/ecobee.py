"""
homeassistant.components.thermostat.ecobee
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Adds support for Ecobee thermostats.

In configuration.yaml:

thermostat:
    platform: ecobee

"""
import logging

import homeassistant.components.ecobee as ecobee
from homeassistant.components.thermostat import (ThermostatDevice, STATE_COOL,
                                                 STATE_IDLE, STATE_HEAT)
from homeassistant.const import (TEMP_CELCIUS, TEMP_FAHRENHEIT, STATE_ON, STATE_OFF)
from homeassistant.helpers.temperature import convert


_LOGGER = logging.getLogger(__name__)


# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices, discovery_info=None):
    """ Sets up the nest thermostat. """

    _LOGGER.warning("Setting up thermostat.ecobee")

    eapi = ecobee.CLIENT
    if not eapi:
        _LOGGER.info("No client yet?")
        return


    devs = []
    for thermostat in eapi.list_thermostats():
        _LOGGER.info("Adding ecobee thermostat {}".format(thermostat.id))
        devs.append(EcobeeThermostat(thermostat))

    add_devices(devs)


class EcobeeThermostat(ThermostatDevice):
    """ Represents an Ecobee thermostat. """

    def __init__(self, device):
        self.device = device
        _LOGGER.info("Setting up thermostat {}".format(self.device.id))

    @property
    def _eapi(self):
        return self.device._eapi

    @property
    def should_poll(self):
        return True

    @property
    def name(self):
        """ Returns the name of the nest, if any. """
        return self.device.name.capitalize()

    @property
    def unit_of_measurement(self):
        """Override.  Unit of measurement this thermostat expresses itself in. """
        if self.device.settings.get('useCelsius', False):
            return TEMP_CELCIUS
        return TEMP_FAHRENHEIT

    @property
    def min_temp(self):
        """ Return minimum temperature. """
        val = 0
        if self.device.settings:
            if self.mode == 'heat' or (self.mode == 'auto' and self.is_heating):
                val = self.device.settings['heatMinTemp'] / 10.0
            elif self.mode == 'cool' or (self.mode == 'auto' and self.is_cooling):
                val = self.device.settings['coolMinTemp'] / 10.0

        return convert(val, self.unit_of_measurement, self.unit_of_measurement)

    @property
    def max_temp(self):
        """ Return maxmum temperature. """
        val = 120
        if self.device.settings:
            if self.mode == 'heat' or (self.mode == 'auto' and self.is_heating):
                val = self.device.settings['heatMaxTemp'] / 10.0
            elif self.mode == 'cool' or (self.mode == 'auto' and self.is_cooling):
                val = self.device.settings['coolMaxTemp'] / 10.0

        return convert(val, self.unit_of_measurement, self.unit_of_measurement)

    @property
    def device_state_attributes(self):
        """Override.  Returns device specific state attributes. """

        return {
            "fan":      self.fan_mode,
            "mode":     self.mode,
            "temperature":  self.current_temperature,
        }

    @property
    def operation(self):
        """Override.  Returns current operation ie. heat, cool, idle """
        if self.is_heating:
            return STATE_HEAT
        if self.is_cooling:
            return STATE_COOL
        return STATE_IDLE


    @property
    def mode(self):
        return self.device.settings.get('hvacMode')

    @property
    def fan_mode(self):
        if self.is_fan:
            return STATE_ON
        return STATE_OFF

    @property
    def current_temperature(self):
        """Override.
        Return current temperature."""

        if not self.device.runtime:
            return None
        return self.device.runtime.get('actualTemperature') / 10.0

    @property
    def target_temperature(self):
        """Override.
        Returns the temperature we try to reach. """

        if not self.device.runtime:
            return None
        if self.mode == 'heat' or (self.mode == 'auto' and self.is_heating):
            return self.device.runtime.get('desiredHeat') / 10.0
        if self.mode == 'cool' or (self.mode == 'auto' and self.is_cooling):
            return self.device.runtime.get('desiredCool') / 10.0
        return None

    @property
    def current_humidity(self):
        return self.device.runtime.get('actualHumidity')

    @property
    def target_humidity(self):
        return self.device.runtime.get('desiredHumidity')

    @property
    def is_fan(self):
        return 'fan' in self.device.running

    @property
    def is_heating(self):
        for key in ('heatPump', 'heatPump2', 'heatPump3', 'auxHeat1', 'auxHeat2', 'auxHeat3'):
            if key in self.device.running:
                return True
        return False

    @property
    def is_cooling(self):
        for key in ('compCool1', 'compCool2'):
            if key in self.device.running:
                return True
        return False


    def update(self):
        """keep up to date"""

#        if self._eapi.authentication_required:
#            _LOGGER.info("Thermostat {} authentication required".format(self.id))
#            self._eapi.authorize_finish()
#            return
        _LOGGER.info("Polling thermostat {}".format(self.device.id))

        # read thermostat status
        self.device.update()


