# -*- coding: utf-8 -*-

# External import
import PySimpleGUI as sg
import json
import os
import dotenv
from enum import Enum
from typing import List

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
marc_fields_json = {}
with open(CURR_DIR + "/marc_fields.json", "r+", encoding="utf-8") as f:
    marc_fields_json = json.load(f)

lang = os.getenv("LANG")
if lang not in ["eng", "fre"]:
    lang = "fre"
curr_screen = None

# --------------- Data retrieveing function def ---------------

def get_marc_data_id_from_label(db:str, lang:str, label:str) -> str:
    """Returns the data id from marc field based on it's label"""
    for data in marc_fields_json[db]:
        if marc_fields_json[db][data]["label"][lang] == label:
            return data
    return None

def get_marc_data_labels(db: str, lang: str) -> List[str]:
    """Returns all data labels from marc field as a list"""
    return [marc_fields_json[db][key]["label"][lang] for key in marc_fields_json[db]]

def get_marc_data_label_by_id(db: str, lang: str, id: str) -> str:
    """Returns the label of a data"""
    return marc_fields_json[db][id]["label"][lang]

def retrieve_data_from_marc_data_field_field(db: str, id: str, tag: str, attr:str):
    """Mother function of get_marc_data_field + attribute.
    
    attr is the attriute name"""
    fields = marc_fields_json[db][id]["fields"]
    for field in fields:
        if field["tag"] == tag:
            return field[attr]

def get_marc_data_fields_tag(db: str, id: str) -> List[str]:
    """Returns the tags of eahc field from a data"""
    return [field["tag"] for field in marc_fields_json[db][id]["fields"]]

def get_marc_data_field_single_line_coded_data(db: str, id: str, tag:str) -> bool:
    return retrieve_data_from_marc_data_field_field(db, id, tag, "single_line_coded_data")

def get_marc_data_field_filtering_subfield(db: str, id: str, tag:str) -> str:
    return retrieve_data_from_marc_data_field_field(db, id, tag, "filtering_subfield")

def get_marc_data_field_subfields(db: str, id: str, tag:str) -> str:
    return ", ".join(retrieve_data_from_marc_data_field_field(db, id, tag, "subfields"))

def get_marc_data_field_positions(db: str, id: str, tag:str) -> str:
    return ", ".join(retrieve_data_from_marc_data_field_field(db, id, tag, "positions"))

# --------------- UI variables ---------------

class GUI_Elems_With_Val(object):
    def __init__(self):
        self.SERVICE = os.getenv("SERVICE")
        self.FILE_PATH = os.getenv("FILE_PATH")
        self.OUTPUT_PATH = os.getenv("OUTPUT_PATH")
        self.LOGS_PATH = os.getenv("LOGS_PATH")
        self.PROCESSING_VAL = os.getenv("PROCESSING_VAL")
        self.ORIGIN_URL = os.getenv("ORIGIN_URL")
        self.TARGET_URL = os.getenv("TARGET_URL")
        self.ORIGIN_DATABASE_MARC = "ORIGIN_DATABASE"
        self.TARGET_DATABASE_MARC = "TARGET_DATABASE"
        self.MARC_DATA_BEING_CONFIGURED = "id"
        self.MARC_DATA_BEING_CONFIGURED_LABEL = get_marc_data_label_by_id(self.ORIGIN_DATABASE_MARC, lang, self.MARC_DATA_BEING_CONFIGURED)
        # self.MARC_DATA_FIELD = get_marc_data_fields_tag(self.ORIGIN_DATABASE_MARC, self.MARC_DATA_BEING_CONFIGURED)[0]
        # self.MARC_DATA_SINGLE_LINE_CODED_DATA = get_marc_data_field_single_line_coded_data(self.ORIGIN_DATABASE_MARC, self.MARC_DATA_BEING_CONFIGURED, self.MARC_DATA_FIELD)
        # self.MARC_DATA_FILTERING_SUBFIELD = get_marc_data_field_filtering_subfield(self.ORIGIN_DATABASE_MARC, self.MARC_DATA_BEING_CONFIGURED, self.MARC_DATA_FIELD)
        # self.MARC_DATA_SUBFIELDS = get_marc_data_field_subfields(self.ORIGIN_DATABASE_MARC, self.MARC_DATA_BEING_CONFIGURED, self.MARC_DATA_FIELD)
        # self.MARC_DATA_POSITIONS = get_marc_data_field_positions(self.ORIGIN_DATABASE_MARC, self.MARC_DATA_BEING_CONFIGURED, self.MARC_DATA_FIELD)
        self.MARC_DATA_FIELD = None
        self.MARC_DATA_SINGLE_LINE_CODED_DATA = None
        self.MARC_DATA_FILTERING_SUBFIELD = None
        self.MARC_DATA_SUBFIELDS = None
        self.MARC_DATA_POSITIONS = None
        self.update_marc_data_being_configured(self.MARC_DATA_BEING_CONFIGURED_LABEL, lang)

        # Processings Specifics
        self.ILN = os.getenv("ILN") # Better_Item
        self.RCR = os.getenv("RCR") # Better_Item
    
    def update_marc_data_being_configured(self, label: str, lang: str):
        """ 
        Takes the label and the lang as argument"""
        db = self.ORIGIN_DATABASE_MARC
        self.MARC_DATA_BEING_CONFIGURED = get_marc_data_id_from_label(db, lang, label)
        id = self.MARC_DATA_BEING_CONFIGURED
        self.MARC_DATA_FIELD = get_marc_data_fields_tag(db, id)[0]
        self.update_marc_field_being_configured(db, id, self.MARC_DATA_FIELD)

    def update_marc_field_being_configured(self, db: str, id: str, tag: str):
        self.MARC_DATA_SINGLE_LINE_CODED_DATA = get_marc_data_field_single_line_coded_data(db, id, tag)
        self.MARC_DATA_FILTERING_SUBFIELD = get_marc_data_field_filtering_subfield(db, id, tag)
        self.MARC_DATA_SUBFIELDS = get_marc_data_field_subfields(db, id, tag)
        self.MARC_DATA_POSITIONS = get_marc_data_field_positions(db, id, tag)

VALLS = GUI_Elems_With_Val()

class GUI_Screens(Enum):
    MAIN_SCREEN = {
        "values":[
            "SERVICE",
            "PROCESSING_VAL",
            "FILE_PATH",
            "OUTPUT_PATH",
            "LOGS_PATH"
        ]
    }
    PROCESSING_CONFIGURATION_SCREEN = {
        "values":[
            "ORIGIN_URL",
            "TARGET_URL",
            "ILN",
            "RCR",
        ]
    }

# --------------- Screen layouts ---------------

MAIN_SCREEN_LAYOUT = [
    # Lang
    [  
        sg.Push(), # to align right
        sg.Button(GUI_Text.CHOSE_LANG.value[lang], k=GUI_Text.CHOSE_LANG.name)
    ],
    
    # Title
    [
        sg.Push(),
        sg.Text(GUI_Text.MAIN_SCREEN_WINDOW_TITLE.value[lang], justification='center', font=("Verdana", 26), k=GUI_Text.MAIN_SCREEN_WINDOW_TITLE.name),
        sg.Push()
    ],

    # Processing
    [
        sg.Text(f"{GUI_Text.PROCESSING.value[lang]} :", k=GUI_Text.PROCESSING.name),
        sg.OptionMenu([processing.name for processing in fcr.FCR_Processings], size=(30, 5), key="PROCESSING_VAL", default_value=VALLS.PROCESSING_VAL)
    ],

    # Original file path
    [sg.Text(f"{GUI_Text.FILE_TO_ANALYZE.value[lang]} :", k=GUI_Text.FILE_TO_ANALYZE.name)],
    [sg.Input(key="FILE_PATH", default_text=VALLS.FILE_PATH, size=(80, None)), sg.FileBrowse()],

    # Output folder
    [sg.Text(f"{GUI_Text.OUTPUT_FOLDER.value[lang]} :", k=GUI_Text.OUTPUT_FOLDER.name)],
    [sg.Input(key="OUTPUT_PATH", default_text=VALLS.OUTPUT_PATH, size=(80, None)), sg.FolderBrowse()],

    # Service name
    [
        sg.Text(f"{GUI_Text.SERVICE_NAME.value[lang]} :", k=GUI_Text.SERVICE_NAME.name),
        sg.Input(key="SERVICE", default_text=VALLS.SERVICE, size=(40, None))
    ],

    # Logs path
    [sg.Text(f"{GUI_Text.LOG_FOLDER.value[lang]} :", k=GUI_Text.LOG_FOLDER.name)],
    [sg.Input(key="LOGS_PATH", default_text=VALLS.LOGS_PATH, size=(80, None)), sg.FolderBrowse()],

    # Submit + Save
    [
        sg.Push(),
        sg.Button(GUI_Text.GO_TO_PROCESSING_CONFIGURATION.value[lang], key=GUI_Text.GO_TO_PROCESSING_CONFIGURATION.name),
        sg.Push(),
        sg.Button(GUI_Text.SAVE_EXECUTION_PARAMETERS.value[lang], key=GUI_Text.SAVE_EXECUTION_PARAMETERS.name)
    ]
]

PROCESSING_CONFIGURATION_SCREEN_MAIN_TAB_LAYOUT = [
    # ----- Row 1-2 -----
    # Origin database URL
    [
        sg.Text(f"{GUI_Text.ORIGIGN_DATABASE_URL.value[lang]} :", k=GUI_Text.ORIGIGN_DATABASE_URL.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]})
    ],
    [
        sg.Input(key="ORIGIN_URL", default_text=VALLS.ORIGIN_URL, size=(80, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]})
    ],

    # ----- Row 3-4 -----
    # Target database URL
    [
        sg.Text(f"{GUI_Text.TARGET_DATABASE_URL.value[lang]} :", k=GUI_Text.TARGET_DATABASE_URL.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN"]})
    ],
    [
        sg.Input(key="TARGET_URL", default_text=VALLS.TARGET_URL, size=(80, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN"]})
    ],

    # ----- Row 5-6 -----
    # Sudoc ILN + RCR
    [
        sg.Text(f"{GUI_Text.ILN_TEXT.value[lang]} :", k=GUI_Text.ILN_TEXT.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]}),
        sg.Input(key="ILN", default_text=VALLS.ILN, size=(4, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]})
    ],
    [
        sg.Text(f"{GUI_Text.RCR_TEXT.value[lang]} :", k=GUI_Text.RCR_TEXT.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]}),
        sg.Input(key="RCR", default_text=VALLS.RCR, size=(10, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]})
    ],

    # ----- Row 7-8 -----
    # 3rd filter parameter
    [
        
    ],
    [
        
    ]
]

PROCESSING_CONFIGURATION_SCREEN_ORIGIN_TAB_LAYOUT = [
    # ----- Database -----
    [
        sg.Text(f"{GUI_Text.ORIGIN_DATABASE_MARC_TEXT.value[lang]} :", k=GUI_Text.ORIGIN_DATABASE_MARC_TEXT.name),
        sg.OptionMenu(list(marc_fields_json.keys()), size=(30, 5), key="ORIGIN_DATABASE_MARC", default_value=VALLS.ORIGIN_DATABASE_MARC)
    ],

    # ----- Data -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_TO_CONFIGURE.value[lang]} :", k=GUI_Text.MARC_DATA_TO_CONFIGURE.name),
        sg.OptionMenu(
            get_marc_data_labels(VALLS.ORIGIN_DATABASE_MARC, lang),
            size=(60, 5), key="MARC_DATA_BEING_CONFIGURED_LABEL",
            default_value=get_marc_data_label_by_id(VALLS.ORIGIN_DATABASE_MARC, lang, VALLS.MARC_DATA_BEING_CONFIGURED)
        )
    ],

    # ----- Field -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_FIELDS_TEXT.value[lang]} :", k=GUI_Text.MARC_DATA_FIELDS_TEXT.name),
        sg.OptionMenu(
            get_marc_data_fields_tag(VALLS.ORIGIN_DATABASE_MARC, VALLS.MARC_DATA_BEING_CONFIGURED) + [GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[lang]],
            size=(30, 5), key="MARC_DATA_FIELD", default_value=VALLS.MARC_DATA_FIELD
        )
    ],

    # ----- Signel lien coded data -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_SINGLE_LINE_CODED_DATA_TEXT.value[lang]} ?", k=GUI_Text.MARC_DATA_SINGLE_LINE_CODED_DATA_TEXT.name),
        sg.Checkbox(GUI_Text.YES.value[lang],
            default=get_marc_data_field_single_line_coded_data(VALLS.ORIGIN_DATABASE_MARC, VALLS.MARC_DATA_BEING_CONFIGURED, VALLS.MARC_DATA_FIELD),
            k='MARC_DATA_SINGLE_LINE_CODED_DATA',
            enable_events=True
        )
    ],

    # ----- Filtering subfield -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_FILTERING_SUBFIELD_TEXT.value[lang]} :", k=GUI_Text.MARC_DATA_FILTERING_SUBFIELD_TEXT.name),
        sg.Input(key="MARC_DATA_FILTERING_SUBFIELD",
            default_text=get_marc_data_field_filtering_subfield(VALLS.ORIGIN_DATABASE_MARC, VALLS.MARC_DATA_BEING_CONFIGURED, VALLS.MARC_DATA_FIELD),
            size=(2, None)
        )
    ],

    # ----- Subfields -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_SUBFIELDS_TEXT.value[lang]} :", k=GUI_Text.MARC_DATA_SUBFIELDS_TEXT.name),
        sg.Input(key="MARC_DATA_SUBFIELDS",
            default_text=get_marc_data_field_subfields(VALLS.ORIGIN_DATABASE_MARC, VALLS.MARC_DATA_BEING_CONFIGURED, VALLS.MARC_DATA_FIELD),
            size=(38, None)
        )
    ],

    # ----- Positions -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_POSITIONS_TEXT.value[lang]} :", k=GUI_Text.MARC_DATA_POSITIONS_TEXT.name),
        sg.Input(key="MARC_DATA_POSITIONS",
            default_text=get_marc_data_field_positions(VALLS.ORIGIN_DATABASE_MARC, VALLS.MARC_DATA_BEING_CONFIGURED, VALLS.MARC_DATA_FIELD),
            size=(38, None)
        )
    ],
    

]

PROCESSING_CONFIGURATION_SCREEN_LAYOUT = [
    # Title
    [
        sg.Push(),
        sg.Text(GUI_Text.PROCESSING_CONFIGURATION_WINDOW_TITLE.value[lang], justification='center', font=("Verdana", 26), k=GUI_Text.PROCESSING_CONFIGURATION_WINDOW_TITLE.name),
        sg.Push()
    ],
    # Chosen processing
    [
        sg.Push(),
        sg.Text(VALLS.PROCESSING_VAL, justification='center', font=("Verdana", 22), k="-display_chosen_processing_in_processing_configuration_screen-"),
        sg.Push()
    ],

    # Tabs
    [
        sg.TabGroup([
            [
                sg.Tab(GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE.value[lang], PROCESSING_CONFIGURATION_SCREEN_MAIN_TAB_LAYOUT, k=GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE.name),
                sg.Tab(GUI_Text.PROCESSING_CONFIGURATION_ORIGIN_TAB_TITLE.value[lang], PROCESSING_CONFIGURATION_SCREEN_ORIGIN_TAB_LAYOUT, k=GUI_Text.PROCESSING_CONFIGURATION_ORIGIN_TAB_TITLE.name)
            ]
        ])
    ],

    # Submit + Save
    [
        sg.Push(),
        sg.Button(GUI_Text.START_ANALYSIS.value[lang], key=GUI_Text.START_ANALYSIS.name),
        sg.Push(),
        sg.Button(GUI_Text.SAVE_THIS_PROCESSING_CONFIGURATION_TAB_PARAMETERS.value[lang], key=GUI_Text.SAVE_THIS_PROCESSING_CONFIGURATION_TAB_PARAMETERS.name)
    ]
]

GLOBAL_LAYOUT = [[
    sg.Column(MAIN_SCREEN_LAYOUT, key=GUI_Screens.MAIN_SCREEN.name),
    sg.Column(PROCESSING_CONFIGURATION_SCREEN_LAYOUT, key=GUI_Screens.PROCESSING_CONFIGURATION_SCREEN.name)
]]

# --------------- UI Function def ---------------
def save_parameters(screen: GUI_Screens, val: dict):
    """Saves the parameters of the screen.
    
    Takes as the current screen."""
    dotenv.set_key(DOTENV_FILE, "LANG", lang)
    for screen_val in screen.value["values"]:
        new_val = val[screen_val]
        if type(new_val) == list and len(new_val) == 1:
            new_val = new_val[0]
        dotenv.set_key(DOTENV_FILE, screen_val, new_val)

def switch_languages(window: sg.Window, lang: str):
    """Switches every test element language.
    
    Takes as argument :
        - window : the window element
        - lang : the lang, as ISO 639-2"""
    for elem in GUI_Text:
        if elem.name in window.key_dict:
            window[elem.name].update(elem.value[lang])
    # Changes the language of data labels in processing configuration
    window["MARC_DATA_BEING_CONFIGURED_LABEL"].update(
        values=get_marc_data_labels(VALLS.ORIGIN_DATABASE_MARC, lang)
        # default_value=get_marc_data_label_by_id(VALLS.ORIGIN_DATABASE_MARC, lang, VALLS.MARC_DATA_BEING_CONFIGURED)
    )

def open_screen(window: sg.Window, screen: GUI_Screens, lang: str) -> sg.Window:
    """Generic function to generate a screen.
    
    Takes as argument the wanted screen entry in GUI_Screen"""
    screen_name = None
    if screen == GUI_Screens.MAIN_SCREEN:
        screen_name = GUI_Text[screen.name + "_NAME"].value[lang]
    if screen == GUI_Screens.PROCESSING_CONFIGURATION_SCREEN:
        screen_name = GUI_Text[screen.name + "_NAME"].value[lang]
    if not window:
        window = sg.Window(screen_name, GLOBAL_LAYOUT, finalize=True)
        toggle_screen_visibility(window, screen)
        return window
    else:
        window.Title = screen_name
        toggle_screen_visibility(window, screen)

def toggle_screen_visibility(window: sg.Window, wanted_screen: GUI_Screens):
    """Display the wanetd screen and hides the other ones"""
    for screen in GUI_Screens:
        if screen != wanted_screen:
            window[screen.name].update(visible=False)
        else:
            window[screen.name].update(visible=True)
    # Display only this Processing used parts
    if screen == GUI_Screens.PROCESSING_CONFIGURATION_SCREEN:
        for elem in [elem for row in window[GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE.name].Rows for elem in row]:
            if not elem.metadata:
                continue
            elif (
                    VALLS.PROCESSING_VAL in elem.metadata["class"]
                    and "PROCESSING_CONFIGURATION_MAIN" in elem.metadata["class"]
                ):
                elem.update(visible=True)
            else:
                elem.update(visible=False)

def reset_marc_field_field_list(db: str, id: str):
    """Resets the seelct UI for the marc field"""
    new_list = get_marc_data_fields_tag(db, id)
    new_list += [GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[lang]]
    window["MARC_DATA_FIELD"].update(values=new_list)

def get_option_menu_PYSimpleGUI_key_by_TKStringVar_name(window: sg.Window, var_name: str) -> str:
    """Returns the PySimpleGUI key associated with this TKStringVar.
    Only used for OptionMenu callbacks"""
    for elem in window.key_dict:
        if type(window[elem]) != sg.OptionMenu:
            continue
        if window[elem].TKStringVar._name == var_name:
            return elem

def option_menu_callback(var, index, mode, key=""):
    """
    For OptionMenu
    var - tkinter control variable.
    index - index of var, '' if var is not a list.
    mode - 'w' for 'write' here.
    """
    # From https://github.com/PySimpleGUI/PySimpleGUI/issues/4454
    key = get_option_menu_PYSimpleGUI_key_by_TKStringVar_name(window, var)
    window.write_event_value(key, window[key].TKStringVar.get())

def update_UI_marc_data_being_configured(window: sg.Window, valls: GUI_Elems_With_Val):
    """Updates the UI of the MARC DAta being configured"""
    reset_marc_field_field_list(valls.ORIGIN_DATABASE_MARC, valls.MARC_DATA_BEING_CONFIGURED)
    window["MARC_DATA_FIELD"].update(value=valls.MARC_DATA_FIELD)
    window["MARC_DATA_SINGLE_LINE_CODED_DATA"].update(value=valls.MARC_DATA_SINGLE_LINE_CODED_DATA)
    window["MARC_DATA_FILTERING_SUBFIELD"].update(value=valls.MARC_DATA_FILTERING_SUBFIELD)
    window["MARC_DATA_SUBFIELDS"].update(value=valls.MARC_DATA_SUBFIELDS)
    window["MARC_DATA_POSITIONS"].update(value=valls.MARC_DATA_POSITIONS)

# # --------------- Window Definition ---------------
# # Create the window
window = None
curr_screen = GUI_Screens.MAIN_SCREEN
window = open_screen(window, curr_screen, lang)
# Ensure thar changin option in OptionMenu generates an event
for elem in window.key_dict:
    if type(window[elem]) == sg.OptionMenu:
        window[elem].TKStringVar.trace("w", option_menu_callback)

# # --------------- Event loop or Window.read call ---------------
is_updating_marc_database = False
# # Display and interact with the Window
while True:
    event, val = window.read()
    print(event)

    # --------------- User left ---------------
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        print("Application quittée par l'usager")
        exit()

    # --------------- Updates language ---------------
    if event == GUI_Text.CHOSE_LANG.name:
        if lang == "eng":
            lang = "fre"
        else:
            lang = "eng"
        switch_languages(window, lang)

    # --------------- Save parameters ---------------
    if (event[0:5] == "SAVE_"):
        save_parameters(curr_screen, val)

    # --------------- Continue to processign configuration ---------------
    if event == GUI_Text.GO_TO_PROCESSING_CONFIGURATION.name:
        curr_screen = GUI_Screens.PROCESSING_CONFIGURATION_SCREEN
        VALLS.PROCESSING_VAL = val["PROCESSING_VAL"]
        open_screen(window, curr_screen, lang)

    # --------------- User selected an Origin database ---------------
    if event == "ORIGIN_DATABASE_MARC" and not is_updating_marc_database:
        is_updating_marc_database = True
        VALLS.ORIGIN_DATABASE_MARC = val["ORIGIN_DATABASE_MARC"]
        VALLS.MARC_DATA_BEING_CONFIGURED_LABEL = get_marc_data_label_by_id(VALLS.ORIGIN_DATABASE_MARC, lang, VALLS.MARC_DATA_BEING_CONFIGURED)
        window["MARC_DATA_BEING_CONFIGURED_LABEL"].update(values=get_marc_data_labels(VALLS.ORIGIN_DATABASE_MARC, lang), value=VALLS.MARC_DATA_BEING_CONFIGURED_LABEL)
        VALLS.update_marc_data_being_configured(VALLS.MARC_DATA_BEING_CONFIGURED_LABEL, lang)
        update_UI_marc_data_being_configured(window, VALLS)
        is_updating_marc_database = False

    # --------------- User selected an Origin database ---------------
    if event == "MARC_DATA_BEING_CONFIGURED_LABEL":
        VALLS.MARC_DATA_BEING_CONFIGURED_LABEL = val["MARC_DATA_BEING_CONFIGURED_LABEL"]
        VALLS.update_marc_data_being_configured(VALLS.MARC_DATA_BEING_CONFIGURED_LABEL, lang)
        update_UI_marc_data_being_configured(window, VALLS)

    # --------------- Close the window && execute main ---------------
    if event == GUI_Text.START_ANALYSIS.name:
        window.close()

        execution_settings = fcr.Execution_Settings(CURR_DIR)
        execution_settings.get_values_from_GUI(val)

        # Launch the main script
        print("Exécution du script principal")
        main.main(execution_settings)