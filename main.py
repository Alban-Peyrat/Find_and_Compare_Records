# -*- coding: utf-8 -*- 

# External imports
import os
import csv
import json

# Internal import
import api.abes.AbesXml as AbesXml
import api.koha.Koha_API_PublicBiblio as Koha_API_PublicBiblio
from scripts.outputing import * # pour éviter de devoir réécrire tous les appels de fonctions
import fcr_classes as fcr

def main(es: fcr.Execution_Settings):
    """Main function.
    Takes as argument an Execution_Settings instance"""

# Init logger
    es.init_logger()
    es.log.big_info("<(~.~)> <(~.~)> Starting main script <(~.~)> <(~.~)>")
    es.log.simple_info("Log level", es.log_level)

    # Leaves if the file doesn't exists
    es.log.simple_info("File", es.file_path)
    if not os.path.exists(es.file_path):
        es.log.critical("Input file does not exist")
        print("Fatal error : input file does not exist")
        exit()

    # Creates output dir if needed
    if not os.path.exists(es.output_path):
        os.makedirs(es.output_path)
        es.log.info("Output directory did not exist : created it")

    # At this point, everything is OK, loads and initialise all vars
    es.generate_files_path()

    # Setting-up the analysis process
    es.log.simple_info("Chosen analysis", es.chosen_analysis["name"])
    results_list = []
    if es.chosen_analysis["TITLE_MIN_SCORE"] > 0:
        results_list.append("TITLE")
    if es.chosen_analysis["PUBLISHER_MIN_SCORE"] > 0:
        results_list.append("PUB")
    if es.chosen_analysis["USE_DATE"]:
        results_list.append("DATE")
    es.log.simple_info("Checks", str(results_list))

    # ----------------- AR220 : a edit
    # Init report
    results_report = fcr.Report()
    # ----------------- Fin de AR220 : a edit

    es.log.simple_info("Processing", es.processing_val)
    if es.processing_val in [fcr.FCR_Processings.BETTER_ITEM.name, fcr.FCR_Processings.BETTER_ITEM_DVD.name]:
        es.log.simple_info("Koha URL", es.origin_url)
        es.log.simple_info("ILN", es.iln)
        es.log.simple_info("RCR", es.rcr)
    if es.processing_val == fcr.FCR_Processings.MARC_FILE_IN_KOHA_SRU.name:
        es.log.simple_info("Koha URL", es.target_url)
    es.log.simple_info("Origin database", es.origin_database.name)
    es.log.simple_info("Target database", es.target_database.name)
    es.log.simple_info("Origin database mapping", es.origin_database_mapping)
    es.log.simple_info("Target database mapping", es.target_database_mapping)

    # ------------------------------ MAIN FUNCTION ------------------------------
    results = []
    es.log.big_info("File processing start")
    
    # Load original file data
    es.load_original_file_data()
    
    # Create CSV output file
    es.csv.create_file(es.original_file_headers)
    es.log.simple_info("CSV output file", es.csv.file_path)
    es.log.simple_info("CSV column configuration file", es.csv_cols_config_path)

    for index in es.original_file_data:
        # Declaration & set-up of record
        line = None
        if es.original_file_data_is_csv:
            line = es.original_file_data[index]
            # Retrieve ISBN + KohaBibNb
            # 0 = ISBN, 1 = 915$a, 2 = 915$b, 3 = 930$c, 4 = 930$e,
            # 5 = 930$a, 6 = 930$j, 7 = 930$v, 8 = L035$a
        rec = fcr.Original_Record(es, line)
        results_report.increase_processed() # report stats

        # Gets input query and original uid for BETTER_ITEMs
        if es.original_file_data_is_csv:
            rec.extract_from_original_line()
            es.log.info(f"--- Processing new line : input query = \"{rec.input_query}\", origin database ID = \"{rec.original_uid}\"")
        else:
            rec.set_fake_csv_file_data()
            es.log.info(f"--- Processing record n°{index}")

        # --------------- ORIGIN DATABASE ---------------
        # Get origin DB record
        # BETTER_ITEMs querying Koha Public biblio
        if es.processing in [fcr.FCR_Processings.BETTER_ITEM, fcr.FCR_Processings.BETTER_ITEM_DVD]:
            origin_record = Koha_API_PublicBiblio.Koha_API_PublicBiblio(rec.original_uid, es.origin_url, service=es.service, format="application/marcxml+xml")
            if origin_record.status == 'Error' :
                rec.trigger_error(f"Koha_API_PublicBiblio : {origin_record.error_msg}")
                results_report.increase_fail(fcr.Errors.KOHA) # report stats
                es.log.error(rec.error_message)
                es.csv.write_line(rec, False)
                results.append(rec.output.to_csv())
                continue # skip to next line
            rec.get_origin_database_data(es.processing, origin_record.record_parsed, es.origin_database, es)
        # MARC_FILE_IN_KOHA_SRU from the file
        if es.processing == fcr.FCR_Processings.MARC_FILE_IN_KOHA_SRU:
            origin_record = es.original_file_data[index]
            if origin_record is None:
                rec.trigger_error(f"MARC file : record was ignored because its chunk raised an exception")
                results_report.increase_fail(fcr.Errors.LOCAL_RECORD) # report stats
                es.log.error(rec.error_message)
                es.csv.write_line(rec, False)
                results.append(rec.output.to_csv())
                continue # skip to next line
            rec.get_origin_database_data(es.processing, origin_record, es.origin_database, es)
            
        # Successfully got origin DB record
        es.log.debug(f"Origin database ID : {rec.origin_database_data.utils.get_id()}")
        es.log.debug(f"Origin database cleaned title : {rec.origin_database_data.utils.get_first_title_as_string()}")

        # --------------- Match records ---------------
        rec.get_matched_records_instance(fcr.Matched_Records(es.operation, rec.input_query, rec.origin_database_data, es))     
        if rec.nb_matched_records == 0:
            rec.trigger_error("{} : no result".format(str(es.operation.name)))

        # ||| needs to be redone with enhanced match records errors
        # Idk when this comment was set but we can do errors by operations I guess, or smething like that
        if rec.error:
            results_report.increase_fail(fcr.Errors.MATCH_RECORD)
            es.log.error(rec.error_message)
            
            # Skip to next line
            es.csv.write_line(rec, False)
            results.append(rec.output.to_csv())
            continue
        
        # Match records was a success
        results_report.increase_success(fcr.Success.MATCH_RECORD) # report stats
        es.log.debug(f"Query used for matched record : {rec.query_used}")
        es.log.debug(f"Action : {rec.action_used.name}")
        es.log.debug(f"Result for {es.operation} : {str(rec.matched_records_ids)}")

        # --------------- FOR EACH MATCHED RECORDS ---------------
        for matched_id in rec.matched_records_ids:
            rec.set_matched_id(matched_id)
            # --------------- SUDOC ---------------
            # Get Sudoc record
            sudoc_record = AbesXml.AbesXml(matched_id,service=es.service)
            if sudoc_record.status == 'Error':
                rec.trigger_error(sudoc_record.error_msg)
                results_report.increase_fail(fcr.Errors.SUDOC) # report stats
                es.log.error(rec.error_message)
                es.csv.write_line(rec, False)
                results.append(rec.output.to_csv())
                continue # skip to next line

            # Successfully got Sudoc record
            rec.reset_error()
            # AR362 : UDE
            
            rec.get_target_database_data(es.processing, matched_id, sudoc_record.record_parsed, es.target_database, es)
            target_record:fcr.Database_Record = rec.target_database_data[matched_id] # for the IDE
            results_report.increase_success(fcr.Success.GLOBAL) # report stats
            es.log.debug(f"Target database ID : {rec.matched_id}")
            es.log.debug(f"Target database cleaned title : {target_record.utils.get_first_title_as_string()}")

            # --------------- MATCHING PROCESS ---------------
            # Garder les logs dans main
            target_record.compare_to(rec.origin_database_data)
            es.log.debug(f"Title scores : Simple ratio = {target_record.title_ratio}, Partial ratio = {target_record.title_partial_ratio}, Token sort ratio = {target_record.title_token_sort_ratio}, Token set ratio = {target_record.title_token_set_ratio}")
            es.log.debug(f"Dates matched ? {target_record.dates_matched}")
            es.log.debug(f"Publishers score = {target_record.publishers_score} (using \"{target_record.chosen_publisher}\" and \"{target_record.chosen_compared_publisher}\")")
            es.log.debug(f"Record ID included = {target_record.local_id_in_compared_record.name}")

            # --------------- END OF THIS LINE ---------------
            es.log.debug(f"Results : {target_record.total_checks.name} (titles : {target_record.checks[fcr.Analysis_Checks.TITLE]}, publishers : {target_record.checks[fcr.Analysis_Checks.PUBLISHER]}, dates : {target_record.checks[fcr.Analysis_Checks.DATE]})")
            es.csv.write_line(rec, True)
            results.append(rec.output.to_csv())

    # Closes CSV file
    es.csv.close_file()

    # --------------- END OF MAIN FUNCTION ---------------
    es.log.big_info("File processing ended")

    # ------------------------------ FINAL OUTPUT ------------------------------
    # --------------- JSON FILE ---------------
    with open(es.file_path_out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    es.log.simple_info("JSON output file", es.file_path_out_json)

    # --------------- CSV FILE ---------------
    es.log.simple_info("CSV output file", es.file_path_out_csv)

    # --------------- REPORT ---------------
    generate_report(es, results_report)
    es.log.simple_info("Report file", es.file_path_out_results)
    es.log.big_info("Report")
    generate_report(es, results_report, logger=es.log)

    es.log.big_info("<(^-^)> <(^-^)> Script fully executed without FATAL errors <(^-^)> <(^-^)>")