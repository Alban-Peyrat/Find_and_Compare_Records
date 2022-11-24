# -*- coding: utf-8 -*- 

# External imports
import os
import csv
import logging
from fuzzywuzzy import fuzz
import json

# Internal import
import logs
import Abes_isbn2ppn
import AbesXml
import Koha_API_PublicBiblio
from analysis import * # pour éviter de devoir réécrire tous les appels de fonctions
from outputing import * # pour éviter de devoir réécrire tous les appels de fonctions

# Load settings
with open('settings.json', encoding="utf-8") as f:
    settings = json.load(f)

# Get the original file
MY_PATH = settings["MY_PATH"]
print("Dossier contenant le fichier à traiter : " + MY_PATH)
file_in_name = input("Nom du fichier : ")
FILES = {}
FILES["IN"] = MY_PATH + "\\" + file_in_name

# Leaves if the file doesn't exists
if not os.path.exists(FILES["IN"]):
    print("Erreur : le fichier n'existe pas")
    exit()

# Get the analysis to perform
ANALYSIS = settings["ANALYSIS"] # Score = 0 to ignore
ANALYSIS_NB = input("\n".join("N°{} : {}".format(str(ii), obj["name"]) for ii, obj in enumerate(ANALYSIS))
                + "\n\nSaisir le numéro de l'analyse : ")

# Leaves if the analysis id is invalid
if ANALYSIS_NB.isnumeric():
    if int(ANALYSIS_NB) >= 0 and int(ANALYSIS_NB) < len(ANALYSIS):
        CHOSEN_ANALYSIS = ANALYSIS[int(ANALYSIS_NB)]
    else:
        print("Erreur : l'analyse choisie n'existe pas")
        exit()
else:
    print("Erreur : il faut indiquer le numéro de l'analyse. A été indiquer :\n" + str(ANALYSIS_NB))
    exit()

# At this point, everything is OK, loads and initialise all vars
SERVICE = settings["SERVICE"]

LOGS_PATH = settings["LOGS_PATH"]

FILES["OUT_RESULTS"] = MY_PATH + "\\resultats.txt"
FILES["OUT_JSON"] = MY_PATH + "\\resultats.json"
FILES["OUT_CSV"] = MY_PATH + "\\resultats.csv"

KOHA_URL = settings["KOHA_URL"]

ILN = settings["ILN"]

CSV_EXPORT_COLS = settings["CSV_EXPORT_COLS"] # /!\ All the columns from the orignal doc will be appended at the end
REPORT_SETTINGS = settings["REPORT_SETTINGS"]

# Setting-up the analysis process
all_checks = ["TITLE", "PUB", "DATE"]
results_list = []
if CHOSEN_ANALYSIS["TITLE_MIN_SCORE"] > 0:
    results_list.append("TITLE")
if CHOSEN_ANALYSIS["PUBLISHER_MIN_SCORE"] > 0:
    results_list.append("PUB")
if CHOSEN_ANALYSIS["USE_DATE"]:
    results_list.append("DATE")

# Init report dic
results_report = {}
results_report["TRAITES"] = 0
results_report["ECHEC_ISBN2PPN"] = 0
results_report["TROP_PPN"] = 0
results_report["SUCCES_ISBN2PPN"] = 0
results_report["ECHEC_KOHA"] = 0
results_report["ECHEC_SUDOC"] = 0
results_report["SUCCES_GLOBAL"] = 0

#On initialise le logger
logs.init_logs(LOGS_PATH,SERVICE,'DEBUG') # rajouter la date et heure d'exécution
logger = logging.getLogger(SERVICE)
logger.info("Fichier en cours de traitement : " + FILES["IN"])
logger.info("URL Koha : " + KOHA_URL)
logger.info("Analyse choisie : " + CHOSEN_ANALYSIS["name"])

# ------------------------------ MAIN FUNCTION ------------------------------
results = []
with open(FILES["IN"], 'r', newline="", encoding="utf-8") as fh:
    logger.info("--------------- Début du traitement du fichier ---------------")
    # for line in fh.readlines():
    csvdata = csv.DictReader(fh, delimiter=";")
    CSV_ORIGINAL_COLS = csvdata.fieldnames
    for line in csvdata:
        # Declaration & set-up of result {dict}
        result = {}
        result['ERROR'] = False
        result['ERROR_MSG'] = ''
        results_report["TRAITES"] += 1 # report stats

        # Retrieve ISBN + KohaBibNb
        # 0 = ISBN, 1 = 915$a, 2 = 915$b, 3 = 930$c, 4 = 930$e,
        # 5 = 930$a, 6 = 930$j, 7 = 930$v, 8 = L035$a
        result.update(line)
        #pour éviter des problèmes de changement de nom de la clef, on conserve l'utilisation du index 1 et last index )
        result["INPUT_ISBN"] = line[CSV_ORIGINAL_COLS[0]]
        result["INPUT_KOHA_BIB_NB"] = line[CSV_ORIGINAL_COLS[len(line)-1]].rstrip()
        logger.info("Traitement de la ligne : ISBN = \"{}\", Koha Bib Nb = \"{}\"".format(result["INPUT_ISBN"],result["INPUT_KOHA_BIB_NB"]))

        # --------------- ISBN2PPN ---------------
        # Get isbn2ppn results
        isbn2ppn_record = Abes_isbn2ppn.Abes_isbn2ppn(result["INPUT_ISBN"],service=SERVICE)
        if isbn2ppn_record.status == 'Error':
            result['ERROR'] = True
            result['ERROR_MSG'] = "Abes_isbn2ppn : " + isbn2ppn_record.error_msg
            results_report["ECHEC_ISBN2PPN"] += 1 # report stats
            log_fin_traitement(logger, result, False)
            results.append(result)
            continue # skip to next line
        
        # isbn2ppn was a success
        results_report["SUCCES_ISBN2PPN"] += 1 # report stats
        result["ISBN2PPN_ISBN"] = isbn2ppn_record.get_isbn_no_sep()
        result["ISBN2PPN_NB_RES"] = isbn2ppn_record.get_nb_results()[0] # We take every result
        result["ISBN2PPN_RES"] = isbn2ppn_record.get_results(merge=True)
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Résultat isbn2ppn : " + " || ".join(result["ISBN2PPN_RES"])))

        # More than 1 match
        if result["ISBN2PPN_NB_RES"] != 1:
            result["ERROR"] = True
            result['ERROR_MSG'] = "Abes_isbn2ppn : trop de résultats"
            logger.error("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Trop de PPN renvoyés : " + str(result['ISBN2PPN_NB_RES'])))
            results_report["TROP_PPN"] += 1 # report stats
            log_fin_traitement(logger, result, False)
            results.append(result)
            continue # skip to next line

        # Only 1 match : gets the PPN
        result["PPN"] = result["ISBN2PPN_RES"][0]

        # --------------- KOHA ---------------
        # Get Koha record
        koha_record = Koha_API_PublicBiblio.Koha_API_PublicBiblio(result["INPUT_KOHA_BIB_NB"], KOHA_URL, service=SERVICE, format="application/marc-in-json")
        # || marc-in-json parce que parfois le XML me renvoie pas de l'UTF-8 et renvoie pas de 214$c
        # || TICKET A FAIRE, exemple : 226701, voir les fichiers Probleme_API.txt et idem+_comprtement_normal
        # j'ai rajouté un filter(None) au moment de l'export CSV mais ça pose problème quand même...
        if koha_record.status == 'Error' :
            result['ERROR'] = True
            result['ERROR_MSG'] = "Koha_API_PublicBiblio : " + koha_record.error_msg
            results_report["ECHEC_KOHA"] += 1 # report stats
            log_fin_traitement(logger, result, False)
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
        if sudoc_record.status == 'Error':
            result['ERROR'] = True
            result['ERROR_MSG'] = sudoc_record.error_msg
            results_report["ECHEC_SUDOC"] += 1 # report stats
            log_fin_traitement(logger, result, False)
            results.append(result)
            continue # skip to next line

        # Successfully got Sudoc record
        results_report["SUCCES_GLOBAL"] += 1 # report stats
        result['SUDOC_Leader'] = sudoc_record.get_leader()
        result['SUDOC_100a'],result['SUDOC_DATE_TYPE'],result['SUDOC_DATE_1'],result['SUDOC_DATE_2'] = sudoc_record.get_dates_pub()
        result['SUDOC_214210c'] = sudoc_record.get_editeurs()
        result['SUDOC_200adehiv'] = nettoie_titre(sudoc_record.get_title_info())
        result["SUDOC_LOCAL_SYSTEM_NB"] = sudoc_record.get_local_system_nb(ILN)
        result["SUDOC_NB_LOCAL_SYSTEM_NB"] = len(result["SUDOC_LOCAL_SYSTEM_NB"])
        if result["SUDOC_NB_LOCAL_SYSTEM_NB"] > 0:
            result["SUDOC_DIFFERENT_LOCAL_SYSTEM_NB"] = not koha_record.bibnb in result["SUDOC_LOCAL_SYSTEM_NB"]
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "PPN : " + result['PPN']))
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Sudoc titre nettoyé : " + result['SUDOC_200adehiv']))

        # --------------- MATCHING PROCESS ---------------
        # Titles
        result['MATCHING_TITRE_SIMILARITE'] = fuzz.ratio(result['SUDOC_200adehiv'].lower(),result['KOHA_200adehiv'].lower())
        result['MATCHING_TITRE_APPARTENANCE'] = fuzz.partial_ratio(result['SUDOC_200adehiv'].lower(),result['KOHA_200adehiv'].lower())
        result['MATCHING_TITRE_INVERSION'] = fuzz.token_sort_ratio(result['SUDOC_200adehiv'],result['KOHA_200adehiv'])
        result['MATCHING_TITRE_INVERSION_APPARTENANCE'] = fuzz.token_set_ratio(result['SUDOC_200adehiv'],result['KOHA_200adehiv'])
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
            result['MATCHING_EDITEUR_SIMILARITE'],result['SUDOC_CHOSEN_ED'],result['KOHA_CHOSEN_ED'] = teste_editeur(result['SUDOC_214210c'], result['KOHA_214210c'])
            logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Scores des éditeurs : " + str(result['MATCHING_EDITEUR_SIMILARITE'])))
        else: # Mandatory to prevent an error at the end
            result['MATCHING_EDITEUR_SIMILARITE'],result['SUDOC_CHOSEN_ED'],result['KOHA_CHOSEN_ED'] = -1, "", ""

        # --------------- ANALYSIS PROCESS ---------------
        # Global validation
        # "" if 0 checks are asked, OK if all checks are OK, else, nb of OK
        if len(results_list) == 0:
            result["FINAL_OK"] = ""
        else:
            sum_of_results = 0
            for check in results_list:
                result[check+"_OK"] = analysis_checks(CHOSEN_ANALYSIS, check, result)
                if result[check + "_OK"] == True:
                    sum_of_results += 1
            if sum_of_results == len(results_list):
                result["FINAL_OK"] = "OK"
            else:
                result["FINAL_OK"] = sum_of_results

        # Adds "" to skipped checks
        for check in all_checks:
            if not check + "_OK" in result:
                result[check + "_OK"] = ""

        # --------------- END OF THIS LINE ---------------
        logger.debug("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE,
            "Résultat : {} (titres : {}, éditeurs : {}, dates : {})".format(str(result["FINAL_OK"]), str(result["TITLE_OK"]), str(result["PUB_OK"]), str(result["DATE_OK"]))))
        log_fin_traitement(logger, result, True)
        results.append(result)

# --------------- END OF MAIN FUNCTION ---------------
logger.info("--------------- Fin du traitement du fichier ---------------")

# ------------------------------ FINAL OUTPUT ------------------------------
# --------------- JSON FILE ---------------
with open(FILES["OUT_JSON"], 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)
logger.info("Fichier contenant les données en JSON : " + FILES["OUT_JSON"])

# --------------- CSV FILE ---------------
# Defines headers
fieldnames_id, fieldnames_names = [], []
for col in CSV_EXPORT_COLS:
    fieldnames_id.append(col["id"])
    fieldnames_names.append(col["name"])
fieldnames_id += CSV_ORIGINAL_COLS
fieldnames_names += CSV_ORIGINAL_COLS
# Generates the file
generate_csv_output(FILES["OUT_CSV"], results, fieldnames_id, fieldnames_names=fieldnames_names)
logger.info("Fichier contenant les données en CSV : " + FILES["OUT_CSV"])

# --------------- REPORT ---------------
generate_report(REPORT_SETTINGS, FILES, KOHA_URL, ILN, CHOSEN_ANALYSIS, results_report)
logger.info("Fichier contenant le rapport : " + FILES["OUT_RESULTS"])
logger.info("--------------- Rapport ---------------")
generate_report(REPORT_SETTINGS, FILES, KOHA_URL, CHOSEN_ANALYSIS, results_report, logger=logger)

logger.info("--------------- Exécution terminée avec succès ---------------")