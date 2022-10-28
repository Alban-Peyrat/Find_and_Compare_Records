# -*- coding: utf-8 -*- 

# External imports
import logging
from fuzzywuzzy import fuzz
import json

# Internal import
import os
import logs
import Abes_isbn2ppn
import AbesXml
import Koha_API_PublicBiblio
from analysis import * # pour éviter de devoir réécrire tous les appels de fonctions

# Load settings
with open('settings.json', encoding="utf-8") as f:
    settings = json.load(f)

# Get the original file
MY_PATH = settings["MY_PATH"]
file_in_name = input("Nom du fichier : ")
FILE_IN = MY_PATH + "\\" + file_in_name

# Leaves if the file doesn't exists
if not os.path.exists(FILE_IN):
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

FILE_OUT_RESULTS = MY_PATH + "\\resultats.txt"
FILE_OUT_JSON = MY_PATH + "\\resultats.json"
FILE_OUT_CSV = MY_PATH + "\\resultats.csv"

KOHA_URL = settings["KOHA_URL"]

CSV_EXPORT_COLS = settings["CSV_EXPORT_COLS"] # /!\ All the columns from the orignal doc will be appended at the end

#On initialise le logger
logs.init_logs(LOGS_PATH,SERVICE,'DEBUG') # rajouter la date et heure d'exécution
logger = logging.getLogger(SERVICE)
logger.info("Fichier en cours de traitement : " + FILE_IN)
logger.info("URL Koha : " + KOHA_URL)

def generate_line_for_csv(res):
    """Generates the line for the CSV export. Returns a string."""

    output = ""
    for col in CSV_EXPORT_COLS:
        if col["id"] in res:
            if col["list"]:
                # output += "|".join(res[col["id"]]) 
                output += "|".join(filter(None, res[col["id"]])) #filter None as a mini fix for Koha XML problem
            else:
                output += str(res[col["id"]])
        output += ";"
    for col in res["LINE_DIVIDED"]:
        output += str(col) + ";"
    return output[:-1]

# ------------------------------ MAIN FUNCTION ------------------------------
results = []
with open(FILE_IN, 'r', encoding="utf-8") as fh:
    logger.info("--------------- Début du traitement du fichier ---------------")
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
        result["INPUT_KOHA_BIB_NB"] = result["LINE_DIVIDED"][len(result["LINE_DIVIDED"])-1].rstrip()
        logger.info("-----> Traitement de la ligne : ISBN = \"{}\", Koha Bib Nb = \"{}\"".format(result["INPUT_ISBN"],result["INPUT_KOHA_BIB_NB"]))

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
            logger.error("{} :: {} :: {}".format(result["ISBN2PPN_ISBN"], SERVICE, "Trop de PPN renvoyés : " + str(result['ISBN2PPN_NB_RES'])))
            logger.info("-> Fin du traitement de la ligne : ISBN = {}, Koha Bib Nb = {}".format(result["INPUT_ISBN"],result["INPUT_KOHA_BIB_NB"]))
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

        logger.info("-> Fin du traitement de la ligne : ISBN = {}, Koha Bib Nb = {}".format(result["INPUT_ISBN"],result["INPUT_KOHA_BIB_NB"]))
        results.append(result)

logger.info("--------------- Fin du traitement du fichier ---------------")

# ------------------------------ RESULT ANALYSIS ------------------------------
logger.info("--------------- Début de l'analyse des résultats ---------------")
logger.info("Analyse choisie : " + CHOSEN_ANALYSIS["name"])

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

# --------------- ANALYSIS PROCESS ---------------
# vérif avec ça : https://www.analyticsvidhya.com/blog/2021/07/fuzzy-string-matching-a-hands-on-guide/

# --------------- LOOP START ---------------
for res in results:
    # --------------- STATS ---------------
    results_report["TRAITES"] += 1
    # was a success ?
    if res["ERROR"]:
        if "Abes_isbn2ppn" in res["ERROR_MSG"]:
            if "trop de" in res["ERROR_MSG"]:
                results_report["SUCCES_ISBN2PPN"] += 1
                results_report["TROP_PPN"] += 1
            else:
                results_report["ECHEC_ISBN2PPN"] += 1

        if "Koha_API_PublicBiblio" in res["ERROR_MSG"]:
            results_report["SUCCES_ISBN2PPN"] += 1
            results_report["ECHEC_KOHA"] += 1
        elif "AbesXml" in res["ERROR_MSG"]:
            results_report["SUCCES_ISBN2PPN"] += 1
            results_report["ECHEC_SUDOC"] += 1
        
        continue #if error, leaves

    # It was a success
    results_report["SUCCES_ISBN2PPN"] += 1
    results_report["SUCCES_GLOBAL"] += 1

    # --------------- ANALYSIS ---------------
    for check in results_list:
        res[check+"_OK"] = analysis_checks(CHOSEN_ANALYSIS, check, res)

    # Global validation
    # "" if 0 checks are asked, OK if all checks are OK, else, nb of OK 
    if len(results_list) == 0:
        res["FINAL_OK"] = ""
    else:
        sum_of_results = 0
        for check in results_list:
            if res[check + "_OK"] == True:
                sum_of_results += 1
        if sum_of_results == len(results_list):
            res["FINAL_OK"] = "OK"
        else:
            res["FINAL_OK"] = sum_of_results

    # Adds "" to skipped checks
    for check in all_checks:
        if not check + "_OK" in res:
            res[check + "_OK"] = ""

    # --------------- WRITING OUTPUT LINES ---------------
    logger.debug("{} :: {} :: {}".format(res["ISBN2PPN_ISBN"], SERVICE,
        "Résultat : {} (titres : {}, éditeurs : {}, dates : {})".format(str(res["FINAL_OK"]), str(res["TITLE_OK"]), str(res["PUB_OK"]), str(res["DATE_OK"]))))
    

# ------------------------------ FINAL OUTPUT ------------------------------
logger.info("--------------- Résultats ---------------")

# --------------- JSON FILE ---------------
with open(FILE_OUT_JSON, 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)
logger.info("Fichier contenant les données en JSON : " + FILE_OUT_JSON)

# --------------- CSV FILE ---------------
with open(FILE_OUT_CSV, 'w', encoding='utf-8') as f_csv:
    logger.info("Fichier contenant les données en CSV : " + FILE_OUT_CSV)
    # /!\ remember to change the headers if the Koha export changes
    f_csv.write(";".join(col["name"] for col in CSV_EXPORT_COLS)+";isbn;915$a;$b;930$c;$e;$a;$j;$v;L035$a"+"\n")

    # --------------- LOOP START ---------------
    for res in results:
        f_csv.write(generate_line_for_csv(res))

# --------------- REPORT ---------------
with open(FILE_OUT_RESULTS, 'w', encoding='utf-8') as f:
    # Header
    f.write("Résultats de l'analyse\n")
    f.write("\n\n")

    # Files + URL + analysis parameters
    f.write("Fichier traité : " + FILE_IN + "\n")
    f.write("URL Koha : " + KOHA_URL + "\n")
    f.write("Analyse choisie : " + CHOSEN_ANALYSIS["name"] + "\n")
    f.write("Score minimum pour les titres : " + str(CHOSEN_ANALYSIS["TITLE_MIN_SCORE"]) + "\n")
    f.write("Nombre minimum de titres valides : " + str(CHOSEN_ANALYSIS["NB_TITLE_OK"]) + "\n")
    f.write("Score minimum pour les éditeurs : " + str(CHOSEN_ANALYSIS["PUBLISHER_MIN_SCORE"]) + "\n")
    f.write("Prise en compte des dates de publication : " + str(CHOSEN_ANALYSIS["USE_DATE"]) + "\n")
    f.write("Fichier contenant les données en JSON : " + FILE_OUT_JSON + "\n")
    f.write("Fichier contenant les données en CSV : " + FILE_OUT_CSV + "\n")
    f.write("\n\n")

    # Results
    f.write("Nombre de cas traités : " + str(results_report["TRAITES"]) + "\n")
    f.write("Nombre d'échecs sur isbn2ppn : " + str(results_report["ECHEC_ISBN2PPN"]) + "\n")
    f.write("Nombre multiples résultats sur isbn2ppn : " + str(results_report["TROP_PPN"]) + "\n")
    f.write("Nombre de correspondance unique sur isbn2ppn : " + str(results_report["SUCCES_ISBN2PPN"]-results_report["TROP_PPN"]) + "\n")
    f.write("Nombre d'échecs sur Koha : " + str(results_report["ECHEC_KOHA"]) + "\n")
    f.write("Nombre d'échecs sur Sudoc : " + str(results_report["ECHEC_SUDOC"]) + "\n")
    f.write("Nombre de cas traités avec succès : " + str(results_report["SUCCES_GLOBAL"]) + "\n")

logger.info("Fichier contenant le rapport : " + FILE_OUT_RESULTS)
logger.info("--------------- Exécution terminée avec succès ---------------")