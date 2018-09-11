import paho.mqtt.client as mqtt 
import time
import _thread
import os
import RPi.GPIO as GPIO
import socket
import fcntl
import struct
from apscheduler.schedulers.background import BackgroundScheduler
from pyfcm import FCMNotification
import datetime

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.OUT)
GPIO.output(7, False)

scheduler = BackgroundScheduler()
scheduler.start()

scheduler_t = BackgroundScheduler()

push_service = FCMNotification(api_key="AIzaSyAE5F6O2xAm9XPIq90vkJbTGAkLJrhsFbI")

temperature_avg = 25.0
soil_avg = 50.0

def on_message_msg(client, userdata, message):
    global temperature_avg, soil_avg
    print("Topic : " + message.topic + " || Message : " + str(message.payload.decode("utf-8")) + "\n")

    server.publish(message.topic, str(message.payload.decode("utf-8")), retain=True)
    msg_list = str(message.payload.decode("utf-8")).split(" / ")
    temperature_list  = msg_list[3].split(":")
    soil_list = msg_list[7].split(":")

    temperature_avg = (float(temperature_list[1])+temperature_avg)/2
    soil_avg = (float(soil_list[1])+soil_avg)/2
    


def on_message_ctrl(client, userdata, message):
    global scheduler, push_service

    current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = str(message.payload.decode("utf-8"))
    print("Topic : " + message.topic + " || Message : " + msg)
    if msg == "OFF":
        GPIO.output(7, False)
        push_service.notify_topic_subscribers(topic_name="uscclab", message_title="樹莓農樁", message_body="水閥 OFF    "+current_time)
    elif msg == "ON":
        GPIO.output(7, True)
        push_service.notify_topic_subscribers(topic_name="uscclab", message_title="樹莓農樁", message_body="水閥 ON    "+current_time)
    elif message.topic=="uscclab/gateway_001/schedule":
        schedule_list = msg.split(" ")
        
        server.publish("uscclab/gateway_001/control", "OFF", retain=True)
        scheduler.shutdown(wait=False)
        scheduler = BackgroundScheduler()
        
        schedule_list.remove('')
        
        if len(schedule_list) != 0:
            for content in schedule_list:
                if content[0] == "1":
                    content_hour = content[2:4]
                    content_minute = content[5:7]
                    scheduler.add_job(scheduler_job, "cron", hour=content_hour, minute=content_minute)
                elif content[0] == "2" or content[0] == "3":
                    schedule_temperature = float(content[3:5])
                    schedule_soil = float(content[3:5])
                    scheduler.add_job(condition_job, "interval", seconds=300, args=[schedule_temperature, schedule_soil])

        scheduler.start()



def scheduler_job():
    server.publish("uscclab/gateway_001/control", "ON", retain=True)
    time.sleep(60)
    server.publish("uscclab/gateway_001/control", "OFF", retain=True)


def condition_job(temperature, soil):
    global temperature_avg, soil_avg, scheduler_t
    
    if temperature_avg>temperature and not scheduler_t.running:
        scheduler_t.add_job(scheduler_job, "interval", seconds=7200)
        scheduler_t.start()
    elif temperature_avg<temperature and scheduler_t.running:
        server.publish("uscclab/gateway_001/control", "OFF", retain=True)
        scheduler_t.shutdown(wait=False)
        scheduler_t = BackgroundScheduler()
    
    if soil_avg<soil:
        scheduler_job()


def get_ipaddress(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,
        struct.pack('256s',bytes(ifname[:15], 'utf-8'))
    )[20:24])


def on_connect(client, userdata, flags, rc):
    print("Connect")


def on_disconnect(client, userdata, rc):
    print("Disconnect")

# enter server and self address here
server_address = "140.116.82.42" #do not revise the server ip  address
gateway_address =  get_ipaddress('wlan0') #revise when connect to router
print(gateway_address)

# may edit instances name here
print("creating new instance")

# need 2 instances, one for sensor and one for server
gateway = mqtt.Client("gateway_g")
server = mqtt.Client("gateway_s")

gateway.on_message = on_message_msg # attach function to callback
server.on_message = on_message_ctrl
gateway.on_connect = on_connect
gateway.on_disconnect = on_disconnect

server.username_pw_set("modlogin","wtf321")
print("Connecting to server at " + server_address)
server.connect(server_address)

print("Connecting to gateway at " + gateway_address)
gateway.connect(gateway_address)

topics_001 = 'uscclab/gateway_001/module_001/#'

topic_data = 'uscclab/gateway_001/module_001/data'
topic_status = 'uscclab/gateway_001/module_001/status'
topic_warning = 'uscclab/gateway_001/module_001/warning'

topic_control = 'uscclab/gateway_001/control'
topic_schedule = 'uscclab/gateway_001/schedule'
topic_sublist = 'uscclab/gateway_001/sublist'


server.loop_start() # start the loop
gateway.loop_start()

#subscribe topics on gateway data/status/warning
gateway.subscribe(topics_001)
print("Gateway subscribe to topics on gateway")


#subscribe topics on server data/status/warning/control
server.subscribe(topic_data)
server.subscribe(topic_status)
server.subscribe(topic_warning)
server.subscribe(topic_control)
server.subscribe(topic_schedule)
server.subscribe(topic_sublist)
print("Gateway subscribe to topics on server")


server.publish(topic_sublist, "1", retain=True)

# start a new thread to pending user input and publish
# _thread.start_new_thread(publish, ("lol",))  # format: start_new_thread(function_name ,("args","second args"))

while True:  # to let the main thread running in the background
    pass


