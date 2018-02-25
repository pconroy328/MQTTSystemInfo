from datetime import timedelta
from subprocess import check_output
import json
import datetime
from collections import OrderedDict

# sudo apt-get install python-dev
# sudo pip install psutil
import os
import psutil
import paho.mqtt.client as mqtt
import logging
import time


class SystemStats(object):
    # ------------------------------------------------------------------------------------------------
    def __init__(self):
        pass

    # ------------------------------------------------------------------------------------------------
    def get_hostname(self):
        return os.uname()[1]

    # ------------------------------------------------------------------------------------------------
    def get_cpu_temperature(self):
        try:
            res = os.popen('vcgencmd measure_temp').readline()
            tempC = float((res.replace("temp=", "").replace("'C\n", "")))
        except:
            return 'N/A'

        return (tempC * 1.8) + 32.0

    # ------------------------------------------------------------------------------------------------
    def get_camera_present(self):
        try:
            res = os.popen('vcgencmd get_camera').readline()
        except:
            return 'N/A'

        return 'supported=1 detected=1' in res

    # ------------------------------------------------------------------------------------------------
    def get_uptime(self):
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime_string = str(timedelta(seconds=uptime_seconds))
        return uptime_string

    # ------------------------------------------------------------------------------------------------
    def get_SSID(self, interface='wlan0'):
        ssid = "None"
        try:
            scanoutput = check_output(['iwconfig', interface])
            for line in scanoutput.split():
                line = line.decode('utf-8')
                if line[:5] == 'ESSID':
                    ssid = line.split('"')[1]
        except:
            pass
        return ssid

    # ------------------------------------------------------------------------------------------------
    def get_wifi_ipaddress(self):
        ip_address = '?.?.?.?'
        try:
            foo = psutil.net_if_addrs()
            if_family = foo['wlan0'][0][0]
            if if_family == 2:
                ip_address = foo['wlan0'][0][1]
        except:
            pass
        return ip_address

    # ------------------------------------------------------------------------------------------------
    def get_eth_ipaddress(self):
        ip_address = '?.?.?.?'
        try:
            foo = psutil.net_if_addrs()
            if_family = foo['eth0'][0][0]
            if if_family == 2:
                ip_address = foo['eth0'][0][1]
        except:
            pass
        return ip_address

    # ------------------------------------------------------------------------------------------------
    def cpu_count(self):
        return psutil.cpu_count()

    # ------------------------------------------------------------------------------------------------
    def cpu_percent(self):
        return psutil.cpu_percent()

    # ------------------------------------------------------------------------------------------------
    def boot_datetime(self):
        return datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------------------------------------
    def rpi_model(self):
        origoutput = check_output(['cat', '/proc/cpuinfo'])
        # Find the Hardware Section
        start = origoutput.find('Hardware')
        # Now advance past the colon
        start = origoutput[start:].find(':') + start
        # Look for next line with starts with 'Revision'
        end = origoutput[start:].find('Revision') + start
        model = origoutput[start + 1:end - 1]
        return model

    # ------------------------------------------------------------------------------------------------
    def rpi_revision(self):
        origoutput = check_output(['cat', '/proc/cpuinfo'])
        # Find the Hardware Section
        start = origoutput.find('Revision')
        # Now advance past the colon
        start = origoutput[start:].find(':') + start
        # Look for next line with starts with 'Revision'
        end = origoutput[start:].find('Serial') + start
        revision = origoutput[start + 1:end - 1]
        return revision

    # ------------------------------------------------------------------------------------------------
    def rpi_model_string(self):
        model = self.rpi_model()
        rev = self.rpi_revision()
        if 'a22082' in rev:
            return 'Pi 3 Model B (Embest, China)'
        elif 'a02082' in rev:
            return 'Pi 3 Model B (Sony, UK)'
        elif '9000C1' in rev:
            return 'Pi Zero W'
        elif '900093' in rev:
            return 'Pi Zero v1.3'
        elif '900092' in rev:
            return 'Pi Zero v1.2'
        elif 'a22042' in rev:
            return 'Pi 2 Model B v1.2'
        elif 'a21041' in rev:
            return 'Pi 2 Model B v1.1 (Embest, China)'
        elif 'a01041' in rev:
            return 'Pi 2 Model B v1.1 (Sony, UK)'
        elif '000e' in rev:
            return 'Pi Model B Rev 2'
        return 'Unknown {}'.format(rev)

    # ------------------------------------------------------------------------------------------------
    def asJSON(self):
        myDict = OrderedDict( {
                    "host" : self.get_hostname(),
                    "eth0 IP" : self.get_eth_ipaddress(),
                    "wlan0 IP" : self.get_wifi_ipaddress(),
                    "booted" : self.boot_datetime(),
                    "uptime": self.get_uptime(),
                    "cpu_pct" : self.cpu_percent(),
                    "cpu_temp": self.get_cpu_temperature(),
                    "cpu_cnt" : self.cpu_count(),
                    "ssid": self.get_SSID(),
                    "model" : self.rpi_model_string(),
                    "camera_present": self.get_camera_present()
                   })
        return json.dumps(myDict)


class MessageHandler(object):
    def __init__(self,broker_address="10.0.0.11"):
        self.aws_broker_address = 'ec2-52-32-56-28.us-west-2.compute.amazonaws.com'
        self.local_broker_address = 'gx100'
        self.broker_address = self.aws_broker_address
        self.client = mqtt.Client(client_id="", clean_session=True, userdata=None)

    #---------------------------------------------------------------------
    def on_connect(self, client, userdata, flags, rc):
        logging.info('Connected to the MQTT broker!')
        pass

    #---------------------------------------------------------------------
    def on_message(self, client, userdata, message):
        logging.warn('Not expecting inbound messages')

    def start(self):
        logging.info('Message handling start - v4')
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker_address)
        #self.client.subscribe(self.doorStatusTopic,0)
        self.client.loop_start()

    def cleanup(self):
        #self.client.unsubscribe(self.doorStatusTopic)
        self.client.disconnect()
        self.client.loop_stop()

    def send_node_status_info(self):
        # logging.info('Sending a MQTT System Info!')
        print 'Sending a MQTT System Info to NODE!'
        data = {}
        data['topic'] = 'NODE'
        data['datetime'] = datetime.datetime.now().replace(microsecond=0).isoformat()
        json_data = SystemStats().asJSON()
        self.client.publish('NODE', json_data,qos=0)

    def send_host_status_info(self):
        # logging.info('Sending a MQTT System Info!')
        print 'Sending a MQTT System Info to hostname!'
        topic = SystemStats().get_hostname().upper()
        data = {}
        data['datetime'] = datetime.datetime.now().replace(microsecond=0).isoformat()
        json_data = SystemStats().asJSON()
        data['topic'] = topic
        self.client.publish(topic, json_data,qos=0)


m = MessageHandler()
m.start()
while True:
    m.send_node_status_info()
    m.send_host_status_info()
    time.sleep(60)