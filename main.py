# -*- coding: utf-8 -*- 

# External imports
import os
import csv
import logging
import json

# Internal import
import scripts.logs as logs
# import api.abes.Abes_isbn2ppn as Abes_isbn2ppn
import api.abes.AbesXml as AbesXml
import api.koha.Koha_API_PublicBiblio as Koha_API_PublicBiblio
from scripts.outputing import * # pour éviter de devoir réécrire tous les appels de fonctions
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

    # Creates output dir if needed
    if not os.path.exists(es.output_path):
        os.makedirs(es.output_path)

    # At this point, everything is OK, loads and initialise all vars
    es.generate_files_path()

    # Setting-up the analysis process
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
            rec = fcr.Original_Record(line, es)
            results_report.increase_processed() # report stats
            # Retrieve ISBN + KohaBibNb
            # 0 = ISBN, 1 = 915$a, 2 = 915$b, 3 = 930$c, 4 = 930$e,
            # 5 = 930$a, 6 = 930$j, 7 = 930$v, 8 = L035$a

            # Gets input query and original uid
            rec.extract_from_original_line(CSV_ORIGINAL_COLS)
            logger.info(f"Processing new line : ISBN = \"{rec.input_query}\", Koha Bib Nb = \"{rec.original_uid}\"")

            # --------------- ORIGIN DATABASE ---------------
            # Get Koha record
            koha_record = Koha_API_PublicBiblio.Koha_API_PublicBiblio(rec.original_uid, es.origin_url, service=es.service, format="application/marcxml+xml")
            # Thfck is this → j'ai rajouté un filter(None) au moment de l'export CSV mais ça pose problème quand même...
            if koha_record.status == 'Error' :
                rec.trigger_error("Koha_API_PublicBiblio : " + koha_record.error_msg)
                results_report.increase_fail(fcr.Errors.KOHA) # report stats
                go_next(logger, results, csv_writer, rec.output.to_retro_CSV(), False)
                continue # skip to next line
            
            # Successfully got Koha record
            # AR362 : UDE
            rec.get_origin_database_data(es.processing, koha_record.record_parsed, fcr.Databases.KOHA_PUBLIC_BIBLIO, es)
            logger.debug("{} :: {} :: {}".format(rec.input_query, es.service, "Koha biblionumber : " + rec.origin_database_data.utils.get_id()))
            logger.debug("{} :: {} :: {}".format(rec.input_query, es.service, "Koha titre nettoyé : " + rec.origin_database_data.utils.get_first_title_as_string()))

            # --------------- Match records ---------------
            rec.get_matched_records_instance(fcr.Matched_Records(es.operation, rec.input_query, rec.origin_database_data, es))     
            if rec.nb_matched_records == 0:
                rec.trigger_error("{} : aucun résultat".format(str(es.operation.name)))
    
            # ||| needs to be redone with enhanced match records errors
            if rec.error:
                results_report.increase_fail(fcr.Errors.MATCH_RECORD)
                logger.error("{} :: {} :: {}".format(rec.input_query, es.service, rec.error_message))
                
                # Skip to next line
                go_next(logger, results, csv_writer, rec.output.to_retro_CSV(), False)
                continue
            
            # Match records was a success
            results_report.increase_success(fcr.Success.MATCH_RECORD) # report stats
            logger.debug("{} :: {} :: {}".format(rec.query_used, es.service, "Résultat {} : ".format(str(es.operation)) + " || ".join(str(rec.matched_records_ids))))

            # --------------- FOR EACH MATCHED RECORDS ---------------
            for matched_id in rec.matched_records_ids:
                rec.set_matched_id(matched_id)
                # --------------- SUDOC ---------------
                # Get Sudoc record
                sudoc_record = AbesXml.AbesXml(matched_id,service=es.service)
                if sudoc_record.status == 'Error':
                    rec.trigger_error(sudoc_record.error_msg)
                    results_report.increase_fail(fcr.Errors.SUDOC) # report stats
                    go_next(logger, results, csv_writer, rec.output.to_retro_CSV(), False)
                    continue # skip to next line

                # Successfully got Sudoc record
                rec.reset_error()
                # AR362 : UDE
                rec.get_target_database_data(es.processing, matched_id, sudoc_record.record_parsed, fcr.Databases.ABESXML, es)
                target_record:fcr.Database_Record = rec.target_database_data[matched_id] # for the IDE
                results_report.increase_success(fcr.Success.GLOBAL) # report stats
                logger.debug("{} :: {} :: {}".format(rec.query_used, es.service, "PPN : " + rec.matched_id))
                logger.debug("{} :: {} :: {}".format(rec.query_used, es.service, "Sudoc titre nettoyé : " + target_record.utils.get_first_title_as_string()))

                # --------------- MATCHING PROCESS ---------------
                # Garder les logs dans main
                target_record.compare_to(rec.origin_database_data)
                logger.debug(f"{rec.query_used} :: {es.service} :: Title scores : Simple ratio = {target_record.title_ratio}, Partial ratio = {target_record.title_partial_ratio}, Token sort ratio = {target_record.title_token_sort_ratio}, Token set ratio = {target_record.title_token_set_ratio}")
                logger.debug(f"{rec.query_used} :: {es.service} :: Dates matched ? {target_record.dates_matched}")
                logger.debug(f"{rec.query_used} :: {es.service} :: Publishers score = {target_record.publishers_score} (using \"{target_record.chosen_publisher}\" and \"{target_record.chosen_compared_publisher}\")")
                logger.debug(f"{rec.query_used} :: {es.service} :: Record ID included = {target_record.local_id_in_compared_record.name}")

                # --------------- END OF THIS LINE ---------------
                logger.debug(f"{rec.query_used} :: {es.service} :: Results : {target_record.total_checks.name} (titles : {target_record.checks[fcr.Analysis_Checks.TITLE]}, publishers : {target_record.checks[fcr.Analysis_Checks.PUBLISHER]}, dates : {target_record.checks[fcr.Analysis_Checks.DATE]})")
                go_next(logger, results, csv_writer, rec.output.to_retro_CSV(), True)

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