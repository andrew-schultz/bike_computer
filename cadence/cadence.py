import math
import re
import sys
import time
import os

from ant.core import driver, node, event, message
from ant.core.constants import *
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub
from pubnub.exceptions import PubNubException

import time
import random

load_dotenv()

NETKEY = b'\xB9\xA5\x21\xFB\xBD\x72\xC3\x45'
PUBNUB_DEFAULT_CHANNEL = os.environ['NEXT_PUBLIC_PUBNUB_DEFAULT_CHANNEL']

# pubnub?
pnconfig = PNConfiguration()
pnconfig.subscribe_key = os.environ['NEXT_PUBLIC_PUBNUB_SUB_KEY']
pnconfig.publish_key = os.environ['NEXT_PUBLIC_PUBNUB_PUB_KEY']
pnconfig.user_id = "my_custom_user_id"
pubnub = PubNub(pnconfig)

class ANTListener(event.EventCallback):
    last_speed_time = 0
    last_speed_revs = 0
    now_speed_revs = 0
#    fivesec_speed_revs = 0
#    tensec_speed_revs = 0
    last_cadence_time = 0
    last_cadence_revs = 0
    now_cadence_revs = 0
#    fives_cadence_revs = 0
    tens_cadence_revs = 0
    wheel_diameter = 0.673 ## Wheel diameter in m

    def process(self, msg, _channel):
        print('processing')
        if isinstance(msg, message.ChannelBroadcastDataMessage):
            self.last_cadence_revs = self.now_cadence_revs
            self.last_speed_revs = self.now_speed_revs
            ## Process Cadence Cumulative Revolutions
            ## ctimeLSB = msg.payload[1],ctimeMSB = msg.payload[2],cadenceLSB = msg.payload[3], cadenceMSB = msg.payload[4]
            ctime = int(format(msg.payload[2],'#010b')+re.sub('0b','',format(msg.payload[1],'#010b')),2)
            self.now_cadence_revs = int(format(msg.payload[4],'#010b')+re.sub('0b','',format(msg.payload[3],'#010b')),2)
            ## Precess Speed Cumulative Revolutions
            ## stimeLSB = msg.payload[5],stimeMSB = msg.payload[6],speedLSB = msg.payload[7],speedMSB = msg.payload[8]
            stime = int(format(msg.payload[6],'#010b')+re.sub('0b','',format(msg.payload[5],'#010b')),2)
            self.now_speed_revs = int(format(msg.payload[8],'#010b')+re.sub('0b','',format(msg.payload[7],'#010b')),2)

            speed_rev_delta = self.now_speed_revs - self.last_speed_revs
            speed_time_delta = stime - self.last_speed_time
            cadence_rev_delta = self.now_cadence_revs - self.last_cadence_revs
            cadence_time_delta = ctime - self.last_speed_time
            speed = (speed_rev_delta/speed_time_delta)*1024*(self.wheel_diameter*math.pi*60*60/1000) ## rev/sec x 0.673*math.pi m/rev x 1km/1000m x 60s/min x 60min/hr
            cadence = (cadence_rev_delta/cadence_time_delta)*1024*60

            stat_dict = {
                'cadence_timestamps': ctime/1024,
                'cadence_revolutions': self.now_cadence_revs,
                'cadence_rev_delta': cadence_rev_delta,
                'cadence_time_delta': cadence_time_delta,
                'cadence': cadence,
                'speed_timestamps': stime/1024,
                'speed_revolutions': self.now_speed_revs,
                'speed_rev_delta': speed_rev_delta,
                'speed_time_delta': speed_time_delta,
                'speed': speed,
            }

            # publish to pubnub channel
            try:
                envelope =  pubnub.publish().channel(PUBNUB_DEFAULT_CHANNEL).message(stat_dict).sync()
                print("publish timetoken: %d" % envelope.result.timetoken)
            except PubNubException as e:
                print(e)

            print("Cadence Timestamps: ", stat_dict['cadence_timestamps'],"|| Cadence Revolutions: ", self.now_cadence_revs)
            print("Cadence Rev Delta: ", cadence_rev_delta, " Cadence Time Delta", cadence_time_delta, " cadence: ", cadence, " RPM")
            print("Speed Timestamps: ", stat_dict['speed_timestamps'], "|| Speed Revolutions: ", self.now_speed_revs)
            print("Speed Rev Delta: ", speed_rev_delta, " Speed Time Delta", speed_time_delta, " Speed: ", speed, " km/hr")
            print("=============")
            self.last_speed_time = stime
            self.last_cadence_time = ctime


    # guy said he'd have issues with connecting to the ant+ dongle, I bet cause he hard coded the device id here
    # can we update to have it scan for whatever is in use?
            
    antDevice = '/dev/ttyUSB0'
    antVendor = 0x0fcf
    # antProduct=0x1009
    antProduct = 0x1008
    stick = driver.USB2Driver(idVendor=antVendor, idProduct=antProduct)
    print('stick', stick.__dict__)
    antnode = node.Node(stick)
    print('antnode', antnode.__dict__)
    antnode.start()
    channel = antnode.getFreeChannel()

    def setup(self):
        print('seting up')
        # Start shit up
        #stick = driver.USB2Driver()
        if not self.antnode.running:
            self.antnode.start()

        # Setup channel
        net = node.Network(name='N:ANT+', key=NETKEY)
        self.antnode.setNetworkKey(0, net)
        self.channel.name = 'C:HRM'
        self.channel.assign(net, CHANNEL_TYPE_TWOWAY_RECEIVE)
        self.channel.setID(121, 0, 0)
        self.channel.searchTimeout = TIMEOUT_NEVER
        self.channel.period = 8070
        self.channel.frequency = 57
        self.channel.open()

    def start_listen(self):
        print('starting listen')

        if not self.antnode.running:
            print('woops gotta setup')
            self.setup()
        # Setup callback
        # Note: We could also register an event listener for non-channel events by
        # calling registerEventListener() on antnode rather than channel.
        self.channel.registerCallback(ANTListener())

    def stop_listen(self):
        # Shutdown
        self.channel.close()
        self.channel.unassign()
        self.antnode.stop()

def init_main():
    listener = ANTListener()
    listener.setup()
    listener.start_listen()

init_main()
    
def main():
    go = 1
    while go:
        speed = random.random()
        cadence = random.random()
        stat_dict = {
            'cadence_timestamps': '123',
            'cadence_revolutions': '23',
            'cadence_rev_delta': '123',
            'cadence_time_delta': '123',
            'cadence': cadence,
            'speed_timestamps': '123',
            'speed_revolutions': '123',
            'speed_rev_delta': '123',
            'speed_time_delta': '123',
            'speed': speed,
        }

        # publish to pubnub channel
        try:
            envelope =  pubnub.publish().channel(PUBNUB_DEFAULT_CHANNEL).message(stat_dict).sync()
            print("publish timetoken: %d" % envelope.result.timetoken)
        except PubNubException as e:
            print(e)

        time.sleep(1.0)

# main()