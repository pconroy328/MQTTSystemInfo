from datetime import timedelta
import socket
from subprocess import check_output
import json
import datetime
from collections import OrderedDict

# sudo apt-get install python-dev
# sudo pip install psutil or sudo apt-get install python3-psutil
# pip3 install paho-mqtt
# pip3 install zeroconf


import os
import psutil
import paho.mqtt.client as mqtt
import logging
import time
import sys

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
class SystemStats(object):
    version = "v2.1 (checking for AP)"

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

        return round((tempC * 1.8) + 32.0,1)

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
            #
            # This will probably break when using Non-Ambiguious Interface names
            scanoutput = check_output(['iwconfig', interface])
            for line in scanoutput.split():
                line = line.decode('utf-8')
                if line[:5] == 'ESSID':
                    ssid = line.split('"')[1]
        except:
            pass
        return ssid

    # ------------------------------------------------------------------------------------------------
    def get_interface_mode(self, interface='wlan0'):
        mode = "??"
        try:
            #
            # This will probably break when using Non-Ambiguious Interface names
            scanoutput = check_output(['iwconfig', interface])
            for line in scanoutput.splitlines():
                line = line.decode('utf-8')
                position=line.find('Mode:')
                if (position > 0):
                    mode=line[position+5:].split(' ',1)[0].strip()
        except:
            pass
        return mode

    # ------------------------------------------------------------------------------------------------
    def get_SignalStrength(self, interface='wlan0'):
        #
        if (self.get_interface_mode(interface) == 'Master'):
           print('Interface is an access point - trying next.')
           interface='wlan1'

        #
        # These are far from standardized:
        #
        # Link Quality=35/70  Signal level=-75 dBm  
        # Link Quality=100/100 Signal level=76/100  Noise level=0/100
    
        signal_strength_str = "?? dBm"
        try:
            #
            # This will probably break when using Non-Ambiguious Interface names
            scanoutput = check_output(['iwconfig', interface])
            for line in scanoutput.splitlines():
                line = line.decode('utf-8')
                position=line.find('Signal level=')
                if (position > 0):
                    signal_strength_str=line[position+13:].strip()
                    print('signal strength -----------> {}'.format(signal_strength_str))

                    if (signal_strength_str.find('dBm')):
                        ss_value = int(signal_strength_str.split(' '))
                        print('         dBm value -----------> {}'.format(ss_value))

                    elif (signal_strength_str.find('/')):
                        ss_value = int(signal_strength_str.split('/'))
                        print('         % value -----------> {}'.format(ss_value))
        except:
            pass
        return signal_strength_str

    # ------------------------------------------------------------------------------------------------
    def get_wifi_ipaddress(self,interface='wlan0'):
        ip_address = '?.?.?.?'
        try:
            foo = psutil.net_if_addrs()
            if_family = foo[interface][0][0]
            if if_family == 2:
                ip_address = foo[interface][0][1]
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
        gigs = (psutil.disk_usage('/').total / 1000 / 1000 / 1000.0)
        ##return f"{gigs:.1f}"
        return round(gigs,1)

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
        origoutput = str(check_output(['cat', '/proc/cpuinfo']))
        ## Older models had a 'Model' section
        start = origoutput.find('Model')
        if (start > 0):
            # Now advance past the colon
            start = origoutput[start:].find(':') + start
            start += 2
            end = origoutput[start:].find('\\n\'')
            model= origoutput[start : (end+start)]
        else:
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
        origoutput = str(check_output(['cat', '/proc/cpuinfo']))
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
        #print('MODEL [{}]'.format(model))
        #print('REV [{}]'.format(rev))
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

        elif '0002' in rev:
            return "B 1.0 256MB Egoman"      
        elif '0003' in rev:
            return "B 1.0 256MB Egoman"
        elif '0004' in rev:
            return "B 2.0 256MB Sony UK"
        elif '0005' in rev:
            return "B 2.0 256MB Qisda"
        elif '0006' in rev:
            return "B 2.0 256MB Egoman"
        elif '0007' in rev:
            return "A 2.0 256MB Egoman"
        elif '0007' in rev:
            return "A 2.0 256MB Sony UK"
        elif '0009' in rev:
            return "A 2.0 256MB Qisda"
        elif '000d' in rev:
            return "B 2.0 512MB Egoman"
        elif '000e' in rev:
            return "B 2.0 512MB Sony UK"
        elif '000f' in rev:
            return "B 2.0 512MB Egoman"
        elif '0010' in rev:
            return "B+ 1.2 512MB Sony UK"
        elif '0011' in rev:
            return "CM1 1.0 512MB Sony UK"
        elif '0012' in rev:
            return "A+ 1.1 256MB Sony UK"
        elif '0013' in rev:
            return "B+ 1.2 512MB Embest"
        elif '0014' in rev:
            return "CM1 1.0 512MB Embest"
        elif '0015' in rev:
            return "A+ 1.1 256MB/512MB Embest"


        # If we got here - we didn't match a revision code
        logging.info( 'Unknown RPi Model {}  Rev {}'.format(model, rev))
        return 'Unknown {}'.format(rev)

    # ------------------------------------------------------------------------------------------------
    def asJSON(self):
        myDict = OrderedDict({
            "topic": 'NODE',
            "host": self.get_hostname(),
            "eth0 IP": self.get_eth_ipaddress(),
            "wlan0 IP": self.get_wifi_ipaddress(),
            "wlan1 IP": self.get_wifi_ipaddress('wlan1'),
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
            
            "signal_strength": self.get_SignalStrength(),

            "model": self.rpi_model_string(),
            "camera_present": self.get_camera_present()
        })
        return json.dumps(myDict)

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
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
        #logging.DEBUG('Sending System Status Info on 'NODE' topic!')
        data = {}
        data['topic'] = 'NODE'
        data['datetime'] = datetime.datetime.now().replace(microsecond=0).isoformat()
        json_data = SystemStats().asJSON()
        print(SystemStats().get_interface_mode())
        self.client.publish('NODE', json_data, qos=0)

    def send_host_status_info(self):
        logging.info('Sending System Status Info on node name topic')
        topic = SystemStats().get_hostname().upper()
        data = {}
        data['datetime'] = datetime.datetime.now().replace(microsecond=0).isoformat()
        json_data = SystemStats().asJSON()
        data['topic'] = topic
        self.client.publish(topic, json_data, qos=0)


def discover_mqtt_host():
    from zeroconf import ServiceBrowser, Zeroconf
    host = None
    info = None

    def on_service_state_change(zeroconf, service_type, name, state_change):
        pass

    zeroconf = Zeroconf()
    browser = ServiceBrowser(zeroconf, "_mqtt._tcp.local.",
                             handlers=[on_service_state_change])
    i = 0
    while not host:
        time.sleep(0.1)
        if browser.services:
            service = list(browser.services.values())[0]
            info = zeroconf.get_service_info(service.name, service.alias)
            ##print('info', info)
            ##print('info.server', info.server)
            host = socket.inet_ntoa(info.address)
        i += 1
        if i > 50:
            break
    zeroconf.close()
    try:
        return info.server, host
    except AttributeError:
        return None


print(SystemStats.version)
logging.basicConfig(filename='/tmp/mqttsysteminfo.log', level=logging.INFO)
logging.info('MQTTSystemInfo v2.1 [signal_strength]')
logging.info('Multicast DNS Service Discovery for Python Browser test')
logging.debug('Attempting to find mqtt broker via mDNS')

try:
   host = sys.argv[1]
   mqtt_broker_address = sys.argv[1]
except:
   print( 'No host passed in on command line. Trying mDNS' )
   
   host = discover_mqtt_host()
   if (host is not None):
       mqtt_broker_address = host[0]
       logging.info( 'Found MQTT Broker using mDNS on {}.{}'.format(host[0], host[1]))
   else:
       logging.warning('Unable to locate MQTT Broker using DNS')
       try:
           mqtt_broker_address = sys.argv[1]
       except:
           logging.critical('mDNS failed and no MQTT Broker address passed in via command line. Exiting')
           sys.exit(1)

logging.debug('Connecting to {}'.format(mqtt_broker_address))
m = MessageHandler(broker_address=mqtt_broker_address)
m.start()

while True:
    m.send_node_status_info()
   
    ##m.send_host_status_info()
    time.sleep(60)
