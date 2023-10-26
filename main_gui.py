# -*- coding: utf-8 -*-

# External import
import PySimpleGUI as sg
import json
import os
import dotenv
from enum import Enum

# Internal import
from theme.theme import *
import main
import fcr_classes as fcr
from fcr_gui_lang import GUI_Text

CURR_DIR = os.path.dirname(__file__)
# Load env var
dotenv.load_dotenv()
DOTENV_FILE = dotenv.find_dotenv()

# Get GUI parameters
sg.set_options(font=font, icon=CURR_DIR + "/theme/logo.ico", window_location=window_location)
sg.theme_add_new(theme_name, theme)
sg.theme(theme_name)

# Load existing settings
settings = {}
with open(CURR_DIR + "/settings.json", "r+", encoding="utf-8") as f:
    settings = json.load(f)

lang = os.getenv("LANG")
if lang not in ["eng", "fre"]:
    lang = "fre"
curr_screen = None

class GUI_Elems_With_Val(Enum):
    SERVICE = os.getenv("SERVICE")
    FILE_PATH = os.getenv("FILE_PATH")
    OUTPUT_PATH = os.getenv("OUTPUT_PATH")
    LOGS_PATH = os.getenv("LOGS_PATH")
    PROCESSING_VAL = os.getenv("PROCESSING_VAL")

class GUI_Elems_No_Val(Enum):
    CHOSE_LANG = 0
    SERVICE_NAME = 1
    PROCESSING = 2
    FILE_TO_ANALYZE = 3
    OUTPUT_FOLDER = 4
    LOG_FOLDER = 5
    GO_TO_MARC_FIELDS = 6
    START_ANALYSIS = 7
    SAVE_THOSE_PARAMETERS = 8

class GUI_Screens(Enum):
    MAIN_SCREEN = {
        "values":[
            GUI_Elems_With_Val.SERVICE,
            GUI_Elems_With_Val.PROCESSING_VAL,
            GUI_Elems_With_Val.FILE_PATH,
            GUI_Elems_With_Val.OUTPUT_PATH,
            GUI_Elems_With_Val.LOGS_PATH
        ]
    }
    MARC_FIELDS = 1

# --------------- Function def ---------------
def save_parameters(screen: GUI_Screens, val: dict):
    """Saves the parameters of the screen.
    
    Takes as the current screen."""
    dotenv.set_key(DOTENV_FILE, "LANG", lang)
    for screen_val in screen.value["values"]:
        new_val = val[screen_val.name]
        if type(new_val) == list and len(new_val) == 1:
            new_val = new_val[0]
        dotenv.set_key(DOTENV_FILE, screen_val.name, new_val)

def switch_languages(window: sg.Window, lang: str):
    """Switches every test element language.
    
    Takes as argument :
        - window : the window element
        - lang : the lang, as ISO 639-2"""
    for elem in GUI_Elems_No_Val:
        if elem.name in window.key_dict:
            window[elem.name].update(GUI_Text[elem.name].value[lang])

def open_screen(screen: GUI_Screens, lang: str) -> sg.Window:
    """Generic function to generate a screen.
    
    Takes as argument the wanted screen entry in GUI_Screen"""
    layout = None
    screen_name = None
    if screen == GUI_Screens.MAIN_SCREEN:
        curr_screen = screen
        layout = get_main_screen_layout(lang)
        screen_name = GUI_Text[screen.name + "_NAME"].value[lang]
    return sg.Window(screen_name, layout)

# ----- Screen layouts -----

def get_main_screen_layout(lang: str) -> list:
    """Returns the main screen layout, takes a lang as ISO 639-2 as argument."""
    layout = [
        # Lang
        [  
            sg.Push(), # to align right
            sg.Button(f"{GUI_Text.CHOSE_LANG.value[lang]}", k=GUI_Elems_No_Val.CHOSE_LANG.name)
        ],
        
        # Processing
        [
            sg.Text(f"{GUI_Text.PROCESSING.value[lang]} :", k=GUI_Elems_No_Val.PROCESSING.name),
            sg.Listbox([processing.name for processing in fcr.FCR_Processings], size=(30, 5), key=GUI_Elems_With_Val.PROCESSING_VAL.name, default_values=GUI_Elems_With_Val.PROCESSING_VAL.value, select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)
        ],

        # Original file path
        [sg.Text(f"{GUI_Text.FILE_TO_ANALYZE.value[lang]} :", k=GUI_Elems_No_Val.FILE_TO_ANALYZE.name)],
        [sg.Input(key=GUI_Elems_With_Val.FILE_PATH.name, default_text=GUI_Elems_With_Val.FILE_PATH.value, size=(80, None)), sg.FileBrowse()],

        # Output folder
        [sg.Text(f"{GUI_Text.OUTPUT_FOLDER.value[lang]} :", k=GUI_Elems_No_Val.OUTPUT_FOLDER.name)],
        [sg.Input(key=GUI_Elems_With_Val.OUTPUT_PATH.name, default_text=GUI_Elems_With_Val.OUTPUT_PATH.value, size=(80, None)), sg.FolderBrowse()],

        # Service name
        [
            sg.Text(f"{GUI_Text.SERVICE_NAME.value[lang]} :", k=GUI_Elems_No_Val.SERVICE_NAME.name),
            sg.Input(key=GUI_Elems_With_Val.SERVICE.name, default_text=GUI_Elems_With_Val.SERVICE.value, size=(40, None))
        ],

        # Logs path
        [sg.Text(f"{GUI_Text.LOG_FOLDER.value[lang]} :", k=GUI_Elems_No_Val.LOG_FOLDER.name)],
        [sg.Input(key=GUI_Elems_With_Val.LOGS_PATH.name, default_text=GUI_Elems_With_Val.LOGS_PATH.value, size=(80, None)), sg.FolderBrowse()],

        # Go to MARC fields edit
        [sg.Button(GUI_Text.GO_TO_MARC_FIELDS.value[lang], key=GUI_Elems_No_Val.GO_TO_MARC_FIELDS.name)],

        # Submit + Save
        [
            sg.Push(),
            sg.Button(GUI_Text.START_ANALYSIS.value[lang], key=GUI_Elems_No_Val.START_ANALYSIS.name),
            sg.Push(),
            sg.Button(GUI_Text.SAVE_THOSE_PARAMETERS.value[lang], key=GUI_Elems_No_Val.SAVE_THOSE_PARAMETERS.name)
        ]
    ]
    return layout

# # --------------- Window Definition ---------------
# # Create the window
curr_screen = GUI_Screens.MAIN_SCREEN
window = open_screen(curr_screen, lang)

# # --------------- Event loop or Window.read call ---------------
# # Display and interact with the Window
while True:
    event, val = window.read()

    # --------------- User left ---------------
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        print("Application quittée par l'usager")
        exit()

    # --------------- Updates language ---------------
    if event == GUI_Elems_No_Val.CHOSE_LANG.name:
        if lang == "eng":
            lang = "fre"
        else:
            lang = "eng"
        switch_languages(window, lang)

    # --------------- Save those parameters ---------------
    if event == GUI_Elems_No_Val.SAVE_THOSE_PARAMETERS.name:
        save_parameters(curr_screen, val)

    # --------------- Close the window && execute main ---------------
    if event == GUI_Elems_No_Val.START_ANALYSIS.name:
        window.close()

        execution_settings = fcr.Execution_Settings(CURR_DIR)
        execution_settings.get_values_from_GUI(val)

        # Launch the main script
        print("Exécution du script principal")
        main.main(execution_settings)