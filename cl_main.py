# -*- coding: utf-8 -*- 

# External import
from datetime import datetime
import xml.etree.ElementTree as ET
import pymarc
from enum import Enum
from typing import List, Dict

# Internal imports
from cl_UDE import Mapped_Fields
from cl_ES import Execution_Settings, Records_Settings, CSV_Cols, Analysis_Checks
from cl_PODA import Processing, Processing_Names, Processing_Data_Target, Action_Names
from cl_DBR import Database_Record
from cl_MR import Matched_Records, Request_Try
from func_string_manip import list_as_string, get_year

# -------------------- Enums --------------------
class Processed_Id_State(Enum):
    FAILED_BEFORE_ORIGIN_DB_GET = "Z"
    FAILED_BEFORE_MATCH_RECORDS_GET = "O"
    FAILED_BEFORE_TARGET_DB_LOOP = "M"
    FAILED_TO_GET_TARGET_DB = "Y"
    FAILED_TO_ANALYZE_TARGET_DB = "T"
    SUCCESS = "A"

class Report_Success(Enum):
    ORIGIN_DB = 1
    MATCH_RECORD_MATCHED = 2
    TARGET_DB = 3
    ANALYSIS = 4
    TARGET_RECORD_GLOBAL = 10
    ORIGIN_RECORD_GLOBAL = 11

class Report_Errors(Enum):
    ORIGIN_DB_KOHA = 100
    ORIGIN_DB_LOCAL_RECORD = 101
    MATCH_RECORD_NO_MATCH = 200
    TARGET_DB_SUDOC = 300
    TARGET_DB_KOHA = 301

# -------------------- Classes --------------------
class Original_Record(object):
    def __init__(self, processing:Processing, records_settings:Records_Settings, lang:str, line:dict=None):
        self.reset_error()
        self.processing = processing
        self.lang = lang
        self.original_line = line
        self.records_settings = records_settings
        self.target_database_data = {}
        self.output = self.Output(self)
    
    def extract_from_original_line(self, headers:list):
        """Extract the first column of the file as the input query and
        the last column as the original UID regardless of the headers name"""
        self.input_query = self.original_line[headers[0]]
        self.original_uid = str(self.original_line[headers[len(self.original_line)-1]]).rstrip()
    
    def set_fake_csv_file_data(self):
        """Sets fake data for fields extracted from CSV file to prevent crashes"""
        self.input_query = "NO INPUT QUERY"
        self.original_uid = "NO ORIGINAL UID"

    def get_matched_records_instance(self, mr: Matched_Records):
        """Extract data from the matched_records result."""
        self.matched_record_instance = mr
        self.query_used = mr.query
        self.action_used = mr.action
        self.nb_matched_records = len(mr.returned_ids)
        self.matched_records_ids = mr.returned_ids
        self.matched_records = mr.returned_records
        self.matched_records_include_records = mr.includes_record
    
    def get_origin_database_data(self, processing: Processing, record: ET.ElementTree | dict | pymarc.record.Record):
        """Extract data from the origin database record"""
        self.origin_database_data = Database_Record(processing, record, self.fcr_processed_id, False, self.records_settings)

    def get_target_database_data(self, processing: Processing, id:str, record: ET.ElementTree | dict | pymarc.record.Record):
        """Extract data from the origin database record"""
        self.target_database_data[id] = Database_Record(processing, record, self.fcr_processed_id, True, self.records_settings)

    def change_target_record_id(self, old_id:str, new_id:str):
        """Changes the ID key in target_database_data and set a new matched_id"""
        self.target_database_data[new_id] = self.target_database_data.pop(old_id)
        self.set_matched_id(new_id)

    def trigger_error(self, msg:str):
        """Updates the errors properties, takes as parameter the error moessage"""
        self.error = True
        self.error_message = str(msg)

    def reset_error(self):
        """Reset error properties"""
        self.error = False
        self.error_message = None

    def set_matched_id(self, id:str):
        """Sets the matched id property, takes a string as argument"""
        self.matched_id = id

    def set_fcr_processed_id(self, origin_db_index:int, state:Processed_Id_State, target_db_index:int=None):
        """Sets the FCR processed id property, takes as argument :
            - the origin DB index being processed as an int
            - A Processed_Id_State member
            - [optional] the target DB index being processed as an int"""
        part1 = f"{origin_db_index:05d}"
        part2 = state.value
        part3 = "XXX"
        if target_db_index != None: # if value is 0, using only if target_db_index would fail
            part3 = f"{target_db_index:03d}"
        self.fcr_processed_id = f"{part1}{part2}{part3}"


    # --- Output methods for other classes / functions ---
    class Output:
        def __init__(self, parent) -> None:
            self.parent = parent
        
        def __special_data(self, out:dict, origin_db=True) -> dict:
            """Special data with special output methods"""
            par:Original_Record = self.parent
            db = "ORIGIN_DB"
            db_data = par.origin_database_data
            if not origin_db:
                db = "TARGET_DB"
                db_data = par.target_database_data[par.matched_id]
            # Dates general processing data
            if list_as_string(db_data.data[Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]) != "":
                temp = db_data.data[Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]
                out[f"{db}_DATE_1"] = temp[0][0]
                out[f"{db}_DATE_2"] = temp[0][1]
            else:
                out[f"{db}_DATE_1"] = ""
                out[f"{db}_DATE_2"] = ""
            # Title
            # out[f"{db}_{Mapped_Fields.TITLE}"] = db_data.utils.get_first_title_as_string()
            out[f"{db}_TITLE_KEY"] = db_data.utils.get_first_title_as_string()
            # Publication dates
            out[f"{db}_{Mapped_Fields.PUBLICATION_DATES}"] = []
            for date_str in db_data.data[Mapped_Fields.PUBLICATION_DATES]:
                out[f"{db}_{Mapped_Fields.PUBLICATION_DATES}"] += get_year(date_str)
            out[f"{db}_{Mapped_Fields.PUBLICATION_DATES}"] = list_as_string(out[f"{db}_{Mapped_Fields.PUBLICATION_DATES}"])
            return out

        def __special_better_item(self, out:dict, origin_db=True) -> dict:
            """Special function for BETTER_ITEM, to transform some data form"""
            par:Original_Record = self.parent
            db = "ORIGIN_DB"
            db_data:Database_Record = par.origin_database_data
            if not origin_db:
                db = "TARGET_DB"
                db_data = par.target_database_data[par.matched_id]
                out[CSV_Cols.TARGET_DB_HAS_ITEMS.name] = len(db_data.data[Mapped_Fields.ITEMS]) > 0
            # Dates in physical description
            if origin_db:
                out[f"{db}_{Mapped_Fields.PHYSICAL_DESCRIPTION.name}"] = []
                for desc_str in db_data.data[Mapped_Fields.PHYSICAL_DESCRIPTION]: #AR259
                    out[f"{db}_{Mapped_Fields.PHYSICAL_DESCRIPTION.name}"] += get_year(desc_str)
                out[f"{db}_{Mapped_Fields.PHYSICAL_DESCRIPTION.name}"] = list_as_string(out[f"{db}_{Mapped_Fields.PHYSICAL_DESCRIPTION.name}"])
            # Delete unused columns
            del out[f"{db}_{Mapped_Fields.GENERAL_PROCESSING_DATA_DATES.name}"]
            return out
        
        def to_json(self, error:Report_Errors=None) -> dict:
            """Returns the data as a dict for the JSON file"""
            out = {}
            par:Original_Record = self.parent

            # Errors
            out["error"] = par.error
            out["error_message"] = par.error_message

            # Original line
            out["original_line"] = None
            if type(par.original_line) == dict:
                out["original_line"] = par.original_line

            # IDs
            out["fcr_processed_id"] = par.fcr_processed_id
            out["input_query"] = par.input_query
            out["original_uid"] = par.original_uid

            # First possible return : failed to get origin DB
            if error in [Report_Errors.ORIGIN_DB_KOHA, Report_Errors.ORIGIN_DB_LOCAL_RECORD]:
                return out

            # Origin database record
            out["origin_database"] = {
                "data":par.origin_database_data.data_to_json(),
                "fcr_processed_id":par.fcr_processed_id
            }

            # Matched records
            out["matched_record_tries"] = par.matched_record_instance.tries_to_json()
            out["query_used"] = par.query_used
            out["action_used"] = par.action_used.name
            out["nb_matched_records"] = par.nb_matched_records
            out["matched_records_ids"] = par.matched_records_ids

            # Second possible return : no matched records
            if error in [Report_Errors.MATCH_RECORD_NO_MATCH]:
                return out

            # Target DB records
            out["target_database"] = {}
            for record_id in par.target_database_data:
                record:Database_Record = par.target_database_data[record_id] # for IDE
                out["target_database"][record_id] = {
                    "data":record.data_to_json(),
                    "fcr_processed_id":record.fcr_processed_id,
                    "analysis":record.analysis_to_json()
                }

            return out

        def to_csv(self) -> dict:
            """Returns the data as a dict for the CSV export"""
            par:Original_Record = self.parent
            out = {}
            processing_fields:Dict[Mapped_Fields, Processing_Data_Target] = par.processing.mapped_data
            try:
                # Errors
                out[CSV_Cols.ERROR.name] = par.error
                out[CSV_Cols.ERROR_MSG.name] = par.error_message

                # Data from the original file
                if par.processing.original_file_data_is_csv:
                    out.update(par.original_line)
                out[CSV_Cols.INPUT_QUERY.name] = par.input_query
                out[CSV_Cols.ORIGIN_DB_INPUT_ID.name] = par.original_uid
                out[CSV_Cols.FCR_PROCESSED_ID.name] = par.fcr_processed_id

                # Origin database record
                for data in processing_fields:
                    if processing_fields[data] in [Processing_Data_Target.BOTH, Processing_Data_Target.ORIGIN]:
                        out[f"ORIGIN_DB_{data.name}"] = list_as_string(par.origin_database_data.data[data])
                out = self.__special_data(out)
                if par.processing.enum_member in [
                    Processing_Names.BETTER_ITEM,
                    Processing_Names.BETTER_ITEM_DVD,
                    Processing_Names.BETTER_ITEM_NO_ISBN,
                    Processing_Names.BETTER_ITEM_MAPS
                    ]:
                    out = self.__special_better_item(out)

                # Match records
                out[CSV_Cols.MATCH_RECORDS_QUERY.name] = par.query_used
                out[CSV_Cols.FCR_ACTION_USED.name] = par.action_used.name
                out[CSV_Cols.MATCH_RECORDS_NB_RESULTS.name] = par.nb_matched_records
                out[CSV_Cols.MATCH_RECORDS_RESULTS.name] = list_as_string(par.matched_records_ids)

                # Matched record
                out[CSV_Cols.MATCHED_ID.name] = par.matched_id

                # Target database record
                target_record:Database_Record = par.target_database_data[par.matched_id] # for the IDE
                for data in processing_fields:
                    if processing_fields[data] in [Processing_Data_Target.BOTH, Processing_Data_Target.TARGET]:
                        out[f"TARGET_DB_{data.name}"] = list_as_string(target_record.data[data])
                out = self.__special_data(out, False)
                if par.processing.enum_member in [
                    Processing_Names.BETTER_ITEM.name,
                    Processing_Names.BETTER_ITEM_DVD.name,
                    Processing_Names.BETTER_ITEM_NO_ISBN.name,
                    Processing_Names.BETTER_ITEM_MAPS.name
                    ]:
                    out = self.__special_better_item(out, False)

                # Analysis
                # Title
                out[CSV_Cols.MATCHING_TITLE_RATIO.name] = target_record.title_ratio
                out[CSV_Cols.MATCHING_TITLE_PARTIAL_RATIO.name] = target_record.title_partial_ratio
                out[CSV_Cols.MATCHING_TITLE_TOKEN_SORT_RATIO.name] = target_record.title_token_sort_ratio
                out[CSV_Cols.MATCHING_TITLE_TOKEN_SET_RATIO.name] = target_record.title_token_set_ratio
                # Dates
                out[CSV_Cols.MATCHING_DATES_RESULT.name] = target_record.dates_matched
                # Publishers
                out[CSV_Cols.MATCHING_PUBLISHER_RESULT.name] = target_record.publishers_score
                out[CSV_Cols.TARGET_DB_CHOSEN_PUBLISHER.name] = target_record.chosen_publisher
                out[CSV_Cols.ORIGIN_DB_CHOSEN_PUBLISHER.name] = target_record.chosen_compared_publisher
                # Ids
                out[CSV_Cols.TARGET_DB_NB_OTHER_ID.name] = target_record.nb_other_db_id
                out[CSV_Cols.IS_ORIGIN_ID_IN_TARGET_OTHER_DB_IDS.name] = target_record.local_id_in_compared_record.value[par.lang]
                # Global validation
                out[CSV_Cols.GLOBAL_VALIDATION_RESULT.name] = target_record.total_checks.value[par.lang]
                out[CSV_Cols.GLOBAL_VALIDATION_NB_SUCCESSFUL_CHECKS.name] = target_record.passed_check_nb
                out[CSV_Cols.GLOBAL_VALIDATION_TITLE_CHECK.name] = target_record.checks[Analysis_Checks.TITLE]
                out[CSV_Cols.GLOBAL_VALIDATION_PUBLISHER_CHECK.name] = target_record.checks[Analysis_Checks.PUBLISHER]
                out[CSV_Cols.GLOBAL_VALIDATION_DATE_CHECK.name] = target_record.checks[Analysis_Checks.DATE]  
                return out
            except:
                return out

class Report(object):
    def __init__(self, es:Execution_Settings):
        self.es = es
        self.time_start = datetime.now()
        self.processed = 0
        self.match_record_single_match = 0
        self.match_record_multiple_match = 0
        self.errors = {}
        for error in Report_Errors:
            self.errors[error.name] = 0
        self.success = {}
        for succ in Report_Success:
            self.success[succ.name] = 0
        self.actions = {}
        for action in es.processing.operation.actions:
            self.actions[action.name] = self.Action(action)

    class Action(object):
        def __init__(self, action:Action_Names) -> None:
            self.name = action.name
            self.action = action
            self.total = 0
            self.success = 0
            self.fail = 0
        
        def increase_total(self):
            self.total += 1

        def increase_success(self):
            self.success += 1
        
        def increase_fail(self):
            self.fail += 1

    def increase_processed(self):
        self.processed += 1
    
    def increase_step(self, step: Report_Success | Report_Errors):
        if type(step) == Report_Success:
            self.success[step.name] += 1
        elif type(step) == Report_Errors:
            self.errors[step.name] += 1
    
    def __get_step(self, step:Report_Success | Report_Errors) -> int:
        if type(step) == Report_Success:
            return self.success[step.name]
        elif type(step) == Report_Errors:
            return self.errors[step.name]
    
    def increase_match_records_actions(self, tries:List[Request_Try]):
        for this_try in tries:
            act:Report.Action = self.actions[this_try.action.name]
            act.increase_total()
            if this_try.returned_ids == []:
                act.increase_fail()
            else:
                act.increase_success()

    def increase_match_record_nb_of_match(self, match_record_matched_ids:list):
        if len(match_record_matched_ids) > 1:
            self.match_record_multiple_match += 1
        else:
            self.match_record_single_match += 1

    def generate_report_output_lines(self) -> List[str]:
        """Returns the report as a list of strings"""
        output = []

        # Header
        output.append("# Results report\n")
        output.append(f"For {self.es.processing.name} ({self.time_start.strftime('%y-%m-%d %H:%M')}) :")
        output.append("\n")

        # Settings infos
        output.append("## Settings\n")
        output.append(f"* Chosen analysis : {self.es.chosen_analysis['name']}")
        output.append(f"* Processed file : {self.es.file_path}")
        output.append(f"* CSV output file : {self.es.file_path_out_csv}")
        output.append(f"* JSON output file : {self.es.file_path_out_json}")
        if self.es.processing.enum_member in [
            Processing_Names.BETTER_ITEM,
            Processing_Names.BETTER_ITEM_DVD,
            Processing_Names.BETTER_ITEM_NO_ISBN,
            Processing_Names.BETTER_ITEM_MAPS
            ]:
            output.append(f"* Koha URL : {self.es.origin_url}")
            output.append(f"* ILN : {self.es.iln}, RCR : {self.es.rcr}")
        if self.es.processing.enum_member == Processing_Names.MARC_FILE_IN_KOHA_SRU:
            output.append(f"* Koha URL : {self.es.target_url}")
        output.append(f"* Origin database : {self.es.processing.origin_database.name} (mapping : {self.es.origin_database_mapping})")
        output.append(f"* Target database : {self.es.processing.target_database.name} (mapping : {self.es.target_database_mapping})")
        output.append("\n")

        # Steps Sucesses
        output.append("## Steps successes :\n")
        output.append(f"* Processed records : {self.processed}")
        output.append(f"* Origin database records successfully retrieved : {self.__get_step(Report_Success.ORIGIN_DB)}")
        output.append(f"* Records matched something : {self.__get_step(Report_Success.MATCH_RECORD_MATCHED)} (single match : {self.match_record_single_match}, multiple matches : {self.match_record_multiple_match})")
        output.append(f"* Target database records successfully retrieved : {self.__get_step(Report_Success.TARGET_DB)}")
        output.append(f"* Records analysed : {self.__get_step(Report_Success.ANALYSIS)}")
        output.append(f"* Origin records successfully processed : {self.__get_step(Report_Success.ORIGIN_RECORD_GLOBAL)}")
        output.append(f"* Target records successfully processed : {self.__get_step(Report_Success.TARGET_RECORD_GLOBAL)}")
        output.append("\n")

        # Steps fails
        output.append("## Steps fails :\n")
        if self.es.processing.enum_member in [
            Processing_Names.BETTER_ITEM,
            Processing_Names.BETTER_ITEM_DVD,
            Processing_Names.BETTER_ITEM_NO_ISBN,
            Processing_Names.BETTER_ITEM_MAPS
            ]:
            output.append(f"* Could not retrieve Koha records : {self.__get_step(Report_Errors.ORIGIN_DB_KOHA)}")
        if self.es.processing.enum_member == Processing_Names.MARC_FILE_IN_KOHA_SRU:
            output.append(f"* Could not retrieve local MARC records : {self.__get_step(Report_Errors.ORIGIN_DB_LOCAL_RECORD)}")
        output.append(f"* Records matched nothing : {self.__get_step(Report_Errors.MATCH_RECORD_NO_MATCH)}")
        if self.es.processing.enum_member in [
            Processing_Names.BETTER_ITEM,
            Processing_Names.BETTER_ITEM_DVD,
            Processing_Names.BETTER_ITEM_NO_ISBN,
            Processing_Names.BETTER_ITEM_MAPS
            ]:
            output.append(f"* Could not retrieve Sudoc records : {self.__get_step(Report_Errors.TARGET_DB_SUDOC)}")
        if self.es.processing.enum_member == Processing_Names.MARC_FILE_IN_KOHA_SRU:
            output.append(f"* Could not retrieve Koha records : {self.__get_step(Report_Errors.TARGET_DB_KOHA)}")
        output.append("\n")

        # Actions details
        output.append("## Actions used details :\n")
        for action in self.actions:
            act:Report.Action = self.actions[action]
            output.append(f"* `{action}` used {act.total} times : {act.success} success, {act.fail} fails")
        

        return output