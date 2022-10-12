# -*- coding: utf-8 -*- 

# External imports
import os
import logging
import re
from unidecode import unidecode
from fuzzywuzzy import fuzz
import json

# Internal import
import logs
import Abes_isbn2ppn
import AbesXml
import Koha_API_PublicBiblio

# Var init
SERVICE = "Compare_Koha_Sudoc_records"
MY_PATH = os.getenv("MY_PATH")
file_in_name = input("Nom du fichier : ")
FILE_IN = MY_PATH + "\\" + file_in_name
FILE_OUT_RESULTS = MY_PATH + "\\resultats.txt"
FILE_OUT_JSON = MY_PATH + "\\resultats.json"
FILE_OUT_CSV = MY_PATH + "\\resultats.csv"
FILE_OUT_ITEM = MY_PATH + "\\FICHIER_POUR_ITEM.txt"
LIST_ERROR_ADM = []
KOHA_URL = os.getenv("KOHA_URL")

#On initialise le logger
logs.init_logs(os.getenv('LOGS_PATH'),SERVICE,'DEBUG') # rajouter la date et heure d'exécution
logger = logging.getLogger(SERVICE)
logger.debug("Fichier en cours de traitement : " + FILE_IN)
logger.debug("URL Koha : " + KOHA_URL)


def prepString(_str, _noise = True, _multiplespaces = True):
    """Returns a string without punctuation and/or multispaces stripped and in lower case.

    Takes as arguments :
        - _str : the string to edit
        - _noise [optional] {bool} : remove punctuation ?
        - _multispaces [optional] {bool} : remove multispaces ?
    """
    # remove noise (punctuation) if asked (by default yes)
    if _noise:
        noise_list = [".", ",", "?", "!", ";","/",":","="]
        for car in noise_list:
            _str = _str.replace(car, " ")
    # replace multiple spaces by ine in string if requested (default yes)
    if _multiplespaces:
        _str = re.sub("\s+", " ", _str).strip()
    return _str.strip().lower()

def nettoie_titre(titre) :
    """Supprime les espaces, la ponctuation et les diacritiques transforme "&" en "et"

    Args:
        titre (string): une chaîne de caractères
    """
    if titre is not None :
        titre_norm = prepString(titre)
        titre_norm = titre_norm.replace('&', 'et')
        titre_norm = titre_norm.replace('œ', 'oe')
        # out = re.sub(r'[^\w]','',unidecode(titre_norm))
        out = unidecode(titre_norm)
        return out.lower()
    else :
        return titre

def teste_date_pub(date_pub_sudoc, date_pub_koha):
    """Checks if one of Sudoc publication date matches on of Koha's and returns True if it's the case.

    Args:
        date_pub_sudoc (tuple of strings): 1st and 2nd publication date in the Sudoc record
        date_pub_koha (tuple of strings): 1st and 2nd publication date in the Koha record
    """
    # si Type de date de pub = reproduction on confronte la date de pub Alma à al date de pub. originale et à la date de reproduction
    # ↑ AlP : j'ai un doute sur ce commentaire du code original

    for date in date_pub_sudoc :
        if date in date_pub_koha:
            return True
    return False

# --- Designé pour Alma ---
# AlP : pas adapté à Koha parce que supposément les documents ont pas de PPN dans Koha
# def teste_ppn(ppn_sudoc,ppn_alma):
    
#     if ppn_sudoc == ppn_alma[5:]:
#         return True
#     else : 
#         return False

# --- Designé pour Alma ---
# AlP : Je gère ça directement dans les conencteurs API
# def zones_multiples(code_champ,code_sous_champ,record):
#     liste_valeurs = []
#     for champ in record.get_fields(code_champ):
#         liste_valeurs.append(champ[code_sous_champ])
#     return liste_valeurs

# --- Designé pour Alma ---
# AlP : pas adapté à Koha parce que supposément les documents ont pas de PPN dans Koha
# def get_ppn(record):
#     ppn_list = []
#     champs_035 = zones_multiples('035','a',record)
#     logger.debug(champs_035)
#     for sys_number in champs_035 :
#         if sys_number is not None :
#             if sys_number.startswith('(PPN)') :
#                 ppn_list.append(sys_number[5:14])
#     return ppn_list

def teste_editeur(list_ed_sudoc, list_ed_koha):
    """Confront every Sudoc publishers with every Koha publishers and returns the pair with the higher matching ratio as a tuple :
            - score
            - chosen Sudoc publisher
            - chosen Koha publisher

    Args:
        list_ed_sudoc (list of strings): all 210/4$c of the Sudoc record
        list_ed_koha (list of strings): all 210/4$c of the Koha record
    """
    score = 0
    return_ed_sudoc = ""
    return_ed_koha = ""
    for ed_sudoc in list_ed_sudoc :
        for ed_koha in list_ed_koha :
            ratio_de_similarite = fuzz.ratio(nettoie_titre(ed_koha),nettoie_titre(ed_sudoc))
            if ratio_de_similarite > score :
                score = ratio_de_similarite
                return_ed_sudoc = ed_sudoc
                return_ed_koha = ed_koha
    return score, return_ed_sudoc, return_ed_koha

# ------------------------------ MAIN FUNCTION ------------------------------
results = []
with open(FILE_IN, 'r', encoding="utf-8") as fh:
    logger.debug("--------------- Début du traitement du fichier ---------------")
    for line in fh.readlines():
        # Declaration & set-up of result {dict}
        result = {}
        result['ERROR'] = False
        result['ERROR_MSG'] = ''

        # Retrieve ISBN + KohaBibNb
        # 0 = ISBN, 1 = 915$a, 2 = 915$b, 3 = 930$c, 4 = 930$e,
        # 5 = 930$a, 6 = 930$j, 7 = 930$v, 8 = L035$a
        result["LINE_DIVIDED"] = line.split(";")
        result["INPUT_ISBN"] = result["LINE_DIVIDED"][0]
        result["INPUT_KOHA_BIB_NB"] = result["LINE_DIVIDED"][8].rstrip()
        logger.debug("-----> Traitement de la ligne : ISBN = \"{}\", Koha Bib Nb = \"{}\"".format(result["INPUT_ISBN"],result["INPUT_KOHA_BIB_NB"]))

        # --------------- ISBN2PPN ---------------
        # Get isbn2ppn results
        isbn2ppn_record = Abes_isbn2ppn.Abes_isbn2ppn(result["INPUT_ISBN"],service=SERVICE)
        if isbn2ppn_record.status == 'Error' :
                result['ERROR'] = True
                result['ERROR_MSG'] = "Abes_isbn2ppn : " + isbn2ppn_record.error_msg
                results.append(result)
                continue # skip to next line
        
        # isbn2ppn was a success
        result["ISBN2PPN_ISBN"] = isbn2ppn_record.get_isbn_no_sep()
        result["ISBN2PPN_NB_RES"] = isbn2ppn_record.get_nb_results()[0] # We take every result
        result["ISBN2PPN_RES"] = isbn2ppn_record.get_results(merge=True)
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Résultat isbn2ppn : " + " || ".join(result["ISBN2PPN_RES"])))

        # More than 1 match
        if result["ISBN2PPN_NB_RES"] != 1:
            result["ERROR"] = True
            result['ERROR_MSG'] = "Abes_isbn2ppn : trop de résultats"
            logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Trop de PPN renvoyés : " + str(result['ISBN2PPN_NB_RES'])))
            logger.debug("-> Fin du traitement de la ligne : ISBN = {}, Koha Bib Nb = {}".format(result["INPUT_ISBN"],result["INPUT_KOHA_BIB_NB"]))
            results.append(result)
            continue # skip to next line

        # Only 1 match : gets the PPN
        result["PPN"] = result["ISBN2PPN_RES"][0]

        # --------------- KOHA ---------------
        # Get Koha record
        koha_record = Koha_API_PublicBiblio.Koha_API_PublicBiblio(result["INPUT_KOHA_BIB_NB"], KOHA_URL, service=SERVICE)
        if koha_record.status == 'Error' :
                result['ERROR'] = True
                result['ERROR_MSG'] = "Koha_API_PublicBiblio : " + koha_record.error_msg
                results.append(result)
                continue # skip to next line
        
        # Successfully got Koha record
        result['KOHA_BIB_NB'] = koha_record.bibnb
        result['KOHA_Leader'] = koha_record.get_leader()
        result['KOHA_100a'], result['KOHA_DATE_TYPE'],result['KOHA_DATE_1'],result['KOHA_DATE_2'] = koha_record.get_dates_pub()
        result['KOHA_214210c'] = koha_record.get_editeurs()
        result['KOHA_200adehiv'] = nettoie_titre(koha_record.get_title_info())
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Koha biblionumber : " + result['KOHA_BIB_NB']))
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Koha titre nettoyé : " + result['KOHA_200adehiv']))

        # --------------- SUDOC ---------------
        # Get Sudoc record
        sudoc_record = AbesXml.AbesXml(result["PPN"],service=SERVICE)
        if sudoc_record.status == 'Error' :
            result['ERROR'] = True
            result['ERROR_MSG'] = sudoc_record.error_msg
            results.append(result)
            continue # skip to next line

        # Successfully got Sudoc record
        result['SUDOC_Leader'] = sudoc_record.get_leader()
        result['SUDOC_100a'],result['SUDOC_DATE_TYPE'],result['SUDOC_DATE_1'],result['SUDOC_DATE_2'] = sudoc_record.get_dates_pub()
        result['SUDOC_214210c'] = sudoc_record.get_editeurs()
        result['SUDOC_200adehiv'] = nettoie_titre(sudoc_record.get_title_info())
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "PPN : " + result['PPN']))
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Sudoc titre nettoyé : " + result['KOHA_200adehiv']))

        # --------------- MATCHING PROCESS ---------------
        # Titles
        result['MATCHING_TITRE_SIMILARITE'] = fuzz.ratio(result['SUDOC_200adehiv'].lower(),result['KOHA_200adehiv'].lower())
        result['MATCHING_TITRE_APPARTENANCE'] = fuzz.partial_ratio(result['SUDOC_200adehiv'].lower(),result['KOHA_200adehiv'].lower())
        result['MATCHING_TITRE_INVERSION'] = fuzz.token_sort_ratio(result['SUDOC_200adehiv'],result['KOHA_200adehiv'])
        result['MATCHING_TITRE_INVERSION_APPARTENANCE'] = fuzz.token_set_ratio(result['SUDOC_200adehiv'],result['KOHA_200adehiv'])
        # ||| Corriger les énoncés
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Score des titres : "
                                     + "Similarité : " + str(result['MATCHING_TITRE_SIMILARITE'])
                                     + " || Appartenance : " + str(result['MATCHING_TITRE_APPARTENANCE'])
                                     + " || Inversion : " + str(result['MATCHING_TITRE_INVERSION'])
                                     + " || Inversion appartenance : " + str(result['MATCHING_TITRE_INVERSION_APPARTENANCE'])
                                     ))

        # Dates
        result['MATCHING_DATE_PUB'] = teste_date_pub((result['SUDOC_DATE_1'],result['SUDOC_DATE_2']),(result['KOHA_DATE_1'],result['KOHA_DATE_2']))
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Correspondance des dates : " + str(result['MATCHING_DATE_PUB'])))

        # Publishers
        if len(result['SUDOC_214210c']) > 0 and len(result['KOHA_214210c']) > 0 : 
            result['MATCHING_EDITEUR_SIMILARITE'],result['SUDOC_214210c'],result['KOHA_214210c'] = teste_editeur(result['SUDOC_214210c'], result['KOHA_214210c'])
            logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Scores des éditeurs : " + str(result['MATCHING_EDITEUR_SIMILARITE'])))

            # AlP : ignoré parce que on fait du physique sur physique, je pense pas que ce soit utile
#             # Si les dates ne matche pas on va voir si la notice possède un lien vers la version physique pour aller tester cette date
#             if not result['MATCHING_DATE_PUB'] :
#                 result['MATCHING_DATE_PUB_PRINT'] = False
#                 result['SUDOC_452'] = sudoc_record.get_ppn_autre_support()
#                 logger.debug("452 : {}".format(result["SUDOC_452"]))
#                 for ppn_print in result['SUDOC_452'] :
#                     if not result['MATCHING_DATE_PUB_PRINT'] :
#                         sudoc_record_print = AbesXml.AbesXml(ppn_print,service=SERVICE)
#                         result['SUDOC_100a_PRINT'],result['SUDOC_DATE_TYPE_PRINT'],result['SUDOC_DATE_1_PRINT'],result['SUDOC_DATE_2_PRINT'] = sudoc_record_print.get_dates_pub()
#                         result['MATCHING_DATE_PUB_PRINT'] = teste_date_pub((result['SUDOC_DATE_1_PRINT'],result['SUDOC_DATE_2_PRINT']),(result['CZ_DATE_1'],result['CZ_DATE_2']))

        logger.debug("-> Fin du traitement de la ligne : ISBN = {}, Koha Bib Nb = {}".format(result["INPUT_ISBN"],result["INPUT_KOHA_BIB_NB"]))
        results.append(result)

logger.debug("--------------- Fin du traitement du fichier ---------------")

# ------------------------------ RESULT ANALYSIS ------------------------------
logger.debug("--------------- Début de l'analyse des résultats ---------------")

# Init report dic
results_report = {}
results_report["TRAITES"] = 0
results_report["ECHEC_ISBN2PPN"] = 0
results_report["TROP_PPN"] = 0
results_report["SUCCES_ISBN2PPN"] = 0
results_report["ECHEC_KOHA"] = 0
results_report["ECHEC_SUDOC"] = 0
results_report["SUCCES_GLOBAL"] = 0

# --------------- ANALYSIS PROCESS ---------------


# ------------------------------ OUTPUT ------------------------------
logger.debug("--------------- Résultats ---------------")

# --------------- JSON FILE ---------------
with open(FILE_OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)
logger.debug("Fichier contenant les données en JSON : " + FILE_OUT_JSON)

# --------------- CSV FILE ---------------
logger.debug("Fichier contenant les données en CSV : " + FILE_OUT_CSV)

# --------------- FILE FOR ITEM ---------------
logger.debug("Fichier pour ITEM : " + FILE_OUT_ITEM)

# --------------- REPORT ---------------
with open(FILE_OUT_RESULTS, 'w', encoding='utf-8') as f:
    # Header
    f.write("Résultats de l'analyse\n")
    f.write("\n\n")

    # Files + URL
    f.write("Fichier traité : " + FILE_IN + "\n")
    f.write("URL Koha : " + KOHA_URL + "\n")
    f.write("Fichier contenant les données en JSON : " + FILE_OUT_JSON + "\n")
    f.write("Fichier contenant les données en CSV : " + FILE_OUT_CSV + "\n")
    f.write("Fichier pour ITEM : " + FILE_OUT_ITEM + "\n")
    f.write("\n\n")

    # Results
    f.write("Nombre de cas traités : " + str(results_report["TRAITES"]) + "\n")
    f.write("Nombre d'échecs sur isbn2ppn : " + str(results_report["ECHEC_ISBN2PPN"]) + "\n")
    f.write("Nombre multiples résultats sur isbn2ppn : " + str(results_report["TROP_PPN"]) + "\n")
    f.write("Nombre de correspondance unique sur isbn2ppn : " + str(results_report["SUCCES_ISBN2PPN"]) + "\n")
    f.write("Nombre d'échecs sur Koha : " + str(results_report["ECHEC_KOHA"]) + "\n")
    f.write("Nombre d'échecs sur Sudoc : " + str(results_report["ECHEC_SUDOC"]) + "\n")
    f.write("Nombre de cas traités avec succès : " + str(results_report["SUCCES_GLOBAL"]) + "\n")
logger.debug("Fichier contenant le rapport : " + FILE_OUT_RESULTS)

logger.debug("--------------- Exécution terminée avec succès ---------------")
            

# Reste à voir :
#   analyse des résultats
#     - les fichiers de sortie
    # - lire ce que ça fait les trucs fuzzy qu'il a fait + corriger mes énoncés dans les logs si nécessaire
    # POURQUOI MON UTF 8 IL MARCHE PAS LA AUSSI
    # la doc

# Forme du fichier pour l'abes : https://documentation.abes.fr/aideitem/index.html#ConstituerFichierDonneesExemplariser