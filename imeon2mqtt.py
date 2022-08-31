#!/usr/bin/python

import requests
import requests.exceptions
import json
import time
from paho.mqtt import client as mqtt_client

LOGIN_URL       = "http://[insert your Imeon's IP here]/login"
DATA_URL1       = "http://[insert your Imeon's IP here]/battery-status"
DATA_URL2       = "http://[insert your Imeon's IP here]/imeon-status"
DATA_URL3       = "http://[insert your Imeon's IP here]/data-lithium"
EMAIL           = "installer@local" # default Imeon login
PASSWORD        = "Installer_P4SS"  # default Imeon pass
broker          = '[insert your MQTT Broker's IP here]'
port            = 1883
sensor_topic    = "homeassistant/Imeon/sensor" # or wherever else you want to send it, will work oob with the provided home assitant config
status_topic    = "homeassistant/Imeon/status" # or wherever else you want to send it, will work oob with the provided home assitant config
client_id       = "Imeon"
username        = "[yourusername]"
password        = "[yourpassword]"
debug           = False # True will display the output on your tty
payload         = {}

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
      if debug:
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)
    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def publish(client, msg, topic):
  while True:
    try:
      result = client.publish(topic, msg, qos=0, retain=False)
      status = result[0]
      if debug:
        if status == 0:
           print(f"Sent `{msg}` to topic `{topic}`")
        else:
           print(f"Failed to send message to topic {topic}")

    except Exception as err:
      print("Waiting 5 seconds to reconnect to MQTT server... (" + str(err)+")")
      time.sleep(5)
      continue
    break


def poll_imeon_data():
  global payload
  session = requests.Session()

  try:
      resp    = session.post(LOGIN_URL, data={"email" : EMAIL , "passwd": PASSWORD}, timeout=2)
      data1   = session.get(DATA_URL1, timeout=2)
      data2   = session.get(DATA_URL2, timeout=2)
      data3   = session.get(DATA_URL3, timeout=2)

      resp.raise_for_status()
      data1.raise_for_status()
      data2.raise_for_status()
      data3.raise_for_status()

      values1 = data1.json()
      values2 = data2.json()
      values3 = data3.json()

      payload["Timestamp"]           = str(time.ctime())
      payload["Battery_status"]      = str(values1['bat_status'])
      #payload["Battery_state"]      = str(values2['state_battery']['message'])
      payload["Battery_activity"]    = str(values2['state_battery']['class'])
      payload["Battery_current"]     = str(values3['battery-current'])
      payload["Battery_tension"]     = str(values3['battery-tension'])
      payload["Battery_temperature"] = str(values3['tmp-bat'])
      payload["Battery_charge"]      = str(values3['bms-soc'])
      payload["Battery_error"]       = str(values3['error'])
      payload["Battery_warning"]     = str(values3['warning'])

      A = str(values2['state_grid']['message'])
      B = str(values2['state_meter']['message'])
      C = str(values2['state_pv']['message'])

      payload["Grid_state"]          = A.rstrip(A[-1])
      payload["Meter_state"]         = B.rstrip(A[-1])
      payload["PV_state"]            = C.rstrip(A[-1])

      payload["Meter_status"]        = str(values2['state_meter']['class'])
      payload["Inverter_state"]      = str(values2['state_inverter']['message'])
      payload["State_timeline"]      = str(values2['state_timeline']['detail'])
      payload["Error_history"]       = str(values1['error_history'][0])

      if debug:
        for x in payload:
          print(x, " : ", payload[x])

  except Exception as err:
      print("Imeon is eating glue again... (" + str(err)+")")
      #time.sleep(10)
      #continue
      raise SystemExit
    #break

def run():
    global payload
    
    client = connect_mqtt()
    client.loop_start()
    client.will_set(status_topic, payload="offline", qos=0, retain=False)
    poll_imeon_data()
    publish(client, "online", status_topic)
    publish(client, json.dumps(payload), sensor_topic)
    client.loop_stop()

if __name__ == '__main__':
    run()
