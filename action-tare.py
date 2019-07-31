#!/usr/bin/env python3
from hermes_python.hermes import Hermes
import serial
import time

MQTT_IP_ADDR = "localhost"
MQTT_PORT = 1883
MQTT_ADDR = "{}:{}".format(MQTT_IP_ADDR, str(MQTT_PORT))
listunite = ["g", "kg", "t"]


def getformatrame(txt):
	if ' virgule ' in txt:
		txt = txt.replace(' virgule ', '.')
	if ' kilogrammes' in txt:
		unite = "kg"
		txt = txt.replace(' kilogrammes', 'kg')
		txt = txt[:txt.index('kg') + 2]
	elif ' kilo' in txt:
		unite = "kg"
		txt = txt.replace(' kilo', 'kg')
		txt = txt[:txt.index('kg') + 2]
	elif ' grammes' in txt:
		unite = "g"
		txt = txt.replace(' grammes', 'g')
		txt = txt[:txt.index('g') + 1]
	elif ' tonnes' in txt:
		unite = "t"
		txt = txt.replace(' tonnes', 't')
		txt = txt[:txt.index('t') + 1]
	virgule = 7
	if '.' in txt:
		virgule = txt.index('.')
	val = 7-len(txt)
	i = 0
	while i < val:
		txt = "0{}".format(txt)
		i = i+1
	return virgule, unite, txt


def getpoids(txt):
	if 'kg' in txt:
		unite = "kg"
		txt = txt[txt.index('kg') - 7:txt.index('kg') + 2]
	elif 'g' in txt:
		unite = "g"
		txt = txt[txt.index('g') - 7:txt.index('g') + 1]
	elif 't' in txt:
		unite = "t"
		txt = txt[txt.index('t') - 7:txt.index('t') + 1]
	else:
		return 0, "err", None
	virgule = txt.index('.')
	return virgule, unite, txt


def gestiontare(ser, slotval):
	ser.write(serial.to_bytes([0x01, 0x05, 0x30, 0x32, 0x4C, 0x0D, 0x0A]))
	time.sleep(1)
	out = str(ser.read(16))
	print("tare lue= {}".format(out))
	vallue = getpoids(out)
	if vallue == [0, "err", None]:
		return 1/0
	print("tare = {}".format(vallue[2]))
	trame = getformatrame(slotval)
	print("slot reçu= {}".format(slotval))
	print("slot formaté= {}".format(trame[2]))
	result = str(float(trame[2]) * pow(10, 3 * (listunite.index(trame[1]) - listunite.index(vallue[1]))))
	print(str(result))
	result = result[result.index('.') - vallue[0]:result.index('.') - (vallue[0] - 7)]
	i = 0
	val = 7 - len(result)
	while i < val:
		result = "0{}".format(result)
		i = i + 1
	result = "{}{}".format(result, vallue[1])
	while True:
		if len(result) == 10:
			break
			result = "{} ".format(result)
	print("trame=\'{}\'".format(result))
	return result


def intent_received(hermes, intent_message):
	if intent_message.intent.intent_name == 'ustaN:tare':
		try:
			ser = serial.Serial(
				port='/dev/ttyACM0',
				baudrate=9600
			)
			if intent_message.slots.weigh_value.first() is None:
				ser.write(serial.to_bytes([0x01, 0x10, 0x30, 0x34, 0x4D, 0x0D, 0x0A]))
				hermes.publish_end_session(intent_message.session_id, "tare success")
			else:
				slotval = intent_message.slots.weigh_value.first().value
				print(str(slotval))
				valuetare = gestiontare(ser, slotval)
				ser.write(serial.to_bytes([0x01, 0x02, 0x30, 0x32]))
				ser.write(valuetare.encode())
				ser.write(serial.to_bytes([0x0D, 0x0A]))
				hermes.publish_end_session(intent_message.session_id, "La nouvelle tare est de {} ".format(slotval))
			ser.close()
		except:
			ser.close()
			hermes.publish_end_session(intent_message.session_id, "tare fail")


with Hermes(MQTT_ADDR) as h:
	h.subscribe_intents(intent_received).start()