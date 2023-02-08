# Author: Taylor Jordan
# GitHub username: Raptor2k1
# Date: 1/29/2023

import zmq
import json
import string
import re


class AssignmentRequest:
    """An object passed along as an information request. Contains data members for a list of strings, a list of image
    file names, and a list of word."""

    def __init__(self):
        self._strings = []
        self._images = []
        self._words = []
        self._string_image_dict = {}
        self._images_subwords = {}

    def get_strings(self):
        return self._strings

    def get_images(self):
        return self._images

    def get_words(self):
        return self._words

    def get_string_image_dict(self):
        return self._string_image_dict

    def get_path_dict(self):
        return self._images_subwords

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

    def keywords_from_files(self):
        """Scans the local image directory and returns the list of words found within file names within it."""

        # Get images from library and create dictionary entry, keyed to file paths
        images = self._images
        for image in images:
            self._images_subwords[image] = []

        # Parse image file names and add word substrings to a word list
        word_list = []
        for key in self._images_subwords.keys():
            file_string = key

            # Assumes normal 3 letter convention if period is detected at that index and slices extension off
            if key[-4] == ".":
                file_string = key[:-4]

            # Split apart all the word-ish substrings in the filename
            split_words = re.split('[_\-,.]+', file_string)

            # Check for new words from split and add to sub-word list in respective object dictionary
            for word in split_words:
                if word not in word_list:
                    if len(word) > 2:
                        self._images_subwords[key].append(word)


def process_request(request_obj):
    """
    Scans the request pipeline for an object containing a list of strings, a list of image file names,
    and list of words. If no list of words is provided, uses the currently-saved internal list.
    If either the image or string list is empty, returns an error explaining why the request is invalid.
    In either case, clears the request pipeline file after the operation is done.
    """

    # Generate list of words available within image file path names
    request_obj.keywords_from_files()

    # Filter out common irrelevant/short words and associated words/strings
    skip_list = ("the", "and", "but", "for")

    # If wordlist not provided abort the process
    if str(type(request_obj)) != "<class '__main__.AssignmentRequest'>":
        return

    # See if any words within the string are contained with an image filename and assign them if they are.
    else:
        # Check if a substring in image name or if a file substring in request substring, then update association
        string_list = request_obj.get_strings()
        check_forward(request_obj, string_list, skip_list)
        check_reverse(request_obj, skip_list)

        # Send the updated request object to the outgoing pipeline
        send_info(request_obj)


def check_forward(request_obj, string_list, skip_list):
    """
    Checks if any request object's string's substrings are contained within a file name and updates the string-file
    association if it is.
    """
    for req_string in string_list:
        string_words = req_string.split()
        for word in string_words:
            cleaned_word = remove_special_chars(word)
            # print(cleaned_word)
            if cleaned_word.lower() in skip_list or len(cleaned_word) < 3:
                continue  # Skip this substring if it's a known irrelevant factor
            word_image = request_obj.image_for_word(cleaned_word)
            request_obj.update_string_image_dict(req_string, word_image)
            if request_obj.get_string_image_dict()[req_string] != "default.png":
                break  # Move to next string once we know current is assigned to an image


def check_reverse(request_obj, skip_list):
    """
    Iterates through strings in the request object and searches for strings still bound to a default image.
    If they are, checks if any filename substrings are contained within the request object's main string.
    Updates the string-file association if it is.
    """
    for each_string in request_obj.get_strings():
        if request_obj.get_string_image_dict()[each_string] == "default.png":
            for key in request_obj.get_path_dict():
                for word_in_path in request_obj.get_path_dict()[key]:
                    cleaned_img_word = remove_special_chars(word_in_path)
                    print("Target String: " + each_string)
                    print("Word Cleaned:", cleaned_img_word)
                    if cleaned_img_word.lower() in skip_list or len(cleaned_img_word) < 3:
                        print("skipped")
                        continue  # Skip this substring if it's a known irrelevant factor

                    if cleaned_img_word.lower() in each_string.lower():
                        print("found!")

                        request_obj.update_string_image_dict(each_string, key)
                        print(request_obj.get_string_image_dict()[each_string])
                        print("Word Image:", key)

                    if request_obj.get_string_image_dict()[each_string] != "default.png":
                        print("Selected!")
                        break  # Move to next string once we know current is assigned to an image


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


# Set up Server's socket container/transport and bind socket
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.setsockopt(zmq.SNDTIMEO, 500)
socket.setsockopt(zmq.LINGER, 0)
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
        print("Attempted to send reply.")
