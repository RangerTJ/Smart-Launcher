# Author: Taylor Jordan
# GitHub username: Raptor2k1
# Date: 1/24/2023
# Description:  Microservice to take a requested JSON dictionary of "images":[array of image file names] and
#               "string":[array of strings] and send a response JSON of string keys with matching image file
#               name values.

import json
import string


class AssignmentRequest:
    """An object passed along as an information request. Contains data members for a list of strings, a list of image
    file names, and a list of word."""

    def __init__(self):
        self._strings = []
        self._images = []
        self._words = []
        self._string_image_dict = {}

    def get_strings(self):
        return self._strings

    def get_images(self):
        return self._images

    def get_words(self):
        return self._words

    def get_string_image_dict(self):
        return self._string_image_dict

    def set_strings(self, string_list):
        self._strings = string_list

    def set_images(self, image_file_list):
        self._images = image_file_list

    def set_words(self, word_list):
        self._words = word_list

    def update_string_image_dict(self, arg_string, image):
        """Adds to or updates an entry in the object's word-image path dictionary."""
        self._string_image_dict[arg_string] = image

    def image_for_word(self, word) -> str:
        """Assigns a word (in a request object) to the first matching file name string found."""
        for image in self._images:
            if word.lower() in image.lower():
                return image

        # Return default image if no matches
        return "default.png"


def process_request(request_obj):
    """
    Scans the request pipeline for an object containing a list of strings, a list of image file names,
    and list of words. If no list of words is provided, uses the currently-saved internal list.
    If either the image or string list is empty, returns an error explaining why the request is invalid.
    In either case, clears the request pipeline file after the operation is done.
    """

    # If wordlist not provided abort the process
    if str(type(request_obj)) != "<class '__main__.AssignmentRequest'>":
        return

    # See if any words within the string are contained with an image filename and assign them if they are.
    else:
        # Filter out common irrelevant/short words and associate words/strings
        skip_list = ("is", "in", "an", "the", "a", "I")
        # Need to append list of all stand-alone alpha characters
        string_list = request_obj.get_strings()
        for req_string in string_list:
            string_words = req_string.split()
            for word in string_words:
                cleaned_word = remove_special_chars(word)
                if cleaned_word in skip_list:
                    continue  # Skip this substring if it's a known irrelevant factor
                word_image = request_obj.image_for_word(cleaned_word)
                request_obj.update_string_image_dict(req_string, word_image)
                if request_obj.get_string_image_dict()[req_string] != "default.png":
                    break  # Move to next string once we know current is assigned to an image

        # Send the updated request object to the outgoing pipeline
        send_info(request_obj)


def send_info(request_obj):
    """
    Updates the return pipeline file with a key and path that matches the input string received.
    Takes an array of request objects as a parameter, each having data members for a string, a key,
    an image file name, and a path to the image.
    """
    # open and write self.request's object or its dictionary attribute
    send_data = request_obj.get_string_image_dict()
    send_data_json = json.dumps(send_data, indent=4)
    with open("test_response.json", "w") as reply_pipe:
        reply_pipe.write(send_data_json)


# Adapted from explanation of strings module located here:
# https://www.scaler.com/topics/remove-special-characters-from-string-python/
def remove_special_chars(substring: str) -> str:
    """Returns an argument string with special characters removed."""
    word = substring.translate(str.maketrans('', '', string.punctuation))
    return word


def check_request_pipeline(pipe_path):
    """
    Opens/closes inbound pipeline file and checks for an assignment request.
    Returns the conversion request as a string, otherwise returns nothing.
    Parameter of pipeline data file to check.
    """

    # Read request pipe data
    with open(pipe_path, "r", encoding="utf-8") as request_pipe:
        requests = request_pipe.read()

    # Return requested pipe data after loading it from JSON
    return json.loads(requests)


# MICROSERVICE OPERATION - Auto-process method
while True:
    with(open("test_request.json", "r")) as request_json:
        request_dict = json.load(request_json)
        if request_dict:
            print("Valid request found!")
            assignment_request_obj = AssignmentRequest()
            assignment_request_obj.set_images(request_dict["images"])
            assignment_request_obj.set_strings(request_dict["strings"])
            process_request(assignment_request_obj)
            print("Response sent")

            # Clear request after processed
            with(open("test_request.json", "w")) as reset_json:
                reset_json.write("{}")
            print("Request pipeline reset")





# Manual process mehod
# # Read the request pipeline and create a temporary request object for it
# assignment_request_obj = AssignmentRequest()
# with(open("test_request.json", "r")) as request_json:
#     request_dict = json.load(request_json)
#     assignment_request_obj.set_images(request_dict["images"])
#     assignment_request_obj.set_strings(request_dict["strings"])
#
# # Process the request and update the response pipeline
# process_request(assignment_request_obj)


# Need to further refine skip list for 1-3 letter common stand-alone filler words
# May adjust opening and read/writing JSON to sockets... or something better?
# Using JSON format means that request/reply data structures should be consistent though, regardless of how it's called
