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
from scripts.outputing import * # pour éviter de devoir réécrire tous les appels de fonctions
import fcr_classes as fcr
import fcr_func as fcf

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
            result['KOHA_BIB_NB'] = fcf.list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.ID])
            temp = rec.origin_database_data.data[fcr.FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]
            result['KOHA_DATE_1'] = temp[0][0]
            result['KOHA_DATE_2'] = temp[0][1]
            result['KOHA_214210c'] = rec.origin_database_data.data[fcr.FCR_Mapped_Fields.PUBLISHERS_NAME]
            result['KOHA_200adehiv'] = fcf.nettoie_titre(fcf.list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.TITLE][0]))
            result['KOHA_305'] = fcf.list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.EDITION_NOTES])
            result["KOHA_PPN"] = fcf.list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.PPN])
            result["KOHA_214210a_DATES"] = []
            for date_str in rec.origin_database_data.data[fcr.FCR_Mapped_Fields.PUBLICATION_DATES]:
                result["KOHA_214210a_DATES"] += fcf.get_year(date_str)
            result["KOHA_214210a_DATES"] = fcf.list_as_string(result["KOHA_214210a_DATES"])
            result["KOHA_215a_DATES"] = []    
            for desc_str in rec.origin_database_data.data[fcr.FCR_Mapped_Fields.PHYSICAL_DESCRIPTION]: #AR259
                result["KOHA_215a_DATES"] += fcf.get_year(desc_str)
            result["KOHA_215a_DATES"] = fcf.list_as_string(result["KOHA_215a_DATES"])
            result['KOHA_010z'] = fcf.list_as_string(rec.origin_database_data.data[fcr.FCR_Mapped_Fields.ERRONEOUS_ISBN])
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
            if result["MATCH_RECORDS_NB_RES"] == 0:
                result["ERROR"] = True
                result['ERROR_MSG'] = "{} : aucun résultat".format(str(es.operation.name))
            # ||| End of AR358 to del
    
            # ||| needs to be redone with enhanced match records errors
            if result["ERROR"]:
                results_report.increase_fail(fcr.Errors.MATCH_RECORD)
                logger.error("{} :: {} :: {}".format(result["INPUT_QUERY"], es.service, str(result["ERROR_MSG"])))
                
                # Skip to next line
                go_next(logger, results, csv_writer, result, False)
                continue
            
            # Match records was a success
            results_report.increase_success(fcr.Success.MATCH_RECORD) # report stats
            logger.debug("{} :: {} :: {}".format(result["MATCH_RECORDS_QUERY"], es.service, "Résultat {} : ".format(str(es.operation)) + " || ".join(str(result["MATCH_RECORDS_RES"]))))

            # --------------- FOR EACH MATCHED RECORDS ---------------
            for matched_id in rec.matched_records_ids:
                this_result = result.copy()
                this_result["MATCHED_ID"] = matched_id
                # --------------- SUDOC ---------------
                # Get Sudoc record
                sudoc_record = AbesXml.AbesXml(matched_id,service=es.service)
                if sudoc_record.status == 'Error':
                    this_result['ERROR'] = True
                    this_result['ERROR_MSG'] = sudoc_record.error_msg
                    results_report.increase_fail(fcr.Errors.SUDOC) # report stats
                    go_next(logger, results, csv_writer, this_result, False)
                    continue # skip to next line

                # Successfully got Sudoc record
                # AR362 : UDE
                rec.get_target_database_data(es.processing, matched_id, sudoc_record.record_parsed, fcr.Databases.ABESXML, es)
                this_record:fcr.Database_Record = rec.target_database_data[matched_id] # for the IDE

                results_report.increase_success(fcr.Success.GLOBAL) # report stats

                # |||| AR362 to del
                temp_rec:fcr.Database_Record = rec.target_database_data[matched_id]
                temp_rec_data = temp_rec.data
                temp = temp_rec_data[fcr.FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]
                if len(temp) < 1:
                    this_result['SUDOC_DATE_1'] = None    
                    this_result['SUDOC_DATE_2'] = None
                else:
                    this_result['SUDOC_DATE_1'] = temp[0][0]
                    this_result['SUDOC_DATE_2'] = temp[0][1]
                this_result['SUDOC_214210c'] = temp_rec_data[fcr.FCR_Mapped_Fields.PUBLISHERS_NAME]
                this_result['SUDOC_200adehiv'] = fcf.nettoie_titre(fcf.list_as_string(temp_rec_data[fcr.FCR_Mapped_Fields.TITLE][0]))
                this_result['SUDOC_305'] = fcf.list_as_string(temp_rec_data[fcr.FCR_Mapped_Fields.EDITION_NOTES])
                this_result["SUDOC_LOCAL_SYSTEM_NB"] = temp_rec_data[fcr.FCR_Mapped_Fields.OTHER_DB_ID]
                # sudoc_record.get_local_system_nb(es.iln)
                this_result["SUDOC_NB_LOCAL_SYSTEM_NB"] = len(this_result["SUDOC_LOCAL_SYSTEM_NB"])
                this_result["SUDOC_LOCAL_SYSTEM_NB"] = fcf.list_as_string(this_result["SUDOC_LOCAL_SYSTEM_NB"])
                this_result["SUDOC_ITEMS"] = temp_rec_data[fcr.FCR_Mapped_Fields.ITEMS]
                # sudoc_record.get_library_items(es.rcr)
                this_result["SUDOC_HAS_ITEMS"] = len(this_result["SUDOC_ITEMS"]) > 0
                if this_result["SUDOC_NB_LOCAL_SYSTEM_NB"] > 0:
                    this_result["SUDOC_DIFFERENT_LOCAL_SYSTEM_NB"] = not koha_record.bibnb in this_result["SUDOC_LOCAL_SYSTEM_NB"]
                this_result["SUDOC_ITEMS"] = fcf.list_as_string(this_result["SUDOC_ITEMS"])
                this_result['SUDOC_010z'] = fcf.list_as_string(temp_rec_data[fcr.FCR_Mapped_Fields.ERRONEOUS_ISBN])
                # |||| END OF AR362 to del
                logger.debug("{} :: {} :: {}".format(this_result["MATCH_RECORDS_QUERY"], es.service, "PPN : " + this_result["MATCHED_ID"]))
                logger.debug("{} :: {} :: {}".format(this_result["MATCH_RECORDS_QUERY"], es.service, "Sudoc titre nettoyé : " + this_result['SUDOC_200adehiv']))

                # --------------- MATCHING PROCESS ---------------

                # Garder les logs dans main
                this_record.compare_to(rec.origin_database_data)
                logger.debug(f"{rec.query_used} :: {es.service} :: Title scores : Simple ratio = {this_record.title_ratio}, Partial ratio = {this_record.title_partial_ratio}, Token sort ratio = {this_record.title_token_sort_ratio}, Token set ratio = {this_record.title_token_set_ratio}")
                logger.debug(f"{rec.query_used} :: {es.service} :: Dates matched ? {this_record.dates_matched}")
                logger.debug(f"{rec.query_used} :: {es.service} :: Publishers score = {this_record.publishers_score} (using \"{this_record.chosen_publisher}\" and \"{this_record.chosen_compared_publisher}\")")
                logger.debug(f"{rec.query_used} :: {es.service} :: Record ID included = {this_record.local_id_in_compared_record.name}")

                # Titles
                # |||AR358 to del
                this_result['MATCHING_TITRE_SIMILARITE'] = temp_rec.title_ratio
                this_result['MATCHING_TITRE_APPARTENANCE'] = temp_rec.title_partial_ratio
                this_result['MATCHING_TITRE_INVERSION'] = temp_rec.title_token_sort_ratio
                this_result['MATCHING_TITRE_INVERSION_APPARTENANCE'] = temp_rec.title_token_set_ratio

                # Dates
                this_result['MATCHING_DATE_PUB'] = this_record.dates_matched

                # Publishers
                this_result['MATCHING_EDITEUR_SIMILARITE'] = this_record.publishers_score
                this_result['SUDOC_CHOSEN_ED'] = this_record.chosen_publisher
                this_result['KOHA_CHOSEN_ED'] = this_record.chosen_compared_publisher

                this_result["SUDOC_LOCAL_SYSTEM_NB"] = this_record.list_of_other_db_id
                this_result["SUDOC_NB_LOCAL_SYSTEM_NB"] = this_record.nb_other_db_id
                this_result["SUDOC_DIFFERENT_LOCAL_SYSTEM_NB"] = this_record.local_id_in_compared_record.name

                this_result['KOHA_214210c'] = fcf.list_as_string(this_result['KOHA_214210c'])
                this_result['SUDOC_214210c'] = fcf.list_as_string(this_result['SUDOC_214210c'])
                
                # Global validation
                this_result["FINAL_OK"] = this_record.total_checks.name
                this_result["NB_OK_CHECKS"] = this_record.passed_check_nb
                this_result["TITLE_OK"] = this_record.checks[fcr.Analysis_Checks.TITLE]
                this_result["PUBLISHER_OK"] = this_record.checks[fcr.Analysis_Checks.PUBLISHER]
                this_result["DATE_OK"] = this_record.checks[fcr.Analysis_Checks.DATE]          
                # ||| END OF |||AR358 to del


                # --------------- END OF THIS LINE ---------------
                logger.debug(f"{rec.query_used} :: {es.service} :: Results : {this_record.total_checks.name} (titles : {this_record.checks[fcr.Analysis_Checks.TITLE]}, publishers : {this_record.checks[fcr.Analysis_Checks.PUBLISHER]}, dates : {this_record.checks[fcr.Analysis_Checks.DATE]})")
                go_next(logger, results, csv_writer, this_result, True)

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