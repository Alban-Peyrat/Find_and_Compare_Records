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
        
        # Original file path
        [sg.Text("Fichier à analyser :")],
        [sg.Input(key="FILE_PATH", default_text=settings["FILE_PATH"], size=(80, None)), sg.FileBrowse()],

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

    # Rewrite settings
    settings["SERVICE"] = val["SERVICE"]
    settings["FILE_PATH"] = val["FILE_PATH"]
    settings["OUTPUT_PATH"] = val["OUTPUT_PATH"]
    settings["LOGS_PATH"] = val["LOGS_PATH"]
    settings["KOHA_URL"] = val["KOHA_URL"]
    settings["ILN"] = val["ILN"]
    settings["RCR"] = val["RCR"]

    f.seek(0)
    json.dump(settings, f, indent=4)
    f.truncate()
    print("Paramètres par défaut sauvegardés avec succès")

    # # --------------- Closing the window ---------------
    window.close()