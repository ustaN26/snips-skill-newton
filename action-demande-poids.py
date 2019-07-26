#!/usr/bin/env python3
from hermes_python.hermes import Hermes
import serial
import time

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

def verbalise_unite(txt):
	if "kg" in txt:
		txt=txt.replace("kg"," kilogramme")
	elif "g" in txt:
		txt=txt.replace("g"," gramme")
	elif "pcs" in txt:
		txt=txt.replace("pcs"," pieces")
	elif "t" in txt:
		txt=txt.replace("t"," tonnes")
	if "." in txt:
		txt=txt.replace(".",",")
	return txt

def intent_received(hermes, intent_message):
	print(intent_message.intent.intent_name)
	if intent_message.intent.intent_name == 'ustaN:demandepoids':
		try:
			ser = serial.Serial(
				port='/dev/ttyACM0',
				baudrate = 9600
			)
			ser.write(serial.to_bytes([0x01,0x09,0x30,0x30,0x05,0x30,0x31,0x4C,0x0D,0x0A]))
			time.sleep(0.5)
			out = ser.read()
			out = verbalise_unite(out)
			out = out.replace(out[0:5]," ")
			print(out)
			ser.close()
			hermes.publish_end_session(intent_message.session_id, "le poids brut est de "+out)
		except:
			ser.close()
			hermes.publish_end_session(intent_message.session_id, "erreur lecture poids")

with Hermes(MQTT_ADDR) as h:
	h.subscribe_intents(intent_received).start()
