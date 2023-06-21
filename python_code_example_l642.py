import requests
from requests.auth import HTTPBasicAuth
import cv2
import urllib
import numpy as np
import os
import json
import time
import asyncio
import websockets
import re
from datetime import datetime
import math

# GLOBAL VARIABLES
# ADJUST THESE BASED ON YOUR OWN NEEDS
DEVICE_AUTHENTICATION = HTTPBasicAuth("admin", "admin")
BASIC_HEADER = {"Content-type": "application/json"}
ADDRESS = "178913009.local"
BASE_URL = "http://{}:9011".format(ADDRESS)
WEBSOCKET_URL = "ws://{}:9012".format(ADDRESS)
SOUND_IMAGE_THRESHOLD = 60
SOUNDSURFACE_COLS = 48
SOUNDSURFACE_ROWS = 36


def helper_date_string_to_time(date_string):
    return datetime.strptime(date_string[0:-9], "%Y-%m-%dT%H:%M:%S.%f").timestamp()


def helper_shape_to_np_array(list, shape):
    np_array = np.array(list)
    np_array.shape = (shape)
    return np_array




# Subscribe to a measurement and get data continuously
async def example_listen_to_measurement_data():
    print("Starting example_listen_to_measurement_data...")
    
    # Create the specified measurement
    soundsurface_response = requests.get(BASE_URL + "/soundsurfaces", auth=DEVICE_AUTHENTICATION, headers=BASIC_HEADER).json()

    print("Creating and connecting to websocket...")
    # create websocket
    async with websockets.connect(WEBSOCKET_URL) as websocket:
        try:
            # get the websocket id of the websocket just created
            websocket_id = json.loads(await websocket.recv())
            
            # print(soundsurface_response)
            # print(websocket_id)

            # create the body for the subscription call
            json_body = {
                "callbackChannelId": websocket_id["id"]
            }

            # subscribe on the soundsurface with the created websocket as output
            requests.post(BASE_URL + "/data/soundsurface/{}/subscription".format(soundsurface_response[0]["id"]), auth=DEVICE_AUTHENTICATION, data=json.dumps(json_body), headers=BASIC_HEADER).json()

            # loop for 1 second and print data (can be changed to loop forever or until a kill switch is pressed)
            t_end = time.time() + 1
            print("Printing measurement data for the next 1 second:")
            while time.time() < t_end:
                response_websocket = await websocket.recv()
                response_websocket = json.loads(response_websocket)
                # print response gotten through the websocket
                print(response_websocket)
                print(len(response_websocket["values"]))
                
                # Write the array to a file
                file_path = "results.txt"  
                # Open the file in write mode
                file = open(file_path, "w")
                # Convert the variable to a string and write it to the file
                file.write(str(response_websocket))
                # Close the file
                file.close()
        except Exception as e:
            # print error message
            print("Request failed with response: {}".format(e))


asyncio.run(example_listen_to_measurement_data())
# asyncio.run(example_listen_to_event_data())
print("Done.")
