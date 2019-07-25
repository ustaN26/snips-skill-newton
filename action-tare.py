#!/usr/bin/env python3
from hermes_python.hermes import Hermes
import serial

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))


def intent_received(hermes, intent_message):
	if intent_message.intent.intent_name == 'ustaN:tare':
		try:
			ser = serial.Serial(
				port='/dev/ttyACM0',
				baudrate = 9600
			)
			ser.write(serial.to_bytes([0x01,0x09,0x30,0x30,0x10,0x30,0x34,0x4D,0x0D,0x0A]))
			ser.close()
			hermes.publish_end_session(intent_message.session_id, "tare success")
		except:
			ser.close()
			hermes.publish_end_session(intent_message.session_id, "tare fail")


with Hermes(MQTT_ADDR) as h:
	h.subscribe_intents(intent_received).start()