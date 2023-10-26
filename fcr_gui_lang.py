# -*- coding: utf-8 -*-

# External import
from enum import Enum

class GUI_Text(Enum):
    MAIN_SCREEN_NAME = {
        "eng": "FCR : execute Find and Compare Records",
        "fre": "FCR : lancer Find and Compare Records"
    }
    # As this is to switch languages, english must be in french
    CHOSE_LANG = {
        "eng": "Passer en français",
        "fre": "Switch to english"
    }
    SERVICE_NAME = {
        "eng": "Service name (for logs)",
        "fre": "Nom du service (pour les logs)"
    }
    FILE_TO_ANALYZE = {
        "eng": "File to be analyzed",
        "fre": "Fichier à analyser"
    }
    OUTPUT_FOLDER = {
        "eng": "Output folder",
        "fre": "Dossier contenant les résultats"
    }
    LOG_FOLDER = {
        "eng": "Log folder",
        "fre": "Dossier contenant les logs"
    }
    START_ANALYSIS = {
        "eng": "Start analysis",
        "fre": "Lancer l'analyse"
    }
    GO_TO_MARC_FIELDS = {
        "eng": "Edit MARC fields mapping",
        "fre": "Modifier la configuration des champs MARC"
    }
    PROCESSING = {
        "eng": "Processing",
        "fre": "Traitement" 
    }
    SAVE_THOSE_PARAMETERS = {
        "eng": "Save those settings",
        "fre": "Sauvegarder ces paramètres" 
    }
