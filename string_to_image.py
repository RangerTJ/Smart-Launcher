# Author: Taylor Jordan
# GitHub username: Raptor2k1
# Date: 1/22/2023
# Description:  Program that associates a folder of image files with words. Dynamically associates uses these words to
#               associate input strings with related images, assuming the images are named in ways that contain key
#               words. Capable of checking a microservice request list and replying with pre-determined associations

import os
import time
import json
import string
import re
import zmq

default_file = "default.png"


class WordImageTool:
    """Represents a collection of words that are associated with specific image files and their affiliated functions."""
    def __init__(self):
        self._images = []
        self._request = None

    def main_menu(self):
        """
        Triggered upon first starting the program or any time the user selects an option to return to the main menu.
        No parameters. Returns nothing when quitting, otherwise triggers different operational loop paths.
        """

        # Update the image directory then start things up
        self.update_image_list()
        mode = input("\nString to Image converter: MAIN MENU\n"
                     "------------------------------------\n"
                     " Associate a string with an image!\n"
                     "------------------------------------\n"
                     "*Input '1' to MATCH A STRING: Type a string and display its matching image.\n"
                     "*Input '2' for REQUEST A SURPRISE: Displays a surprise phrase and image!\n"
                     "*Input '3' for IMAGE DIRECTORY: Lists all images currently available for assignment.\n"
                     "*Input 'HELP' to for additional instructions on all features.\n"
                     "*Input 'QUIT' to CLOSE this application.\n"
                     ">>>")

        # Handle user decisions
        if mode == "1":
            self.manual_menu()

        elif mode == "2":
            self.surprise_menu()

        elif mode == "3":
            print("Current Files Available for Association\n"
                  "-----------------------------------------\n")
            self.list_images()
            print("\n")

        elif mode.lower() == "help":
            help_me(0)
            self.main_menu()

        elif mode.lower == "quit":
            print("Closing the application...")
            time.sleep(1)
            quit()

        else:
            self.main_menu()

    # Primary Functional Loops
    def manual_menu(self):
        """"""

        self.update_image_list()
        choice = input("\nString to Image converter: MATCH A STRING\n"
                       "------------------------------------\n"
                       "  Input a string and see its image!\n"
                       "------------------------------------\n"
                       "*Input '1' to START.\n"
                       "*Input '2' to return to the MAIN MENU.\n"
                       "*Input 'HELP' to for additional instructions on manually assigning text to an image.\n"
                       ">>>")

        # Type a string and match it to an image
        if choice == '1':
            my_string = input("\nType in your new string now. Hit 'Enter' when you are done to submit it.\n"
                              "You will then be presented with the available image that best corresponds.\n")
            self.string_to_image_display(my_string)
            self.manual_menu()

        elif choice.lower() == "2":
            self.main_menu()

        elif choice.lower() == "help":
            help_me(1)
            self.manual_menu()

        elif choice.lower == "quit":
            print("Closing the application...")
            time.sleep(1)
            quit()

        else:
            self.main_menu()

    # PLACEHOLDER CONTENT
    def surprise_menu(self):
        """
        Triggered upon first starting the program or any time the user selects an option to return to the main menu.
        No parameters. Returns nothing when quitting, otherwise triggers different operational loop paths.
        """

        mode = input("\nString to Image converter: REQUEST A SURPRISE\n"
                     "----------------------------\n"
                     " View a Surprise Image!\n"
                     "---------------------------\n"
                     "*Input '1' to see a surprise image!\n"
                     "*Input '2' to return to the MAIN MENU.\n"
                     "*Input 'HELP' to for additional instructions on all features.\n"
                     "*Input 'QUIT' to CLOSE this application.\n"
                     ">>>")

        # Handle user decisions
        if mode == "1":
            surprise = request_surprise()
            self.string_to_image_display(surprise)
            self.surprise_menu()

        elif mode.lower() == "2":
            self.main_menu()

        elif mode.lower() == "help":
            help_me(0)
            self.surprise_menu()

        elif mode.lower == "quit":
            print("Closing the application...")
            time.sleep(1)
            quit()

        else:
            self.surprise_menu()

    # Helper Methods
    def string_to_image_display(self, arg_string):
        """
        Breaks down an argument string into sub-strings and searches each one for each key word in the gallery dict.
        If one is found, the associated image in the dictionary is displayed (for a local-call). The matched image path
        image is also passed along for use by the listening mode loop (as a string).
        """

        # Call microservice to request association
        chosen_image = self.request_association(arg_string)
        print("Displaying", chosen_image, "in 1 second...")
        time.sleep(1)
        os.startfile("images\\" + chosen_image)
        return

    def request_association(self, user_input: str):
        """
        Requests the association of a string with an image using an association microservice.
        Sends an array containing the one string to associate and the current list of locally-available images.
        Receives a dictionary of the string and image path to associate with it and decodes it.
        Returns the image to associate with the file.
        """

        # Connect the socket to the server - timeout set to half a second, since locally processed
        context = zmq.Context()
        print("Attempting connection to ASSIGNMENT SERVER...")
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.SNDTIMEO, 500)
        socket.setsockopt(zmq.RCVTIMEO, 500)
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect("tcp://localhost:5555")

        # Compile and send request
        request_json = {"strings": [user_input], "files": self._images}
        print("Sending request...")
        socket.send_json(request_json)

        # Process Reply
        if socket.poll(500) == 0:
            print("No server response detected. Default image used.")
            socket.close()
            return default_file
        else:
            reply = json.loads(socket.recv().decode())
            print(reply, "received...")
            if reply[user_input] == ".defaultChoice":
                print("Image selected:", default_file)
                reply[user_input] = default_file
            else:
                print("Image selected:", reply[user_input])
            socket.close()
            return reply[user_input]

    def update_image_list(self):
        """"""

        # Reset the image list then repopulate it
        self._images = []
        images = os.listdir(path='images')
        for image in images:
            self._images.append(image)

    def list_images(self):
        """Generates and returns a list of all image file names currently available and updates working image list."""
        print("\nImages files available for word-image association...\n"
              "------------------------------------------------------\n")
        self.update_image_list()
        for image in self._images:
            print(image, "\n")


class AssignmentRequest:
    """An object passed along as an information request. Contains data members for a list of strings, a list of image
    file names, and a list of word."""

    def __init__(self):
        self._strings = []
        self._images = []
        self._words = []
        self._word_dict = {}
        self._string_image_dict = {}

    def get_strings(self):
        return self._strings

    def get_images(self):
        return self._images

    def get_words(self):
        return self._words

    def get_word_dict(self):
        return self._word_dict

    def get_string_image_dict(self):
        return self._string_image_dict

    def set_strings(self, string_list):
        self._strings = string_list

    def set_images(self, image_file_list):
        self._images = image_file_list

    def set_words(self, word_list):
        self._words = word_list

    def update_word_dict(self, word, image):
        """Adds to or updates an entry in the object's word-image path dictionary."""
        self._word_dict[word] = image

    def update_string_image_dict(self, arg_string, image):
        """Adds to or updates an entry in the object's word-image path dictionary."""
        self._string_image_dict[arg_string] = image


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


# Functions for Random Images based on files available
def keywords_from_files():
    """Scans the local image directory and returns the list of words found within file names within it."""

    # Get images from library
    file_list = []
    images = os.listdir(path='images')
    for image in images:
        file_list.append(image)

    # Parse image file names and add word substrings to a word list
    word_list = []
    for image in file_list:
        file_string = image
        if image[-4] == ".":
            file_string = image[:-4]

        # Split apart all the words in
        split_words = re.split('[_\-,.]+', file_string)

        # Check for new words from split and add to word list
        for word in split_words:
            if word not in word_list:
                if len(word) > 2:
                    word_list.append(word)

    # Return the word list
    return word_list


def request_surprise():
    """
    Generates a list of words in images in local library. Sends word list via socket JSON to a
    microservice that will return a relevant word or phrase. An image is displayed based on the phrase
    returned from the microservice.
    """

    # Generate word list
    word_list = keywords_from_files()

    # Send request to partner microservice
    context = zmq.Context()
    print("Attempting connection to SURPRISE SERVER...")
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5556")
    socket.send_string(str(word_list))

    # Decode reply socket (and close it)
    reply = socket.recv().decode()
    socket.close()
    return reply

    # TO-DO: Here or in interface loop: Open image based on reply (using MY microservice or built-ins)


# Help Documentation for Interface Loop
def help_me(chapter: int):
    """Prints sections of help code that vary depending on where the help request came from."""

    intro = "\nHELP: How this Program Works\n" \
            "----------------------------\n" \
            "Welcome! This program lets you affiliate a string with an image file. To navigate through\n" \
            "this program, simply input the number in the console that matches your choice. Think of these as\n" \
            "console 'buttons'. At any menu, to return to a previous menu (or exit at the main menu), simply\n" \
            "input any value that does not correspond to a menu option and hit 'enter'. Simply hitting 'enter'\n" \
            "with no value entered works too! It is also probably the fastest method of navigational backtracking.\n" \
            "A local user can enter a string in the console and your device will display the image file that best\n" \
            "fits your prompt (Main Menu option '1'). You can also manually respond to a microservice request,\n" \
            "where a request pipeline with a list of images available and a list of strings that need to be\n" \
            "assigned to them exist. The program then assigns each string a matching image and returns their\n" \
            "relation as a dictionary in a response pipeline, for use by another program (Main Menu option '2').\n" \
            "If you would like to further refine word-image associations for local user string inputs, you can\n" \
            "go to the settings area (Main Menu option '3') and can add or remove key words used in string-image\n" \
            "assignment. For more detailed help on these specific tasks, use 'HELP' in any other section, as needed."

    manual = "\nHELP: How to See my Text String's Image\n" \
             "---------------------------------------\n" \
             "From this menu, simply input '1' to start the process. You will be asked to enter a string of text.\n" \
             "Once you are done, you just hit 'enter and your device should load up your standard image-viewing\n" \
             "program and display the image that best fits your string! If it did not match anything specific,\n" \
             "a default image will be displayed. If you think the image is not a close enough match, you can expand\n" \
             "the possible matching images by adding additional image files to the '\images' subdirectory of this\n" \
             "program and using the settings menu (option '3' from Main Menu) to add additional key words that you\n" \
             "would like the program to pick up on and associate with one of the images in the image folder."

    request = "\nHELP: Respond to a Microservice Request\n" \
              "---------------------------------------\n" \
              "From this menu, simply input '1' to initiate the response to the most recent microservice request.\n" \
              "A request pipeline JSON file will then be read (containing a dictionary with 'images' associated\n" \
              "with a list of image file names/paths that a requesting service has available and 'strings' that\n" \
              "are associated with a list of strings that the requestor would like to be assigned to a relevant \n" \
              "image. Using these two data points, the program then determines what strings should be associated\n" \
              "with what images and updates a response JSON file that can be accessed by the requesting service.\n" \
              "The response JSON contains a dictionary of the requested strings (as keys) with their matching\n" \
              "image filename or path as their value. That way it is easy for a service to use the response to\n" \
              "index directly to the images associated with the strings they have available locally.\n" \
              "All of this is self-contained and is not influenced by this program's key word database."

    settings = "\nHELP: Adjusting Settings\n" \
               "------------------------\n" \
               "The settings menu has several options to further customize and influence the underlying programming\n" \
               "of this application. Option '1' lets you enter a new word to be used as a reference point to\n" \
               "search for matching images for a string. If the keyword already exists, it simply refreshes it\n" \
               "by searching through the images available and assigning it the one that is most appropriate." \
               "Option '2' works similarly, but refreshes all existing keywords in the entire underlying dictionary\n" \
               "that is used to associate a specific word (or part of a word) with a particular image. Option '3'\n" \
               "is for when you want to remove a word from this dictionary so that it is no longer used as a\n" \
               "reference point for assigning an image to a string. If you accidentally add or delete keywords\n" \
               "you can fix it in this menu by simply using options '1' (add) or '3' (remove) respectively.\n" \
               "Underlying relational assignments remain the same once the word is in the dictionary, so removing\n" \
               "a word and then adding it back (and vice versa) will not impact results. Option '4' is for when you\n" \
               "do not necessarily want to change anything, but it lets you view what word-image relations exist\n" \
               "under-the-hood. This same summary also displays where appropriate when using options 1, 2, or 3\n" \
               "as appropriate to help give context to actions being taken."

    # Print out help relevant to current section
    if chapter == 0:
        print(intro)
    elif chapter == 1:
        print(manual)
    elif chapter == 2:
        print(request)
    elif chapter == 3:
        print(settings)


# START PROGRAM: Generate a blank dictionary file if necessary
word_images = WordImageTool()
word_images.main_menu()


# Compatibility Notes
# ------------
# Priority to left side of strings and image names. Name files and write strings accordingly for maximum compatibility.
# For a string to be assigned a non-default image, the request just needs a dictionary with a list of available image
# file names and a list of strings to be assigned to them.
# Avoid contractions on any word that you want to be assigned to an image. It'll mess up the algorithm.
# Inclusive/plural and longer spellings of image names will make it easier to match a word to them
# Ex. dogs.png would match with both dog and dogs; doggie would match with doggie and dog


# TODO LIST
# -----------
# May need to expand knockout list for common irrelevant words
# (OBSOLETE?) Import word list from file method added to settings - tie into interface later if needed
# Update local method to get dynamic word list directly from input string vs. maintaining a word association dictionary
# (OPTIONAL - need to weigh pros/cons)
# Clean up data saving points
# Do a sweep for redundant code
# (OPTIONAL) Expand word checks to repeat again in opposite order if no match found on first pass
# for cases when a word may fit into another one way, but not the other. Could do for images to if period and
# everything after was sliced off, theoretically (less false negative connections)
# RANDOMIZATION CONCEPT: Could theoretically key words to a list instead of a image path string, which would allow for
#                        selection of an image inside the list (random or otherwise) - would need to re-write most logic
# Future GUI stuff: Use form interface and access python functions on back end somehow?
# Have web JS call hosted python script
# Just import microservice and then call it from the manual request, rather than all the convoluted stuff with word
# dictionaries. Just need to make the skip list more robust.

# Microservice Interactions
# -------------------------
# Takes data in form of a JSON containing a dictionary with 3 specific keys that have lists as values
# *"strings"
# *"images" (relative image paths/file names)
# Replies with a dictionary of strings keyed to relative file paths
# May swap JSON to sockets or something later, but interaction should be the same

# Experimental Stuff
# ------------------
# PROOF OF CONCEPT FOR ACCESSING DYNAMIC FILEPATHS FROM OS BELOW
# current_directory = os.path.dirname(__file__)
# default_img_filepath = os.path.join(current_directory, new_dict["sys_default"])
# os.startfile(full_filepath)
# print(default_img_filepath)
# print(json.dumps(default_img_filepath))
