# to run, include these arguments
# role: aggregator or node
# if node, specific location for devices

import sys
import asyncio
import json
import signal
import logging
import time
from typing import cast
from typing import Any, Dict, Optional, Tuple, List
from components.Shelly import ShellyDevice
from components.Bluetti import Bluetti
from components.MQTT import Node
from bluetti_mqtt.bluetooth import (
    check_addresses, scan_devices, BluetoothClient, ModbusError,
    ParseError, BadConnectionError
)
from bluetti_mqtt.core import (
    BluettiDevice, ReadHoldingRegisters, DeviceCommand
)


printInfo = True
printDebug = True
printError = True
#logging.basicConfig(level=logging.DEBUG)

fileName = 'data/devices.json'

#if an arg has been passed
if len(sys.argv) > 0:
    location = sys.argv[1]
else:
    location = ''


# ============================
# Logging Helper
# ============================
def log_info(message: str) -> None:
    """Logs an info message."""
    logging.info(message)
    log_print(message, printInfo)

def log_error(message: str) -> None:
    """Logs an error message."""
    logging.error(message)
    log_print(message, printError)

def log_debug(message: str) -> None:
    """Logs a debug message."""
    logging.debug(message)
    log_print(message, printDebug)

def log_print(message:str, b:bool):
    if b:
        print(message)

# ============================
# Utilities
# ============================
def handle_signal(signal_num: int, frame: Any) -> None:
    """Handles termination signals for graceful shutdown."""
    log_info(f"Received signal {signal_num}, shutting down gracefully...")
    sys.exit(0)

# this packages up all the data for MQTT publishing
async def log(freq):
    allData = {

    }

    while True:

        # allData['CT'] = ct.data # current
        # allData['Power Station'] = ps.data #battery %, power, etc

        # if ina219 != False:
        #     allData['RPi'] = ina219.data # current, voltage, power
        # if ina260 != False:
        #     allData['PV'] = ina260.data # current, voltage, power
        # allData['R1'] = dl.state #

        #print(allData)

        mqtt.publish(packageData(allData))
        await asyncio.sleep(freq)


def packageData(data):

    pData = {}

    pData['battery'] = data['Power Station']['total_battery_percent']
    pData['ac_out'] = data['Power Station']['ac_output_power']
    pData['ac_in'] = data['Power Station']['ac_input_power']
    pData['dc_out'] = data['Power Station']['dc_output_power']
    pData['dc_in'] = data['Power Station']['dc_input_power']
    pData['r1'] = data['R1']
    if ina260 != False:
        pData['pv'] = data['PV']['power W']
    else:
        pData['pv'] = False
    if ina219 != False:
        pData['rpi']=data['RPi']['power W']
    else:
        pData['rpi']= False
    pData['load'] = data['CT']['current A'] * 120 #convert CT Irms to W
    return pData
    
async def main(location):
    network = "BoroughHall"
    mqtt = Node()
    
    # listener
    mqtt.start()

    # Read data from a JSON file
    try:
        with open(fileName, "r") as json_file:
            devices = json.load(json_file)
    except Exception as e:
        log_error(f"Error during reading devices.json file: {e}")
        savedDevices = []

    if not devices:
        log_error("No devices found. Exiting")
        sys.exit(0)

    s = asyncio.create_task(shellyLoop(location,devices))
    await s

    # for entry in devices:
    #     if entry['location'] == location:
    #         if entry['manufacturer'] == 'bluetti':
    #             entry['device'] = Bluetti(entry["address"],entry["name"])
    #             try:
    #                 result = await getStatusBluetti(entry['device'])
    #             except Exception as e:
    #                 log_error(f"Error getting Bluetti status: {e}")
    #                 return

    #             if result:
    #                 print(f"Method executed successfully. Result:")
    #                 print(result)

    #             else:
    #                 print(f"Method executed successfully. No data returned.")
       
async def shellyLoop(location,devices):  

    while True:
        for entry in devices:
            if entry['location'] == location:
                if entry['manufacturer'] == 'shelly':

                    entry['device'] = ShellyDevice(entry["address"], entry["name"])
                    try:
                        result = await getStatusShelly(entry['device'])

                        if result:
                            print(f"RPC Method executed successfully. Result:")
                            print(json.dumps(result))

                        else:
                            print(f"RPC Method executed successfully. No data returned.")
                    except Exception as e:
                        log_error(f"Error getting Shelly status: {e}")
            await asyncio.sleep(20)



if __name__ == "__main__":

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        asyncio.run(main(location))
    except KeyboardInterrupt:
        log_info("Script interrupted by user via KeyboardInterrupt.")
    except Exception as e:
        log_error(f"Unexpected error in main: {e}")
