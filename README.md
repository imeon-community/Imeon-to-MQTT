# Imeon-to-MQTT
A python script to extract values from the inverter and inject them in an MQTT server. Typical use case for Home assistant or Jeedom.

I wanted to extract values from the Imeon and add them to my Home Assistant env.
The modbus approach works but is kinda painful and not so guaranteed to work.
So instead, I polled the "hidden" webpages in the interface to get all the data
needed and shipped them to MQTT.

- http://A.B.C.D/imeon-status
- http://A.B.C.D/battery-status
- http://A.B.C.D/data-lithium

Then just run it with a recurring crontab like :
*/5    * * * *   /usr/bin/python /usr/local/python/imeon-stats.py >/dev/null 2>&1
(provided as an exemple in the repo as well)

Have fun.

PS: For the one using Home assistant, configuration files are in the repo, 
    to create dashboards like those:

![imeon solar dasboard for home assistant exemple](https://github.com/imeon-community/Imeon-to-MQTT/blob/main/Solar%20supervision.jpg)
