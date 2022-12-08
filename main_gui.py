# -*- coding: utf-8 -*-

# External import
import PySimpleGUI as sg
import json

# Internal import
from theme.theme import *

# Get GUI parameters
sg.set_options(font=font, icon=theme_name + "./theme/logo.ico", window_location=window_location)
sg.theme_add_new(theme_name, theme)
sg.theme(theme_name)

# Load existing settings
with open('./settings.json', "r+", encoding="utf-8") as f:
    settings = json.load(f)

    # # --------------- The Layout ---------------
    layout = [
        # Service name
        [sg.Text("Nom du service :")],
        [sg.Input(key="SERVICE", default_text=settings["SERVICE"], size=(50, None))],
        
        # Data source
        [
            sg.Text("Source de données :"),
            sg.Radio("Fichier", "DATA-SOURCE", default=True, size=(7,1), key='DATA-SOURCE-FILE'),
            sg.Radio("Rapport Koha", "DATA-SOURCE", default=False, size=(12,1), key="DATA-SOURCE-KOHA-REPORT")
        ],

        # Original file path
        [sg.Text("Fichier à analyser :")],
        [sg.Input(key="FILE_PATH", default_text=settings["FILE_PATH"], size=(80, None)), sg.FileBrowse()],

        # Koha report number
        [sg.Text("Si utilisation d'un rapport Koha :")],
        [
            sg.Text("Numéro de rapport :"),
            sg.Input(key="KOHA-REPORT-NB", default_text=settings["KOHA-REPORT-NB"], size=(6, None)),
            sg.Text("Identifiant:"),
            sg.Input(key="KOHA-USERID", default_text=settings["KOHA-USERID"], size=(15, None)),
            sg.Text("Mot de passe :"),
            sg.Input(key="KOHA-PASSWORD", default_text=settings["KOHA-PASSWORD"], size=(15, None), password_char="*"),
        ],

        # Output folder
        [sg.Text("Dossier contenant les résultats :")],
        [sg.Input(key="OUTPUT_PATH", default_text=settings["OUTPUT_PATH"], size=(80, None)), sg.FolderBrowse()],

        # Logs path
        [sg.Text("Dossier contenant les logs :")],
        [sg.Input(key="LOGS_PATH", default_text=settings["LOGS_PATH"], size=(80, None)), sg.FolderBrowse()],

        # Koha URL
        [
            sg.Text("Koha URL :"),
            sg.Input(key="KOHA_URL", default_text=settings["KOHA_URL"], size=(60, None))
        ],

        # ILN
        [
            sg.Text("ILN :"),
            sg.Input(key="ILN", default_text=settings["ILN"], size=(3, None))
        ],

        # RCR
        [
            sg.Text("RCR :"),
            sg.Input(key="RCR", default_text=settings["RCR"], size=(9, None))
        ],

        # Submit
        [sg.Button('Sauvegarder les paramètres par défaut', key="submit")]
    ]

    # # --------------- Window Definition ---------------
    # # Create the window
    window = sg.Window("Paramétrer les valeurs par défaut de Compare Koha Sudoc records", layout)

    # # --------------- Event loop or Window.read call ---------------
    # # Display and interact with the Window
    # event, values = window.read()
    event, val = window.read()


    if event == sg.WIN_CLOSED or event == 'Cancel': # if user closes window or clicks cancel
        print("Application quittée par l'usager")
        exit()


    # # --------------- Closing the window ---------------
    window.close()

    print("---------- Lancement de l'application ----------")