#!/usr/bin/python


import requests
import requests.exceptions
import json
import time
from paho.mqtt import client as mqtt_client

LOGIN_URL       = "http://192.168.1.14/login"
DATA_URL1       = "http://192.168.1.14/battery-status"
DATA_URL2       = "http://192.168.1.14/imeon-status"
DATA_URL3       = "http://192.168.1.14/data-lithium"
DATA_URL4       = "http://192.168.1.14/scan?scan_time=&single=true"
EMAIL           = "installer@local" # default Imeon login
PASSWORD        = "Installer_P4SS"  # default Imeon pass
broker          = '192.168.1.100'
port            = 1883
sensor_topic    = "homeassistant/imeon/sensor" # or wherever else you want to send it, will work oob with the provided home assitant config
status_topic    = "homeassistant/imeon/status" # or wherever else you want to send it, will work oob with the provided home assitant config
client_id       = "Imeon"
username        = "homeassistant"
password        = "passwd"
debug           = True # True will display the output
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



def publish_discovery(client):

    base = "homeassistant/sensor/imeon"

    # Mapping intelligent des unités + classes
    
    def detect_meta(key):

        k = key.lower()

        # PRIORITÉ : apparent power (VA)
        if "apperent_power" in k or "apparent_power" in k:
            return ("VA", "apparent_power", "measurement")

        # PRIORITÉ : active power (W)
        elif "active_power" in k or ("power" in k and "apperent" not in k and "apparent" not in k):
            return ("W", "power", "measurement")

        elif "voltage" in k or "tension" in k:
            return ("V", "voltage", "measurement")

        elif "current" in k:
            return ("A", "current", "measurement")

        elif "temperature" in k or "tmp" in k:
            return ("°C", "temperature", "measurement")

        elif "soc" in k or "percent" in k or "charge" in k:
            return ("%", "battery", "measurement")

        elif "frequency" in k:
            return ("Hz", None, "measurement")

        elif "energy" in k:
            return ("kWh", "energy", "total_increasing")

        else:
            return (None, None, None)


    for key in payload.keys():

        sensor_id = key.lower().replace(" ", "_")
        name = key.replace("_", " ")

        unit, device_class, state_class = detect_meta(key)

        topic = f"{base}/{sensor_id}/config"

        payload_discovery = {
            "name": name,
            "state_topic": sensor_topic,
            "value_template": f"{{{{ value_json.{key} }}}}",
            "unique_id": f"imeon_{sensor_id}",
            "availability_topic": status_topic,
            "payload_available": "online",
            "payload_not_available": "offline",
            "device": {
                "identifiers": ["imeon_device"],
                "name": "Imeon Inverter",
                "manufacturer": "Imeon",
                "model": "IMEON"
            }
        }

        # Ajouts dynamiques propres HA
        if unit:
            payload_discovery["unit_of_measurement"] = unit
        if device_class:
            payload_discovery["device_class"] = device_class
        if state_class:
            payload_discovery["state_class"] = state_class

        client.publish(topic, json.dumps(payload_discovery), retain=True)


def poll_imeon_data():
  global payload
  session = requests.Session()

  try:
      resp    = session.post(LOGIN_URL, data={"email" : EMAIL , "passwd": PASSWORD}, timeout=2)
      data1   = session.get(DATA_URL1, timeout=2)
      data2   = session.get(DATA_URL2, timeout=2)
      data3   = session.get(DATA_URL3, timeout=2)
      data4   = session.get(DATA_URL4, timeout=2)
      
      resp.raise_for_status()
      data1.raise_for_status()
      data2.raise_for_status()
      data3.raise_for_status()
      data4.raise_for_status()

      values1 = data1.json()
      values2 = data2.json()
      values3 = data3.json()
      values4 = data4.json()
#--------------------DATA battery-status -----------------------
      payload["Timestamp"]                              = str(time.ctime())
      payload["Battery_id"]                             = str(values1['bat_id'])
      payload["Battery_model"]                          = str(values1['bat_model'])
      payload["Battery_reason"]                         = str(values1['bat_reason'])
      payload["Battery_status"]                         = str(values1['bat_status'])
      payload["Battery_type"]                           = str(values1['bat_type'])
      payload["Battery_can_comm"]                       = str(values1['can_comm'])
      payload["Battery_can_status"]                     = str(values1['can_status'])
      payload["Battery_error_history"]                  = str(values1['error_history'])
      payload["Battery_etat"]                           = str(values1['etat'])
      payload["Battery_id"]                             = str(values1['id'])
      payload["Battery_imeon_comm"]                     = str(values1['imeon_comm'])
      payload["Battery_protocol_status"]                = str(values1['protocol_status'])
      payload["Battery_warning_error"]                  = str(values1['warning_error'])
#--------------------DATA imeon-status -----------------------
      payload["Battery_state_badge"]                    = str(values2['state_battery']['badge'])
      payload["Battery_state_class"]                    = str(values2['state_battery']['class'])
      payload["Battery_state_message"]                  = str(values2['state_battery']['message'])
      payload["Battery_date_class"]                     = str(values2['state_date']['class'])
      payload["Battery_date_date"]                      = str(values2['state_date']['date'])
      payload["Battery_date_hour"]                      = str(values2['state_date']['hour'])
      payload["Battery_date_message"]                   = str(values2['state_date']['message'])
      payload["Battery_date_timestamp"]                 = str(values2['state_date']['timestamp'])
      payload["Ethernet_state_badge"]                   = str(values2['state_ethernet']['badge'])
      payload["Ethernet_state_class"]                   = str(values2['state_ethernet']['class'])
      payload["Ethernet_state_message"]                 = str(values2['state_ethernet']['message'])
      payload["grid_state_badge"]                       = str(values2['state_grid']['badge'])
      payload["grid_state_class"]                       = str(values2['state_grid']['class'])
      payload["grid_state_message"]                     = str(values2['state_grid']['message'])
      payload["hotspot_state_badge"]                    = str(values2['state_hotspot']['badge'])
      payload["hotspot_state_class"]                    = str(values2['state_hotspot']['class'])
      payload["hotspot_state_message"]                  = str(values2['state_hotspot']['message'])
      payload["internet_state_badge"]                   = str(values2['state_internet']['badge'])
      payload["internet_state_class"]                   = str(values2['state_internet']['class'])
      payload["internet_state_message"]                 = str(values2['state_internet']['message'])
      payload["inverter_state_badge"]                   = str(values2['state_inverter']['badge'])
      payload["inverter_state_class"]                   = str(values2['state_inverter']['class'])
      payload["inverter_state_message"]                 = str(values2['state_inverter']['message'])
      payload["meter_state_badge"]                      = str(values2['state_meter']['badge'])
      payload["meter_state_class"]                      = str(values2['state_meter']['class'])
      payload["meter_state_message"]                    = str(values2['state_meter']['message'])
      payload["parallel_state_badge"]                   = str(values2['state_parallel']['badge'])
      payload["parallel_state_class"]                   = str(values2['state_parallel']['class'])
      payload["parallel_state_message"]                 = str(values2['state_parallel']['message'])
      payload["pv_state_badge"]                         = str(values2['state_pv']['badge'])
      payload["pv_state_class"]                         = str(values2['state_pv']['class'])
      payload["pv_state_message"]                       = str(values2['state_pv']['message'])
      payload["relay_state_badge"]                      = str(values2['state_relay']['badge'])
      payload["relay_state_class"]                      = str(values2['state_relay']['class'])
      payload["relay_state_message"]                    = str(values2['state_relay']['message'])
      payload["retrofit_state_badge"]                   = str(values2['state_retrofit']['badge'])
      payload["retrofit_state_class"]                   = str(values2['state_retrofit']['class'])
      payload["retrofit_state_message"]                 = str(values2['state_retrofit']['message'])
      payload["timeline_state_badge"]                   = str(values2['state_timeline']['badge'])
      payload["timeline_state_class"]                   = str(values2['state_timeline']['class'])
      payload["timeline_state_detail"]                  = str(values2['state_timeline']['detail'])
      payload["timeline_state_message"]                 = str(values2['state_timeline']['message'])
      payload["update_state_badge"]                     = str(values2['state_update']['badge'])
      payload["update_state_class"]                     = str(values2['state_update']['class'])
      payload["update_state_message"]                   = str(values2['state_update']['message'])
      payload["wifi_state_badge"]                       = str(values2['state_wifi']['badge'])
      payload["wifi_state_class"]                       = str(values2['state_wifi']['class'])
      payload["wifi_state_message"]                     = str(values2['state_wifi']['message'])
      payload["wifi_state_ssid"]                        = str(values2['state_wifi']['ssid'])

#--------------------DATA data-lithium -----------------------
      payload["Battery_current"]                        = str(values3['battery-current'])
      payload["Battery_tension"]                        = str(values3['battery-tension'])
      payload["Battery_temperature"]                    = str(values3['tmp-bat'])
      payload["Battery_charge"]                         = str(values3['bms-soc'])
      payload["Battery_error"]                          = str(values3['error'])
      payload["Battery_warning"]                        = str(values3['warning'])
#--------------------DATA scan?scan_time=&single=true -----------------------
      payload["AC_input_total_active_power"]            = str(values4['val'][0]['ac_input_total_active_power'])
      payload["AC_output_backup_apperent_power"]        = str(values4['val'][0]['ac_output_apperent_power_r'])
      payload["AC_output_voltage"]                      = str(values4['val'][0]['ac_output_voltage'])
      payload["AC_output_current"]                      = str(values4['val'][0]['ac_output_current'])
      payload["AC_output_frequency"]                    = str(values4['val'][0]['ac_output_frequency'])
      payload["AC_output_power_r"]                      = str(values4['val'][0]['ac_output_power_r'])
      payload["AC_output_total_active_power"]           = str(values4['val'][0]['ac_output_total_active_power'])
      payload["AC_output_total_apperent_power"]         = str(values4['val'][0]['ac_output_total_apperent_power'])
      payload["Battery_current_2"]                      = str(values4['val'][0]['battery_current'])
      payload["Battery_power"]                          = str(values4['val'][0]['battery_power'])
      payload["Battery_soc"]                            = str(values4['val'][0]['battery_soc'])      
      payload["Grid_consumption"]                       = str(values4['val'][0]['em_power'])      
      payload["Grid_status"]                            = str(values4['val'][0]['em_status'])      
      payload["Ext_battery_temperature"]                = str(values4['val'][0]['external_battery_temperature']) 
      payload["Grid_current"]                           = str(values4['val'][0]['grid_current_r']) 
      payload["Grid_frequency"]                         = str(values4['val'][0]['grid_frequency'])
      payload["Grid_power_r"]                           = str(values4['val'][0]['grid_power_r'])
      payload["Grid_voltage"]                           = str(values4['val'][0]['grid_voltage_r'])
      payload["Inverter_temperature"]                   = str(values4['val'][0]['inner_temperature'])
      payload["Inverter_power"]                         = str(values4['val'][0]['inverter_power'])
      payload["max_temperature_detecting_pointers"]     = str(values4['val'][0]['max_temperature_detecting_pointers'])
      payload["output_load_percent"]                    = str(values4['val'][0]['output_load_percent'])
      payload["p_battery_voltage"]                      = str(values4['val'][0]['p_battery_voltage']) 
      payload["pv_input_power1"]                        = str(values4['val'][0]['pv_input_power1'])        
      payload["pv_input_power2"]                        = str(values4['val'][0]['pv_input_power2'])   
      payload["pv_input_voltage_1"]                     = str(values4['val'][0]['pv_input_voltage1']) 
      payload["pv_input_voltage_2"]                     = str(values4['val'][0]['pv_input_voltage2']) 
      payload["solar_input_current1"]                   = str(values4['val'][0]['solar_input_current1'])      
      payload["solar_input_current2"]                   = str(values4['val'][0]['solar_input_current2'])     
       
      A = str(values2['state_grid']['message'])
      B = str(values2['state_meter']['message'])
      C = str(values2['state_pv']['message'])

      payload["Grid_state"]          = A.rstrip(A[-1])
      payload["Meter_state"]         = B.rstrip(A[-1])
      payload["PV_state"]            = C.rstrip(A[-1])

      payload["Meter_status"]        = str(values2['state_meter']['class'])
      payload["Inverter_state"]      = str(values2['state_inverter']['message'])
      payload["State_timeline"]      = str(values2['state_timeline']['detail'])
#      payload["Error_history"]       = str(values1['error_history'][0])

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
    client.will_set(status_topic, payload="offline", qos=0, retain=True)
 
    poll_imeon_data()   
    publish_discovery(client)
    
    publish(client, "online", status_topic)
    publish(client, json.dumps(payload), sensor_topic)
    client.loop_stop()

if __name__ == '__main__':
    run()
