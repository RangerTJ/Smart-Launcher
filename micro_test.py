# Author: Taylor Jordan
# GitHub username: Raptor2k1
# Date: 1/24/2023
# Description:  Test script for interaction with the microservice.

import os
import json


def update_image_list():
    """"""

    image_list = []
    images = os.listdir(path='images')
    for image in images:
        image_list.append(image)
    return image_list


# Generate test data
test_strings = ["I like alf.", "You have a dog.", "What's up?", "You have a baby."]
test_images = update_image_list()
request_dict = {"strings": test_strings, "images": test_images}

# Write the request
request_json = json.dumps(request_dict, indent=4)
with open("test_request.json", "w") as request_pipe:
    request_pipe.write(request_json)

# Pause until verified that the response has been sent
input("Enter any value to continue.")

# Read the response and act on it
with(open("test_response.json", "r")) as response_json:
    response_dict = json.load(response_json)
    print("Demonstration Purposes: Able to recall matching images based on strings used as a key:\n"
          "---------------------------------------------------------------------------------------")
    for key in response_dict.keys():
        print(key + ":", response_dict[key])
        key_path = "images\\" + response_dict[key]
        os.startfile(key_path)

# Note: May need a second response pipeline to verify response received
# Microservice pauses until the OK signal comes in and clears response file at that point
# ... or just does it directly with sockets or something magic like that
