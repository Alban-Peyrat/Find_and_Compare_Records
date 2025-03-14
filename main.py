# -*- coding: utf-8 -*- 

# External imports
import os
import json

# Internal import
import api.abes.AbesXml as AbesXml
import api.koha.Koha_API_PublicBiblio as Koha_API_PublicBiblio
from cl_error import Errors, get_error_instance
from cl_ES import Execution_Settings, Analysis_Checks
from cl_MR import Matched_Records
from cl_DBR import Database_Record
from cl_PODA import Processing_Names
from cl_main import Original_Record, Processed_Id_State, Report, Report_Errors, Report_Success
from func_file_check import check_file_existence, check_dir_existence

def temp_id(index:int):
    """Defines a temporary index"""
    return f"FCR INDEX {index}"

def main(es: Execution_Settings):
    """Main function.
    Takes as argument an Execution_Settings instance"""

    # Check if log dir exists
    if not check_dir_existence(es.logs_path, create=False):
        # Attempt creating it 
        if check_dir_existence(es.logs_path, create=True):
            print("Log directory did not exist : created it")
        # Attempt failed, leave
        else:
            print("Fatal error : log directory does not exist and failed to create it")
            exit()
    # Init logger
    es.init_logger()
    es.log.big_info("<(~.~)> <(~.~)> Starting main script <(~.~)> <(~.~)>")
    es.log.simple_info("Log level", es.log_level)

    # Leaves if the file doesn't exists
    es.log.simple_info("File", es.file_path)
    if not check_file_existence(es.file_path):
        es.log.critical("Input file does not exist")
        print("Fatal error : input file does not exist")
        exit()

    # Check if output dir exists
    if not check_dir_existence(es.output_path, create=False):
        # Attempt creating it 
        if check_dir_existence(es.output_path, create=True):
            es.log.info("Output directory did not exist : created it")
        # Attempt failed, leave
        else:
            es.log.critical("Output directory did not exist : failed to create it")
            print("Fatal error : output directory does not exist and failed to create it")
            exit()

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

    # Init report
    results_report = Report(es)

    es.log.simple_info("Processing", es.processing.name)
    if es.processing.enum_member in [
        Processing_Names.BETTER_ITEM,
        Processing_Names.BETTER_ITEM_DVD,
        Processing_Names.BETTER_ITEM_NO_ISBN,
        Processing_Names.BETTER_ITEM_MAPS
        ]:
        es.log.simple_info("Koha URL", es.origin_url)
        es.log.simple_info("ILN", es.iln)
        es.log.simple_info("RCR", es.rcr)
    if es.processing.enum_member == Processing_Names.MARC_FILE_IN_KOHA_SRU:
        es.log.simple_info("Koha URL", es.target_url)
    es.log.simple_info("Origin database", es.processing.origin_database.name)
    es.log.simple_info("Target database", es.processing.target_database.name)
    es.log.simple_info("Origin database mapping", es.origin_database_mapping)
    es.log.simple_info("Target database mapping", es.target_database_mapping)

    # ------------------------------ MAIN FUNCTION ------------------------------
    results = []
    json_output = []
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
        if es.processing.original_file_data_is_csv:
            line = es.original_file_data[index]
            # Retrieve ISBN + KohaBibNb
            # 0 = ISBN, 1 = 915$a, 2 = 915$b, 3 = 930$c, 4 = 930$e,
            # 5 = 930$a, 6 = 930$j, 7 = 930$v, 8 = L035$a
        rec = Original_Record(es.processing, es.get_records_settings(), es.lang, line)
        rec.set_fcr_processed_id(index, Processed_Id_State.FAILED_BEFORE_ORIGIN_DB_GET)
        results_report.increase_processed() # report stats

        # Gets input query and original uid for BETTER_ITEMs
        if es.processing.original_file_data_is_csv:
            rec.extract_from_original_line(es.original_file_headers)
            es.log.info(f"--- Processing new line : input query = \"{rec.input_query}\", origin database ID = \"{rec.original_uid}\"")
        else:
            rec.set_fake_csv_file_data()
            es.log.info(f"--- Processing record n°{index}")

        # --------------- ORIGIN DATABASE ---------------
        # Get origin DB record
        # BETTER_ITEMs querying Koha Public biblio
        if es.processing.enum_member in [
            Processing_Names.BETTER_ITEM,
            Processing_Names.BETTER_ITEM_DVD,
            Processing_Names.BETTER_ITEM_NO_ISBN,
            Processing_Names.BETTER_ITEM_MAPS
            ]:
            origin_record = Koha_API_PublicBiblio.Koha_API_PublicBiblio(rec.original_uid, es.origin_url, service=es.service, format="application/marcxml+xml")
            if origin_record.status == 'Error' :
                rec.trigger_error(f"Koha_API_PublicBiblio : {origin_record.error_msg}")
                results_report.increase_step(Report_Errors.ORIGIN_DB_KOHA) # report stats
                es.log.error(rec.error_message)
                es.csv.write_line(rec, False)
                results.append(rec.output.to_csv())
                json_output.append(rec.output.to_json(Report_Errors.ORIGIN_DB_KOHA))
                continue # skip to next line
            rec.get_origin_database_data(es.processing, origin_record.record_parsed)
        # MARC_FILE_IN_KOHA_SRU from the file
        elif es.processing.enum_member == Processing_Names.MARC_FILE_IN_KOHA_SRU:
            origin_record = es.original_file_data[index]
            if origin_record is None:
                rec.trigger_error(f"MARC file : {get_error_instance(Errors.MARC_CHUNK_RAISED_EXCEPTION).get_msg(es.lang)}")
                results_report.increase_step(Report_Errors.ORIGIN_DB_LOCAL_RECORD) # report stats
                es.log.error(rec.error_message)
                es.csv.write_line(rec, False)
                results.append(rec.output.to_csv())
                json_output.append(rec.output.to_json(Report_Errors.ORIGIN_DB_KOHA))
                continue # skip to next line
            rec.get_origin_database_data(es.processing, origin_record)
            rec.original_uid = rec.origin_database_data.utils.get_id()
            
        # Successfully got origin DB record
        es.log.debug(f"Origin database ID : {rec.origin_database_data.utils.get_id()}")
        es.log.debug(f"Origin database cleaned title : {rec.origin_database_data.utils.get_first_title_as_string()}")
        rec.set_fcr_processed_id(index, Processed_Id_State.FAILED_BEFORE_MATCH_RECORDS_GET)
        results_report.increase_step(Report_Success.ORIGIN_DB) # report stats

        # --------------- Match records ---------------
        es.log.info("Starting record matching process...")
        rec.get_matched_records_instance(Matched_Records(es.operation, rec.input_query, rec.origin_database_data, es.target_url, es.lang, es.service)) 
        if rec.nb_matched_records == 0:
            rec.trigger_error(f"{es.operation.name} : {get_error_instance(Errors.OPERATION_NO_RESULT).get_msg(es.lang)}")

        if rec.error:
            results_report.increase_step(Report_Errors.MATCH_RECORD_NO_MATCH) # report stats
            results_report.increase_match_records_actions(rec.matched_record_instance.tries)
            es.log.error(rec.error_message)
            
            # Skip to next line
            es.csv.write_line(rec, False)
            results.append(rec.output.to_csv())
            json_output.append(rec.output.to_json(Report_Errors.MATCH_RECORD_NO_MATCH))
            continue
        
        # Match records was a success
        rec.set_fcr_processed_id(index, Processed_Id_State.FAILED_BEFORE_TARGET_DB_LOOP)
        results_report.increase_step(Report_Success.MATCH_RECORD_MATCHED) # report stats
        results_report.increase_match_records_actions(rec.matched_record_instance.tries) # report stats
        results_report.increase_match_record_nb_of_match(rec.matched_records_ids) # report stats
        es.log.debug(f"Query used for matched record : {rec.query_used}")
        es.log.debug(f"Action : {rec.action_used.name}")
        es.log.debug(f"Result for {es.operation.name} : {str(rec.matched_records_ids)}")

        # --------------- FOR EACH MATCHED RECORDS ---------------
        # If Sudoc SRU in BETTER_ITEMs, query AbesXML because SRU don't have L035 (18/01/2024)
        record_list = rec.matched_records_ids
        list_is_id = True
        if len(rec.matched_records) > 0:
            record_list = rec.matched_records
            list_is_id = False
            # Tiny brain can't comprehend how to mrege all the if so I'm nesting them
            if es.processing.enum_member in [
                Processing_Names.BETTER_ITEM,
                Processing_Names.BETTER_ITEM_DVD,
                Processing_Names.BETTER_ITEM_NO_ISBN,
                Processing_Names.BETTER_ITEM_MAPS
                ]:
                if "SRU_SUDOC" in rec.action_used.name:
                    record_list = rec.matched_records_ids
                    list_is_id = True

        for ii, record_from_mr_list in enumerate(record_list):
            # Enumerate is to make sure I don't accidentally merge two records without ID
            # /!\ THIS IS WHAT DEFINES THE CURRENT ID OF THE LOOP /!\
            # rec.matched_id changes depending on the target db being anaylzed
            if list_is_id:
                rec.set_matched_id(record_from_mr_list)
            else:
                rec.set_matched_id(temp_id(ii))
            rec.set_fcr_processed_id(index, Processed_Id_State.FAILED_TO_GET_TARGET_DB, ii)

            # --------------- TARGET DATABASE ---------------
            # Get target DB record
            # BETTER_ITEMs querying Sudoc XML
            if es.processing.enum_member in [
                Processing_Names.BETTER_ITEM,
                Processing_Names.BETTER_ITEM_DVD,
                Processing_Names.BETTER_ITEM_NO_ISBN,
                Processing_Names.BETTER_ITEM_MAPS
                ]:
                target_db_queried_record = AbesXml.AbesXml(rec.matched_id,service=es.service)
                if target_db_queried_record.status == 'Error':
                    rec.trigger_error(f"Sudoc XML : {target_db_queried_record.error_msg}")
                    results_report.increase_step(Report_Errors.TARGET_DB_SUDOC) # report stats
                    es.log.error(rec.error_message)
                    es.csv.write_line(rec, False)
                    results.append(rec.output.to_csv())
                    continue # skip to next line
                rec.get_target_database_data(es.processing, rec.matched_id, target_db_queried_record.record_parsed)
            # MARC_FILE_IN_KOHA_SRU from the file
            elif es.processing.enum_member == Processing_Names.MARC_FILE_IN_KOHA_SRU:
                rec.get_target_database_data(es.processing, rec.matched_id, record_from_mr_list)
                target_record:Database_Record = rec.target_database_data[f"FCR INDEX {ii}"] # for the IDE
                if target_record.utils.get_id().strip() != "":
                    rec.change_target_record_id(temp_id(ii), target_record.utils.get_id().strip())

            # Successfully got target db record
            rec.reset_error()
            target_record:Database_Record = rec.target_database_data[rec.matched_id] # for the IDE
            rec.set_fcr_processed_id(index, Processed_Id_State.FAILED_TO_ANALYZE_TARGET_DB, ii)

            results_report.increase_step(Report_Success.TARGET_DB) # report stats
            es.log.debug(f"Target database ID : {rec.matched_id}")
            es.log.debug(f"Target database cleaned title : {target_record.utils.get_first_title_as_string()}")

            # --------------- ANALYSIS PROCESS ---------------
            # Garder les logs dans main
            target_record.compare_to(rec.origin_database_data)
            rec.set_fcr_processed_id(index, Processed_Id_State.SUCCESS, ii)
            results_report.increase_step(Report_Success.ANALYSIS) # report stats
            es.log.debug(f"Title scores : Simple ratio = {target_record.title_ratio}, Partial ratio = {target_record.title_partial_ratio}, Token sort ratio = {target_record.title_token_sort_ratio}, Token set ratio = {target_record.title_token_set_ratio}")
            es.log.debug(f"Dates matched ? {target_record.dates_matched}")
            es.log.debug(f"Publishers score = {target_record.publishers_score} (using \"{target_record.chosen_publisher}\" and \"{target_record.chosen_compared_publisher}\")")
            es.log.debug(f"Record ID included = {target_record.local_id_in_compared_record.name}")

            # --------------- END OF THIS LINE ---------------
            es.log.debug(f"Results : {target_record.total_checks.name} (titles : {target_record.checks[Analysis_Checks.TITLE]}, publishers : {target_record.checks[Analysis_Checks.PUBLISHER]}, dates : {target_record.checks[Analysis_Checks.DATE]})")
            es.csv.write_line(rec, True)
            results.append(rec.output.to_csv())
            results_report.increase_step(Report_Success.TARGET_RECORD_GLOBAL) # report stats

        # JSON output
        json_output.append(rec.output.to_json())

        results_report.increase_step(Report_Success.ORIGIN_RECORD_GLOBAL) # report stats
    # Closes CSV file
    es.csv.close_file()

    # --------------- END OF MAIN FUNCTION ---------------
    es.log.big_info("File processing ended")

    # ------------------------------ FINAL OUTPUT ------------------------------
    # --------------- JSON FILE ---------------
    with open(es.file_path_out_json, 'w', encoding='utf-8') as f:
        json.dump(json_output, f, ensure_ascii=False, indent=4)
    es.log.simple_info("JSON output file", es.file_path_out_json)

    # --------------- CSV FILE ---------------
    es.log.simple_info("CSV output file", es.file_path_out_csv)

    # --------------- REPORT ---------------
    es.log.simple_info("Report file", es.file_path_out_results)
    es.log.big_info("Report")
    with open(es.file_path_out_results, 'w', encoding='utf-8') as f:    
        for line in results_report.generate_report_output_lines():
            # File
            f.write(line + "\n")
            # Log
            if line.replace("\n", "").strip() != "":
                es.log.info(line.replace("\n", "").replace("#", "---")) # Do not log line breaks & #

    es.log.big_info("<(^-^)> <(^-^)> Script fully executed without FATAL errors <(^-^)> <(^-^)>")