# Author: Taylor Jordan
# GitHub username: Raptor2k1
# Date: 1/29/2023

import zmq
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
        # Filter out common irrelevant/short words and associated words/strings
        skip_list = ("is", "in", "an", "the", "a", "I", "or", "and", "but", "on", "o", "o'", )
        # Need to append list of all stand-alone alpha characters? (function to append all single ascii chars?)
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
    socket.send_json(send_data)


# Adapted from explanation of strings module located here:
# https://www.scaler.com/topics/remove-special-characters-from-string-python/
def remove_special_chars(substring: str) -> str:
    """Returns an argument string with special characters removed."""
    word = substring.translate(str.maketrans('', '', string.punctuation))
    return word


# START THE SERVER AND REQUEST/REPLY LOOP
# Set up socket container/transport and bind socket
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

print("Server started!\n")

while True:
    # Listen for client request
    request_str = socket.recv().decode()
    request_dict = json.loads(request_str)
    print("Received Request JSON...")

    # Error handling - if not both a strings and images key, reply with an error message
    if "strings" not in request_dict or "images" not in request_dict:
        print("Error: Request contained improper structure. Sending error message.")
        socket.send_string("format_error")
        print("Format error reply sent.")

    else:
        # Create an object for the request
        assignment_request_obj = AssignmentRequest()
        assignment_request_obj.set_images(request_dict["images"])
        assignment_request_obj.set_strings(request_dict["strings"])

        # Process the request object and send appropriate reply
        process_request(assignment_request_obj)
        print("Reply sent.")
