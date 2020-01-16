from datetime import timedelta
from socket import socket
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
import sys
import logging

# from zeroconf import Zeroconf, ServiceInfo, MyListener, ServiceBrowser
from zeroconf import IPVersion, ServiceBrowser, ServiceStateChange, Zeroconf


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
    def root_disk_size(self):
        return (psutil.disk_usage('/').total / 1000 / 1000 / 1000.0)

    # ------------------------------------------------------------------------------------------------
    def root_disk_percent_full(self):
        return psutil.disk_usage('/').percent

    # ------------------------------------------------------------------------------------------------
    def boot_datetime(self):
        return datetime.datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")

    # ------------------------------------------------------------------------------------------------
    def network_rcv_errors(self):
        return psutil.net_io_counters().errin

    # ------------------------------------------------------------------------------------------------
    def network_xmt_errors(self):
        return psutil.net_io_counters().errout

    # ------------------------------------------------------------------------------------------------
    # ------------------------------------------------------------------------------------------------
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
        # 15Jan2020
        if '900021' in rev:
            return 'A+ 1.1 512MB Sony UK'
        elif '900032' in rev:
            return 'B+ 1.2 512MB Sony UK'
        elif '900092' in rev:
            return 'Zero 1.2 512MB Sony UK'
        elif '900093' in rev:
            return 'Zero 1.3 512MB Sony UK'
        elif '9000c1' in rev:
            return 'Zero W 1.1 512MB Sony UK'
        elif '9020e0' in rev:
            return '3A+ 1.0 512MB Sony UK'
        elif '920092' in rev:
            return 'Zero 1.2 512MB Embest'
        elif '920093' in rev:
            return 'Zero 1.3 512MB Embest'
        elif '900061' in rev:
            return 'CM 1.1 512MB Sony UK'
        elif 'a01040' in rev:
            return '2B 1.0 1GB Sony UK'
        elif 'a01041' in rev:
            return '2B 1.1 1GB Sony UK'
        elif 'a02082' in rev:
            return '3B 1.2 1GB Sony UK'
        elif 'a020a0' in rev:
            return 'CM3 1.0 1GB Sony UK'
        elif 'a020d3' in rev:
            return '3B+ 1.3 1GB Sony UK'
        elif 'a02042' in rev:
            return '2B (with BCM2837) 1.2 1GB Sony UK'
        elif 'a21041' in rev:
            return '2B 1.1 1GB Embest'
        elif 'a22042' in rev:
            return '2B (with BCM2837) 1.2 1GB Embest'
        elif 'a22082' in rev:
            return '3B 1.2 1GB Embest'
        elif 'a220a0' in rev:
            return 'CM3 1.0 1GB Embest'
        elif 'a32082' in rev:
            return '3B 1.2 1GB Sony Japan'
        elif 'a52082' in rev:
            return '3B 1.2 1GB Stadium'
        elif 'a22083' in rev:
            return '3B 1.3 1GB Embest'
        elif 'a02100' in rev:
            return 'CM3+ 1.0 1GB Sony UK'
        elif 'a03111' in rev:
            return '4B 1.1 1GB Sony UK'
        elif 'b03111' in rev:
            return '4B 1.1 2GB Sony UK'
        elif 'c03111' in rev:
            return '4B 1.1 4GB Sony UK'
        elif 'c03112' in rev:
            return '4B 1.2 4GB Sony UK'

        return 'Unknown {}'.format(rev)

    # ------------------------------------------------------------------------------------------------
    def asJSON(self):
        myDict = OrderedDict({
            "host": self.get_hostname(),
            "eth0 IP": self.get_eth_ipaddress(),
            "wlan0 IP": self.get_wifi_ipaddress(),
            "booted": self.boot_datetime(),
            "uptime": self.get_uptime(),
            "cpu_pct": self.cpu_percent(),
            "cpu_temp": self.get_cpu_temperature(),
            "cpu_cnt": self.cpu_count(),
            "root_size": self.root_disk_size(),
            "root_percent": self.root_disk_percent_full(),
            "xmt_errors": self.network_xmt_errors(),
            "rcv_errors": self.network_rcv_errors(),
            "ssid": self.get_SSID(),
            "model": self.rpi_model_string(),
            "camera_present": self.get_camera_present()
        })
        return json.dumps(myDict)


class MessageHandler(object):
    def __init__(self, broker_address="mqtt.local"):
        # self.local_broker_address = ''
        self.broker_address = broker_address
        self.client = mqtt.Client(client_id="", clean_session=True, userdata=None)

    # ---------------------------------------------------------------------
    def on_connect(self, client, userdata, flags, rc):
        logging.info('Connected to the MQTT broker!')
        pass

    # ---------------------------------------------------------------------
    def on_message(self, client, userdata, message):
        logging.warning('Not expecting inbound messages')

    def start(self):
        logging.info('Message handling start - v4')
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        print('Start - connecting to ', self.broker_address)
        self.client.connect(self.broker_address)
        # self.client.subscribe(self.doorStatusTopic,0)
        self.client.loop_start()

    def cleanup(self):
        # self.client.unsubscribe(self.doorStatusTopic)
        self.client.disconnect()
        self.client.loop_stop()

    def send_node_status_info(self):
        # logging.info('Sending a MQTT System Info!')
        print('Sending a MQTT System Info to NODE!')
        data = {}
        data['topic'] = 'NODE'
        data['datetime'] = datetime.datetime.now().replace(microsecond=0).isoformat()
        json_data = SystemStats().asJSON()
        self.client.publish('NODE', json_data, qos=0)

    def send_host_status_info(self):
        # logging.info('Sending a MQTT System Info!')
        logging.info('Sending a MQTT System Info to hostname!')
        topic = SystemStats().get_hostname().upper()
        data = {}
        data['datetime'] = datetime.datetime.now().replace(microsecond=0).isoformat()
        json_data = SystemStats().asJSON()
        data['topic'] = topic
        self.client.publish(topic, json_data, qos=0)


def on_service_state_change(
        zeroconf: Zeroconf, service_type: str, name: str, state_change: ServiceStateChange
) -> None:
    print("Service %s of type %s state changed: %s" % (name, service_type, state_change))

    if state_change is ServiceStateChange.Added:
        info = zeroconf.get_service_info(service_type, name)
        if info:
            addresses = ["%s:%d" % (socket.inet_ntoa(addr), cast(int, info.port)) for addr in info.addresses]
            print("  Addresses: %s" % ", ".join(addresses))
            print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            print("  Server: %s" % (info.server,))
            if info.properties:
                print("  Properties are:")
                for key, value in info.properties.items():
                    print("    %s: %s" % (key, value))
            else:
                print("  No properties")
        else:
            print("  No info")
        print('\n')


logging.basicConfig(filename='/tmp/mqttsysteminfo.log', level=logging.DEBUG)
logging.info('Attempting to find mqtt broker via mDNS')

print("Multicast DNS Service Discovery for Python Browser test")
r = Zeroconf()
print("Testing browsing for a service...")
type = "_mqtt._tcp.local."

browser = ServiceBrowser(r, type, handlers=[on_service_state_change])
time.sleep(60)
r.close()

try:
    mqtt_broker_address = sys.argv[1]
except:
    mqtt_broker_address = 'mqtt.local'

print('Connecting to ', mqtt_broker_address)

m = MessageHandler(broker_address=mqtt_broker_address)
m.start()

while True:
    m.send_node_status_info()
    m.send_host_status_info()
    time.sleep(60)
