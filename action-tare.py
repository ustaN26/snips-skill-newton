#!/usr/bin/env python3
from hermes_python.hermes import Hermes

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))


def intent_received(hermes, intent_message):
	if intent_message.intent.intent_name == 'ustaN:tare':
		hermes.publish_end_session(intent_message.session_id, "tared successfully")

with Hermes(MQTT_ADDR) as h:
	h.subscribe_intents(intent_received).start()