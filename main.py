# -*- coding: utf-8 -*- 

# External imports
import os
import csv
import logging
from fuzzywuzzy import fuzz
import json

# Internal import
import scripts.logs as logs
# import api.abes.Abes_isbn2ppn as Abes_isbn2ppn
import api.abes.AbesXml as AbesXml
import api.koha.Koha_API_PublicBiblio as Koha_API_PublicBiblio
from analysis import * # pour éviter de devoir réécrire tous les appels de fonctions
from scripts.outputing import * # pour éviter de devoir réécrire tous les appels de fonctions
import scripts.prep_data as prep_data
import fcr_classes as fcr

def main(es: fcr.Execution_Settings):
    """Main function.
    Takes as argument an Execution_Settings instance"""

    # Get the original file
    print("Fichier à traiter :", es.file_path)

    # Leaves if the file doesn't exists
    if not os.path.exists(es.file_path):
        print("Erreur : le fichier n'existe pas")
        exit()

    # At this point, everything is OK, loads and initialise all vars
    es.generate_files_path()

    # Setting-up the analysis process
    all_checks = ["TITLE", "PUB", "DATE"]
    results_list = []
    if es.chosen_analysis["TITLE_MIN_SCORE"] > 0:
        results_list.append("TITLE")
    if es.chosen_analysis["PUBLISHER_MIN_SCORE"] > 0:
        results_list.append("PUB")
    if es.chosen_analysis["USE_DATE"]:
        results_list.append("DATE")

    # ----------------- AR220 : a edit
    # Init report
    results_report = fcr.Report()
    # ----------------- Fin de AR220 : a edit

    #On initialise le logger
    logs.init_logs(es.logs_path, es.service,'DEBUG') # rajouter la date et heure d'exécution
    logger = logging.getLogger(es.service)
    logger.info("File : " + es.file_path)
    logger.info("Origin database URL : " + es.origin_url)
    logger.info("Chosen analysis : " + es.chosen_analysis["name"])

    # ------------------------------ MAIN FUNCTION ------------------------------
    results = []
    with open(es.file_path, 'r', newline="", encoding="utf-8") as fh:
        logger.info("--------------- File processing start ---------------")
        
        # Load original file data
        csvdata = csv.DictReader(fh, delimiter=";")
        CSV_ORIGINAL_COLS = csvdata.fieldnames

        # Create CSV output file
        # Defines headers
        fieldnames_id, fieldnames_names = [], []
        for col in es.csv_export_cols_json:
            fieldnames_id.append(col["id"])
            fieldnames_names.append(col["name"])
        fieldnames_id += CSV_ORIGINAL_COLS
        fieldnames_names += CSV_ORIGINAL_COLS
        # Generates the file header
        f_csv = open(es.file_path_out_csv, 'w', newline="", encoding='utf-8')
        csv_writer = csv.DictWriter(f_csv, extrasaction="ignore", fieldnames=fieldnames_id, delimiter=";")
        generate_csv_output_header(csv_writer, fieldnames_id, fieldnames_names=fieldnames_names)
        logger.info("CSV output file : " + es.file_path_out_csv)

        for line in csvdata:
            # Declaration & set-up of record
            rec = fcr.Original_Record(line)
            results_report.increase_processed() # report stats
            # Retrieve ISBN + KohaBibNb
            # 0 = ISBN, 1 = 915$a, 2 = 915$b, 3 = 930$c, 4 = 930$e,
            # 5 = 930$a, 6 = 930$j, 7 = 930$v, 8 = L035$a

            # Gets input query and original uid
            rec.extract_from_original_line(CSV_ORIGINAL_COLS)
            logger.info(f"Processing new line : ISBN = \"{rec.input_query}\", Koha Bib Nb = \"{rec.original_uid}\"")

            # ||| AR358 to del
            result = {}
            result['ERROR'] = False
            result['FAKE_ERROR'] = False
            result['ERROR_MSG'] = ''
            result.update(line)
            result["INPUT_QUERY"] = line[CSV_ORIGINAL_COLS[0]]
            result["INPUT_KOHA_BIB_NB"] = line[CSV_ORIGINAL_COLS[len(line)-1]].rstrip()
            # ||| End of AR358 to del


            # --------------- ORIGIN DATABASE ---------------
            # Get Koha record
            koha_record = Koha_API_PublicBiblio.Koha_API_PublicBiblio(result["INPUT_KOHA_BIB_NB"], es.origin_url, service=es.service, format="application/marcxml+xml")
            # j'ai rajouté un filter(None) au moment de l'export CSV mais ça pose problème quand même...
            if koha_record.status == 'Error' :
                result['ERROR'] = True
                result['ERROR_MSG'] = "Koha_API_PublicBiblio : " + koha_record.error_msg
                results_report.increase_fail(fcr.Errors.KOHA) # report stats
                go_next(logger, results, csv_writer, result, False)
                continue # skip to next line
            
            # Successfully got Koha record
            
            # AR362 : UDE
            rec.get_origin_database_data(es.processing, koha_record.record_parsed, fcr.Databases.KOHA_PUBLIC_BIBLIO, es)

            # |||| AR362 to del
            result['KOHA_BIB_NB'] = list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.ID])
            temp = rec.origin_database_data.data[fcr.FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]
            result['KOHA_DATE_1'] = temp[0][1]
            result['KOHA_DATE_2'] = temp[0][2]
            result['KOHA_214210c'] = rec.origin_database_data.data[fcr.FCR_Mapped_Fields.PUBLISHERS_NAME]
            result['KOHA_200adehiv'] = nettoie_titre(list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.TITLE][0]))
            result['KOHA_305'] = list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.EDITION_NOTES])
            result["KOHA_PPN"] = list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.PPN])
            result["KOHA_214210a_DATES"] = []
            for date_str in rec.origin_database_data.data[fcr.FCR_Mapped_Fields.PUBLICATION_DATES]:
                result["KOHA_214210a_DATES"] += prep_data.get_year(date_str)
            result["KOHA_214210a_DATES"] = list_as_string(result["KOHA_214210a_DATES"])
            result["KOHA_215a_DATES"] = []    
            for desc_str in rec.origin_database_data.data[fcr.FCR_Mapped_Fields.PHYSICAL_DESCRIPTION]: #AR259
                result["KOHA_215a_DATES"] += prep_data.get_year(desc_str)
            result["KOHA_215a_DATES"] = list_as_string(result["KOHA_215a_DATES"])
            result['KOHA_010z'] = list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.ERRONEOUS_ISBN])
            # old
            # result['KOHA_BIB_NB'] = koha_record.bibnb
            # result['KOHA_Leader'] = koha_record.get_leader()
            # result['KOHA_100a'], result['KOHA_DATE_TYPE'],result['KOHA_DATE_1'],result['KOHA_DATE_2'] = koha_record.get_dates_pub()
            # result['KOHA_214210c'] = koha_record.get_editeurs()
            # result['KOHA_200adehiv'] = nettoie_titre(koha_record.get_title_info())
            # result['KOHA_305'] = koha_record.get_note_edition()
            # result["KOHA_PPN"] = koha_record.get_ppn(es.source_ppn_field, es.source_ppn_subfield)
            # result["KOHA_214210a_DATES"] = []
            # for date_str in koha_record.get_dates_from_21X():
            #     result["KOHA_214210a_DATES"] += prep_data.get_year(date_str)
            # result["KOHA_215a_DATES"] = []    
            # for desc_str in koha_record.get_desc(): #AR259
            #     result["KOHA_215a_DATES"] += prep_data.get_year(desc_str)
            # result['KOHA_010z'] = koha_record.get_wrong_isbn()
            # |||| END OF AR362 to del
            logger.debug("{} :: {} :: {}".format(rec.input_query, es.service, "Koha biblionumber : " + result['KOHA_BIB_NB']))
            logger.debug("{} :: {} :: {}".format(rec.input_query, es.service, "Koha titre nettoyé : " + result['KOHA_200adehiv']))


            # --------------- Match records ---------------
            rec.get_matched_records_instance(fcr.Matched_Records(es.operation, rec.input_query, es))     

            # ||| AR358 to del |||
            result["MATCH_RECORDS_QUERY"] = rec.query_used
            result["MATCH_RECORDS_NB_RES"] = rec.nb_matched_records
            result["MATCH_RECORDS_RES"] = rec.matched_records_ids
            # result["MATCH_RECORDS_RES_RECORDS"] = rec.matched_records
            if result["MATCH_RECORDS_NB_RES"] > 1:
                result["ERROR"] = True
                result["FAKE_ERROR"] = True
                result['ERROR_MSG'] = "{} : trop de résultats".format(str(es.operation.name))
            if result["MATCH_RECORDS_NB_RES"] == 0:
                result["ERROR"] = True
                result["FAKE_ERROR"] = False
                result['ERROR_MSG'] = "{} : aucun résultat".format(str(es.operation.name))
            if result["MATCH_RECORDS_NB_RES"] == 1: # Only 1 match : gets the PPN
                result["MATCHED_ID"] = result["MATCH_RECORDS_RES"][0]
            # ||| End of AR358 to del
    
            # ||| needs to be redone with enhanced match records errors
            if result["ERROR"]:
                if result["FAKE_ERROR"]: # report stats
                    results_report.increase_fail(fcr.Errors.MATCH_RECORD_FAKE)
                    logger.error("{} :: {} :: {}".format(result["MATCH_RECORDS_QUERY"], es.service, "{} : {}".format(str(result["ERROR_MSG"]), str(result["MATCH_RECORDS_NB_RES"]))))
                else:
                    results_report.increase_fail(fcr.Errors.MATCH_RECORD_REAL)
                    logger.error("{} :: {} :: {}".format(result["INPUT_QUERY"], es.service, str(result["ERROR_MSG"])))
                
                # Skip to next line
                go_next(logger, results, csv_writer, result, False)
                continue
            
            # Match records was a success
            results_report.increase_success(fcr.Success.MATCH_RECORD) # report stats
            logger.debug("{} :: {} :: {}".format(result["MATCH_RECORDS_QUERY"], es.service, "Résultat {} : ".format(str(es.operation)) + " || ".join(str(result["MATCH_RECORDS_RES"]))))

            # --------------- SUDOC ---------------
            # Get Sudoc record
            sudoc_record = AbesXml.AbesXml(result["MATCHED_ID"],service=es.service)
            if sudoc_record.status == 'Error':
                result['ERROR'] = True
                result['ERROR_MSG'] = sudoc_record.error_msg
                results_report.increase_fail(fcr.Errors.SUDOC) # report stats
                go_next(logger, results, csv_writer, result, False)
                continue # skip to next line

            # Successfully got Sudoc record
            # AR362 : UDE
            rec.get_target_database_data(es.processing, sudoc_record.record_parsed, fcr.Databases.ABESXML, es)


            results_report.increase_success(fcr.Success.GLOBAL) # report stats


            # |||| AR362 to del
            temp = rec.target_database_data.data[fcr.FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]
            if len(temp) < 1:
                result['SUDOC_DATE_1'] = None    
                result['SUDOC_DATE_2'] = None
            else:
                result['SUDOC_DATE_1'] = temp[0][1]
                result['SUDOC_DATE_2'] = temp[0][2]
            result['SUDOC_214210c'] = rec.target_database_data.data[fcr.FCR_Mapped_Fields.PUBLISHERS_NAME]
            result['SUDOC_200adehiv'] = nettoie_titre(list_as_string(rec.target_database_data.data[fcr.FCR_Mapped_Fields.TITLE][0]))
            result['SUDOC_305'] = list_as_string(rec.target_database_data.data[fcr.FCR_Mapped_Fields.EDITION_NOTES])
            result["SUDOC_LOCAL_SYSTEM_NB"] = rec.target_database_data.data[fcr.FCR_Mapped_Fields.OTHER_DB_ID]
            # sudoc_record.get_local_system_nb(es.iln)
            result["SUDOC_NB_LOCAL_SYSTEM_NB"] = len(result["SUDOC_LOCAL_SYSTEM_NB"])
            result["SUDOC_LOCAL_SYSTEM_NB"] = list_as_string(result["SUDOC_LOCAL_SYSTEM_NB"])
            result["SUDOC_ITEMS"] = rec.target_database_data.data[fcr.FCR_Mapped_Fields.ITEMS]
            # sudoc_record.get_library_items(es.rcr)
            result["SUDOC_HAS_ITEMS"] = len(result["SUDOC_ITEMS"]) > 0
            if result["SUDOC_NB_LOCAL_SYSTEM_NB"] > 0:
                result["SUDOC_DIFFERENT_LOCAL_SYSTEM_NB"] = not koha_record.bibnb in result["SUDOC_LOCAL_SYSTEM_NB"]
            result["SUDOC_ITEMS"] = list_as_string(result["SUDOC_ITEMS"])
            result['SUDOC_010z'] = list_as_string(rec.target_database_data.data[fcr.FCR_Mapped_Fields.ERRONEOUS_ISBN])
            # old
            # result['SUDOC_Leader'] = sudoc_record.get_leader()
            # result['SUDOC_100a'],result['SUDOC_DATE_TYPE'],result['SUDOC_DATE_1'],result['SUDOC_DATE_2'] = sudoc_record.get_dates_pub()
            # result['SUDOC_214210c'] = sudoc_record.get_editeurs()
            # result['SUDOC_200adehiv'] = nettoie_titre(sudoc_record.get_title_info())
            # result['SUDOC_305'] = sudoc_record.get_note_edition()
            # result["SUDOC_LOCAL_SYSTEM_NB"] = sudoc_record.get_local_system_nb(es.iln)
            # result["SUDOC_NB_LOCAL_SYSTEM_NB"] = len(result["SUDOC_LOCAL_SYSTEM_NB"])
            # if result["SUDOC_NB_LOCAL_SYSTEM_NB"] > 0:
            #     result["SUDOC_DIFFERENT_LOCAL_SYSTEM_NB"] = not koha_record.bibnb in result["SUDOC_LOCAL_SYSTEM_NB"]
            # result["SUDOC_ITEMS"] = sudoc_record.get_library_items(es.rcr)
            # result["SUDOC_HAS_ITEMS"] = len(result["SUDOC_ITEMS"]) > 0
            # result['SUDOC_010z'] = sudoc_record.get_wrong_isbn()
            # |||| END OF AR362 to del
            logger.debug("{} :: {} :: {}".format(result["MATCH_RECORDS_QUERY"], es.service, "PPN : " + result["MATCHED_ID"]))
            logger.debug("{} :: {} :: {}".format(result["MATCH_RECORDS_QUERY"], es.service, "Sudoc titre nettoyé : " + result['SUDOC_200adehiv']))

            # --------------- MATCHING PROCESS ---------------
            # Titles
            result['MATCHING_TITRE_SIMILARITE'] = fuzz.ratio(result['SUDOC_200adehiv'].lower(),result['KOHA_200adehiv'].lower())
            result['MATCHING_TITRE_APPARTENANCE'] = fuzz.partial_ratio(result['SUDOC_200adehiv'].lower(),result['KOHA_200adehiv'].lower())
            result['MATCHING_TITRE_INVERSION'] = fuzz.token_sort_ratio(result['SUDOC_200adehiv'],result['KOHA_200adehiv'])
            result['MATCHING_TITRE_INVERSION_APPARTENANCE'] = fuzz.token_set_ratio(result['SUDOC_200adehiv'],result['KOHA_200adehiv'])
            logger.debug("{} :: {} :: {}".format(result["MATCH_RECORDS_QUERY"], es.service, "Score des titres : "
                                        + "Similarité : " + str(result['MATCHING_TITRE_SIMILARITE'])
                                        + " || Appartenance : " + str(result['MATCHING_TITRE_APPARTENANCE'])
                                        + " || Inversion : " + str(result['MATCHING_TITRE_INVERSION'])
                                        + " || Inversion appartenance : " + str(result['MATCHING_TITRE_INVERSION_APPARTENANCE'])
                                        ))

            # Dates
            result['MATCHING_DATE_PUB'] = teste_date_pub((result['SUDOC_DATE_1'],result['SUDOC_DATE_2']),(result['KOHA_DATE_1'],result['KOHA_DATE_2']))
            logger.debug("{} :: {} :: {}".format(result["MATCH_RECORDS_QUERY"], es.service, "Correspondance des dates : " + str(result['MATCHING_DATE_PUB'])))

            # Publishers
            if len(result['SUDOC_214210c']) > 0 and len(result['KOHA_214210c']) > 0 : 
                result['MATCHING_EDITEUR_SIMILARITE'],result['SUDOC_CHOSEN_ED'],result['KOHA_CHOSEN_ED'] = teste_editeur(result['SUDOC_214210c'], result['KOHA_214210c'])
                logger.debug("{} :: {} :: {}".format(result["MATCH_RECORDS_QUERY"], es.service, "Scores des éditeurs : " + str(result['MATCHING_EDITEUR_SIMILARITE'])))
            else: # Mandatory to prevent an error at the end
                result['MATCHING_EDITEUR_SIMILARITE'],result['SUDOC_CHOSEN_ED'],result['KOHA_CHOSEN_ED'] = -1, "", ""

            result["SUDOC_DIFFERENT_LOCAL_SYSTEM_NB"] = not koha_record.bibnb in result["SUDOC_LOCAL_SYSTEM_NB"]

            # ||| temp output
            result['KOHA_214210c'] = list_as_string(result['KOHA_214210c'])
            result['SUDOC_214210c'] = list_as_string(result['SUDOC_214210c'])
            # ||| END OF temp output

            # --------------- ANALYSIS PROCESS ---------------
            # Global validation
            # "" if 0 checks are asked, OK if all checks are OK, else, nb of OK
            if len(results_list) == 0:
                result["FINAL_OK"] = ""
            else:
                sum_of_results = 0
                for check in results_list:
                    result[check+"_OK"] = analysis_checks(es.chosen_analysis, check, result)
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
            logger.debug("{} :: {} :: {}".format(result["MATCH_RECORDS_QUERY"], es.service,
                "Résultat : {} (titres : {}, éditeurs : {}, dates : {})".format(str(result["FINAL_OK"]), str(result["TITLE_OK"]), str(result["PUB_OK"]), str(result["DATE_OK"]))))
            go_next(logger, results, csv_writer, result, True)

        # Closes CSV file
        f_csv.close()

    # --------------- END OF MAIN FUNCTION ---------------
    logger.info("--------------- File processing ended ---------------")

    # ------------------------------ FINAL OUTPUT ------------------------------
    # --------------- JSON FILE ---------------
    with open(es.file_path_out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    logger.info("JSON output file : " + es.file_path_out_json)

    # --------------- CSV FILE ---------------
    logger.info("CSV output file : " + es.file_path_out_csv)

    # --------------- REPORT ---------------
    generate_report(es, results_report)
    logger.info("Report file : " + es.file_path_out_results)
    logger.info("--------------- Report ---------------")
    generate_report(es, results_report, logger=logger)

    logger.info("--------------- <(^-^)> <(^-^)> Script fully executed without FATAL errors <(^-^)> <(^-^)> ---------------")

def generate_csv_output_header(csv_writer, fieldnames_id, fieldnames_names=[]):
    """Generates the CSV output file headers.
    
    Argument :
        - csv_writeer : the csv_writer
        - fieldnames_id {list of str} : name of the keys to export
        - delimiter [optionnal] {str}
        - fieldnames_names [optionnal] {list of str} : header name if different from the key ID"""
    if fieldnames_names == []:
        csv_writer.writeheader()
    else:
        new_headers = {}
        for ii, id in enumerate(fieldnames_id):
            new_headers[id] = fieldnames_names[ii]
        csv_writer.writerow(new_headers)

def go_next(logger, results, csv_writer, result, success):
    """Executes all necessary things before continuing to next line"""
    csv_writer.writerow(result)
    log_fin_traitement(logger, result, success)
    results.append(result)

def delete_control_char(txt: str) -> str:
    """Returns the string without control characters"""
    return re.sub(r"[\x00-\x1F]", " ", str(txt))

def list_as_string(this_list: list) -> str:
    """Returns the list as a string :
        - "" if the lsit is empty
        - the first element as a string if there's only one element
        - if after removing empty elements there is only one element, thsi element as a string
        - the lsit a string if there are multiple elements.
    Takes as argument a list"""
    if len(this_list) == 0:
        return ""
    elif len(this_list) == 1:
        return delete_control_char(str(this_list[0]))
    else:
        if type(this_list) != list:
            return delete_control_char(str(this_list))
        non_empty_elements = []
        for elem in this_list:
            if elem:
                non_empty_elements.append(elem)
        if len(non_empty_elements) == 0:
            return ""
        elif len(non_empty_elements) == 1:
            return delete_control_char(str(non_empty_elements[0]))
        else:
            return delete_control_char(str(non_empty_elements))