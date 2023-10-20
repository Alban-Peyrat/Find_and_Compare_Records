# -*- coding: utf-8 -*-

# External import
from enum import Enum

class Main_GUI(Enum):
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
