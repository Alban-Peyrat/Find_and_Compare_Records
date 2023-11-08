# -*- coding: utf-8 -*-

# External import
from enum import Enum

class GUI_Text(Enum):
    # Names and window titles
    MAIN_SCREEN_NAME = {
        "eng": "FCR : execute Find and Compare Records",
        "fre": "FCR : lancer Find and Compare Records"
    }
    MAIN_SCREEN_WINDOW_TITLE = {
        "eng": "Chose the processing and the file configuration",
        "fre": "Choisir le traitement et la configuration des fichiers"
    }
    PROCESSING_CONFIGURATION_SCREEN_NAME = {
        "eng": "FCR : configure processing",
        "fre": "FCR : configurer le traitement"
    }
    PROCESSING_CONFIGURATION_WINDOW_TITLE = {
        "eng": "Processing configuration",
        "fre": "Configuration du traitement"
    }
    PROCESSING_CONFIGURATION_MAIN_TAB_TITLE = {
        "eng": "Processing main configuration",
        "fre": "Configuration principale du traitement"
    }
    PROCESSING_DATABASE_CONFIGURATION_TAB_TITLE = {
        "eng": "Database MARC fields configuration",
        "fre": "Configuration des champs MARC BDD"
    }
    PROCESSING_CHOSE_DATABASE_MAPPINGS_TAB_TITLE = {
        "eng": "Chose database mappings",
        "fre": "Choisir les mappings de BDD"
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
    SAVE_EXECUTION_PARAMETERS = {
        "eng": "Save these execution settings",
        "fre": "Sauvegarder ces paramètres d'exécution" 
    }
    GO_TO_PROCESSING_CONFIGURATION = {
        "eng": "Next (processing configuration)",
        "fre": "Suivant (configuration du traitement)"
    }
    ORIGIGN_DATABASE_URL = {
        "eng": "Origin database URL",
        "fre": "URL de la base de données d'origine"
    }
    SAVE_MAIN_PROCESSING_CONFIGURATION_PARAMETERS = {
        "eng": "Save main processing configuration settings",
        "fre": "Sauvegarder les paramètres principaux de ce traitement" 
    }
    TARGET_DATABASE_URL = {
        "eng": "Target database URL",
        "fre": "URL de la base de données de destination"
    }
    ILN_TEXT = {
        "eng":"ILN",
        "fre":"ILN"
    }
    RCR_TEXT = {
        "eng":"RCR",
        "fre":"RCR"
    }
    DATABASE_MARC_TEXT = {
        "eng": "Select mapping",
        "fre": "Sélectionner le mapping"
    }
    MARC_DATA_TO_CONFIGURE = {
        "eng": "Data to configure",
        "fre": "Configurer la donnée"
    }
    MARC_DATA_FIELDS_TEXT = {
        "eng": "Field",
        "fre": "Champ"
    }
    MARC_DATA_NEW_FIELD_TEXT = {
        "eng": "Add new field",
        "fre": "Ajouter un nouveau champ"
    }
    MARC_DATA_SINGLE_LINE_CODED_DATA_TEXT = {
        "eng": "Is single line coded data",
        "fre": "Est une donnée codé en une ligne"
    }
    YES = {
        "eng": "Yes",
        "fre": "Oui"
    }
    MARC_DATA_FILTERING_SUBFIELD_TEXT = {
        "eng": "Filtering subfield",
        "fre": "Sous-champ filtre"
    }
    MARC_DATA_SUBFIELDS_TEXT = {
        "eng": 'Subfields to export (separated by ",")',
        "fre": 'Sous-champs à exporter (séparés par ",")'
    }
    MARC_DATA_POSITIONS_TEXT = {
        "eng": 'Positions to export (separated by ",")',
        "fre": 'Positions à exporter (séparées par ",")'
    }
    MARC_DATA_ADD_FIELD_TEXT = {
        "eng": "Field",
        "fre": "Champ"
    }
    SAVE_THIS_MARC_FIELD = {
        "eng": "Save this MARC field",
        "fre": "Sauvegarder ce champ MARC" 
    }
    CHOSE_ORIGIN_DATABASE_TEXT = {
        "eng": "Origin database mapping",
        "fre": "Mapping de la BDD d'origine"
    }
    CHOSE_TARGET_DATABASE_TEXT = {
        "eng": "Target database mapping",
        "fre": "Mapping de la BDD de destination"
    }
    SAVE_CHOSEN_DATABASE_MAPPINGS = {
        "eng": "Save chosen database mappings",
        "fre": "Sauvegarder les mappings de BDD choisis" 
    }