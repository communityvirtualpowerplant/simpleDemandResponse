import sys
import asyncio
import json
import signal
import logging
from typing import Any, Dict, Optional, Tuple, List
from deviceClasses.Shelly import ShellyDevice
from deviceClasses.Bluetti import Bluetti
from bluetti_mqtt.bluetooth import (
    check_addresses, scan_devices, BluetoothClient, ModbusError,
    ParseError, BadConnectionError
)
from bluetti_mqtt.core import (
    BluettiDevice, ReadHoldingRegisters, DeviceCommand
)

# ============================
# Shelly Configuration Constants
# ============================
SHELLY_GATT_SERVICE_UUID = "5f6d4f53-5f52-5043-5f53-56435f49445f"
RPC_CHAR_DATA_UUID = "5f6d4f53-5f52-5043-5f64-6174615f5f5f"
RPC_CHAR_TX_CTL_UUID = "5f6d4f53-5f52-5043-5f74-785f63746c5f"
RPC_CHAR_RX_CTL_UUID = "5f6d4f53-5f52-5043-5f72-785f63746c5f"
ALLTERCO_MFID = 0x0BA9  # Manufacturer ID for Shelly devices

# not in use
BLUETTI_GATT_SERVICE_UUID = "0000ff00-0000-1000-8000-00805f9b34fb"

printInfo = True
printDebug = True
printError = True
#logging.basicConfig(level=logging.DEBUG)

fileName = 'data/devices.json'

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

async def main() -> None:
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

    for entry in devices:
        if entry['manufacturer'] == 'shelly':
            selected_device_info = entry

            shelly = ShellyDevice(entry["address"], 0, 1)

        else:
            bluetti = Bluetti(entry["address"])

    # result = await execute_toggle(device)

    # if result:
    #     print(f"RPC Method '{rpc_method}' executed successfully. Result:")
    #     print_with_jq(result.get("result", {}))
    # else:
    #     print(f"RPC Method executed successfully. No data returned.")

    result = await getStatusShelly(shelly)

    if result:
        print(f"RPC Method executed successfully. Result:")
        #print(json.dumps(result.get("result", {})))

        data = result.get("result", {})
        #print(json.dumps(data))
        try:
            print(f"Channel 0: {data['input:0']}")
            print(f"Channel 1: {data['input:1']}")
            print(f"Switch 0: {data['switch:0']}")
            print(f"Switch 1: {data['switch:1']}")
        except:
            print('no data???')

    else:
        print(f"RPC Method executed successfully. No data returned.")

    result = await getStatusBluetti(bluetti)

# get status
async def getStatusShelly(device: ShellyDevice):

    #id_input = 0
    params = None
    rpc_method='Shelly.GetStatus'
    
    try:
        result = await device.call_rpc(rpc_method, params=params)
        if result:
            print(f"RPC Method '{rpc_method}' executed successfully. Result:")
        else:
            print(f"RPC Method '{rpc_method}' executed successfully. No data returned.")

    except Exception as e:
        print(f"Unexpected error during command execution: {e}")

    return result
        
# async def getStatusBluetti(device: BluettiDevice):

#     method='get_status'

#     try:
#         print(f'Connecting to {device.address}')
#         client = BluetoothClient(device.address)
#         asyncio.get_running_loop().create_task(client.run())

#         # Wait for device connection
#         while not client.is_ready:
#             print('Waiting for connection...')
#             await asyncio.sleep(1)
#             continue

#         # Poll device
#         #while True:
#         for command in device.log_command:
#             commandResponse = await log_command(client, device, command)
#             for k,v in commandResponse.items():
#                 print(k + ": " + str(v))
#                 myData[k]=v
    
#     except Exception as e:
#         print(f"Unexpected error during command execution: {e}")

#     #print(myData)
#     return result


async def getStatusBluetti(device: BluettiDevice):

    address = device.address

    myData={
    }

    devices = await check_addresses({address})
    if len(devices) == 0:
        sys.exit('Could not find the given device to connect to')
    device = devices[0]

    print(f'Connecting to {device.address}')
    client = BluetoothClient(device.address)
    asyncio.get_running_loop().create_task(client.run())

    # Wait for device connection
    while not client.is_ready:
        print('Waiting for connection...')
        await asyncio.sleep(1)
        continue

    # Poll device
    #while True:
    for command in device.logging_commands:
        commandResponse = await device.logging_commands(client, device, command)
        for k,v in commandResponse.items():
            print(k + ": " + str(v))
            myData[k]=v
    
    return myData


async def log_command(client: BluetoothClient, device: BluettiDevice, command: DeviceCommand):
    response_future = await client.perform(command)
    try:
        response = cast(bytes, await response_future)
        if isinstance(command, ReadHoldingRegisters):
            body = command.parse_response(response)
            parsed = device.parse(command.starting_address, body)
            return parsed #print(parsed.keys())
        #log_packet(log_file, response, command)
    except (BadConnectionError, BleakError, ModbusError, ParseError) as err:
        print(f'Got an error running command {command}: {err}')
        #log_invalid(log_file, err, command)


if __name__ == "__main__":
    # Suppress FutureWarnings
    import warnings

    warnings.simplefilter("ignore", FutureWarning)

    # Setup signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log_info("Script interrupted by user via KeyboardInterrupt.")
    except Exception as e:
        log_error(f"Unexpected error in main: {e}")