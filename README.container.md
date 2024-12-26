# build
```podman build -t imeon2mqtt .```

# run once
```
podman run -e IMEONIP=192.168.9.12 \
           -e MQTTBROKERIP=192.0.2.69 \
           -e MQTTBROKERUSER=mqtt \
           -e MQTTBROKERPASS=mqtt \
           imeon2mqtt /usr/local/python/imeon2mqtt.py
```

# run recurring
```
podman run -d --restart=always --replace \
           -e IMEONIP=192.168.9.12 \
           -e MQTTBROKERIP=192.0.2.69 \
           -e MQTTBROKERUSER=mqtt \
           -e MQTTBROKERPASS=mqtt \
           --name imeon2mqtt \
           imeon2mqtt
```

