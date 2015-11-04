"""
homeassistant.components.ecobee
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Connects to ecobee.com, keeps the connection object.

You will need to go to ecobee.com, login, and create a new device in
the "Developer" section.  Grab the API key and add it to...

In configuration.yaml:

ecobee:
    api_key: [your key]

When you next start homeassistant, watch the logfile for the ecobee
message about entering your pin on the website.  Grab the pin, go to
ecobee.com and in the 'my apps' section in the menu, add a new
application, and when asked to enter an authorization code, enter the
4-character pin from the logfile.

"""

import logging

from homeassistant import bootstrap
from homeassistant.const import (
    EVENT_HOMEASSISTANT_START,
    EVENT_PLATFORM_DISCOVERED, CONF_API_KEY,
    ATTR_SERVICE, ATTR_DISCOVERED)
from homeassistant.helpers import validate_config
from homeassistant.loader import get_component


DOMAIN = "ecobee"
DEPENDENCIES = []
#REQUIREMENTS = ['python-ecobee==1.0.0']

DISCOVER_THERMOSTATS = "ecobee.thermostats"
DISCOVER_SENSORS     = "ecobee.sensors"
COMMAND_CLASS_THERMOSTAT         = "thermostat"
COMMAND_CLASS_SENSOR_TEMPERATURE = "temperature"
COMMAND_CLASS_SENSOR_HUMIDITY    = "humidity"
COMMAND_CLASS_SENSOR_OCCUPANCY   = "occupancy"

ATTR_NODE_ID = "node_id"
ATTR_VALUE_ID = "value_id"

DISCOVERY_COMPONENTS = [
    ('thermostat', DISCOVER_THERMOSTATS, [COMMAND_CLASS_THERMOSTAT]),
    ('sensor',     DISCOVER_SENSORS, [
            COMMAND_CLASS_SENSOR_TEMPERATURE,
            COMMAND_CLASS_SENSOR_HUMIDITY,
            COMMAND_CLASS_SENSOR_OCCUPANCY,
        ]
    )
]

CLIENT = None

def setup(hass, config):
    """ Sets up the Wink component. """
    global CLIENT

    logger = logging.getLogger(__name__)

    if not validate_config(config, {DOMAIN: [CONF_API_KEY]}, logger):
        return False

    try:
        import ecobee
    except ImportError:
        logger.exception(
            "Error while importing dependency nest."
            "Did you maybe not install the python-ecobee dependency?")
        return False

    CLIENT = ecobee.Client(config[DOMAIN][CONF_API_KEY])
    if CLIENT.authentication_required:
        CLIENT.authorize_finish()

    def start_ecobee(event):
        if CLIENT.authentication_required:
            CLIENT.authorize_finish()
        CLIENT.update()

        logger.info("Scanning for ecobee components")

    hass.bus.listen_once(EVENT_HOMEASSISTANT_START, start_ecobee)

    return True
