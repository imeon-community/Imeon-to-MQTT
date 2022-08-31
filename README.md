# Imeon-to-MQTT
A python script to extract values from the inverter and inject them in an MQTT server. Typical use case for Home assistant or Jeedom.

I wanted to extract values from the Imeon and add them to my Home Assistant env.
The modbus approach works but is kinda painful and not so guaranteed to work.
So instead, I polled the "hidden" webpages in the interface to get all the data
needed and shipped them to MQTT.

- http://A.B.C.D/imeon-status
- http://A.B.C.D/battery-status
- http://A.B.C.D/data-lithium

For the one using Home assistant, configuration files are in the repo.
Have fun.
