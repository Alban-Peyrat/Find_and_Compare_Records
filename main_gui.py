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
marc_fields_json = {}
with open(CURR_DIR + "/json_configs/marc_fields.json", "r+", encoding="utf-8") as f:
    marc_fields_json = json.load(f)
analysis = []
with open(CURR_DIR + "/json_configs/analysis.json", "r+", encoding="utf-8") as f:
    analysis = json.load(f)

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

def get_analysis_names_as_list():
    return [this["name"] for this in analysis]

def get_analysis_index_from_name(name: str):
    for index, this in enumerate(analysis):
        if this["name"] == name:
            return index

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
        self.ORIGIN_DATABASE_MAPPING = os.getenv("ORIGIN_DATABASE_MAPPING")
        self.TARGET_DATABASE_MAPPING = os.getenv("TARGET_DATABASE_MAPPING")
        self.DATABASE_MAPPING = self.ORIGIN_DATABASE_MAPPING
        self.MARC_DATA_BEING_CONFIGURED = "id"
        self.MARC_DATA_BEING_CONFIGURED_LABEL = get_marc_data_label_by_id(self.DATABASE_MAPPING, lang, self.MARC_DATA_BEING_CONFIGURED)
        self.MARC_DATA_FIELD = None
        self.MARC_DATA_NEW_FIELD = None
        self.MARC_DATA_SINGLE_LINE_CODED_DATA = None
        self.MARC_DATA_FILTERING_SUBFIELD = None
        self.MARC_DATA_SUBFIELDS = None
        self.MARC_DATA_POSITIONS = None
        self.CHOSEN_ANALYSIS = 0
        self.update_marc_data_being_configured(self.MARC_DATA_BEING_CONFIGURED_LABEL, lang)

        # Processings Specifics
        self.ILN = os.getenv("ILN") # Better_Item
        self.RCR = os.getenv("RCR") # Better_Item
        self.FILTER1 = os.getenv("FILTER1")
        self.FILTER2 = os.getenv("FILTER2")
        self.FILTER3 = os.getenv("FILTER3")
    
    def update_marc_data_being_configured(self, label: str, lang: str):
        """ 
        Takes the label and the lang as argument"""
        db = self.DATABASE_MAPPING
        self.MARC_DATA_BEING_CONFIGURED = get_marc_data_id_from_label(db, lang, label)
        id = self.MARC_DATA_BEING_CONFIGURED
        self.MARC_DATA_FIELD = get_marc_data_fields_tag(db, id)[0]
        self.update_marc_field_being_configured(db, id, self.MARC_DATA_FIELD)

    def update_marc_field_being_configured(self, db: str, id: str, tag: str):
        self.MARC_DATA_SINGLE_LINE_CODED_DATA = get_marc_data_field_single_line_coded_data(db, id, tag)
        self.MARC_DATA_FILTERING_SUBFIELD = get_marc_data_field_filtering_subfield(db, id, tag)
        self.MARC_DATA_SUBFIELDS = get_marc_data_field_subfields(db, id, tag)
        self.MARC_DATA_POSITIONS = get_marc_data_field_positions(db, id, tag)

    def default_marc_field_being_configured(self):
        """Defaults all values for the current field"""
        self.MARC_DATA_SINGLE_LINE_CODED_DATA = False
        self.MARC_DATA_FILTERING_SUBFIELD = ""
        self.MARC_DATA_SUBFIELDS = ""
        self.MARC_DATA_POSITIONS = ""
    
    def rename_data_being_configured(self, new_name: str):
        self.MARC_DATA_BEING_CONFIGURED_LABEL = new_name
    
    def change_current_database_mapping(self, new_mapping: str):
        self.DATABASE_MAPPING = new_mapping

    def set_chosen_analysis(self, nb: int):
        """Updates the chosen analysis. Takes as argument the integer of the analysis"""
        self.CHOSEN_ANALYSIS = nb

VALLS = GUI_Elems_With_Val()

class GUI_Screens(Enum):
    MAIN_SCREEN = {
        "values":[
            "SERVICE",
            "PROCESSING_VAL",
            "FILE_PATH",
            "OUTPUT_PATH",
            "LOGS_PATH"
        ],
        "tabs":[]
    }
    PROCESSING_CONFIGURATION_SCREEN = {
        "values":[
        ],
        "tabs":[
            {
                GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE.name:{
                    "values":[
                        "ORIGIN_URL",
                        "TARGET_URL",
                        "ILN",
                        "RCR",
                        "FILTER1",
                        "FILTER2",
                        "FILTER3"
                    ]
                },
            },
            {
                GUI_Text.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE.name:{
                    "values":[
                    ]
                }
            },
            {
                GUI_Text.PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE.name:{
                    "values":[
                        "ORIGIN_DATABASE_MAPPING",
                        "TARGET_DATABASE_MAPPING"
                    ]
                }
            }
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
        sg.Text(f"{GUI_Text.TARGET_DATABASE_URL.value[lang]} :", k=GUI_Text.TARGET_DATABASE_URL.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.OTHER_DB_IN_LOCAL_DB.name]})
    ],
    [
        sg.Input(key="TARGET_URL", default_text=VALLS.TARGET_URL, size=(80, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.OTHER_DB_IN_LOCAL_DB.name]})
    ],

    # ----- Row 5-6 -----
    # Sudoc ILN + RCR (filter1-2)
    [
        sg.Text(f"{GUI_Text.ILN_TEXT.value[lang]} :", k=GUI_Text.ILN_TEXT.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]}),
        sg.Input(key="ILN", default_text=VALLS.ILN, size=(4, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]}),
        sg.Text(f"{GUI_Text.FILTER1_TEXT.value[lang]} :", k=GUI_Text.FILTER1_TEXT.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.OTHER_DB_IN_LOCAL_DB.name]}),
        sg.Input(key="FILTER1", default_text=VALLS.FILTER1, size=(4, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.OTHER_DB_IN_LOCAL_DB.name]})
    ],
    [
        sg.Text(f"{GUI_Text.RCR_TEXT.value[lang]} :", k=GUI_Text.RCR_TEXT.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]}),
        sg.Input(key="RCR", default_text=VALLS.RCR, size=(10, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.BETTER_ITEM.name]}),
        sg.Text(f"{GUI_Text.FILTER2_TEXT.value[lang]} :", k=GUI_Text.FILTER2_TEXT.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.OTHER_DB_IN_LOCAL_DB.name]}),
        sg.Input(key="FILTER2", default_text=VALLS.FILTER2, size=(4, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.OTHER_DB_IN_LOCAL_DB.name]})
    ],

    # ----- Row 7-8 -----
    # 3rd filter parameter
    [
        sg.Text(f"{GUI_Text.FILTER3_TEXT.value[lang]} :", k=GUI_Text.FILTER3_TEXT.name, metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.OTHER_DB_IN_LOCAL_DB.name]}),
        sg.Input(key="FILTER3", default_text=VALLS.FILTER3, size=(4, None), metadata={"class":["PROCESSING_CONFIGURATION_MAIN", fcr.FCR_Processings.OTHER_DB_IN_LOCAL_DB.name]})
    ],
    [
        
    ],

    # ----- Row 9 : Save -----
    [
        sg.Button(GUI_Text.SAVE_MAIN_PROCESSING_CONFIGURATION_PARAMETERS.value[lang], key=GUI_Text.SAVE_MAIN_PROCESSING_CONFIGURATION_PARAMETERS.name)
    ]
]

PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE_TAB_LAYOUT = [
    # ----- Database -----
    [
        sg.Text(f"{GUI_Text.DATABASE_MAPPING_TEXT.value[lang]} :", k=GUI_Text.DATABASE_MAPPING_TEXT.name),
        sg.OptionMenu(list(marc_fields_json.keys()), size=(30, 5), key="DATABASE_MAPPING", default_value=VALLS.DATABASE_MAPPING),
        sg.Push(),
        sg.Button(GUI_Text.SAVE_DATABASE_CONFIGURATION_AS_NEW.value[lang], key=GUI_Text.SAVE_DATABASE_CONFIGURATION_AS_NEW.name)
    ],

    # ----- Data -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_TO_CONFIGURE.value[lang]} :", k=GUI_Text.MARC_DATA_TO_CONFIGURE.name),
        sg.OptionMenu(
            get_marc_data_labels(VALLS.DATABASE_MAPPING, lang),
            size=(60, 5), key="MARC_DATA_BEING_CONFIGURED_LABEL",
            default_value=get_marc_data_label_by_id(VALLS.DATABASE_MAPPING, lang, VALLS.MARC_DATA_BEING_CONFIGURED)
        ),
        sg.Button(GUI_Text.RENAME_DATA.value[lang], key=GUI_Text.RENAME_DATA.name)

    ],

    # ----- Field -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_FIELDS_TEXT.value[lang]} :", k=GUI_Text.MARC_DATA_FIELDS_TEXT.name),
        sg.OptionMenu(
            get_marc_data_fields_tag(VALLS.DATABASE_MAPPING, VALLS.MARC_DATA_BEING_CONFIGURED) + [GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[lang]],
            size=(30, 5), key="MARC_DATA_FIELD", default_value=VALLS.MARC_DATA_FIELD
        ),
        sg.Text(f"{GUI_Text.MARC_DATA_ADD_FIELD_TEXT.value[lang]} :", k=GUI_Text.MARC_DATA_ADD_FIELD_TEXT.name, metadata={"class":["ADD_NEW_MARC_FIELD"]}),
        sg.Input(key="MARC_DATA_NEW_FIELD",
            default_text="",
            size=(5, None),
            metadata={"class":["ADD_NEW_MARC_FIELD"]}
        )
    ],

    # ----- Single line coded data -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_SINGLE_LINE_CODED_DATA_TEXT.value[lang]} ?", k=GUI_Text.MARC_DATA_SINGLE_LINE_CODED_DATA_TEXT.name),
        sg.Checkbox(GUI_Text.YES.value[lang],
            default=get_marc_data_field_single_line_coded_data(VALLS.DATABASE_MAPPING, VALLS.MARC_DATA_BEING_CONFIGURED, VALLS.MARC_DATA_FIELD),
            k='MARC_DATA_SINGLE_LINE_CODED_DATA',
            enable_events=True
        )
    ],

    # ----- Filtering subfield -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_FILTERING_SUBFIELD_TEXT.value[lang]} :", k=GUI_Text.MARC_DATA_FILTERING_SUBFIELD_TEXT.name),
        sg.Input(key="MARC_DATA_FILTERING_SUBFIELD",
            default_text=get_marc_data_field_filtering_subfield(VALLS.DATABASE_MAPPING, VALLS.MARC_DATA_BEING_CONFIGURED, VALLS.MARC_DATA_FIELD),
            size=(2, None)
        )
    ],

    # ----- Subfields -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_SUBFIELDS_TEXT.value[lang]} :", k=GUI_Text.MARC_DATA_SUBFIELDS_TEXT.name),
        sg.Input(key="MARC_DATA_SUBFIELDS",
            default_text=get_marc_data_field_subfields(VALLS.DATABASE_MAPPING, VALLS.MARC_DATA_BEING_CONFIGURED, VALLS.MARC_DATA_FIELD),
            size=(38, None)
        )
    ],

    # ----- Positions -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_POSITIONS_TEXT.value[lang]} :", k=GUI_Text.MARC_DATA_POSITIONS_TEXT.name),
        sg.Input(key="MARC_DATA_POSITIONS",
            default_text=get_marc_data_field_positions(VALLS.DATABASE_MAPPING, VALLS.MARC_DATA_BEING_CONFIGURED, VALLS.MARC_DATA_FIELD),
            size=(38, None)
        )
    ],

    # ----- SAve button -----
    [
        sg.Button(GUI_Text.SAVE_THIS_MARC_FIELD.value[lang], key=GUI_Text.SAVE_THIS_MARC_FIELD.name)
    ],

]

PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_LAYOUT = [
    # ----- Origin Database -----
    [
        sg.Text(f"{GUI_Text.CHOSE_ORIGIN_DATABASE_TEXT.value[lang]} :", k=GUI_Text.CHOSE_ORIGIN_DATABASE_TEXT.name),
        sg.OptionMenu(list(marc_fields_json.keys()), size=(30, 5), key="ORIGIN_DATABASE_MAPPING", default_value=VALLS.ORIGIN_DATABASE_MAPPING)
    ],

    # ----- Origin Database -----
    [
        sg.Text(f"{GUI_Text.CHOSE_TARGET_DATABASE_TEXT.value[lang]} :", k=GUI_Text.CHOSE_TARGET_DATABASE_TEXT.name),
        sg.OptionMenu(list(marc_fields_json.keys()), size=(30, 5), key="TARGET_DATABASE_MAPPING", default_value=VALLS.TARGET_DATABASE_MAPPING)
    ],

    # ----- SAve button -----
    [
        sg.Button(GUI_Text.SAVE_CHOSEN_DATABASE_MAPPINGS.value[lang], key=GUI_Text.SAVE_CHOSEN_DATABASE_MAPPINGS.name)
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
        sg.TabGroup(k="PROCESSING_CONFIGURATION_SCREEN_TABS", layout=[
            [
                sg.Tab(GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE.value[lang], PROCESSING_CONFIGURATION_SCREEN_MAIN_TAB_LAYOUT, k=GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE.name),
                sg.Tab(GUI_Text.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE.value[lang], PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE_TAB_LAYOUT, k=GUI_Text.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE.name),
                sg.Tab(GUI_Text.PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE.value[lang], PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_LAYOUT, k=GUI_Text.PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE.name)
            ]
        ])
    ],

    # Submit
    [
        sg.Push(),
        sg.Button(GUI_Text.START_ANALYSIS.value[lang], key=GUI_Text.START_ANALYSIS.name),
        sg.Push()
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
    val_list = []
    if screen.value["tabs"]:
        for tab in screen.value["tabs"]:
            if val[screen.name + "_TABS"] in tab.keys():
                val_list = tab[val[screen.name + "_TABS"]]["values"]
    else:
        val_list = screen.value["values"]
    for screen_val in val_list:
        new_val = val[screen_val]
        if type(new_val) == list and len(new_val) == 1:
            new_val = new_val[0]
        dotenv.set_key(DOTENV_FILE, screen_val, new_val)

def save_marc_field(val, lang):
    db = val["DATABASE_MAPPING"]
    data_id = get_marc_data_id_from_label(db, lang, val["MARC_DATA_BEING_CONFIGURED_LABEL"])
    this_field = None
    if val["MARC_DATA_FIELD"] == GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[lang]:
        this_field = {"tag":val["MARC_DATA_NEW_FIELD"]}
        marc_fields_json[db][data_id]["fields"].append(this_field)
    else:
        for field in marc_fields_json[db][data_id]["fields"]:
            if field["tag"] == val["MARC_DATA_FIELD"]:
                this_field = field
    this_field["single_line_coded_data"] = val["MARC_DATA_SINGLE_LINE_CODED_DATA"]
    this_field["filtering_subfield"] = val["MARC_DATA_FILTERING_SUBFIELD"]
    this_field["subfields"] = val["MARC_DATA_SUBFIELDS"]
    this_field["positions"] = val["MARC_DATA_POSITIONS"]
    with open(CURR_DIR + "/json_configs/marc_fields.json", "w", encoding="utf-8") as f:
        json.dump(marc_fields_json, f, indent=4)
    
def save_data_rename(new_name: str, val: dict, lang: str, valls: GUI_Elems_With_Val, window: sg.Window):
    db = val["DATABASE_MAPPING"]
    data_id = get_marc_data_id_from_label(db, lang, val["MARC_DATA_BEING_CONFIGURED_LABEL"])
    marc_fields_json[db][data_id]["label"][lang] = new_name
    with open(CURR_DIR + "/json_configs/marc_fields.json", "w", encoding="utf-8") as f:
        json.dump(marc_fields_json, f, indent=4)
    # Change the label inside VALLS
    valls.rename_data_being_configured(new_name)
    # Change the label in the UI
    remove_TKString_trace("MARC_DATA_BEING_CONFIGURED_LABEL", window)
    window["MARC_DATA_BEING_CONFIGURED_LABEL"].update(values=get_marc_data_labels(valls.DATABASE_MAPPING, lang), value=new_name)
    add_TKString_trace("MARC_DATA_BEING_CONFIGURED_LABEL", window)

def save_mapping_as_new(new_name: str, val: dict, valls:GUI_Elems_With_Val, window: sg.Window):
    db = val["DATABASE_MAPPING"]
    new_mapping = marc_fields_json[db]
    marc_fields_json[new_name] = new_mapping
    with open(CURR_DIR + "/json_configs/marc_fields.json", "w", encoding="utf-8") as f:
        json.dump(marc_fields_json, f, indent=4)
    # Change the value inside VALLS
    valls.change_current_database_mapping(new_name)
    # Update the UI
    window["DATABASE_MAPPING"].update(values=list(marc_fields_json.keys()), value=valls.DATABASE_MAPPING)
    window["ORIGIN_DATABASE_MAPPING"].update(values=list(marc_fields_json.keys()), value=valls.ORIGIN_DATABASE_MAPPING)
    window["TARGET_DATABASE_MAPPING"].update(values=list(marc_fields_json.keys()), value=valls.TARGET_DATABASE_MAPPING)


def switch_languages(window: sg.Window, lang: str):
    """Switches every test element language.
    
    Takes as argument :
        - window : the window element
        - lang : the lang, as ISO 639-2"""
    for elem in GUI_Text:
        if elem.name in window.key_dict:
            window[elem.name].update(elem.value[lang])
    # Changes the language of data labels in processing configuration
    VALLS.MARC_DATA_BEING_CONFIGURED_LABEL = get_marc_data_label_by_id(VALLS.DATABASE_MAPPING, lang, VALLS.MARC_DATA_BEING_CONFIGURED)
    window["MARC_DATA_BEING_CONFIGURED_LABEL"].update(
        values=get_marc_data_labels(VALLS.DATABASE_MAPPING, lang),
        value=VALLS.MARC_DATA_BEING_CONFIGURED_LABEL
        # default_value=get_marc_data_label_by_id(VALLS.DATABASE_MAPPING, lang, VALLS.MARC_DATA_BEING_CONFIGURED)
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
    # window["MARC_DATA_FIELD"].update(values=new_list)
    window["MARC_DATA_FIELD"].update(values=new_list, value=new_list[0])
    

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

def remove_TKString_trace(key:str, window: sg.Window):
    """Removes the trace, takes as argument the key for the element and the window"""
    trace_info = window[key].TKStringVar.trace_info()
    temp, trace_name = trace_info[len(trace_info)-1]
    window[key].TKStringVar.trace_remove("write", trace_name)

def add_TKString_trace(key:str, window: sg.Window):
    """Adds back the trace, takes as argument the key for the element and the window"""
    window[key].TKStringVar.trace("w", option_menu_callback)

def update_UI_marc_data_being_configured(window: sg.Window, valls: GUI_Elems_With_Val):
    """Updates the UI of the MARC DAta being configured"""
    reset_marc_field_field_list(valls.DATABASE_MAPPING, valls.MARC_DATA_BEING_CONFIGURED)
    window["MARC_DATA_FIELD"].update(value=valls.MARC_DATA_FIELD)
    window["MARC_DATA_SINGLE_LINE_CODED_DATA"].update(value=valls.MARC_DATA_SINGLE_LINE_CODED_DATA)
    window["MARC_DATA_FILTERING_SUBFIELD"].update(value=valls.MARC_DATA_FILTERING_SUBFIELD)
    window["MARC_DATA_SUBFIELDS"].update(value=valls.MARC_DATA_SUBFIELDS)
    window["MARC_DATA_POSITIONS"].update(value=valls.MARC_DATA_POSITIONS)

def toggle_UI_elems_for_new_marc_field(active: bool, window: sg.Window):
    """Toggles all elements used to add a new field.
    Takes as argument a boolean"""
    for elem in [elem for row in window[GUI_Text.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE.name].Rows for elem in row]:
        if not elem.metadata:
            continue
        if "ADD_NEW_MARC_FIELD" in elem.metadata["class"]:
            elem.update(visible=active)

    # If new marc fields, sets to default values infos
    if active:
        VALLS.default_marc_field_being_configured()
        window["MARC_DATA_SINGLE_LINE_CODED_DATA"].update(value=False)
        for key in ["MARC_DATA_FILTERING_SUBFIELD", "MARC_DATA_SUBFIELDS", "MARC_DATA_POSITIONS"]:
            window[key].update(value="")

def ask_chosen_analysis(lang: str):
    """Last popup, starts the main script"""
    list_val = get_analysis_names_as_list()
    window = sg.Window(GUI_Text.CHOSE_ANALYSIS.value[lang],
        [
            [
                sg.Text(GUI_Text.CHOSE_ANALYSIS.value[lang])
            ],
            [
                sg.OptionMenu(values=list_val, key="CHOSEN_ANALYSIS", default_value=list_val[0])],
            [
                sg.Button(GUI_Text.START_MAIN.value[lang], key=GUI_Text.START_MAIN.name)
            ]
    ])
    while True:
        event, val = window.read()
        if event == GUI_Text.START_MAIN.name:
            window.close()
            return get_analysis_index_from_name(val["CHOSEN_ANALYSIS"])

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
    # print(event)#debug

    # --------------- User left ---------------
    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
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
        if event == "SAVE_THIS_MARC_FIELD":
            save_marc_field(val, lang)
        else:
            save_parameters(curr_screen, val)

    # --------------- Continue to processign configuration ---------------
    if event == GUI_Text.GO_TO_PROCESSING_CONFIGURATION.name:
        curr_screen = GUI_Screens.PROCESSING_CONFIGURATION_SCREEN
        VALLS.PROCESSING_VAL = val["PROCESSING_VAL"]
        open_screen(window, curr_screen, lang)
        toggle_UI_elems_for_new_marc_field(False, window)

    # --------------- User selected a mapping ---------------
    if event == "DATABASE_MAPPING" and not is_updating_marc_database:
        is_updating_marc_database = True
        VALLS.DATABASE_MAPPING = val["DATABASE_MAPPING"]
        VALLS.MARC_DATA_BEING_CONFIGURED_LABEL = get_marc_data_label_by_id(VALLS.DATABASE_MAPPING, lang, VALLS.MARC_DATA_BEING_CONFIGURED)
        window["MARC_DATA_BEING_CONFIGURED_LABEL"].update(values=get_marc_data_labels(VALLS.DATABASE_MAPPING, lang), value=VALLS.MARC_DATA_BEING_CONFIGURED_LABEL)
        VALLS.update_marc_data_being_configured(VALLS.MARC_DATA_BEING_CONFIGURED_LABEL, lang)
        update_UI_marc_data_being_configured(window, VALLS)
        is_updating_marc_database = False

    # --------------- User selected a MARC data ---------------
    if event == "MARC_DATA_BEING_CONFIGURED_LABEL":
        VALLS.MARC_DATA_BEING_CONFIGURED_LABEL = val["MARC_DATA_BEING_CONFIGURED_LABEL"]
        VALLS.update_marc_data_being_configured(VALLS.MARC_DATA_BEING_CONFIGURED_LABEL, lang)
        update_UI_marc_data_being_configured(window, VALLS)

    # --------------- User selected a MARC field for a data ---------------
    if event == "MARC_DATA_FIELD":
        # MUST REMOVE THIS TRACE ELSE IT WILL INFINITELY LOOP
        remove_TKString_trace("MARC_DATA_FIELD", window)
        # trace is removed
        VALLS.MARC_DATA_FIELD = val["MARC_DATA_FIELD"]
        if VALLS.MARC_DATA_FIELD == GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[lang]:
            toggle_UI_elems_for_new_marc_field(True, window)
            VALLS.default_marc_field_being_configured()
        else:
            toggle_UI_elems_for_new_marc_field(False, window)
            VALLS.update_marc_field_being_configured(VALLS.DATABASE_MAPPING, VALLS.MARC_DATA_BEING_CONFIGURED, VALLS.MARC_DATA_FIELD)
        update_UI_marc_data_being_configured(window, VALLS)
        # DO NOT FORGET TO REENABLE THE TRACING
        add_TKString_trace("MARC_DATA_FIELD", window)

    # --------------- User wants to rename data ---------------
    new_name = None
    if event == GUI_Text.RENAME_DATA.name:
        new_name = sg.popup_get_text(GUI_Text.RENAME_DATA_POPUP_TEXT.value[lang] + f" ({VALLS.MARC_DATA_BEING_CONFIGURED}) :")
        if new_name != None:
            save_data_rename(new_name, val, lang, VALLS, window)   

    # --------------- User wants to save new mapping ---------------
    if event == GUI_Text.SAVE_DATABASE_CONFIGURATION_AS_NEW.name:
        new_name = sg.popup_get_text(GUI_Text.SAVE_DATABASE_CONFIGURATION_AS_NEW_POPUP_TEXT.value[lang] + " :")
        if new_name != None:
            save_mapping_as_new(new_name, val, VALLS, window) 

    # --------------- Close the window && execute main ---------------
    if event == GUI_Text.START_ANALYSIS.name:
        window.close()
        execution_settings = fcr.Execution_Settings(CURR_DIR)
        execution_settings.get_values_from_GUI(val)
        execution_settings.define_chosen_analysis(ask_chosen_analysis(lang))

        # Launch the main script
        print("Switching to main")
        main.main(execution_settings)