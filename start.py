import json
import requests
import logging
from pyHS100 import SmartPlug, Discover
import time
import datetime as dt

import constants

logger = logging.getLogger()
logger.setLevel(logging.INFO)

last_action = dt.datetime.now()

# Returns the sensor state
def get_sensor_state(url):
    try:
        response = requests.get(url)
        json_data = json.loads(response.text)
        return json_data['state']['presence'] is True
    except:
        logger.exception("An Exception occurred")
        return True

# Returns the Smart Plug identified by an alias
def get_smart_plug(alias):
    for device in Discover.discover().values():
        if device.alias == alias:
            return SmartPlug(device.host)
    return None

# Turns on a Kasa Smart Plug identified by an alias
def turn_on_or_off_smart_plug(alias, turn_on=False):
    plug = get_smart_plug(alias)
    if plug is not None:
        plug.turn_on() if turn_on else plug.turn_off()

# Returns the State of Kasa Smart Plug identified by an alias
def get_smart_plug_state(alias):
    plug = get_smart_plug(alias)
    if plug is not None:
        return True if plug.state == 'ON' else False;
    return False

# Main Loop
while True:

    time.sleep(constants.SECONDS_TIMEOUT)

    now = dt.datetime.now()

    # Turning the Switch on
    if get_sensor_state(constants.URL_SENSOR):
        if get_smart_plug_state(constants.ALIAS_SMART_PLUG) is False:
            turn_on_or_off_smart_plug(constants.ALIAS_SMART_PLUG, True)
        last_action = now
        continue

    # Turning the Switch off
    if (now - last_action).total_seconds() > constants.SECONDS_COOL_DOWN:
        last_action = now
        if get_smart_plug_state(constants.ALIAS_SMART_PLUG):
            turn_on_or_off_smart_plug(constants.ALIAS_SMART_PLUG, False)
    # DO NOT do anything in the Cool Down
