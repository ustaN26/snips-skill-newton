#!/usr/bin/env python3
from hermes_python.hermes import Hermes
import serial
import time

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))

def getPoids(txt,typepds):
	if 'kg' in txt:
		txt = txt[txt.index('kg')-7:txt.index('kg')+2]
		txt = txt.replace(str(txt[0:7]), str(float(str(txt[0:7]))))
		txt = txt.replace('kg', ' kilogramme')
	elif 'g' in txt:
		txt = txt[txt.index('g') - 7:txt.index('g') + 1]
		txt = txt.replace(str(txt[0:7]), str(float(str(txt[0:7]))))
		txt = txt.replace('g', ' gramme')
	elif 'pcs' in txt:
		txt = txt[txt.index('pcs') - 7:txt.index('pcs') + 3]
		txt = txt.replace(str(txt[0:7]), str(float(str(txt[0:7]))))
		txt = txt.replace('pcs', ' pieces')
	elif 't' in txt:
		txt = txt[txt.index('t') - 7:txt.index('t') + 1]
		txt = txt.replace(str(txt[0:7]), str(float(str(txt[0:7]))))
		txt = txt.replace('t', ' tonnes')
	else:
		return "erreur trame"
	if '.' in txt:
		txt = txt.replace('.', ',')
	return "le poids {} est de {}".format(typepds,txt)


def sendcmd(typepds, ser):
	if typepds == "tare":
		ser.write(serial.to_bytes([0x01, 0x05, 0x30, 0x32, 0x4C, 0x0D, 0x0A]))
	elif typepds == "net":
		ser.write(serial.to_bytes([0x01, 0x05, 0x30, 0x33, 0x4C, 0x0D, 0x0A]))
	else:
		ser.write(serial.to_bytes([0x01, 0x05, 0x30, 0x31, 0x4C, 0x0D, 0x0A]))


def intent_received(hermes, intent_message):
	print(intent_message.intent.intent_name)
	if intent_message.intent.intent_name == 'ustaN:demandepoids':
		try:
			ser = serial.Serial(
				port='/dev/ttyACM0',
				baudrate=9600
			)
			if intent_message.slots.type_poids.first() is None
				typepds="net"
			else
				typepds=str(intent_message.slots.type_poids.first().value)
			sendcmd(typepds,ser)
			time.sleep(1)
			out = str(ser.read(16))
			print("trame= "+out)
			out = getPoids(out,typepds)
			print("sortie= "+out)
			ser.close()
			hermes.publish_end_session(intent_message.session_id, out)
		except OSError as err:
			ser.close()
			hermes.publish_end_session(intent_message.session_id, "erreur lecture poids")
			hermes.publish_end_session(intent_message.session_id, str(err))


with Hermes(MQTT_ADDR) as h:
	h.subscribe_intents(intent_received).start()
