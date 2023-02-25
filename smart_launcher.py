"""
Author: Taylor Jordan
GitHub username: Raptor2k1
Date: 2/21/2023

Description:    Launches files or folders contained within a target directory based on input strings, or randomly by
                using a "surprise" launcher feature. For manual string input, it determines which file to launch by
                identifying matching substrings between target file and the input string.

Requirements:   Needs the chooseRandom.py server script from https://github.com/fitellieburger/CS361/ for the surprise
                service to function properly. The script must be run/server must be active in order for the random
                assignment service to function correctly. Similarly, smart_selector.py from my own project page
                must be running in order for string-file launching to work. This server script is available at:
                https://github.com/Raptor2k1/361-Project

References:     Sockets / ZeroMQ
                https://zeromq.org/get-started/

                RegEx String Splitting
                https://pynative.com/python-regex-split/

                Speech Recognition
                https://pypi.org/project/SpeechRecognition/
                https://www.scaler.com/topics/remove-special-characters-from-string-python/
                https://stackoverflow.com/questions/62401885/python-speech-recognition-stuck-at-listening
"""

import os
import time
import json
import string
import re
import zmq
import sys
import speech_recognition
from pathlib import PureWindowsPath


# Initialize Target Directory for Launching Files
default_path_init = PureWindowsPath("Launch-Files/")
default_path_current = default_path_init

# Set up the screen clear command based on OS (defaults to Windows vs Linux/iOS)
clear_cmd = 'cls'
if os.name != 'nt':
    clear_cmd = 'clear'


class WordFileTool:
    """Represents a collection of words that are associated with specific files and their affiliated functions."""
    def __init__(self):
        self._files = []
        self._request = None

    # INTERFACE LOOPS
    def main_menu(self):
        """
        Triggered upon first starting the program or any time the user selects an option to return to the main menu.
        User input triggers different operational paths, based on input. Paths available to launch a file based on text
        input, launch a random file, edit program settings, view help text, and quit the application.
        """

        # Update the file directory then start things up
        os.system(clear_cmd)
        self.update_file_list()
        choice = input("\nSmart Launcher: MAIN MENU\n"
                       "------------------------------------\n"
                       " Launch a file with a string!\n"
                       "------------------------------------\n"
                       "*Input '1' to TEXT LAUNCH: Type in text that references an available file's name to start it!\n"
                       "*Input '2' for VOICE COMMAND: Launches a file with your voice!\n"
                       "*Input '3' for a SURPRISE: Launches a mystery file! Surprise!\n"
                       "*Input '4' for SETTINGS: Change the launch directory or view its contents.\n"
                       "*Input 'HELP' to for additional information on all features.\n"
                       "*Input 'QUIT' to CLOSE this application.\n"
                       ">>>")

        # Handle user decisions
        if choice == "1":
            self.string_launcher()
        elif choice == "2":
            self.voice_launcher()
        elif choice == "3":
            self.surprise()
        elif choice == "4":
            self.settings_menu()
        elif choice.lower() == "help":
            os.system(clear_cmd)
            help_me(0)
            input("\nPress 'Enter' to continue.")
            self.main_menu()
        elif choice.lower() == "quit":
            print("Closing the application...")
            time.sleep(1)
            sys.exit()
        else:
            self.main_menu()

    def string_launcher(self):
        """
        Takes user input and runs it through a string-file association service to determine the most appropriate
        file to match the input string. It then launches this file.
        """

        os.system(clear_cmd)
        self.update_file_list()
        my_string = input("\nType in your new string now. Hit 'Enter' when you are done, to submit it.\n"
                          "The program will then launch a matching file, if one is found!\n"
                          ">>>")
        self.string_to_file_launch(my_string)
        input("\nPress 'Enter' to continue.")
        self.main_menu()

    def voice_launcher(self):
        """
        Takes user input and runs it through a string-file association service to determine the most appropriate
        file to match the input string. It then launches this file.
        """

        os.system(clear_cmd)
        self.update_file_list()
        input("\nPress 'Enter' to begin recording your voice command.\n"
              "Note: Background noise may prevent the phrase recorder from stopping when you\n"
              "are done speaking. If this happens, just remain quiet after your phrase and wait\n"
              "for the 6-second time-out to complete.")
        my_string = voice_string()
        self.string_to_file_launch(my_string)
        input("\nPress 'Enter' to continue.")
        self.main_menu()

    def surprise(self):
        """
        Submits a list of available launch files to a random selection microservice and launches it via the results of a
        text-file association microservice.
        """

        os.system(clear_cmd)
        self.update_file_list()
        surprise = request_surprise()
        self.string_to_file_launch(surprise)
        input("\nPress 'Enter' to continue.")
        self.main_menu()

    def settings_menu(self):
        """
        A command-line menu that his interface options to 1) Change the target launch directory, 2) Reset the launch
        directory to default, and 3) View available files in the current launch directory. Also includes standard
        commands to return to the main menu, show a help screen, or close the application.
        """

        os.system(clear_cmd)
        choice = input("\nSmart Launcher: SETTINGS\n"
                       "-------------------------------------------------\n"
                       " View or Change Launch Parameters!\n"
                       f" Launch Folder: {default_path_current}\n"
                       "-------------------------------------------------\n"
                       "*Input '1' to LIST LAUNCHABLE FILES in the current target directory.\n"
                       "*Input '2' to CHANGE LAUNCH DIRECTORY for files.\n"
                       "*Input '3' to RESET LAUNCH DIRECTORY to default ('Launch-Files' folder in root directory).\n"
                       "*Input '4' to RETURN to the MAIN MENU.\n"
                       "*Input 'HELP' to for additional information on customizing the settings.\n"
                       "*Input 'QUIT' to CLOSE this application.\n"
                       ">>>")

        # Handle user decisions
        if choice == "1":
            self.list_files()
            input("\nPress 'Enter' to continue.")
            self.settings_menu()
        elif choice == "2":
            change_path()
            self.settings_menu()
        elif choice == "3":
            reset_defaults()
            self.settings_menu()
        elif choice == "4":
            self.main_menu()
        elif choice.lower() == "help":
            os.system(clear_cmd)
            help_me(1)
            input("\nPress 'Enter' to continue.")
            self.settings_menu()
        elif choice.lower() == "quit":
            print("Closing the application...")
            time.sleep(1)
            sys.exit()
        else:
            self.settings_menu()

    # FUNCTIONAL METHODS
    def string_to_file_launch(self, arg_string):
        """
        Uses a string-to-file association service to determine the mots appropriate file to launch based on the
        parameter string. Launches the file if a matches is found, otherwise returns a message that there was no match
        and displays available launch files, for reference.
        """

        # Call microservice to request association
        chosen_file = self.request_association(arg_string)

        if chosen_file is None:
            print("No files that match that string were detected.")
            self.list_files()
        else:
            print("\nLaunching", chosen_file, "in 1 second...")
            time.sleep(1)
            os.startfile(default_path_current / chosen_file)
        return

    def request_association(self, user_input: str):
        """
        Requests the association of a string with a file using an association microservice.
        Sends an array containing the one string to associate and the current list of locally-available files.
        Receives a dictionary of the string and image path to associate with it and decodes it.
        Returns the file name to associate with the parameter string.
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
            print("No server response detected. No file launched.")
            socket.close()
            return  # default_file_current
        else:
            reply = json.loads(socket.recv().decode())
            print(reply, "received...")
            if reply[user_input] == ".defaultChoice":
                reply[user_input] = None
            else:
                print("File selected:", reply[user_input])
            socket.close()
            return reply[user_input]

    def update_file_list(self):
        """Updates the list of available files in the current launch directory, for reference by the program."""

        # Reset the file list then repopulate it
        self._files = []
        files = os.listdir(path=default_path_current)
        for file in files:
            self._files.append(file)

    def list_files(self):
        """Generates and returns a list of all file names currently available and updates working file list."""
        print("\nFiles available for word-file association...\n"
              "-----------------------------------------------")
        self.update_file_list()
        for file in self._files:
            print(file)


# Adapted from suggestion at: https://www.scaler.com/topics/remove-special-characters-from-string-python/
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


def keywords_from_files():
    """Scans the launch file directory and returns the list of words found within file names within it."""

    # Get files from library
    file_list = []
    files = os.listdir(path=default_path_current)
    for file in files:
        file_list.append(file)

    # Parse file names and add word substrings to a word list
    word_list = []
    for file in file_list:
        file_string = file
        if len(file) > 3 and file[-4] == ".":
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


def change_path():
    """Changes the current launch directory of files. Prints a message if the path is invalid."""
    os.system(clear_cmd)
    path = input("Please enter a new target file directory:\n"
                 ">>>")
    global default_path_current
    default_path_current = PureWindowsPath(path)

    if os.path.isdir(default_path_current) is True:
        save_default()
    else:
        print("Invalid Filepath. Please try again with a valid directory. Do not target a file.")


def save_default():
    """Saves the current definitions for the default file path and file in 'pathdata.txt' in the root directory."""

    print("Saving changes to default path...")
    with open('pathdata.txt', 'w') as path_json:
        if os.path.exists(default_path_current):
            path_json.write(str(default_path_current))
        else:
            print("No change made - the target path does not exist.")
            time.sleep(1)


def load_saved_defaults():
    """Loads the last saved definition of the default file directory."""

    global default_path_current
    if os.path.exists('pathdata.txt') is False:
        save_default()
    else:
        with open('pathdata.txt', 'r') as path_json:
            default_path_current = PureWindowsPath(path_json.read())
            save_default()


def reset_defaults():
    """Resets the launch directory to default, then saves the change."""
    global default_path_current
    default_path_current = default_path_init
    save_default()


def default_check():
    """Checks for the default local folder and creates it if it does not yet exist."""
    if os.path.exists(default_path_init) is False:
        os.mkdir(default_path_init)


def request_surprise():
    """
    Generates a list of words in files in the local library. Sends word list via socket JSON to a
    microservice that will return a relevant word or phrase. A file is launched based on the phrase
    returned from the microservice.
    """

    # Generate word list
    word_list = keywords_from_files()

    # Send request to partner microservice
    context = zmq.Context()
    print("\nAttempting connection to SURPRISE SERVER...")
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.SNDTIMEO, 500)
    socket.setsockopt(zmq.RCVTIMEO, 500)
    socket.setsockopt(zmq.LINGER, 0)
    socket.connect("tcp://localhost:5556")
    socket.send_string(str(word_list))

    if socket.poll(500) == 0:
        print("No server response detected. No file launched.")
        socket.close()
        return  # default_file_current
    else:
        # Decode reply socket (and close it)
        reply = socket.recv().decode()
        socket.close()
        return reply


# Help Documentation for Interface Loop
def help_me(chapter: int):
    """Prints a help text corresponding with the argument chapter integer."""

    intro = "\nHELP: How this Program Works\n" \
            "----------------------------\n"\
            "NAVIGATION: Navigate through the features of this program by typing in the respective \n" \
            "commands that are denoted by the user interface. In general, this simply means entering \n" \
            "the number that corresponds to the menu option that you would like to select. At any menu \n" \
            "screen, you can also type ‘HELP’ to view a help prompt or ‘QUIT’ to exit the program \n" \
            "(without the quotes, in both cases). The commands are case-insensitive, so capitalization will \n" \
            "not effect whether they will work. After any selection input, just hit 'Enter' to confirm it.\n" \
            "\nTEXT LAUNCH: The main feature of this program is launching a file from a target directory \n" \
            "based on text that you input. Do you want to see a random photo that matches a sentence? \n" \
            "Go for it! Want to launch a game based on a question or a phrase? That works too! As long as \n" \
            "some part of your text input has text that corresponds with the name of a file in the target \n" \
            "launch folder, it will be started up automatically! In the even that multiple files match your \n" \
            "input, one of them will be randomly selected. In the event that your text doesn't have a match, \n" \
            "the program will let you know and return a list of the available files to launch to help you tailor \n" \
            "a more relevant input for the next attempt.\n" \
            "\nVOICE COMMAND: This feature is pretty nifty. So long as your operating system’s default microphone \n" \
            "is working and you have an internet connection, this will record a voice sample, then send it to \n" \
            "Google’s Speech Recognition service for analysis. Assuming it is legible, your voice sample will be \n" \
            "converted to text and used to launch a file in the launch folder that matches up with the text \n" \
            "detected in your speech pattern. When you select this option, you will initially be prompted to hit \n" \
            "‘Enter’ to start recording your voice sample. The speech recognition service will print out some \n" \
            "summary information to show how it attempted to recognize the voice sample.  If it was successful, \n" \
            "it will display the matching file found and launch it for you. You may hit ‘Enter’ again to return \n" \
            "to the main menu afterwards.\n" \
            "\nSURPRISE: Can’t decide on what game to play, or what music to listen to? Use the surprise feature \n" \
            "to have a random-selection microservice automatically choose one for you! As long is there is at \n" \
            "least one file available in the current launch folder, this should work every time \n" \
            "(though it wouldn't be terribly random with only one file).\n" \
            "\nSETTINGS: If you want to drill down a little deeper into the program and view the current launch \n" \
            "folder and its available files, you can check them out right here! If you would rather choose a \n" \
            "different launch folder, rather than placing things that you want to launch within the default \n" \
            "location, you can change it here! If you change your mind, or select the wrong folder, you can \n" \
            "always use the reset feature to change it back!"

    settings = "\nHELP: Adjusting Settings\n" \
               "------------------------\n" \
               "LIST LAUNCHABLE FILES: This option lists the name of the current launch directory at the \n" \
               "top, and beneath that are all available files within it. Any of these files or folders \n" \
               "can be launched or opened if this program selects one of them (whether by text-file association \n" \
               "or random selection). You can add more files to launch by placing them in this folder, or \n" \
               "alternatively, you can change the target folder to a different location, if that is more \n" \
               "appropriate for your needs. As you may have noticed, the current launch directory will always \n" \
               "be displayed as part of this menu’s banner. If it is a relative path, you may just see a lone \n" \
               "folder name. If it is set as an absolute path, you may see a fuller, more \n" \
               "‘traditional’ looking complete path that includes your hard driver letter and the like.\n" \
               "\nCHANGE LAUNCH DIRECTORY: This option will prompt you to enter a new directory path to use \n" \
               "as the basis for launching files. You may use a relative path starting at the root directory \n" \
               "of wherever this script is run, or you can use an absolute path (for example, if you were to \n" \
               "copy/paste a directory path from File Explorer and use that). If your suggested path is invalid, \n" \
               "a message will let you know, and return you to the settings menu (at which point you can try again \n" \
               "with a valid path, if you would like). \n" \
               "\nRESET LAUNCH DIRECTORY: If you ever need to start over, you can use this option to simply reset \n" \
               "the program to its default setting, where it looks for files to launch in a ‘Launch-Files’ folder \n" \
               "that is located in the same directory as the program script. This is handy if you assign the wrong \n" \
               "folder as the launch directory by mistake, or something else unforeseen happens that requires \n" \
               "rolling back a launch directory change.\n" \
               "\nNAVIGATION: As with all other menus within the program, you can navigate through the options \n" \
               "in the settings menu by simply inputting the number that corresponds with the option you want, \n" \
               "and hitting ‘Enter’ to confirm the action. As with the main menu, you may also type ‘HELP’ or \n" \
               "‘QUIT’ at any time to bring up this help screen or quit the application, respectively."

    # Print out help relevant to current section
    if chapter == 0:
        print(intro)
    elif chapter == 1:
        print(settings)


def voice_string():
    """Uses speech recognition to convert a voice sample into a string. Returns the string."""

    # Define speech recognizer, record sample, and send to google for conversion to string
    recognizer = speech_recognition.Recognizer()
    try:
        with speech_recognition.Microphone() as source:
            print("Voice sampling started... Sampling will stop after 6 seconds.")
            voice_sample = recognizer.listen(source, timeout=6, phrase_time_limit=6)
            print("Analyzing voice sample with Google Speech Recognition...")
            text = recognizer.recognize_google(voice_sample)
            return text
    except speech_recognition.UnknownValueError:
        print("Your audio sample was incomprehensible. Please try again.")
        return ""
    except speech_recognition.RequestError:
        print("There was an issue requesting results from Google. Please check your connection or try again later.")
        return ""


# START PROGRAM: Generate a blank dictionary file if necessary
default_check()
load_saved_defaults()
word_files = WordFileTool()
word_files.main_menu()
