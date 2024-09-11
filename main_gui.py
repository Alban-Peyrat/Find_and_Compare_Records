# -*- coding: utf-8 -*-

# External import
import FreeSimpleGUI as sg
import json
import os
import dotenv
from enum import Enum
from typing import List, Dict

# Internal import
from theme.theme import *
from cl_ES import Execution_Settings
from cl_PODA import Processing_Names
import main
from fcr_gui_lang import GUI_Text
from func_file_check import check_dir_existence, check_file_existence

CURR_DIR = os.path.dirname(__file__)
# Load env var
dotenv.load_dotenv()
DOTENV_FILE = dotenv.find_dotenv()

# Get GUI parameters
sg.set_options(font=font, icon=CURR_DIR + "/theme/logo.ico", window_location=window_location)
sg.theme_add_new(theme_name, theme)
sg.theme(theme_name)

# Sets up an execution Settings instance
VALLS = Execution_Settings(CURR_DIR)
VALLS.load_env_values()

# --------------- Screen classes & enums ---------------

class Tab_Names(Enum):
    PROCESSING_CONFIGURATION_MAIN_TAB_TITLE = 0
    PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE = 1
    PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE = 2

class Tab(object):
    def __init__(self, tab:Tab_Names, values:List[str], text:GUI_Text) -> None:
        self.enum_member = tab
        self.name = tab.name
        self.id = tab.value
        self.values = values
        self.text_enum_member = text
        self.text_name = text.name
        
class Screen_Names(Enum):
    MAIN_SCREEN = 0
    PROCESSING_CONFIGURATION_SCREEN = 1

class Screen(object):
    def __init__(self, screen:Screen_Names, values:List[str],  tabs:Dict[Tab_Names, Tab]) -> None:
        self.enum_member = screen
        self.name = screen.name
        self.id = screen.value
        self.values = values
        self.tabs = tabs

        
    def get_tab(self, tab:Tab_Names|str|int) -> Tab:
        """Returns the Screen instance for the given processing.
        Argument can either be :
            - Screen_Names member
            - Screen_Names member name
            - Screen_Names member value"""
        if type(tab) == Tab_Names:
            return self.tabs[tab]
        elif type(tab) == str:
            return self.tabs[Tab_Names[tab]]
        elif type(tab) == int:
            for member in Tab_Names:
                if member.value == tab:
                    return self.tabs[member]
        return None

curr_screen = None
SCREENS_LIST = {
    Screen_Names.MAIN_SCREEN:Screen(
        screen=Screen_Names.MAIN_SCREEN,
        values=[
            "SERVICE",
            "LOG_LEVEL",
            "PROCESSING_VAL",
            "FILE_PATH",
            "OUTPUT_PATH",
            "CSV_OUTPUT_JSON_CONFIG_PATH",
            "LOGS_PATH",
        ],
        tabs={}
    ),
    Screen_Names.PROCESSING_CONFIGURATION_SCREEN:Screen(
        screen=Screen_Names.PROCESSING_CONFIGURATION_SCREEN,
        values=[],
        tabs = {
            Tab_Names.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE:Tab(
                tab=Tab_Names.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE,
                values=[
                    "ORIGIN_URL",
                    "TARGET_URL",
                    "ILN",
                    "RCR",
                    "FILTER1",
                    "FILTER2",
                    "FILTER3"
                ],
                text=GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE
            ),
            Tab_Names.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE:Tab(
                tab=Tab_Names.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE,
                values=[],
                text=GUI_Text.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE
            ),
            Tab_Names.PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE:Tab(
                tab=Tab_Names.PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE,
                values=[
                    "ORIGIN_DATABASE_MAPPING",
                    "TARGET_DATABASE_MAPPING"
                ],
                text=GUI_Text.PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE
            )
        }
    )
}

def get_screen(screen:Screen_Names|str|int) -> Screen:
    """Returns the Screen instance for the given processing.
    Argument can either be :
        - Screen_Names member
        - Screen_Names member name
        - Screen_Names member value"""
    if type(screen) == Screen_Names:
        return SCREENS_LIST[screen]
    elif type(screen) == str:
        return SCREENS_LIST[Screen_Names[screen]]
    elif type(screen) == int:
        for member in Screen_Names:
            if member.value == screen:
                return SCREENS_LIST[member]
    return None

# --------------- Screen layouts ---------------

MAIN_SCREEN_LAYOUT = [
    # LANG
    [  
        sg.Push(), # to align right
        sg.Button(GUI_Text.CHOSE_LANG.value[VALLS.lang], k=GUI_Text.CHOSE_LANG.name)
    ],
    
    # Title
    [
        sg.Push(),
        sg.Text(GUI_Text.MAIN_SCREEN_WINDOW_TITLE.value[VALLS.lang], justification='center', font=("Verdana", 26), k=GUI_Text.MAIN_SCREEN_WINDOW_TITLE.name),
        sg.Push()
    ],

    # Processing
    [
        sg.Text(f"{GUI_Text.PROCESSING.value[VALLS.lang]} :", k=GUI_Text.PROCESSING.name),
        sg.OptionMenu([processing.name for processing in Processing_Names], size=(30, 5), key="PROCESSING_VAL", default_value=VALLS.processing.name)
    ],

    # Original file path
    [sg.Text(f"{GUI_Text.FILE_TO_ANALYZE.value[VALLS.lang]} :", k=GUI_Text.FILE_TO_ANALYZE.name)],
    [sg.Input(key="FILE_PATH", default_text=VALLS.file_path, size=(80, None)), sg.FileBrowse()],

    # Output folder
    [sg.Text(f"{GUI_Text.OUTPUT_FOLDER.value[VALLS.lang]} :", k=GUI_Text.OUTPUT_FOLDER.name)],
    [sg.Input(key="OUTPUT_PATH", default_text=VALLS.output_path, size=(80, None)), sg.FolderBrowse()],

    # CSV export file path
    [sg.Text(f"{GUI_Text.CSV_COLS_CONFIG_FILE_PATH_TEXT.value[VALLS.lang]} :", k=GUI_Text.CSV_COLS_CONFIG_FILE_PATH_TEXT.name)],
    [sg.Input(key="CSV_OUTPUT_JSON_CONFIG_PATH", default_text=VALLS.csv_cols_config_path, size=(80, None)), sg.FileBrowse()],


    # Service name & log lovel
    [
        sg.Text(f"{GUI_Text.SERVICE_NAME.value[VALLS.lang]} :", k=GUI_Text.SERVICE_NAME.name),
        sg.Input(key="SERVICE", default_text=VALLS.service, size=(25, None)),
        sg.Text(f"{GUI_Text.LOG_LEVEL_TEXT.value[VALLS.lang]} :", k=GUI_Text.LOG_LEVEL_TEXT.name),
        sg.OptionMenu(VALLS.UI_get_log_levels(), size=(9, None), key="LOG_LEVEL", default_value=VALLS.log_level)
    ],

    # Logs path
    [
        sg.Text(f"{GUI_Text.LOG_FOLDER.value[VALLS.lang]} :", k=GUI_Text.LOG_FOLDER.name),
        sg.Input(key="LOGS_PATH", default_text=VALLS.logs_path, size=(55, None)), sg.FolderBrowse()
    ],

    # Submit + Save
    [
        sg.Push(),
        sg.Button(GUI_Text.GO_TO_PROCESSING_CONFIGURATION.value[VALLS.lang], key=GUI_Text.GO_TO_PROCESSING_CONFIGURATION.name),
        sg.Push(),
        sg.Button(GUI_Text.SAVE_EXECUTION_PARAMETERS.value[VALLS.lang], key=GUI_Text.SAVE_EXECUTION_PARAMETERS.name)
    ]
]

PROCESSING_CONFIGURATION_SCREEN_MAIN_TAB_LAYOUT = [
    # ----- Row 1-2 -----
    # Origin database URL
    [
        sg.Text(
            f"{GUI_Text.ORIGIGN_DATABASE_URL.value[VALLS.lang]} :",
            k=GUI_Text.ORIGIGN_DATABASE_URL.name,
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.BETTER_ITEM.name,
                Processing_Names.BETTER_ITEM_DVD.name,
                Processing_Names.BETTER_ITEM_NO_ISBN.name,
                Processing_Names.BETTER_ITEM_MAPS.name
            ]}
        )
    ],
    [
        sg.Input(
            key="ORIGIN_URL",
            default_text=VALLS.origin_url,
            size=(80, None),
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.BETTER_ITEM.name,
                Processing_Names.BETTER_ITEM_DVD.name,
                Processing_Names.BETTER_ITEM_NO_ISBN.name,
                Processing_Names.BETTER_ITEM_MAPS.name
            ]}
        )
    ],

    # ----- Row 3-4 -----
    # Target database URL
    [
        sg.Text(
            f"{GUI_Text.TARGET_DATABASE_URL.value[VALLS.lang]} :",
            k=GUI_Text.TARGET_DATABASE_URL.name,
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.MARC_FILE_IN_KOHA_SRU.name
            ]}
        )
    ],
    [
        sg.Input(
            key="TARGET_URL",
            default_text=VALLS.target_url,
            size=(80, None),
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.MARC_FILE_IN_KOHA_SRU.name
            ]}
        )
    ],

    # ----- Row 5-6 -----
    # Sudoc ILN + RCR (filter1-2)
    [
        sg.Text(
            f"{GUI_Text.ILN_TEXT.value[VALLS.lang]} :",
            k=GUI_Text.ILN_TEXT.name,
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.BETTER_ITEM.name,
                Processing_Names.BETTER_ITEM_DVD.name,
                Processing_Names.BETTER_ITEM_NO_ISBN.name,
                Processing_Names.BETTER_ITEM_MAPS.name
            ]}
        ),
        sg.Input(
            key="ILN",
            default_text=VALLS.iln,
            size=(4, None),
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.BETTER_ITEM.name,
                Processing_Names.BETTER_ITEM_DVD.name,
                Processing_Names.BETTER_ITEM_NO_ISBN.name,
                Processing_Names.BETTER_ITEM_MAPS.name
            ]}
        ),
        sg.Text(
            f"{GUI_Text.FILTER1_TEXT.value[VALLS.lang]} :",
            k=GUI_Text.FILTER1_TEXT.name,
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.MARC_FILE_IN_KOHA_SRU.name
            ]}
        ),
        sg.Input(
            key="FILTER1",
            default_text=VALLS.filter1,
            size=(4, None),
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.MARC_FILE_IN_KOHA_SRU.name
            ]}
        )
    ],
    [
        sg.Text(
            f"{GUI_Text.RCR_TEXT.value[VALLS.lang]} :",
            k=GUI_Text.RCR_TEXT.name,
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.BETTER_ITEM.name,
                Processing_Names.BETTER_ITEM_DVD.name,
                Processing_Names.BETTER_ITEM_NO_ISBN.name,
                Processing_Names.BETTER_ITEM_MAPS.name
            ]}
        ),
        sg.Input(
            key="RCR",
            default_text=VALLS.rcr,
            size=(10, None),
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.BETTER_ITEM.name,
                Processing_Names.BETTER_ITEM_DVD.name,
                Processing_Names.BETTER_ITEM_NO_ISBN.name,
                Processing_Names.BETTER_ITEM_MAPS.name
            ]}
        ),
        sg.Text(
            f"{GUI_Text.FILTER2_TEXT.value[VALLS.lang]} :",
            k=GUI_Text.FILTER2_TEXT.name,
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.MARC_FILE_IN_KOHA_SRU.name
            ]}
        ),
        sg.Input(
            key="FILTER2",
            default_text=VALLS.filter2,
            size=(4, None),
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.MARC_FILE_IN_KOHA_SRU.name
            ]}
        )
    ],

    # ----- Row 7-8 -----
    # 3rd filter parameter
    [
        sg.Text(
            f"{GUI_Text.FILTER3_TEXT.value[VALLS.lang]} :",
            k=GUI_Text.FILTER3_TEXT.name,
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.MARC_FILE_IN_KOHA_SRU.name
            ]}
        ),
        sg.Input(
            key="FILTER3",
            default_text=VALLS.filter3,
            size=(4, None),
            metadata={"class":[
                "PROCESSING_CONFIGURATION_MAIN",
                Processing_Names.MARC_FILE_IN_KOHA_SRU.name
            ]}
        )
    ],
    [
        
    ],

    # ----- Row 9 : Save -----
    [
        sg.Button(GUI_Text.SAVE_MAIN_PROCESSING_CONFIGURATION_PARAMETERS.value[VALLS.lang], key=GUI_Text.SAVE_MAIN_PROCESSING_CONFIGURATION_PARAMETERS.name)
    ]
]

PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE_TAB_LAYOUT = [
    # ----- Database -----
    [
        sg.Text(f"{GUI_Text.DATABASE_MAPPING_TEXT.value[VALLS.lang]} :", k=GUI_Text.DATABASE_MAPPING_TEXT.name),
        sg.OptionMenu(VALLS.UI_get_mappings_names(), size=(30, 5), key="DATABASE_MAPPING", default_value=VALLS.UI_curr_database_mapping),
        sg.Push(),
        sg.Button(GUI_Text.SAVE_DATABASE_CONFIGURATION_AS_NEW.value[VALLS.lang], key=GUI_Text.SAVE_DATABASE_CONFIGURATION_AS_NEW.name)
    ],

    # ----- Data -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_TO_CONFIGURE.value[VALLS.lang]} :", k=GUI_Text.MARC_DATA_TO_CONFIGURE.name),
        sg.OptionMenu(
            VALLS.get_data_labels_as_list(),
            size=(60, 5), key="MARC_DATA_BEING_CONFIGURED_LABEL",
            default_value=VALLS.get_data_label_by_id()
        ),
        sg.Button(GUI_Text.SAVE_RENAME_DATA.value[VALLS.lang], key=GUI_Text.SAVE_RENAME_DATA.name)

    ],

    # ----- Field -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_FIELDS_TEXT.value[VALLS.lang]} :", k=GUI_Text.MARC_DATA_FIELDS_TEXT.name),
        sg.OptionMenu(
            VALLS.get_data_field_tags() + [GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[VALLS.lang]],
            size=(30, 5), key="MARC_DATA_FIELD", default_value=VALLS.UI_curr_field
        ),
        sg.Text(f"{GUI_Text.MARC_DATA_ADD_FIELD_TEXT.value[VALLS.lang]} :", k=GUI_Text.MARC_DATA_ADD_FIELD_TEXT.name, metadata={"class":["ADD_NEW_MARC_FIELD"]}),
        sg.Input(key="MARC_DATA_NEW_FIELD",
            default_text="",
            size=(5, None),
            metadata={"class":["ADD_NEW_MARC_FIELD"]}
        )
    ],

    # ----- Single line coded data -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_SINGLE_LINE_CODED_DATA_TEXT.value[VALLS.lang]} ?", k=GUI_Text.MARC_DATA_SINGLE_LINE_CODED_DATA_TEXT.name),
        sg.Checkbox(GUI_Text.YES.value[VALLS.lang],
            default=VALLS.get_data_field_single_line_coded_data(),
            k='MARC_DATA_SINGLE_LINE_CODED_DATA',
            enable_events=True
        )
    ],

    # ----- Filtering subfield -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_FILTERING_SUBFIELD_TEXT.value[VALLS.lang]} :", k=GUI_Text.MARC_DATA_FILTERING_SUBFIELD_TEXT.name),
        sg.Input(key="MARC_DATA_FILTERING_SUBFIELD",
            default_text=VALLS.get_data_field_filtering_subfield(),
            size=(2, None)
        )
    ],

    # ----- Subfields -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_SUBFIELDS_TEXT.value[VALLS.lang]} :", k=GUI_Text.MARC_DATA_SUBFIELDS_TEXT.name),
        sg.Input(key="MARC_DATA_SUBFIELDS",
            default_text=VALLS.get_data_field_subfields(),
            size=(38, None)
        )
    ],

    # ----- Positions -----
    [
        sg.Text(f"{GUI_Text.MARC_DATA_POSITIONS_TEXT.value[VALLS.lang]} :", k=GUI_Text.MARC_DATA_POSITIONS_TEXT.name),
        sg.Input(key="MARC_DATA_POSITIONS",
            default_text=VALLS.get_data_field_positions(),
            size=(38, None)
        )
    ],

    # ----- SAve button -----
    [
        sg.Button(GUI_Text.SAVE_THIS_MARC_FIELD.value[VALLS.lang], key=GUI_Text.SAVE_THIS_MARC_FIELD.name)
    ],

]

PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_LAYOUT = [
    # ----- Origin Database -----
    [
        sg.Text(f"{GUI_Text.CHOSE_ORIGIN_DATABASE_TEXT.value[VALLS.lang]} :", k=GUI_Text.CHOSE_ORIGIN_DATABASE_TEXT.name),
        sg.OptionMenu(VALLS.UI_get_mappings_names(), size=(30, 5), key="ORIGIN_DATABASE_MAPPING", default_value=VALLS.origin_database_mapping)
    ],

    # ----- Origin Database -----
    [
        sg.Text(f"{GUI_Text.CHOSE_TARGET_DATABASE_TEXT.value[VALLS.lang]} :", k=GUI_Text.CHOSE_TARGET_DATABASE_TEXT.name),
        sg.OptionMenu(VALLS.UI_get_mappings_names(), size=(30, 5), key="TARGET_DATABASE_MAPPING", default_value=VALLS.target_database_mapping)
    ],

    # ----- SAve button -----
    [
        sg.Button(GUI_Text.SAVE_CHOSEN_DATABASE_MAPPINGS.value[VALLS.lang], key=GUI_Text.SAVE_CHOSEN_DATABASE_MAPPINGS.name)
    ],

]

PROCESSING_CONFIGURATION_SCREEN_LAYOUT = [
    # Title
    [
        sg.Push(),
        sg.Text(GUI_Text.PROCESSING_CONFIGURATION_WINDOW_TITLE.value[VALLS.lang], justification='center', font=("Verdana", 26), k=GUI_Text.PROCESSING_CONFIGURATION_WINDOW_TITLE.name),
        sg.Push()
    ],
    # Chosen processing
    [
        sg.Push(),
        sg.Text(VALLS.processing.name, justification='center', font=("Verdana", 22), k="-display_chosen_processing_in_processing_configuration_screen-"),
        sg.Push()
    ],

    # Tabs
    [
        sg.TabGroup(k="PROCESSING_CONFIGURATION_SCREEN_TABS", layout=[
            [
                sg.Tab(GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE.value[VALLS.lang], PROCESSING_CONFIGURATION_SCREEN_MAIN_TAB_LAYOUT, k=GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE.name),
                sg.Tab(GUI_Text.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE.value[VALLS.lang], PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE_TAB_LAYOUT, k=GUI_Text.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE.name),
                sg.Tab(GUI_Text.PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE.value[VALLS.lang], PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_LAYOUT, k=GUI_Text.PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE.name)
            ]
        ])
    ],

    # Submit
    [
        sg.Push(),
        sg.Button(GUI_Text.START_ANALYSIS.value[VALLS.lang], key=GUI_Text.START_ANALYSIS.name),
        sg.Push()
    ]
]

GLOBAL_LAYOUT = [[
    sg.Column(MAIN_SCREEN_LAYOUT, key=get_screen(Screen_Names.MAIN_SCREEN).name),
    sg.Column(PROCESSING_CONFIGURATION_SCREEN_LAYOUT, key=get_screen(Screen_Names.PROCESSING_CONFIGURATION_SCREEN).name)
]]

# --------------- UI Function def ---------------
def save_parameters(screen: Screen, val: dict):
    """Saves the parameters of the screen.
    
    Takes as parameters :
        - screen :the current screen
        - val : all values of the window"""
    dotenv.set_key(DOTENV_FILE, "LANG", VALLS.lang)
    val_list = []
    if screen.tabs:
        val_list = screen.get_tab(val[screen.name + "_TABS"]).values
    else:
        val_list = screen.values
    for screen_val in val_list:
        new_val = val[screen_val]
        if type(new_val) == list and len(new_val) == 1:
            new_val = new_val[0]
        dotenv.set_key(DOTENV_FILE, screen_val, new_val)

def save_marc_field(val: dict):
    """Saves the current MARC field in marc_fields.json
    Takes as arguments :
        - val : all values of the window"""
    db = val["DATABASE_MAPPING"]
    data_id = VALLS.get_data_id_from_label(db, val["MARC_DATA_BEING_CONFIGURED_LABEL"])
    this_field = None
    if val["MARC_DATA_FIELD"] == GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[VALLS.lang]:
        this_field = {"tag":val["MARC_DATA_NEW_FIELD"]}
        VALLS.marc_fields_json[db][data_id]["fields"].append(this_field)
    else:
        for field in VALLS.marc_fields_json[db][data_id]["fields"]:
            if field["tag"] == val["MARC_DATA_FIELD"]:
                this_field = field
    this_field["single_line_coded_data"] = val["MARC_DATA_SINGLE_LINE_CODED_DATA"]
    this_field["filtering_subfield"] = val["MARC_DATA_FILTERING_SUBFIELD"]
    this_field["subfields"] = val["MARC_DATA_SUBFIELDS"].split(",")
    this_field["positions"] = val["MARC_DATA_POSITIONS"].split(",")
    with open(CURR_DIR + "/json_configs/marc_fields.json", "w", encoding="utf-8") as f:
        json.dump(VALLS.marc_fields_json, f, indent=4)
    window["MARC_DATA_FIELD"].update(values=VALLS.get_data_field_tags() + [GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[VALLS.lang]], value=val["MARC_DATA_NEW_FIELD"])
    
def save_data_rename(new_name: str, val: dict, window: sg.Window):
    """Saves the new name for this data in the current language
    Takes as arguments :
        - new_name : the new name
        - val : all values of the window
        - window : the curent window"""
    db = val["DATABASE_MAPPING"]
    data_id = VALLS.get_data_id_from_label(db, val["MARC_DATA_BEING_CONFIGURED_LABEL"])
    VALLS.marc_fields_json[db][data_id]["label"][VALLS.lang] = new_name
    with open(CURR_DIR + "/json_configs/marc_fields.json", "w", encoding="utf-8") as f:
        json.dump(VALLS.marc_fields_json, f, indent=4)
    # Change the label inside VALLS
    VALLS.UI_rename_curr_data(new_name)
    # Change the label in the UI
    remove_TKString_trace("MARC_DATA_BEING_CONFIGURED_LABEL", window)
    window["MARC_DATA_BEING_CONFIGURED_LABEL"].update(values=VALLS.get_data_labels_as_list(), value=new_name)
    add_TKString_trace("MARC_DATA_BEING_CONFIGURED_LABEL", window)

def save_mapping_as_new(new_name: str, val: dict, window: sg.Window):
    """Saves a new mapping based on the current one
    Takes as arguments :
        - new_name : the new name
        - val : all values of the window
        - window : the curent window"""
    db = val["DATABASE_MAPPING"]
    new_mapping = VALLS.marc_fields_json[db]
    VALLS.marc_fields_json[new_name] = new_mapping
    with open(CURR_DIR + "/json_configs/marc_fields.json", "w", encoding="utf-8") as f:
        json.dump(VALLS.marc_fields_json, f, indent=4)
    # Change the value inside VALLS
    VALLS.UI_change_curr_database_mapping(new_name)
    # Update the UI
    window["DATABASE_MAPPING"].update(values=VALLS.UI_get_mappings_names(), value=VALLS.UI_curr_database_mapping)
    window["ORIGIN_DATABASE_MAPPING"].update(values=VALLS.UI_get_mappings_names(), value=VALLS.origin_database_mapping)
    window["TARGET_DATABASE_MAPPING"].update(values=VALLS.UI_get_mappings_names(), value=VALLS.target_database_mapping)


def switch_languages(window: sg.Window):
    """Switches every test element language.
    
    Takes as argument :
        - window : the window element"""
    for elem in GUI_Text:
        if elem.name in window.key_dict:
            window[elem.name].update(elem.value[VALLS.lang])
    # Changes the language of data labels in processing configuration
    VALLS.UI_update_curr_data_label()
    window["MARC_DATA_BEING_CONFIGURED_LABEL"].update(
        values=VALLS.get_data_labels_as_list(),
        value=VALLS.UI_curr_data_label
    ) 

def open_screen(window: sg.Window, screen: Screen) -> sg.Window:
    """Generic function to generate a screen.
    
    Takes as arguments :
        - window : the current window
        - screen : the wanted screen entry in GUI_Screen"""
    screen_name = None
    if screen == get_screen(Screen_Names.MAIN_SCREEN):
        screen_name = GUI_Text[screen.name + "_NAME"].value[VALLS.lang]
    if screen == get_screen(Screen_Names.PROCESSING_CONFIGURATION_SCREEN):
        screen_name = GUI_Text[screen.name + "_NAME"].value[VALLS.lang]
    if not window:
        window = sg.Window(screen_name, GLOBAL_LAYOUT, finalize=True)
        toggle_screen_visibility(window, screen)
        return window
    else:
        window.Title = screen_name
        toggle_screen_visibility(window, screen)

def toggle_screen_visibility(window: sg.Window, wanted_screen: Screen):
    """Display the wanetd screen and hides the other ones
    Takes as arguments :
        - window : the current window
        - screen : the wanted screen entry in GUI_Screen"""
    for screen in SCREENS_LIST:
        if SCREENS_LIST[screen] != wanted_screen:
            window[SCREENS_LIST[screen].name].update(visible=False)
        else:
            window[SCREENS_LIST[screen].name].update(visible=True)
    # Display only this Processing used parts
    if SCREENS_LIST[screen].name == get_screen(Screen_Names.PROCESSING_CONFIGURATION_SCREEN).name:
        for elem in [elem for row in window[GUI_Text.PROCESSING_CONFIGURATION_MAIN_TAB_TITLE.name].Rows for elem in row]:
            if not elem.metadata:
                continue
            elif (
                    VALLS.processing.name in elem.metadata["class"]
                    and "PROCESSING_CONFIGURATION_MAIN" in elem.metadata["class"]
                ):
                elem.update(visible=True)
            else:
                elem.update(visible=False)

def reset_marc_field_field_list():
    """Resets the seelct UI for the current marc field"""
    new_list = VALLS.get_data_field_tags()
    new_list += [GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[VALLS.lang]]
    window["MARC_DATA_FIELD"].update(values=new_list, value=new_list[0])
    

def get_option_menu_PYSimpleGUI_key_by_TKStringVar_name(window: sg.Window, var_name: str) -> str:
    """Returns the PySimpleGUI key associated with this TKStringVar.
    Only used for OptionMenu callbacks.
    
    Takes as argument :
        - window : the current window
        - var_name : the tkinter control variable"""
    for elem in window.key_dict:
        if type(window[elem]) != sg.OptionMenu:
            continue
        if window[elem].TKStringVar._name == var_name:
            return elem

def option_menu_callback(var, index, mode, key=""):
    """Enables event for Option Menus
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

def update_UI_marc_data_being_configured(window: sg.Window):
    """Updates the UI of the MARC DAta being configured. Takes as argument the current window"""
    reset_marc_field_field_list()
    window["MARC_DATA_FIELD"].update(value=VALLS.UI_curr_field)
    window["MARC_DATA_SINGLE_LINE_CODED_DATA"].update(value=VALLS.UI_curr_single_line_coded_data)
    window["MARC_DATA_FILTERING_SUBFIELD"].update(value=VALLS.UI_curr_filtering_subfield)
    window["MARC_DATA_SUBFIELDS"].update(value=VALLS.UI_curr_subfields)
    window["MARC_DATA_POSITIONS"].update(value=VALLS.UI_curr_positions)

def toggle_UI_elems_for_new_marc_field(active: bool, window: sg.Window):
    """Toggles all elements used to add a new field.
    Takes as argument a boolean and the current window"""
    for elem in [elem for row in window[GUI_Text.PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE.name].Rows for elem in row]:
        if not elem.metadata:
            continue
        if "ADD_NEW_MARC_FIELD" in elem.metadata["class"]:
            elem.update(visible=active)

    # If new marc fields, sets to default values infos
    if active:
        VALLS.UI_reset_curr_field_subvalues()
        window["MARC_DATA_SINGLE_LINE_CODED_DATA"].update(value=False)
        for key in ["MARC_DATA_FILTERING_SUBFIELD", "MARC_DATA_SUBFIELDS", "MARC_DATA_POSITIONS"]:
            window[key].update(value="")

def ask_chosen_analysis():
    """Last popup, starts the main script"""
    list_val = VALLS.get_analysis_names_as_list()
    window = sg.Window(GUI_Text.CHOSE_ANALYSIS.value[VALLS.lang],
        [
            [
                sg.Text(GUI_Text.CHOSE_ANALYSIS.value[VALLS.lang])
            ],
            [
                sg.OptionMenu(values=list_val, key="CHOSEN_ANALYSIS", default_value=list_val[0])],
            [
                sg.Button(GUI_Text.START_MAIN.value[VALLS.lang], key=GUI_Text.START_MAIN.name)
            ]
    ])
    while True:
        event, val = window.read()
        if event == GUI_Text.START_MAIN.name:
            window.close()
            return VALLS.get_analysis_index_from_name(val["CHOSEN_ANALYSIS"])

# # --------------- Window Definition ---------------
# # Create the window
window = None
curr_screen = get_screen(Screen_Names.MAIN_SCREEN)
window = open_screen(window, curr_screen)
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
        VALLS.UI_switch_lang()
        switch_languages(window)

    # --------------- Save parameters ---------------
    if (event[0:5] == "SAVE_"):
        new_name = None
        # ------- Save Marc Field -------
        if event == GUI_Text.SAVE_THIS_MARC_FIELD.name:
            save_marc_field(val)
        # ------- Save Rename Data -------
        elif event == GUI_Text.SAVE_RENAME_DATA.name:
            new_name = sg.popup_get_text(GUI_Text.SAVE_RENAME_DATA_POPUP_TEXT.value[VALLS.lang] + f" ({VALLS.UI_curr_data}) :")
            if new_name != None:
                save_data_rename(new_name, val, window)
        # ------- Save New Mapping -------
        elif event == GUI_Text.SAVE_DATABASE_CONFIGURATION_AS_NEW.name:
            new_name = sg.popup_get_text(GUI_Text.SAVE_DATABASE_CONFIGURATION_AS_NEW_POPUP_TEXT.value[VALLS.lang] + " :")
            if new_name != None:
                save_mapping_as_new(new_name, val, window) 
        else:
            save_parameters(curr_screen, val)

    # --------------- User selected a mapping ---------------
    if event == "PROCESSING_VAL":
        window["-display_chosen_processing_in_processing_configuration_screen-"].update(value=val["PROCESSING_VAL"])

    # --------------- Continue to processign configuration ---------------
    if event == GUI_Text.GO_TO_PROCESSING_CONFIGURATION.name:
        # Checks if the paths are valid
        invalid_file_paths = []
        info_file_paths = []
        # --- Input file
        if not check_file_existence(val["FILE_PATH"]):
            invalid_file_paths.append(f"- {GUI_Text.FILE_TO_ANALYZE.value[VALLS.lang]} : {GUI_Text.FILE_CHECK_FILE_DOES_NOT_EXIST.value[VALLS.lang]} ({val['FILE_PATH']})")
        # --- Output folder
        for path_gui_key in ["OUTPUT_PATH", "LOGS_PATH"]:
            path_gui_text = GUI_Text.OUTPUT_FOLDER.value[VALLS.lang]
            if path_gui_key == "LOGS_PATH":
                path_gui_text = GUI_Text.LOG_FOLDER.value[VALLS.lang]
            if not check_dir_existence(val[path_gui_key], create=False):
                # Attempt creating it 
                if check_dir_existence(val[path_gui_key], create=True):
                    info_file_paths.append(f"- {path_gui_text} : {GUI_Text.FILE_CHECK_CREATED_FOLDER.value[VALLS.lang]} ({val[path_gui_key]})")
                # Attempt failed
                else:
                    invalid_file_paths.append(f"- {path_gui_text} : {GUI_Text.FILE_CHECK_FAILED_TO_CREATE_FOLDER.value[VALLS.lang]} ({val[path_gui_key]})")
        # If paths are OK, go to next screen
        if invalid_file_paths == []:
            # If some folders were created, show an info pop-up
            if info_file_paths != []:
                sg.popup(f"{GUI_Text.FILE_CHECK_INFO_CONFIG.value[VALLS.lang]} :", "\n".join(info_file_paths), title=GUI_Text.FILE_CHECK_INFO_CONFIG.value[VALLS.lang])
            VALLS.UI_update_main_screen_values(val)
            curr_screen = get_screen(Screen_Names.PROCESSING_CONFIGURATION_SCREEN)
            open_screen(window, curr_screen)
            toggle_UI_elems_for_new_marc_field(False, window)
        else:
            info_txt = ""
            if info_file_paths != []:
                info_txt = f"{GUI_Text.FILE_CHECK_INFO_CONFIG.value[VALLS.lang]} :\n" + "\n".join(info_file_paths)
            sg.popup(f"{GUI_Text.FILE_CHECK_ERROR_CONFIG.value[VALLS.lang]} :", "\n".join(invalid_file_paths), info_txt, title=GUI_Text.FILE_CHECK_ERROR_CONFIG.value[VALLS.lang])
            

    # --------------- User selected a mapping ---------------
    if event == "DATABASE_MAPPING" and not is_updating_marc_database:
        is_updating_marc_database = True
        VALLS.UI_change_curr_database_mapping(val["DATABASE_MAPPING"])
        VALLS.UI_update_curr_data_label()
        window["MARC_DATA_BEING_CONFIGURED_LABEL"].update(values=VALLS.get_data_labels_as_list(), value=VALLS.UI_curr_data_label)
        VALLS.UI_update_curr_data()
        update_UI_marc_data_being_configured(window)
        is_updating_marc_database = False

    # --------------- User selected a MARC data ---------------
    if event == "MARC_DATA_BEING_CONFIGURED_LABEL":
        VALLS.UI_update_curr_data(val["MARC_DATA_BEING_CONFIGURED_LABEL"])
        VALLS.UI_update_curr_data_label()
        update_UI_marc_data_being_configured(window)

    # --------------- User selected a MARC field for a data ---------------
    if event == "MARC_DATA_FIELD":
        # MUST REMOVE THIS TRACE ELSE IT WILL INFINITELY LOOP
        remove_TKString_trace("MARC_DATA_FIELD", window)
        # trace is removed
        VALLS.UI_update_curr_field(val["MARC_DATA_FIELD"])
        if VALLS.UI_curr_field == GUI_Text.MARC_DATA_NEW_FIELD_TEXT.value[VALLS.lang]:
            toggle_UI_elems_for_new_marc_field(True, window)
            VALLS.UI_reset_curr_field_subvalues()
        else:
            toggle_UI_elems_for_new_marc_field(False, window)
            VALLS.UI_update_curr_field_subvalues()
        update_UI_marc_data_being_configured(window)
        # DO NOT FORGET TO REENABLE THE TRACING
        add_TKString_trace("MARC_DATA_FIELD", window)

    # --------------- Close the window && execute main ---------------
    if event == GUI_Text.START_ANALYSIS.name:
        VALLS.UI_update_processing_configuration_values(val)
        window.close()
        VALLS.define_chosen_analysis(ask_chosen_analysis())

        # Launch the main script
        print("Switching to main")
        main.main(VALLS)