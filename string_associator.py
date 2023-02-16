# Author: Taylor Jordan
# GitHub username: Raptor2k1
# Date: 2/13/2023
# Description:  Program that associates a folder of files with words. Dynamically associates uses these words to
#               associate input strings with related files, assuming they are named in ways that contain parsable
#               words. Capable of checking a microservice request list and replying with pre-determined associations.
#               Uses a randomization microservice for a "surprise" result option.

import os
import time
import json
import string
import re
import zmq

# Initialize Default Trackers
default_file_init = "default.png"
default_path_init = "images"
default_file_current = default_file_init
default_path_current = default_path_init


class WordFileTool:
    """Represents a collection of words that are associated with specific files and their affiliated functions."""
    def __init__(self):
        self._files = []
        self._request = None

    def main_menu(self):
        """
        Triggered upon first starting the program or any time the user selects an option to return to the main menu.
        No parameters. Returns nothing when quitting, otherwise triggers different operational loop paths.
        """

        # Update the file directory then start things up
        self.update_file_list()
        mode = input("\nString to File Launcher: MAIN MENU\n"
                     "------------------------------------\n"
                     " Launch a file with a string!\n"
                     "------------------------------------\n"
                     "*Input '1' for MATCH A STRING: Type a string and display its matching file.\n"
                     "*Input '2' for REQUEST A SURPRISE: Displays a surprise phrase and file!\n"
                     "*Input '3' for view FILE DIRECTORY: Lists all files currently available for assignment.\n"
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
            self.list_files()
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

        self.update_file_list()
        choice = input("\nString to File Launcher:: MATCH A STRING\n"
                       "---------------------------------------------\n"
                       "  Input a string and launch a matching file!\n"
                       "---------------------------------------------\n"
                       "*Input '1' to START.\n"
                       "*Input '2' to return to the MAIN MENU.\n"
                       "*Input 'HELP' to for additional instructions on this feature.\n"
                       ">>>")

        # Input a string and match it to a file
        if choice == '1':
            my_string = input("\nType in your new string now. Hit 'Enter' when you are done to submit it.\n"
                              "You will then be presented with an available file that corresponds to it.\n")
            self.string_to_file_display(my_string)
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

        mode = input("\nString to File Launcher: REQUEST A SURPRISE\n"
                     "--------------------------\n"
                     " Launch a Surprise File!\n"
                     "--------------------------\n"
                     "*Input '1' to launch a surprise file!\n"
                     "*Input '2' to return to the MAIN MENU.\n"
                     "*Input 'HELP' to for additional instructions on this feature.\n"
                     "*Input 'QUIT' to CLOSE this application.\n"
                     ">>>")

        # Handle user decisions
        if mode == "1":
            surprise = request_surprise()
            self.string_to_file_display(surprise)
            self.surprise_menu()

        elif mode.lower() == "2":
            self.main_menu()

        elif mode.lower() == "help":
            help_me(2)
            self.surprise_menu()

        elif mode.lower == "quit":
            print("Closing the application...")
            time.sleep(1)
            quit()

        else:
            self.surprise_menu()

    # Helper Methods
    def string_to_file_display(self, arg_string):
        """
        Breaks down an argument string into sub-strings and searches each one for each key word in the gallery dict.
        If one is found, the associated file in the dictionary is displayed (for a local-call).
        """

        # Call microservice to request association
        chosen_file = self.request_association(arg_string)
        print("Displaying", chosen_file, "in 1 second...")
        time.sleep(1)
        os.startfile(default_path_current + "\\" + chosen_file)
        return

    def request_association(self, user_input: str):
        """
        Requests the association of a string with an image using an association microservice.
        Sends an array containing the one string to associate and the current list of locally-available files.
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
        request_json = {"strings": [user_input], "files": self._files}
        print("Sending request...")
        socket.send_json(request_json)

        # Process Reply
        if socket.poll(500) == 0:
            print("No server response detected. Default file used.")
            socket.close()
            return default_file_current
        else:
            reply = json.loads(socket.recv().decode())
            print(reply, "received...")
            if reply[user_input] == ".defaultChoice":
                print("File selected:", default_file_current)
                reply[user_input] = default_file_current
            else:
                print("File selected:", reply[user_input])
            socket.close()
            return reply[user_input]

    def update_file_list(self):
        """"""

        # Reset the file list then repopulate it
        self._files = []
        files = os.listdir(path=default_path_current)
        for file in files:
            self._files.append(file)

    def list_files(self):
        """Generates and returns a list of all file file names currently available and updates working file list."""
        print("\nFiles available for word-file association...\n"
              "------------------------------------------------\n")
        self.update_file_list()
        for file in self._files:
            print(file, "\n")


class AssignmentRequest:
    """An object passed along as an information request. Contains data members for a list of strings, a list of image
    file names, and a list of word."""

    def __init__(self):
        self._strings = []
        self._files = []
        self._words = []
        self._word_dict = {}
        self._string_file_dict = {}

    def get_strings(self):
        return self._strings

    def get_files(self):
        return self._files

    def get_words(self):
        return self._words

    def get_word_dict(self):
        return self._word_dict

    def get_string_file_dict(self):
        return self._string_file_dict

    def set_strings(self, string_list):
        self._strings = string_list

    def set_files(self, file_list):
        self._files = file_list

    def set_words(self, word_list):
        self._words = word_list

    def update_word_dict(self, word, file):
        """Adds to or updates an entry in the object's word-image path dictionary."""
        self._word_dict[word] = file

    def update_string_file_dict(self, arg_string, file):
        """Adds to or updates an entry in the object's word-image path dictionary."""
        self._string_file_dict[arg_string] = file


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


# Functions for Random Files based on files available
def keywords_from_files():
    """Scans the local file directory and returns the list of words found within file names within it."""

    # Get files from library
    file_list = []
    files = os.listdir(path=default_path_current)
    for file in files:
        file_list.append(file)

    # Parse file names and add word substrings to a word list
    word_list = []
    for file in file_list:
        file_string = file
        if file[-4] == ".":
            file_string = file[:-4]

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
    Generates a list of words in files in the local library. Sends word list via socket JSON to a
    microservice that will return a relevant word or phrase. An image is displayed based on the phrase
    returned from the microservice.
    """

    # Generate word list
    word_list = keywords_from_files()

    # Send request to partner microservice
    context = zmq.Context()
    print("Attempting connection to SURPRISE SERVER...")
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.SNDTIMEO, 500)
    socket.setsockopt(zmq.RCVTIMEO, 500)
    socket.setsockopt(zmq.LINGER, 0)
    socket.connect("tcp://localhost:5556")
    socket.send_string(str(word_list))

    if socket.poll(500) == 0:
        print("No server response detected. Default file used.")
        socket.close()
        return default_file_current
    else:
        # Decode reply socket (and close it)
        reply = socket.recv().decode()
        socket.close()
        return reply


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
            "where a request pipeline with a list of files available and a list of strings that need to be\n" \
            "assigned to them exist. The program then assigns each string a matching image and returns their\n" \
            "relation as a dictionary in a response pipeline, for use by another program (Main Menu option '2').\n" \
            "If you would like to further refine word-image associations for local user string inputs, you can\n" \
            "go to the settings area (Main Menu option '3') and can add or remove key words used in string-image\n" \
            "assignment. For more detailed help on these specific tasks, use 'HELP' in any other section, as needed."

    manual = "\nHELP: Launching a file Based on Input\n" \
             "---------------------------------------\n" \
             "From this menu, simply input '1' to start the process. You will be asked to enter a string of text.\n" \
             "Once you are done, you just hit 'enter and your device should load up your standard image-viewing\n" \
             "program and display the image that best fits your string! If it did not match anything specific,\n" \
             "a default image will be displayed. If you think the image is not a close enough match, you can expand\n" \
             "the possible matching images by adding additional image files to the '\images' subdirectory of this\n" \
             "program and using the settings menu (option '3' from Main Menu) to add additional key words that you\n" \
             "would like the program to pick up on and associate with one of the images in the image folder."

    surprise = "\nHELP: Launching a Surprise File\n" \
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
        print(surprise)
    elif chapter == 3:
        print(settings)


# START PROGRAM: Generate a blank dictionary file if necessary
word_files = WordFileTool()
word_files.main_menu()


# TODO LIST
# -----------
# Customize default file and filepath
# Save/Load persistent default
# Reset to original defaults option

# Experimental Stuff
# ------------------
# PROOF OF CONCEPT FOR ACCESSING DYNAMIC FILEPATHS FROM OS BELOW
# current_directory = os.path.dirname(__file__)
# default_img_filepath = os.path.join(current_directory, new_dict["sys_default"])
# os.startfile(full_filepath)
# print(default_img_filepath)
# print(json.dumps(default_img_filepath))
