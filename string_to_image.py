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


class WordImageTool:
    """Represents a collection of words that are associated with specific image files and their affiliated functions."""
    def __init__(self):
        self._word_dict = {}
        self._images = []
        self._request = None

    def set_dict(self, dictionary):
        self._word_dict = dictionary

    def get_dict(self):
        return self._word_dict

    def main_loop(self):
        """
        Triggered upon first starting the program or any time the user selects an option to return to the main menu.
        No parameters. Returns nothing when quitting, otherwise triggers different operational loop paths.
        """

        # Update the image directory then start things up
        self.update_image_list()
        # print(self._images)
        self.save()
        mode = input("\nString to Image converter: MAIN MENU\n"
                     "------------------------------------\n"
                     " Associate a string with an image!\n"
                     "------------------------------------\n"
                     "*Input '1' to CONVERT A STRING: Type up a new string and be presented with its matching image.\n"
                     "*Input '2' for REQUEST HANDLING: Respond to requests to assign images to strings.\n"
                     " a separate service, and send matching image information back to the requesting application.\n"
                     "*Input '3' to SETTINGS: Update relationships between key words and their assigned images.\n"
                     "*Input 'HELP' to for additional instructions on all features.\n"
                     "*Input anything else to QUIT the application.\n"
                     ">>>")

        # Handle user decisions
        if mode == "1":
            self.manual_loop()
        elif mode == "2":
            self.request_loop()
        elif mode == "3":
            self.settings_loop()
        elif mode.lower() == "help":
            help_me(0)
            self.main_loop()

        # Save changes to word-image dictionary and exit
        else:
            print("\nSaving changes to word-image associations...\n")
            self.save()
            time.sleep(0.5)
            return

    # Primary Functional Loops
    def manual_loop(self):
        """"""

        choice = input("\nString to Image converter: CONVERT A STRING\n"
                       "------------------------------------\n"
                       "  Input a string and see its image!\n"
                       "------------------------------------\n"
                       "*Input '1' to START.\n"
                       "*Input 'HELP' to for additional instructions on manually assigning text to an image.\n"
                       "*Input any other value to return to the MAIN MENU.\n"
                       ">>>")

        # Type a string and match to an image
        if choice == '1':
            my_string = input("\nType in your new string now. Hit 'Enter' when you are done to submit it.\n"
                              "You will then be presented with the available image that best corresponds.\n")
            self.string_to_image_display(my_string)
            self.manual_loop()

        # Ask for help
        elif choice.lower() == "help":
            help_me(1)
            self.manual_loop()

        # Return to main menu
        else:
            self.main_loop()

    def request_loop(self):
        """
        Processes the most recent request pipeline and ensures that the response pipeline data matches
        the results that were requested.
        """

        choice = input("\nString to Image converter: REQUEST HANDLING\n"
                       "--------------------------------------------\n"
                       " Listen and reply to another app's request.\n"
                       "--------------------------------------------\n"
                       "*Input '1' to CHECK for string assignment requests from another program.\n"
                       " These strings will be processed, then a matching image and its filepath will be\n"
                       " assigned. Results will be sent back via the response pipeline.\n"
                       "*Input 'HELP' to for additional instructions on text-image assignment requests.\n"
                       "*Input any other value to return the MAIN MENU.\n"
                       ">>>")

        # Check requests and process if needed
        if choice == "1":

            # Open the request file and assign its contents to a working request object
            request_obj = AssignmentRequest()
            with(open("request.json", "r")) as request_json:
                request_dict = json.load(request_json)
                request_obj.set_images(request_dict["images"])
                request_obj.set_strings(request_dict["strings"])
                # print(request_obj.get_images())
                # print(request_obj.get_strings())
                self._request = request_obj

            # Generate word-image dictionary for request object
            self._request.gen_request_word_dict()

            # Process the request and update the reply pipe
            self.process_request()

            # Return to main menu
            self.request_loop()

        # Ask for help
        elif choice.lower() == "help":
            help_me(2)
            self.request_loop()

        # Return to main menu
        else:
            self.main_loop()

    def settings_loop(self):
        """"""

        # TODO: Can pretty much gut this entire thing if I use the automated version like in requests, since
        # customization would no longer be necessary. Or change layout to instead add overrides or something.

        choice = input("\nString to Image converter: SETTINGS\n"
                       "----------------------------------------\n"
                       "   Update word/image associations.\n"
                       "----------------------------------------\n"
                       "*Input '1' to ADD NEW or REFRESH a word-image association.\n"
                       "*Input '2' to AUTOMATICALLY REFRESH ALL current word/image associations.\n"
                       "*Input '3' to REMOVE the image association for a SINGLE WORD.\n"
                       "*Input '4' for a SUMMARY of current word-image associations. \n"
                       "*Input 'HELP' to for additional instructions on using the settings.\n"
                       "*Input any other value to return to the MAIN MENU.\n"
                       ">>>")

        # Generate dict value for single word
        if choice == "1":
            self.assignment_ui()
            self.list_words()
            self.settings_loop()

        # Auto-update dict keys for all existing words
        elif choice == "2":
            self.assign_words_all()
            self.list_words()
            self.settings_loop()

        # Delete a specific word from the gallery dictionary
        elif choice == "3":
            self.list_words()
            del_word = input("\nPlease enter a word to un-assign from an image.\n"
                             ">>>")
            self.del_word(del_word)
            self.list_words()
            self.settings_loop()

        # Print Dictionary Summary
        elif choice == "4":
            self.list_words()
            self.settings_loop()

        # Ask for help
        elif choice.lower() == "help":
            help_me(3)
            self.settings_loop()

        # Return to main menu
        else:
            self.main_loop()

    # Helper Methods
    def string_to_image_display(self, arg_string):
        """
        Breaks down an argument string into sub-strings and searches each one for each key word in the gallery dict.
        If one is found, the associated image in the dictionary is displayed (for a local-call). The matched image path
        image is also passed along for use by the listening mode loop (as a string).
        """

        string_list = arg_string.split()
        word_list = self._word_dict.keys()
        for substring in string_list:
            # print(word_list)
            # print()
            for word in word_list:
                cleaned_word = remove_special_chars(word)
                cleaned_substring = remove_special_chars(substring)
                if cleaned_word.lower() in cleaned_substring.lower():
                    print("Displaying", self._word_dict[word], "in 1 second...")
                    time.sleep(1)
                    os.startfile(self._word_dict[word])
                    return

        # Use default image in the event that no image was found
        print("No key words found related to your string, displaying the default image.")
        time.sleep(1)
        os.startfile(self._word_dict['sys_default'])

    def word_to_image_request(self, word) -> str:
        """
        Associates a word with an image
        """

        # Split string into word list and check each substring against word list/image dictionary and return results
        if word.lower() in self._request.get_images().lower():
            return self._request.get_word_dict()[word]

        # Return default image info if no match - matching app must use same path/name in this implementation
        # Can work with partner to adjust default phrasing
        return "default.png"

    # Edit Mode Functions
    def assignment_ui(self):
        """
        Prompt for word to update. Then manually update a single key's associated image file.
        Summarize actions once complete.
        """

        # Input the word you would like to be assigned an image
        word_choice = input("\nPlease enter a word that you would like to be assigned to an image.\n"
                            ">>>")
        if " " in word_choice:
            print("\nPlease enter a SINGLE word and try again.\n"
                  "While special characters are allowed, they may result in difficulty matching to a \n"
                  "non-default image.\n")
            self.assignment_ui()
        else:
            self.assign_word(word_choice)
            self.settings_loop()

    def assign_word(self, word):
        """
        Directly updates dictionary for a key word with its associated filepath.
        Called by assign_words_all and assignment_UI.
        """

        # Initializes new word to default assignment
        print("Initializing", word, "to the default image...")
        self._word_dict[word] = "images\\" + "default.png"

        # Updates image list, then searches it for an image containing the word, and assigns the first it encounters
        self.update_image_list()
        for filename in self._images:
            if word.lower() in filename.lower():
                self._word_dict[word] = "images\\" + filename
                print("Word-affiliation updated! The word", word, "will now be affiliated with the image",
                      filename + ".")
                self.save()

    def assign_word_request(self, word):
        """
        Directly updates dictionary for a key word with its associated filepath.
        Called by assign_words_all and assignment_UI.
        """

        # Updates image list, then searches it for an image containing the word, and assigns the first it encounters
        self.update_image_list()
        for filename in self._images:
            if word.lower() in filename:
                self._word_dict[word] = "images\\" + filename
                print("\nWord-affiliation updated! The word", word, "will now be affiliated with the image",
                      filename + ".")
                self.save()
                return

        # If not match found for a word
        print("\nNo image match found for the word", word + ". It will remain unaffiliated with an image for now.\n")

    def assign_words_all(self):
        """
        Automatically update all current keys based on image names. Skips the words not in the image names.
        Summarize actions once complete. No return parameters. Updates image list and word dictionary attribute
        directly instead.
        """
        words = self._word_dict.keys()

        # Assign everything anew (matches will get a new designation)
        for word in words:
            self.assign_word(word)

    def list_words(self):
        """
        Lists all word-image associations as assigned (including empty associations).
        """

        print("\nWords Association Status\n"
              "------------------------")
        for word in self._word_dict.keys():
            print(word + ":", self._word_dict[word])

    # def import_wordlist(self, list_file):
    #     """
    #     Opens a word list json file and reads its contents and gives the word a dictionary entry.
    #     Runs auto-assign after to make sure all keys have an assignment.
    #     """
    #
    #     # Read word list JSON and transcribe
    #     with open(list_file, "r") as word_list:
    #         new_words = json.load(word_list)
    #         for word in new_words:
    #             self._word_dict[word] = None
    #
    #     # Assigns all words, after importing them
    #     self.assign_words_all()

    def process_request(self):
        """
        Scans the request pipeline for an object containing a list of strings, a list of image file names,
        and list of words. If no list of words is provided, uses the currently-saved internal list.
        If either the image or string list is empty, returns an error explaining why the request is invalid.
        In either case, clears the request pipeline file after the operation is done.
        """

        # If wordlist not provided, use internal wordlist from dict
        print(type(self._request))
        if str(type(self._request)) != "<class '__main__.AssignmentRequest'>":
            print("Invalid request object.")
            return

        # See if any words within the string are contained with an image filename and assign them if they are.
        else:
            # Filter out common irrelevant/short words
            skip_list = ("is", "in", "an", "the")
            string_list = self._request.get_strings()
            for req_string in string_list:
                string_words = req_string.split()
                for word in string_words:
                    cleaned_word = remove_special_chars(word)
                    if cleaned_word in skip_list:
                        continue  # Skip this substring if it's a known irrelevant factor
                    word_image = self._request.image_for_word(cleaned_word)
                    self._request.update_string_image_dict(req_string, word_image)
                    if self._request.get_string_image_dict()[req_string] != "default.png":
                        break  # Move to next string once we know current is assigned to an image

            # Send the updated request object to the outgoing pipeline
            self.send_info()

    def send_info(self):
        """
        Updates the return pipeline file with a key and path that matches the input string received.
        Takes an array of request objects as a parameter, each having data members for a string, a key,
        an image file name, and a path to the image.
        """
        # open and write self.request's object or its dictionary attribute
        send_data = self._request.get_string_image_dict()
        send_data_json = json.dumps(send_data, indent=4)
        with open("response.json", "w") as reply_pipe:
            reply_pipe.write(send_data_json)
        print("\nResponse sent.\n")

        # Success confirmation explanation
        print("Request process successful - requested strings have been associated with an image and relational\n"
              "data has been returned for processing by the requesting application!\n")

    def del_word(self, word):
        """Deletes a key word and affiliated path from the gallery dictionary."""
        self._word_dict.pop(word, "That key does not exist. Please try again.")
        print("The word", word, "has been removed from consideration and is no longer associated with any image.")
        self.save()

    def view_key(self, word):
        """Views a specific key and its filepath. Opens image file for viewing reference."""
        print(word + ": " + self._word_dict[word])

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

    def save(self):
        """Saves all current changes to the dictionary to JSON."""
        save_json = json.dumps(self._word_dict, indent=4)
        with open("persistentData.json", "w") as save_dict:
            save_dict.write(save_json)


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

    def gen_request_word_dict(self):
        """Generates a word-image relation based on the word list and image files."""
        for word in self._words:
            self._word_dict[word] = self.image_for_word(word)

    def image_for_word(self, word) -> str:
        """Assigns a word (in a request object) to the first matching file name string found."""
        for image in self._images:
            # print(word, image)
            if word.lower() in image.lower():
                # print("------------")
                # print("Success!\n", image)
                return image

        # Return default image if no matches
        return "default.png"


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


def help_me(chapter: int):
    """Prints sections of help code that vary depending on where the help request came from."""
    intro = "Intro Tutorial: Placeholder helpful paragraph about bla bla bla bla bla bla bla..."
    manual = "Tutorial on manual strings"
    request = "Tutorial on requests handling"
    settings = "Tutorial on adjusting settings"

    # Print out help relevant to current section
    if chapter == 0:
        print(intro)
        print(manual)
        print(request)
        print(settings)
    elif chapter == 1:
        print(manual)
    elif chapter == 2:
        print(request)
    elif chapter == 3:
        print(settings)


# START PROGRAM: Generate a blank dictionary file if necessary
if os.path.exists("persistentData.json") is False:
    new_dict = {"sys_default": "images\\default.png"}
    dict_json = json.dumps(new_dict, indent=4)  # GET RID OF INDENT? REMEMBER TO FACTOR IN LATER
    with open("persistentData.json", "w") as word_image_dict:
        word_image_dict.write(dict_json)

# Create live dictionary object from persistent JSON file
word_images = WordImageTool()
with(open("persistentData.json", "r")) as word_image_json:
    temp_dict = json.load(word_image_json)
    word_images.set_dict(temp_dict)

# Run the main program loop
word_images.main_loop()

# Save changes to dictionary from this session (so they persist to the next)
print("Exiting the program...")
time.sleep(0.5)
print("Saving word-image dictionary changes...")
updated_dict_json = json.dumps(word_images.get_dict())
with open("persistentData.json", "w") as word_image_dict:
    word_image_dict.write(updated_dict_json)
time.sleep(1)
print("Done!")
time.sleep(1)

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
