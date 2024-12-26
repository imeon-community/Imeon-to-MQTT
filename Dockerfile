FROM python:slim

RUN python3 -m pip install requests paho-mqtt==1.6.1

RUN mkdir /usr/local/python
ADD imeon2mqtt.py /usr/local/python
RUN chmod +x /usr/local/python/imeon2mqtt.py

CMD while true; do /usr/local/python/imeon2mqtt.py; sleep 60; done

