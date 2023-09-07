# -*- coding: utf-8 -*-

# External import
import PySimpleGUI as sg
import json
import os
from dotenv import load_dotenv
import dotenv

# Internal import
from theme.theme import *

# Load env var (the settings)
load_dotenv()
DOTENV_FILE = dotenv.find_dotenv()

# Get GUI parameters
sg.set_options(font=font, icon=theme_name + "./theme/logo.ico", window_location=window_location)
sg.theme_add_new(theme_name, theme)
sg.theme(theme_name)

# # --------------- The Layout ---------------
layout = [
    # Service name
    [sg.Text("Nom du service :")],
    [sg.Input(key="SERVICE", default_text=os.getenv("SERVICE"), size=(50, None))],
    
    # Original file path
    [sg.Text("Fichier à analyser :")],
    [sg.Input(key="FILE_PATH", default_text=os.getenv("FILE_PATH"), size=(80, None)), sg.FileBrowse()],

    # Koha report number
    [sg.Text("Rapport Koha :")],
    [
        sg.Text("Numéro de rapport :"),
        sg.Input(key="KOHA_REPORT_NB", default_text=os.getenv("KOHA_REPORT_NB"), size=(6, None)),
        sg.Text("Identifiant:"),
        sg.Input(key="KOHA_USERID", default_text=os.getenv("KOHA_USERID"), size=(15, None)),
        sg.Text("Mot de passe :"),
        sg.Input(key="KOHA_PASSWORD", default_text=os.getenv("KOHA_PASSWORD"), size=(15, None), password_char="*"),
    ],

    # Output folder
    [sg.Text("Dossier contenant les résultats :")],
    [sg.Input(key="OUTPUT_PATH", default_text=os.getenv("OUTPUT_PATH"), size=(80, None)), sg.FolderBrowse()],

    # Logs path
    [sg.Text("Dossier contenant les logs :")],
    [sg.Input(key="LOGS_PATH", default_text=os.getenv("LOGS_PATH"), size=(80, None)), sg.FolderBrowse()],

    # Koha URL
    [
        sg.Text("Koha URL :"),
        sg.Input(key="KOHA_URL", default_text=os.getenv("KOHA_URL"), size=(60, None))
    ],

    # Koha PPN + ILN + RCR
    [
        sg.Text("Koha champ PPN :"),
        sg.Input(key="KOHA_PPN_FIELD", default_text=os.getenv("KOHA_PPN_FIELD"), size=(3, None)),
        sg.Text("Koha sous-champ PPN :"),
        sg.Input(key="KOHA_PPN_SUBFIELD", default_text=os.getenv("KOHA_PPN_SUBFIELD"), size=(1, None)),
        sg.Text("ILN :"),
        sg.Input(key="ILN", default_text=os.getenv("ILN"), size=(3, None)),
        sg.Text("RCR :"),
        sg.Input(key="RCR", default_text=os.getenv("RCR"), size=(9, None))
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
dotenv.set_key(DOTENV_FILE, "SERVICE", val["SERVICE"])
dotenv.set_key(DOTENV_FILE, "FILE_PATH", val["FILE_PATH"])
dotenv.set_key(DOTENV_FILE, "KOHA_REPORT_NB", val["KOHA_REPORT_NB"])
dotenv.set_key(DOTENV_FILE, "KOHA_USERID", val["KOHA_USERID"])
dotenv.set_key(DOTENV_FILE, "KOHA_PASSWORD", val["KOHA_PASSWORD"])
dotenv.set_key(DOTENV_FILE, "OUTPUT_PATH", val["OUTPUT_PATH"])
dotenv.set_key(DOTENV_FILE, "LOGS_PATH", val["LOGS_PATH"])
dotenv.set_key(DOTENV_FILE, "KOHA_URL", val["KOHA_URL"])
dotenv.set_key(DOTENV_FILE, "KOHA_PPN_FIELD", val["KOHA_PPN_FIELD"])
dotenv.set_key(DOTENV_FILE, "KOHA_PPN_SUBFIELD", val["KOHA_PPN_SUBFIELD"])
dotenv.set_key(DOTENV_FILE, "ILN", val["ILN"])
dotenv.set_key(DOTENV_FILE, "RCR", val["RCR"])

print("Paramètres par défaut sauvegardés avec succès")

# # --------------- Closing the window ---------------
window.close()