# mqtt-gateway

## Connect to Wifi:

https://www.raspberrypi.org/documentation/configuration/wireless/wireless-cli.md

## Wifi auto reconnect (had connected before):

http://alexba.in/blog/2015/01/14/automatically-reconnecting-wifi-on-a-raspberrypi/

## Auto launch :

https://www.raspberrypi-spy.co.uk/2015/02/how-to-autorun-a-python-script-on-raspberry-pi-boot/

## Install mosquitto broker :

https://www.instructables.com/id/Installing-MQTT-BrokerMosquitto-on-Raspberry-Pi/

### cd /etc/mosquitto/conf.d/

### vim listener.conf

### add:

listener 1883

listener 9001

protocol websockets

### sudo service mosquitto restart

## Network Service Discovery :

https://pastebin.com/0RhJyZud

http://pjack1981.blogspot.com/2012/07/avahi.html

### create a service named '_mosquitto._tcp'
