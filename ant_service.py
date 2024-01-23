import csv
import math
import os
import uuid
import datetime

from openant.easy.node import Node
from openant.devices import ANTPLUS_NETWORK_KEY
from openant.devices.common import DeviceType
from openant.devices.scanner import Scanner
from openant.devices.utilities import auto_create_device
from dotenv import load_dotenv
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeCallback
from pubnub.exceptions import PubNubException


def writeToCsv(service):
    speed_fields = ['timestamp', 'speed', 'distance'] 
    cadence_fields = ['timestamp', 'cadence']
    heart_rate_fields = ['timestamp', 'heart_rate']

    if service.recorded_data_cadence or service.recorded_data_heart_rate or service.recorded_data_speed:
        file_key = uuid.uuid4()

        with open(f'./public/{file_key}_speed.csv', 'w', newline='') as file: 
            writer = csv.DictWriter(file, fieldnames = speed_fields)
            writer.writeheader() 
            if service.recorded_data_speed:
                for row in service.recorded_data_speed:
                    speed = row['speed'] if row['speed'] else '0'
                    distance = row['distance'] if row['distance'] else '0'
                    writer.writerow({'timestamp': row['timestamp'], 'speed': speed, 'distance': distance})

        with open(f'./public/{file_key}_cadence.csv', 'w', newline='') as file: 
            writer = csv.DictWriter(file, fieldnames = cadence_fields)
            writer.writeheader() 
            if service.recorded_data_cadence:
                for row in service.recorded_data_cadence:
                    cadence = row['cadence'] if row['cadence'] else '0'
                    writer.writerow({'timestamp': row['timestamp'], 'cadence': cadence})

        with open(f'./public/{file_key}_heart_rate.csv', 'w', newline='') as file: 
            writer = csv.DictWriter(file, fieldnames = heart_rate_fields)
            writer.writeheader() 
            if service.recorded_data_heart_rate:
                for row in service.recorded_data_heart_rate:
                    heart_rate = row['heart_rate'] if row['heart_rate'] else '0'
                    writer.writerow({'timestamp': row['timestamp'], 'heart_rate': heart_rate})

        return file_key
    else:
        return False


class GeneralService:
    def __init__(self):
        self.recording = False
        self.recorded_data_speed = []
        self.recorded_data_cadence = []
        self.recorded_data_heart_rate = []
    
    def clear(self):
        self.recorded_data_speed = []
        self.recorded_data_cadence = []
        self.recorded_data_heart_rate = []

    def start(self):
        self.recording = True

    def stop(self):
        self.recording = False

    def record_speed(self, data):
        self.recorded_data_speed.append(data)

    def record_cadence(self, data):
        self.recorded_data_cadence.append(data)

    def record_heart_rate(self, data):
        self.recorded_data_heart_rate.append(data)


def auto_scanner(file_path=None, device_id=0, device_type=0, auto_create=False):
    # list of auto created devices
    devices = []

    local_service = GeneralService()

    WHEEL_CIRCUMFERENCE = 1.127

    load_dotenv()

    # ANT USB node
    node = Node()
    node.set_network_key(0x00, ANTPLUS_NETWORK_KEY)

    # the scanner
    scanner = Scanner(node, device_id=device_id, device_type=device_type)

    PUBNUB_DEFAULT_CHANNEL = os.environ['NEXT_PUBLIC_PUBNUB_DEFAULT_CHANNEL']
    PUBNUB_USER = 'ant_service'

    # pubnub?
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = os.environ['NEXT_PUBLIC_PUBNUB_SUB_KEY']
    pnconfig.publish_key = os.environ['NEXT_PUBLIC_PUBNUB_PUB_KEY']
    pnconfig.user_id = 'ant_service'
    pubnub = PubNub(pnconfig)

    pubnub.subscribe() \
        .channels(PUBNUB_DEFAULT_CHANNEL) \
        .execute()

    class SubscribeHandler(SubscribeCallback):
        def presence(self, pubnub, presence):
            pass  # Handle incoming presence data

        def message(self, pubnub, message):
            if message.publisher != PUBNUB_USER:
                if message.message['action'] == 'record':
                    handleSetRecording(message.message['record'])

        def signal(self, pubnub, signal):
            pass # Handle incoming signals

        def file(self, pubnub, file_message):
            pass # Handle incoming files

    pubnub.add_listener(SubscribeHandler())


    def handleRecordStop():
        file_key = writeToCsv(local_service)

        if file_key:
            data_dict = {
                'uuid': str(file_key),
                'action': 'statsReady'
            }

            # publish file_key to pubnub channel
            try:
                envelope = pubnub.publish().channel(PUBNUB_DEFAULT_CHANNEL).message(data_dict).sync()
                # print("publish timetoken: %d" % envelope.result.timetoken)
            except PubNubException as e:
                print(e)

        # clear the data lists
        local_service.clear()

    def handleSetRecording(record):
        local_service.recording = record
        print('recording is now', local_service.recording)
        if not local_service.recording:
            handleRecordStop()

    # local function to call when device updates common data
    def on_update(device_tuple, common):
        device_id = device_tuple[0]
        print(f"Device #{device_id} commond data update: {common}")

    # local function to call when device update device speific page data
    def on_device_data(device, page_name, data):
        data_dict = {
            'device_name': device.name,
            'device_id': device.device_id,
            'broadcast': page_name,
            'timestamp': datetime.datetime.now().timestamp(),
        }

        if 'speed' in page_name:
            # calculate_distance accepts tire/wheel circumference in meters, float
            distance = data.calculate_distance(2.127) / 1000
            speed = data.calculate_speed(2.127)
            # device_timestamp = data.cumulative_operating_time

            if speed:
                data_dict['speed'] = round(speed, 2)
            else:
                data_dict['speed'] = speed

            if distance:
                data_dict['distance'] = round(distance, 2)
            else:
                data_dict['distance'] = distance

            data_dict['device_type'] = 'speed'

        if 'cadence' in page_name:
            cadence = data.cadence
            # device_timestamp = data.cumulative_operating_time

            if cadence:
                data_dict['cadence'] = round(cadence, 2)
            else:
                data_dict['cadence'] = cadence

            data_dict['device_type'] = 'cadence'

        if 'heart_rate' in page_name:
            heart_rate = data.heart_rate
            # device_timestamp = data.operating_time

            if heart_rate:
                data_dict['heart_rate'] = round(heart_rate, 2)
            else:
                data_dict['heart_rate'] = heart_rate

            data_dict['device_type'] = 'heart_rate'

        # print(data_dict)
        if local_service.recording:
            if 'cadence' in page_name:
                local_service.record_cadence(data_dict)
            elif 'speed' in page_name:
                local_service.record_speed(data_dict)
            elif 'heart_rate' in page_name:
                local_service.record_heart_rate(data_dict)

        # publish to pubnub channel
        try:
            envelope =  pubnub.publish().channel(PUBNUB_DEFAULT_CHANNEL).message(data_dict).sync()
            # print("publish timetoken: %d" % envelope.result.timetoken)
        except PubNubException as e:
            print(e)

    # local function to call when a device is found - also does the auto-create if enabled
    def on_found(device_tuple):
        device_id, device_type, device_trans = device_tuple
        print(
            f"Found new device #{device_id} {DeviceType(device_type)}; device_type: {device_type}, transmission_type: {device_trans}"
        )

        if auto_create and len(devices) < 16:
            try:
                dev = auto_create_device(node, device_id, device_type, device_trans)
                # closure callback of on_device_data with device
                dev.on_device_data = lambda _, page_name, data: on_device_data(
                    dev, page_name, data
                )
                devices.append(dev)
            except Exception as e:
                print(f"Could not auto create device: {e}")

    # add callback functions to scanner
    scanner.on_found = on_found
    scanner.on_update = on_update

    # start scanner, exit on keyboard and clean up USB device on exit
    try:
        print(
            f"Starting scanner for #{device_id}, type {device_type}, press Ctrl-C to finish"
        )
        node.start()
    except KeyboardInterrupt:
        print(f"Closing ANT+ node...")
    finally:
        scanner.close_channel()
        if file_path:
            print(f"Saving/updating found devices to {file_path}")
            scanner.save(file_path)

        for dev in devices:
            dev.close_channel()

        node.stop()


def _run(args):
    if args.device_type == DeviceType.Unknown.name:
        device_type = 0
    else:
        device_type = DeviceType[args.device_type].value

    auto_scanner(
        file_path=args.outfile,
        device_id=args.device_id,
        device_type=device_type,
        auto_create=True,
    )

def main():
    auto_scanner(
        file_path='./log.json',
        device_id=0,
        device_type=0,
        auto_create=True,
    )

main()


def add_subparser(subparsers, name="cadence"):
    parser = subparsers.add_parser(
        name=name,
        description="Scan for ANT+ devices and print information to terminal/save to file",
    )
    parser.add_argument(
        "--logging",
        dest="logLevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )
    parser.add_argument(
        "--outfile",
        "-o",
        type=str,
        help=".json file to save found device info",
    )
    parser.add_argument(
        "--device_type",
        "-t",
        type=str,
        default=DeviceType.Unknown.name,
        choices=[x.name for x in DeviceType],
        help="Device type to scan for, default Unknown is all",
    )
    parser.add_argument(
        "--device_id",
        "-i",
        type=int,
        default=0,
        help="Device ID to scan for, default 0 is all",
    )
    parser.add_argument(
        "--auto_create",
        "-a",
        action="store_true",
        help="Auto-create device profile object and print device page data updates",
    )

    parser.set_defaults(func=_run)
