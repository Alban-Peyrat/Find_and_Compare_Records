# -*- coding: utf-8 -*-

# External import
import PySimpleGUI as sg
import json
import os
from dotenv import load_dotenv

# Internal import
from theme.theme import *
import main
import fcr_classes as fcr
import fcr_gui_lang as gui_txt

# Load env var
load_dotenv()

# Get GUI parameters
sg.set_options(font=font, icon="theme/logo.ico", window_location=window_location)
sg.theme_add_new(theme_name, theme)
sg.theme(theme_name)

# Load existing settings
settings = {}
with open('./settings.json', "r+", encoding="utf-8") as f:
    settings = json.load(f)
lang = os.getenv("LANG")

# --------------- The Layout ---------------
layout = [
    # Service name
    [sg.Text(f"{gui_txt.Main_GUI.SERVICE_NAME.value[lang]} :"), sg.Input(key="SERVICE", default_text=os.getenv("SERVICE"), size=(40, None))],
    
    # Processing
    [sg.Text(f"{gui_txt.Main_GUI.PROCESSING.value[lang]} :"), sg.Listbox(["better_item", "ensp"], size=(20, 5), key="labels_APPLI", select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)],

    # Data source
    # [
    #     sg.Text("Source de données :"),
    #     sg.Radio("Fichier", "DATA_SOURCE", default=True, size=(7,1), key='DATA-SOURCE-FILE'),
    #     sg.Radio("Rapport Koha", "DATA_SOURCE", default=False, size=(12,1), key="DATA-SOURCE-KOHA-REPORT")
    # ],

    # Original file path
    [sg.Text(f"{gui_txt.Main_GUI.FILE_TO_ANALYZE.value[lang]} :")],
    [sg.Input(key="FILE_PATH", default_text=os.getenv("FILE_PATH"), size=(80, None)), sg.FileBrowse()],

    # Koha report number
    # [sg.Text("Si utilisation d'un rapport Koha :")],
    # [
    #     sg.Text("Numéro de rapport :"),
    #     sg.Input(key="KOHA_REPORT_NB", default_text=os.getenv("KOHA_REPORT_NB"), size=(6, None)),
    #     sg.Text("Identifiant:"),
    #     sg.Input(key="KOHA_USERID", default_text=os.getenv("KOHA_USERID"), size=(15, None)),
    #     sg.Text("Mot de passe :"),
    #     sg.Input(key="KOHA_PASSWORD", default_text=os.getenv("KOHA_PASSWORD"), size=(15, None), password_char="*"),
    # ],

    # Output folder
    [sg.Text(f"{gui_txt.Main_GUI.OUTPUT_FOLDER.value[lang]} :")],
    [sg.Input(key="OUTPUT_PATH", default_text=os.getenv("OUTPUT_PATH"), size=(80, None)), sg.FolderBrowse()],

    # Logs path
    [sg.Text(f"{gui_txt.Main_GUI.LOG_FOLDER.value[lang]} :")],
    [sg.Input(key="LOGS_PATH", default_text=os.getenv("LOGS_PATH"), size=(80, None)), sg.FolderBrowse()],

    # Koha URL
    # [
    #     sg.Text("Koha URL :"),
    #     sg.Input(key="KOHA_URL", default_text=os.getenv("KOHA_URL"), size=(60, None))
    # ],

    # Koha PPN + ILN + RCR
    # [
    #     sg.Text("Koha champ PPN :"),
    #     sg.Input(key="SOURCE_PPN_FIELD", default_text=os.getenv("SOURCE_PPN_FIELD"), size=(3, None)),
    #     sg.Text("Koha sous-champ PPN :"),
    #     sg.Input(key="SOURCE_PPN_SUBFIELD", default_text=os.getenv("SOURCE_PPN_SUBFIELD"), size=(1, None)),
    #     sg.Text("ILN :"),
    #     sg.Input(key="ILN", default_text=os.getenv("ILN"), size=(3, None)),
    #     sg.Text("RCR :"),
    #     sg.Input(key="RCR", default_text=os.getenv("RCR"), size=(9, None))
    # ],

    # Go to MARC fields edit
    [sg.Button(gui_txt.Main_GUI.GO_TO_MARC_FIELDS.value[lang], key="submit")],

    # Submit
    [sg.Button(gui_txt.Main_GUI.START_ANALYSIS.value[lang], key="submit")]
]

# # --------------- Window Definition ---------------
# # Create the window
window = sg.Window("FCR : execute Find and Compare Records", layout)

# # --------------- Event loop or Window.read call ---------------
# # Display and interact with the Window
# event, values = window.read()
event, val = window.read()

if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
    print("Application quittée par l'usager")
    exit()

# # --------------- Closing the window ---------------
window.close()

execution_settings = fcr.Execution_Settings()
execution_settings.get_values_from_GUI(val)

# Launch the main script
print("Exécution du script principal")
main.main(execution_settings)