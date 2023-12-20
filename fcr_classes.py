# -*- coding: utf-8 -*- 

# External import
import os
from dotenv import load_dotenv
import logging
import json
import xml.etree.ElementTree as ET
import pymarc
import re
from typing import Dict, List, Tuple, Optional, Union
from fuzzywuzzy import fuzz

# Internal imports
import scripts.logs as logs
import fcr_func as fcf
from fcr_enum import *

# ----- Match Records imports -----
# Internal imports
import api.abes.Abes_id2ppn as id2ppn
import api.abes.Sudoc_SRU as ssru
import api.koha.Koha_SRU as Koha_SRU

# -------------------- Execution settings (ES) --------------------

class Execution_Settings(object):
    def __init__(self, dir: str):
        # Load csv export file settings
        with open(dir + "/json_configs/csv_export_cols.json", "r+", encoding="utf-8") as f:
            self.csv_export_cols_json = json.load(f)
        
        # Load analysis settings
        with open(dir + "/json_configs/analysis.json", "r+", encoding="utf-8") as f:
            self.analysis_json = json.load(f)

        # Load marc fields
        with open(dir + "/json_configs/marc_fields.json", "r+", encoding="utf-8") as f:
            self.marc_fields_json = json.load(f)
    
    def load_env_values(self):
        load_dotenv()
        # General
        self.lang = os.getenv("SERVICE")
        if self.lang not in ["eng", "fre"]:
            self.lang = "eng"
        self.service = os.getenv("SERVICE")
        self.file_path = os.getenv("FILE_PATH")
        self.output_path = os.getenv("OUTPUT_PATH")
        self.logs_path = os.getenv("LOGS_PATH")
        # Processing & operations
        self.UI_change_processing(os.getenv("PROCESSING_VAL"))
        self.get_operation()
        # Database specifics
        self.origin_url = os.getenv("ORIGIN_URL")
        self.origin_database_mapping = os.getenv("ORIGIN_DATABASE_MAPPING")
        self.target_url = os.getenv("TARGET_URL")
        self.target_database_mapping = os.getenv("TARGET_DATABASE_MAPPING")
        self.iln = os.getenv("ILN") # Better Item
        self.rcr = os.getenv("RCR") # Better Item
        self.filter1 = os.getenv("FILTER1") # Other DB in local DB
        self.filter2 = os.getenv("FILTER2") # Other DB in local DB
        self.filter3 = os.getenv("FILTER3") # Other DB in local DB
        # UI specifics
        self.UI_curr_database_mapping = self.origin_database_mapping
        self.UI_curr_data = "id"
        self.UI_curr_data_label = self.get_data_label_by_id(self.UI_curr_database_mapping, self.UI_curr_data)
        self.UI_update_curr_data(self.UI_curr_data_label)
        self.UI_curr_field = self.get_data_field_tags()[0]
        self.UI_new_field = None
        self.UI_curr_single_line_coded_data = None
        self.UI_curr_filtering_subfield = None
        self.UI_curr_subfields = None
        self.UI_curr_positions = None
        self.chosen_analysis = 0
        self.define_chosen_analysis(0)
    
    # ----- Methods for main -----
    def generate_files_path(self):
        self.file_path_out_results = self.output_path + "/resultats.txt"
        self.file_path_out_json = self.output_path + "/resultats.json"
        self.file_path_out_csv = self.output_path + "/resultats.csv"
    
    def get_operation(self):
        self.operation = PROCESSING_OPERATION_MAPPING[self.processing]

    def define_chosen_analysis(self, nb: int):
        self.chosen_analysis = self.analysis_json[nb]
        self.chosen_analysis_checks = {}
        if self.chosen_analysis["TITLE_MIN_SCORE"] > 0:
            self.chosen_analysis_checks[Analysis_Checks.TITLE] = None
        if self.chosen_analysis["PUBLISHER_MIN_SCORE"] > 0:
            self.chosen_analysis_checks[Analysis_Checks.PUBLISHER] = None
        if self.chosen_analysis["USE_DATE"]:
            self.chosen_analysis_checks[Analysis_Checks.DATE] = None
    
    def init_logger(self):
        """Init the logger"""
        logs.init_logs(self.logs_path, self.service,'DEBUG')
        self.logger = logging.getLogger(self.service)
        self.logger.info("File : " + self.file_path)
        self.logger.info("Origin database URL : " + self.origin_url)
        self.logger.info("Chosen analysis : " + self.chosen_analysis["name"])

    def log_debug(self, msg:str):
        """Log a debug statement logging first the service then the message"""
        self.logger.debug(f"{self.service} :: {msg}")

    def log_big_info(self, msg:str):
        """Logs a info statement encapsuled between ----"""
        self.logger.info(f"--------------- {msg} ---------------")

    def log_error(self, msg:str):
        """Log a error statement logging first the service then the message"""
        self.logger.error(f"{self.service} :: {msg}")

    # ----- Methods for UI -----
    def UI_switch_lang(self):
        """Switch the two languages"""
        if self.lang == "eng":
            self.lang = "fre"
        else:
            self.lang = "eng"

    def UI_update_curr_data(self, label=None):
        """Update the current data 
        Takes as argument :
        - label : the data id label in selected language"""
        if not label:
            label = self.UI_curr_data_label
        db = self.UI_curr_database_mapping
        self.UI_curr_data = self.get_data_id_from_label(db, label)
        id = self.UI_curr_data
        self.UI_update_curr_field(self.get_data_field_tags(db, id)[0])
        self.UI_update_curr_field_subvalues(db, id, self.UI_curr_field)

    def UI_update_curr_data_label(self, id=None):
        """Update the current data label 
        Takes as argument :
        - id : the data id"""
        if not id:
            id = self.UI_curr_data
        self.UI_curr_data_label = self.get_data_label_by_id(id=id)

    def UI_update_curr_field(self, tag: str):
        """Update the current data label"""
        self.UI_curr_field = tag
    
    def UI_update_curr_field_subvalues(self, db=None, id=None, tag=None):
        """Update the current field
        Takes as argument :
            - db : the database name in marc_fields.json as a string
            - id : the data id
            - tag : the MARC tag as a string"""
        if not db:
            db = self.UI_curr_database_mapping
        if not id:
            id = self.UI_curr_data
        if not tag:
            tag = self.UI_curr_field
        self.UI_curr_single_line_coded_data = self.get_data_field_single_line_coded_data(db, id, tag)
        self.UI_curr_filtering_subfield = self.get_data_field_filtering_subfield(db, id, tag)
        self.UI_curr_subfields = self.get_data_field_subfields(db, id, tag)
        self.UI_curr_positions = self.get_data_field_positions(db, id, tag)

    def UI_reset_curr_field_subvalues(self):
        """Defaults all values for the current field"""
        self.UI_curr_single_line_coded_data = False
        self.UI_curr_filtering_subfield = ""
        self.UI_curr_subfields = ""
        self.UI_curr_positions = ""

    def UI_rename_curr_data(self, new_name: str):
        """Updates the current data label.
        Takes as argument the new label"""
        self.UI_curr_data_label = new_name

    def UI_change_curr_database_mapping(self, new_mapping: str):
        """Updates the current dataabse mapping.
        Takes as argument the new mappnig"""
        self.UI_curr_database_mapping = new_mapping

    def UI_change_processing(self, processing_val: str):
        """Updates the current dataabse mapping.
        Takes as argument the new val AS A STRING not a FCR_Processings entry"""
        self.processing_val = processing_val
        self.processing = FCR_Processings[self.processing_val]

    def UI_update_main_screen_values(self, val:dict):
        """Updates all data from the UI inside this instance"""
        self.service = val["SERVICE"]
        self.file_path = val["FILE_PATH"]
        self.output_path = val["OUTPUT_PATH"]
        self.logs_path = val["LOGS_PATH"]
        self.UI_change_processing(val["PROCESSING_VAL"])
        self.get_operation()

    def UI_update_processing_configuration_values(self, val:dict):
        """Updates all data from the UI inside this instance"""
        self.origin_url = val["ORIGIN_URL"]
        self.target_url = val["TARGET_URL"]
        self.iln = val["ILN"]
        self.rcr = val["RCR"]
        self.filter1 = val["FILTER1"]
        self.filter2 = val["FILTER2"]
        self.filter3 = val["FILTER3"]
        self.origin_database_mapping = val["ORIGIN_DATABASE_MAPPING"]
        self.target_database_mapping = val["TARGET_DATABASE_MAPPING"]

    # ----- Methods for retrieving data from mappings -----
    def UI_get_mappings_names(self) -> list:
        """Returns all mappings names as a list"""
        return list(self.marc_fields_json.keys())
    
    def get_data_id_from_label(self, db=None, label=None) -> str:
        """Returns the data id from marc field based on it's label.
        Takes as argument :
            - db : the database name in marc_fields.json as a string
            - label : the data id label in selected language
        Returns None if no match was found"""
        if not db:
            db = self.UI_curr_database_mapping
        if not label:
            label = self.UI_curr_data_label
        for data in self.marc_fields_json[db]:
            if self.marc_fields_json[db][data]["label"][self.lang] == label:
                return data
        return None
    
    def get_data_labels_as_list(self, db=None) -> List[str]:
        """Returns all data labels from marc field as a list.
        Takes as argument :
            - db : the database name in marc_fields.json as a string"""
        if not db:
            db = self.UI_curr_database_mapping
        return [self.marc_fields_json[db][key]["label"][self.lang] for key in self.marc_fields_json[db]]

    def get_data_label_by_id(self, db=None, id=None) -> str:
        """Returns the label of a data
        Takes as argument :
            - db : the database name in marc_fields.json as a string
            - id : the data id"""
        if not db:
            db = self.UI_curr_database_mapping
        if not id:
            id = self.UI_curr_data
        return self.marc_fields_json[db][id]["label"][self.lang]

    def get_data_field_tags(self, db=None, id=None) -> List[str]:
        """Returns the tags of each field from a data
        Takes as argument :
            - db : the database name in marc_fields.json as a string
            - id : the data id"""
        if not db:
            db = self.UI_curr_database_mapping
        if not id:
            id = self.UI_curr_data
        return [field["tag"] for field in self.marc_fields_json[db][id]["fields"]]

    def retrieve_data_from_data_field_subvalues(self, attr:str, db=None, id=None, tag=None):
        """Mother function of get_marc_data_field + attribute.
        Takes as argument :
            - db : the database name in marc_fields.json as a string
            - id : the data id
            - tag : the MARC tag as a string
            - attr : the attribute name (positions, subfields, etc.)"""
        if not db:
            db = self.UI_curr_database_mapping
        if not id:
            id = self.UI_curr_data
        if not tag:
            tag = self.UI_curr_field
        fields = self.marc_fields_json[db][id]["fields"]
        for field in fields:
            if field["tag"] == tag:
                return field[attr]

    def get_data_field_single_line_coded_data(self, db=None, id=None, tag=None) -> bool:
        """Returns if the field is a sinngle line coded data
        Takes as argument :
            - db : the database name in marc_fields.json as a string
            - id : the data id
            - tag : the MARC tag as a string"""
        if not db:
            db = self.UI_curr_database_mapping
        if not id:
            id = self.UI_curr_data
        if not tag:
            tag = self.UI_curr_field
        return self.retrieve_data_from_data_field_subvalues("single_line_coded_data", db, id, tag)

    def get_data_field_filtering_subfield(self, db=None, id=None, tag=None) -> str:
        """Returns the filtering subfield of this field
        Takes as argument :
            - db : the database name in marc_fields.json as a string
            - id : the data id
            - tag : the MARC tag as a string"""
        if not db:
            db = self.UI_curr_database_mapping
        if not id:
            id = self.UI_curr_data
        if not tag:
            tag = self.UI_curr_field
        return self.retrieve_data_from_data_field_subvalues("filtering_subfield", db, id, tag)

    def get_data_field_subfields(self, db=None, id=None, tag=None) -> str:
        """Returns the subfields to export for this field
        Takes as argument :
            - db : the database name in marc_fields.json as a string
            - id : the data id
            - tag : the MARC tag as a string"""
        if not db:
            db = self.UI_curr_database_mapping
        if not id:
            id = self.UI_curr_data
        if not tag:
            tag = self.UI_curr_field
        return ", ".join(self.retrieve_data_from_data_field_subvalues("subfields", db, id, tag))

    def get_data_field_positions(self, db=None, id=None, tag=None) -> str:
        """Returns the positions to export for this field
        Takes as argument :
            - db : the database name in marc_fields.json as a string
            - id : the data id
            - tag : the MARC tag as a string"""
        if not db:
            db = self.UI_curr_database_mapping
        if not id:
            id = self.UI_curr_data
        if not tag:
            tag = self.UI_curr_field
        return ", ".join(self.retrieve_data_from_data_field_subvalues("positions", db, id, tag))

    # ----- Methods for retrieving data from analysis -----
    def get_analysis_names_as_list(self):
        """Returns all analysis names as a list"""
        return [this["name"] for this in self.analysis_json]

    def get_analysis_index_from_name(self, name: str) -> int:
        """Returns the index of an analysis.
        Takes as argument the name of the analysis"""
        for index, this in enumerate(self.analysis_json):
            if this["name"] == name:
                return index

# -------------------- DATABASE RECORD (DBR) --------------------

class Database_Record(object):
    """Contains extracted data from the record.
    The data property contains every mapped data for the chosen processing"""
    def __init__(self, processing: FCR_Processings, record: ET.ElementTree | dict | pymarc.record.Record, database: Databases, is_target_db: bool, es: Execution_Settings):
        self.processing = processing
        self.record = record
        self.database = database
        self.is_target_db = is_target_db
        self.ude = Universal_Data_Extractor(self.record, self.database, self.is_target_db, es)
        self.data = {}
        for data in processing.value:
            if (
                (processing.value[data] == FCR_Processing_Data_Target.BOTH)
                or (self.is_target_db and processing.value[data] == FCR_Processing_Data_Target.TARGET)
                or (not self.is_target_db and processing.value[data] == FCR_Processing_Data_Target.ORIGIN)
            ):
                if data in self.database.value:
                    #temp
                    filter_value = ""
                    if self.database.value[data] == "RCR":
                        filter_value = es.rcr
                    if self.database.value[data] == "ILN":
                        filter_value = es.iln
                    #temp
                    self.data[data] = self.ude.get_by_mapped_field_name(data, filter_value)
                else:
                    self.data[data] = self.ude.get_by_mapped_field_name(data)
        self.chosen_analysis = es.chosen_analysis
        self.chosen_analysis_checks = es.chosen_analysis_checks
        self.utils = self.Utils(self)

    def __compare_titles(self, compared_to):
        """Compares the titles and sets their keys"""
        self.compared_title_key = compared_to.utils.get_first_title_as_string()
        self.title_key = self.utils.get_first_title_as_string()
        self.title_ratio = fuzz.ratio(self.title_key, self.compared_title_key)
        self.title_partial_ratio = fuzz.partial_ratio(self.title_key, self.compared_title_key)
        self.title_token_sort_ratio = fuzz.token_sort_ratio(self.title_key, self.compared_title_key)
        self.title_token_set_ratio = fuzz.token_set_ratio(self.title_key, self.compared_title_key)
    
    def __compare_dates(self, compared_to) -> None:
        """Compares if one of the record dates matches on one of the compared record."""
        self.dates_matched = False
        # Merge dates lists
        this_dates = []
        for dates in self.data[FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]:
            this_dates.extend(dates)
        compared_dates = []
        for dates in compared_to.data[FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]:
            compared_dates.extend(dates)
        for date in this_dates:
            if date in compared_dates and date != "    ": # excludes empty dates
                self.dates_matched = True
                return
    
    def __compare_publishers(self, compared_to) -> None:
        """Compares every publishers in this record with every publishers in comapred record"""
        self.publishers_score = -1
        self.chosen_publisher = ""
        self.chosen_compared_publisher = ""
        # I fboth don't have results, comparison can't be done
        if len(self.data[FCR_Mapped_Fields.PUBLISHERS_NAME]) == 0 or len(compared_to.data[FCR_Mapped_Fields.PUBLISHERS_NAME]) == 0:
            return
        for publisher in self.data[FCR_Mapped_Fields.PUBLISHERS_NAME]:
            publisher = fcf.clean_publisher(publisher)
            for compared_publisher in compared_to.data[FCR_Mapped_Fields.PUBLISHERS_NAME]:
                compared_publisher = fcf.clean_publisher(compared_publisher)
                ratio = fuzz.ratio(publisher, compared_publisher)
                if ratio > self.publishers_score:
                    self.publishers_score = ratio
                    self.chosen_publisher = publisher
                    self.chosen_compared_publisher = compared_publisher

    def __compare_other_db_id(self, compared_to):
        """Checks if this record id is in the comapred other database IDs"""
        self.local_id_in_compared_record = Other_Database_Id_In_Target.UNKNOWN
        self.list_of_other_db_id = self.data[FCR_Mapped_Fields.OTHER_DB_ID]
        self.nb_other_db_id = len(self.list_of_other_db_id)
        id = fcf.list_as_string(compared_to.data[FCR_Mapped_Fields.ID])
        if self.nb_other_db_id == 0:
            self.local_id_in_compared_record = Other_Database_Id_In_Target.NO_OTHER_DB_ID
        elif self.nb_other_db_id == 1 and id in self.list_of_other_db_id:
            self.local_id_in_compared_record = Other_Database_Id_In_Target.ONLY_THIS_OTHER_DB_ID
        elif self.nb_other_db_id > 1 and id in self.list_of_other_db_id:
            self.local_id_in_compared_record = Other_Database_Id_In_Target.THIS_ID_INCLUDED
        elif id not in self.list_of_other_db_id:
            self.local_id_in_compared_record = Other_Database_Id_In_Target.THIS_ID_NOT_INCLUDED

    def __analysis_check_title(self):
        self.check_title_nb_valids = 0
        # for each matching score, checks if it's high enough
        title_score_list = [
            self.title_ratio,
            self.title_partial_ratio,
            self.title_token_sort_ratio,
            self.title_token_set_ratio
            ]
        for title_score in title_score_list:
            if title_score >= self.chosen_analysis["TITLE_MIN_SCORE"]:
                self.check_title_nb_valids += 1
        self.checks[Analysis_Checks.TITLE] = (self.check_title_nb_valids >= self.chosen_analysis["NB_TITLE_OK"])

    def __analysis_checks(self, check):
        """Launches the check for the provided analysis"""
        # Titles
        if check == Analysis_Checks.TITLE:
            self.__analysis_check_title()
        # Publishers
        elif check == Analysis_Checks.PUBLISHER:
            self.checks[Analysis_Checks.PUBLISHER] = (self.publishers_score >= self.chosen_analysis["PUBLISHER_MIN_SCORE"])
        # Dates
        elif check == Analysis_Checks.DATE:
            self.checks[Analysis_Checks.DATE] = self.dates_matched

    def __finalize_analysis(self):
        """Summarizes all checks"""
        self.total_checks = Analysis_Final_Results.UNKNOWN
        self.passed_check_nb = 0
        self.checks = {}
        for check in Analysis_Checks:
            self.checks[check] = None
        if len(self.chosen_analysis_checks) == 0:
            self.total_checks = Analysis_Final_Results.NO_CHECK
        else:
            for check in self.chosen_analysis_checks:
                self.__analysis_checks(check)
                if self.checks[check] == True:
                    self.passed_check_nb += 1
            if self.passed_check_nb == len(self.chosen_analysis_checks):
                self.total_checks = Analysis_Final_Results.TOTAL_MATCH
            elif self.passed_check_nb > 0:
                self.total_checks = Analysis_Final_Results.PARTIAL_MATCH
            else:
                self.total_checks = Analysis_Final_Results.NO_MATCH

    def compare_to(self, compared_to):
        """Execute the analysis processs
        Takes as argument:
        - compared_to {Database_Record instance} : the record from origin database"""
        self.__compare_titles(compared_to)
        self.__compare_dates(compared_to)
        self.__compare_publishers(compared_to)
        self.__compare_other_db_id(compared_to)
        self.__finalize_analysis()

    
    # --- Utils methods for other classes / functions ---
    class Utils:
        def __init__(self, parent) -> None:
            self.parent = parent
            self.data: dict = self.parent.data

        def get_id(self) -> str:
            """Returns the record ID as a string"""
            return fcf.list_as_string(self.data[FCR_Mapped_Fields.ID])

        def get_first_title_as_string(self) -> str:
            """Returns the first title cleaned up as a strin"""
            return fcf.nettoie_titre(fcf.list_as_string(self.data[FCR_Mapped_Fields.TITLE][0]))

        def get_titles_as_string(self) -> str:
            """Returns all titles cleaned up as a str"""
            return fcf.nettoie_titre(fcf.list_as_string(self.data[FCR_Mapped_Fields.TITLE]))

        def get_authors_as_string(self) -> str:
            """Returns all authors cleaned up as a str"""
            return fcf.nettoie_titre(fcf.list_as_string(self.data[FCR_Mapped_Fields.AUTHORS]))

        def get_all_publishers_as_string(self) -> str:
            """Returns all authors cleaned up as a str"""
            return fcf.clean_publisher(fcf.list_as_string(self.data[FCR_Mapped_Fields.PUBLISHERS_NAME]))

        def get_all_publication_dates(self) -> Tuple[List[int], int, int]:
            """Returns a tuple :
                - all publication dates as a list of int
                - the oldest date as a int (None if no date)
                - the newest date as a int (None if no date)"""
            dates = []
            for date_str in self.data[FCR_Mapped_Fields.PUBLICATION_DATES]:
                dates += fcf.get_year(date_str)
            # Intifies
            for date in dates:
                date = int(date)
            if dates == []:
                return dates, None, None
            return dates, min(dates), max(dates)
            
            
# -------------------- MATCH RECORDS (MR) --------------------

class Request_Try(object):
    """"""
    def __init__(self, try_nb: int, action: Actions):
        self.try_nb = try_nb
        self.action = action
        self.status = Try_Status.UNKNWON
        self.error_type = None
        self.msg = None
        self.query = None
        self.returned_ids = []
        self.returned_records = []
        self.includes_records = False
    
    def error_occured(self, msg: Match_Records_Errors | str):
        if type(self.msg) == Match_Records_Errors:
            self.error_type = msg
            self.msg = Match_Records_Error_Messages[self.error_type.name]
        else:
            self.error_type = Match_Records_Errors.GENERIC_ERROR
            self.msg = msg
        self.status = Try_Status.ERROR
    
    def define_special_status(self, status: Try_Status, msg: str):
        self.msg = msg
        if type(status) != Try_Status:
            return
        self.status = status
    
    def define_used_query(self, query: str):
        self.query = query

    def add_returned_ids(self, ids: list):
        self.returned_ids = ids
        self.status = Try_Status.SUCCESS
    
    def add_returned_records(self, records: list):
        self.returned_records = records
        self.includes_records = True

class Matched_Records(object):
    """
    
    Takes as argument :
        - operation {Operations Instance} (defaults to SEARCH_IN_SUDOC_BY_ISBN)"""
    def __init__(self, operation: Operations, query: str, local_record:Database_Record, es: Execution_Settings):
        self.error = None
        self.error_msg = None
        self.tries = []
        self.returned_ids = []
        self.returned_records = []
        self.includes_record = False

       # Get the operation, defaults on SEARCH_IN_SUDOC one
        self.operation = Operations.SEARCH_IN_SUDOC_BY_ISBN
        if type(operation) == Operations:
            self.operation = operation

        self.query = query
        self.local_record = local_record
        self.es = es

        # Calls the operation
        self.execute_operation()
        self.query = self.tries[-1].query

    def execute_operation(self):
        """Searches in the Sudoc with 3 possibles tries :
            - isbn2ppn
            - if failed, isbn2ppn after ISBN conversion
            - if failed again, Sudoc SRU on ISB index
        
        Requires match_records query to be an ISBN"""
        for index, action in enumerate(Try_Operations[self.operation.name].value):
            thisTry = Request_Try(index, action)
            self.request_action(action, thisTry)
            self.tries.append(thisTry)

            # If matched ids were returned, break the loop as we have our results
            if thisTry.returned_ids != []:
                self.returned_ids = thisTry.returned_ids

                if thisTry.includes_records:
                    self.returned_records = thisTry.returned_records
                    self.includes_record = True
                break
        
        # Checks if results were found
        if self.returned_ids == []:
            self.error = Match_Records_Errors.NOTHING_WAS_FOUND
            self.error_msg = Match_Records_Error_Messages[self.error.name]


    def request_action(self, action: Actions, thisTry: Request_Try):
        """Makes the request for this specific action and returns a list of IDs as a result"""
        # Actions based on the same connector are siilar, do not forget to udate all of them

        # Action SRU SUdoc ISBN
        if action == Actions.SRU_SUDOC_ISBN:
            sru = ssru.Sudoc_SRU()
            sru_request = ssru.Part_Of_Query(
                ssru.SRU_Indexes.ISB,
                ssru.SRU_Relations.EQUALS,
                self.query
            )
            thisTry.define_used_query(sru.generate_query([sru_request]))
            res = sru.search(
                thisTry.query,
                record_schema=ssru.SRU_Record_Schemas.UNIMARC,
                record_packing=ssru.SRU_Record_Packings.XML,
                maximum_records=100,
                start_record=1
            )
            if (res.status == "Error"):
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_records_id())
                thisTry.add_returned_records(res.get_records())

        # Action isbn2ppn
        elif action == Actions.ISBN2PPN:
            i2p = id2ppn.Abes_id2ppn(webservice=id2ppn.Webservice.ISBN, useJson=True)
            res = i2p.get_matching_ppn(self.query)
            thisTry.define_used_query(res.get_id_used())
            if res.status != id2ppn.Id2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action isbn2ppn with changed ISBN
        elif action == Actions.ISBN2PPN_MODIFIED_ISBN:
            #AR226
            # Converting the ISBN to 10<->13
            if len(self.query) == 13:
                new_query = self.query[3:-1]
                new_query += id2ppn.compute_isbn_10_check_digit(list(str(new_query)))
            elif len(self.query) == 10:
                # Doesn't consider 979[...] as the original issue should only concern old ISBN
                new_query = "978" + self.query[:-1]
                new_query += id2ppn.compute_isbn_13_check_digit(list(str(new_query)))
            
            # Same thing as Action ISBN2PPN
            i2p = id2ppn.Abes_id2ppn(useJson=True)
            res = i2p.get_matching_ppn(self.query)
            thisTry.define_used_query(res.get_id_used())
            if res.status != id2ppn.Id2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action SRU SUdoc EAN
        elif action == Actions.EAN2PPN:
            # Gets the first EAN
            ean = ""
            for val in self.local_record.data[FCR_Mapped_Fields.EAN]:
                if type(val) == str and val != "":
                    ean = val
                    break
            # No EAN was found, throw an error
            if ean == "":
                thisTry.error_occured(Match_Records_Errors.NO_EAN_WAS_FOUND)
                return
            i2p = id2ppn.Abes_id2ppn(webservice=id2ppn.Webservice.EAN, useJson=True)
            res = i2p.get_matching_ppn(ean)
            thisTry.define_used_query(ean)
            if res.status != id2ppn.Id2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action SRU SUdoc MTI title AUT author EDI publisher APu date TDO v
        if action == Actions.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V:
            sru = ssru.Sudoc_SRU()
            # Extract data
            title = fcf.delete_for_sudoc(self.local_record.utils.get_titles_as_string())
            author = fcf.delete_for_sudoc(self.local_record.utils.get_authors_as_string())
            publisher = fcf.delete_for_sudoc(self.local_record.utils.get_all_publishers_as_string())
            dates, oldest_date, newest_date = self.local_record.utils.get_all_publication_dates()
            # Ensure no data is Empty 
            if title.strip() == "" or author.strip() == "" or publisher.strip() == "" or len(dates) < 1:
                thisTry.error_occured(Match_Records_Errors.REQUIRED_DATA_MISSING)
                return
            # Generate query
            sru_request = [
                ssru.Part_Of_Query(
                    ssru.SRU_Indexes.MTI,
                    ssru.SRU_Relations.EQUALS,
                    title,
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Indexes.AUT,
                    ssru.SRU_Relations.EQUALS,
                    author,
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Indexes.EDI,
                    ssru.SRU_Relations.EQUALS,
                    publisher,
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Filters.APU,
                    ssru.SRU_Relations.SUPERIOR_OR_EQUAL,
                    oldest_date,
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Filters.APU,
                    ssru.SRU_Relations.INFERIOR_OR_EQUAL,
                    newest_date,
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Filters.TDO,
                    ssru.SRU_Relations.EQUALS,
                    ssru.SRU_Filter_TDO.V,
                    ssru.SRU_Boolean_Operators.AND
                )
            ]
            thisTry.define_used_query(sru.generate_query(sru_request))
            res = sru.search(
                thisTry.query,
                record_schema=ssru.SRU_Record_Schemas.UNIMARC,
                record_packing=ssru.SRU_Record_Packings.XML,
                maximum_records=100,
                start_record=1
            )
            if (res.status == "Error"):
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_records_id())
                thisTry.add_returned_records(res.get_records())

        # Action SRU SUdoc MTI title AUT author APu date TDO v
        if action == Actions.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V:
            sru = ssru.Sudoc_SRU()
            # Extract data
            title = fcf.delete_for_sudoc(self.local_record.utils.get_titles_as_string())
            author = fcf.delete_for_sudoc(self.local_record.utils.get_authors_as_string())
            dates, oldest_date, newest_date = self.local_record.utils.get_all_publication_dates()
            # Ensure no data is Empty 
            if title.strip() == "" or author.strip() == "" or len(dates) < 1:
                thisTry.error_occured(Match_Records_Errors.REQUIRED_DATA_MISSING)
                return
            # Generate query
            sru_request = [
                ssru.Part_Of_Query(
                    ssru.SRU_Indexes.MTI,
                    ssru.SRU_Relations.EQUALS,
                    title,
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Indexes.AUT,
                    ssru.SRU_Relations.EQUALS,
                    author,
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Filters.APU,
                    ssru.SRU_Relations.SUPERIOR_OR_EQUAL,
                    oldest_date,
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Filters.APU,
                    ssru.SRU_Relations.INFERIOR_OR_EQUAL,
                    newest_date,
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Filters.TDO,
                    ssru.SRU_Relations.EQUALS,
                    ssru.SRU_Filter_TDO.V,
                    ssru.SRU_Boolean_Operators.AND
                )
            ]
            thisTry.define_used_query(sru.generate_query(sru_request))
            res = sru.search(
                thisTry.query,
                record_schema=ssru.SRU_Record_Schemas.UNIMARC,
                record_packing=ssru.SRU_Record_Packings.XML,
                maximum_records=100,
                start_record=1
            )
            if (res.status == "Error"):
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_records_id())
                thisTry.add_returned_records(res.get_records())

        # Action SRU SUdoc TOU title + author + publisher + date TDO v
        if action == Actions.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V:
            sru = ssru.Sudoc_SRU()
            # Extract data
            title = fcf.delete_for_sudoc(self.local_record.utils.get_titles_as_string())
            author = fcf.delete_for_sudoc(self.local_record.utils.get_authors_as_string())
            publisher = fcf.delete_for_sudoc(self.local_record.utils.get_all_publishers_as_string())
            dates, oldest_date, newest_date = self.local_record.utils.get_all_publication_dates()
            # Ensure no data is Empty 
            if title.strip() == "" or author.strip() == "" or publisher.strip() == "" or len(dates) < 1:
                thisTry.error_occured(Match_Records_Errors.REQUIRED_DATA_MISSING)
                return
            # Generate query
            sru_request = [
                ssru.Part_Of_Query(
                    ssru.SRU_Indexes.TOU,
                    ssru.SRU_Relations.EQUALS,
                    fcf.delete_duplicate_words(" ".join([title, author, publisher])),
                    ssru.SRU_Boolean_Operators.AND
                ),
                f" AND (tou={' or tou='.join([str(num) for num in dates])})",
                ssru.Part_Of_Query(
                    ssru.SRU_Filters.TDO,
                    ssru.SRU_Relations.EQUALS,
                    ssru.SRU_Filter_TDO.V,
                    ssru.SRU_Boolean_Operators.AND
                )
            ]
            thisTry.define_used_query(sru.generate_query(sru_request))
            res = sru.search(
                thisTry.query,
                record_schema=ssru.SRU_Record_Schemas.UNIMARC,
                record_packing=ssru.SRU_Record_Packings.XML,
                maximum_records=100,
                start_record=1
            )
            if (res.status == "Error"):
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_records_id())
                thisTry.add_returned_records(res.get_records())

        # Action SRU SUdoc TOU title + author + date TDO v
        if action == Actions.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V:
            sru = ssru.Sudoc_SRU()
            # Extract data
            title = fcf.delete_for_sudoc(self.local_record.utils.get_titles_as_string())
            author = fcf.delete_for_sudoc(self.local_record.utils.get_authors_as_string())
            dates, oldest_date, newest_date = self.local_record.utils.get_all_publication_dates()
            # Ensure no data is Empty 
            if title.strip() == "" or author.strip() == "" or len(dates) < 1:
                thisTry.error_occured(Match_Records_Errors.REQUIRED_DATA_MISSING)
                return
            # Generate query
            sru_request = [
                ssru.Part_Of_Query(
                    ssru.SRU_Indexes.TOU,
                    ssru.SRU_Relations.EQUALS,
                    fcf.delete_duplicate_words(" ".join([title, author])),
                    ssru.SRU_Boolean_Operators.AND
                ),
                f" AND (tou={' or tou='.join([str(num) for num in dates])})",
                ssru.Part_Of_Query(
                    ssru.SRU_Filters.TDO,
                    ssru.SRU_Relations.EQUALS,
                    ssru.SRU_Filter_TDO.V,
                    ssru.SRU_Boolean_Operators.AND
                )
            ]
            thisTry.define_used_query(sru.generate_query(sru_request))
            res = sru.search(
                thisTry.query,
                record_schema=ssru.SRU_Record_Schemas.UNIMARC,
                record_packing=ssru.SRU_Record_Packings.XML,
                maximum_records=100,
                start_record=1
            )
            if (res.status == "Error"):
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_records_id())
                thisTry.add_returned_records(res.get_records())

# Action SRU SUdoc TOU title + author + publisher + date TDO v
        if action == Actions.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V:
            sru = ssru.Sudoc_SRU()
            # Extract data
            title = fcf.delete_for_sudoc(self.local_record.utils.get_titles_as_string())
            author = fcf.delete_for_sudoc(self.local_record.utils.get_authors_as_string())
            publisher = fcf.delete_for_sudoc(self.local_record.utils.get_all_publishers_as_string())
            # Ensure no data is Empty 
            if title.strip() == "" or author.strip() == "" or publisher.strip() == "":
                thisTry.error_occured(Match_Records_Errors.REQUIRED_DATA_MISSING)
                return
            # Generate query
            sru_request = [
                ssru.Part_Of_Query(
                    ssru.SRU_Indexes.TOU,
                    ssru.SRU_Relations.EQUALS,
                    fcf.delete_duplicate_words(" ".join([title, author, publisher])),
                    ssru.SRU_Boolean_Operators.AND
                ),
                ssru.Part_Of_Query(
                    ssru.SRU_Filters.TDO,
                    ssru.SRU_Relations.EQUALS,
                    ssru.SRU_Filter_TDO.V,
                    ssru.SRU_Boolean_Operators.AND
                )
            ]
            thisTry.define_used_query(sru.generate_query(sru_request))
            res = sru.search(
                thisTry.query,
                record_schema=ssru.SRU_Record_Schemas.UNIMARC,
                record_packing=ssru.SRU_Record_Packings.XML,
                maximum_records=100,
                start_record=1
            )
            if (res.status == "Error"):
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_records_id())
                thisTry.add_returned_records(res.get_records())

        # Action in Koha SRU

# -------------------- UNIVERSAL DATA EXTRACTOR (UDE) --------------------

class Marc_Field(object):
    """Contains the configuration of a field for a data type in the database.
    
    Takes as argument a dict, from Marc_Fields_Data isntances."""
    def __init__(self, data_obj: dict):
        self.tag = data_obj["tag"]
        self.tag_as_int = 99999 #only used to check if control field
        if self.tag.isdigit():
            self.tag_as_int = int(self.tag)
        self.single_line_coded_data = data_obj["single_line_coded_data"]
        self.filtering_subfield = data_obj["filtering_subfield"]
        self.subfields = data_obj["subfields"]
        self.positions = data_obj["positions"]
    
    def as_dict(self) -> dict:
        """Returns this field configuration as a dict."""
        output = {}
        output["tag"] = str(self.tag)
        output["single_line_coded_data"] = self.single_line_coded_data
        output["filtering_subfield"] = self.filtering_subfield
        output["subfields"] = self.subfields
        output["positions"] = self.positions
        return output

class Marc_Fields_Data(object):
    """Contains all the fields configurations for a data type in the database.
    
    Takes as argumetn a dict, coming from the chosen database in marc_fields.json"""
    def __init__(self, data_obj: dict):
        self.label = data_obj["label"]
        self.fields = []
        for field in data_obj["fields"]:
            self.fields.append(Marc_Field(field))
    
    def as_dict(self) -> dict:
        """Return this data type configuration as a dict."""
        output = {}
        output["label"] = self.label
        output["fields"] = []
        for field in self.fields:
            output["fields"].append(field.as_dict())
        return output

class Marc_Fields_Mapping(object):
    """Contains the mapping between every data type and MARC fields for this database.
    
    Takes as argument :
        - es : execution settings
        - is_target_db {bool} : determines if the database is ORIGIN_DATABSE/TARGET_DATABASE
    in marc_fields.json"""
    def __init__(self,  es: Execution_Settings, is_target_db: bool = False):
        """Loads the marc field mapping"""
        self.is_target_db = is_target_db
        self.marc_fields_json = {}
        if self.is_target_db and type(self.is_target_db) == bool:
            self.load_mapping(es, "TARGET_DATABASE")
        elif not self.is_target_db and type(self.is_target_db) == bool:
            self.load_mapping(es, "ORIGIN_DATABASE")
            self.marc_fields_json = es.marc_fields_json["ORIGIN_DATABASE"]
    
    def load_mapping(self, es: Execution_Settings, name: str):
        """Loads a marc field mappig by name from marc_fields.json (debgging)"""
        self.marc_fields_json = es.marc_fields_json[name]
        self.id = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.ID.value])
        self.ppn = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.PPN.value])
        self.ean = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.EAN.value])
        self.general_processing_data_dates = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES.value])
        self.erroneous_isbn = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.ERRONEOUS_ISBN.value])
        self.title = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.TITLE.value])
        self.authors = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.AUTHORS.value])
        self.publishers_name = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.PUBLISHERS_NAME.value])
        self.edition_note = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.EDITION_NOTES.value])
        self.publication_dates = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.PUBLICATION_DATES.value])
        self.contents_notes = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.CONTENTS_NOTES.value])
        self.physical_desription = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.PHYSICAL_DESCRIPTION.value])
        self.other_edition_in_other_medium_bibliographic_id = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.OTHER_ED_IN_OTHER_MEDIUM_BIBG_ID.value])
        self.other_database_id = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.OTHER_DB_ID.value])
        self.items = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.ITEMS.value])
        self.items_barcode = Marc_Fields_Data(self.marc_fields_json[FCR_Mapped_Fields.ITEMS_BARCODE.value])

class Universal_Data_Extractor(object):
    """Central class to extract data from a record.
    
    Takes as argument :
        - the parsed record
        - Databases instance
        - is_target_db {bool} : determines if the database is ORIGIN_DATABSE/TARGET_DATABASE
    in marc_fields.json
        - es : execution settings"""
    def __init__(self, record: ET.ElementTree | dict | pymarc.record.Record, database: Databases, is_target_db: bool, es: Execution_Settings):
        self.record = record
        self.format = Record_Formats.UNKNOWN
        if type(self.record) == ET.Element:
            self.format = Record_Formats.ET_ELEMENT
        elif type(self.record) == dict:
            self.format = Record_Formats.JSON_DICT
        elif type(self.record) == pymarc.record.Record:
            self.format = Record_Formats.PYMARC_RECORD
        self.database = database
        self.xml_namespace = self.get_xml_namespace()
        self.is_target_db = is_target_db
        self.marc_fields_mapping = Marc_Fields_Mapping(es, self.is_target_db)
    
    # --- Resources methods ---

    def get_xml_namespace(self) -> str:
        """Returns the namespace code with a "/" at the beginning and a ":" at the end"""
        if self.database == Databases.KOHA_PUBLIC_BIBLIO:
            return "/" + Xml_Namespaces.MARC.value + ":"
        elif self.database == Databases.KOHA_SRU:
            return "/" + Xml_Namespaces.MARC.value + ":"
        else:
            return ""

    def extract_data_from_marc_field(self, mapped_field_data: Marc_Fields_Data, filter_value: Optional[str] = "") -> List[List[Union[str, List[str]]]]:
        """Mother function of all get_DATA (except leader).
        
        Returns a list of list of string (add another layer of list if the field was coded data with positions)"""
        marc_fields: List[Marc_Field] = mapped_field_data.fields
        if self.format == Record_Formats.ET_ELEMENT:
            return self.extract_data_from_marc_field_XML(marc_fields, filter_value)
        if self.format == Record_Formats.JSON_DICT:
            return self.extract_data_from_marc_field_JSON(marc_fields, filter_value)
        if self.format == Record_Formats.PYMARC_RECORD:
            return self.extract_data_from_marc_field_PYMARC(marc_fields, filter_value)

    def extract_data_from_marc_field_XML(self, marc_fields: List[Marc_Field], filter_value: Optional[str] = "") -> List[List[Union[str, List[str]]]]:
        """Gets data from XML record"""
        output: List[List[Union[str, List[str]]]] = []
        for marc_field in marc_fields:
            # Control fields
            if marc_field.tag_as_int < 10:
                for field in self.record.findall(f"./{self.xml_namespace}controlfield[@tag='{marc_field.tag}']", XML_NS):
                    output.append([field.text])
            # Datafields
            else:
                # Gets the field to analyze
                list_of_fields: List[ET.Element] = []
                for field in self.record.findall(f"./{self.xml_namespace}datafield[@tag='{marc_field.tag}']", XML_NS):
                    # If filtering subfield, exclude this field if not correct
                    if marc_field.filtering_subfield:
                        for subfield in field.findall(f"./{self.xml_namespace}subfield[@code='{marc_field.filtering_subfield}']", XML_NS):
                            if subfield.text.startswith(filter_value):
                                list_of_fields.append(field)
                    else:
                        list_of_fields.append(field)

                # For each field to analyze
                for field in list_of_fields:
                    # Retrieves all the subfield mapped
                    subfields_values: List[str] = []
                    # If specific subfields were mapped
                    for marc_subfield in marc_field.subfields:
                        for subfield in field.findall(f"./{self.xml_namespace}subfield[@code='{marc_subfield}']", XML_NS):
                            subfields_values.append(subfield.text)
                    # If no specific subfield was mapped
                    if len(marc_field.subfields) == 0:
                        for subfield in field.findall(f"./{self.xml_namespace}subfield", XML_NS):
                            subfields_values.append(subfield.text)
                    # If coded data, retrieve only asked position
                    output.append(self.extract_subfield_values(subfields_values, marc_field))
        return output

    def extract_data_from_marc_field_JSON(self, marc_fields: List[Marc_Field], filter_value: Optional[str] = None) -> List[List[Union[str, List[str]]]]:
        """Gets data from JSON record"""
        output: List[List[Union[str, List[str]]]] = []
        for marc_field in marc_fields:
            # Control fields
            if marc_field.tag_as_int < 10:
                for field in self.record["fields"]:
                    if marc_field.tag in field.keys():
                        output.append([field[marc_field.tag]])
            # Datafields
            else:
                # Gets the field to analyze
                list_of_fields: List[dict] = [] # The dict is the one after the tag {"035":{THIS_ONE}}
                for field in self.record["fields"]:
                    if marc_field.tag in field.keys():
                        # If filtering subfield, exclude this field if not correct
                        if marc_field.filtering_subfield:
                            for subfield in field[marc_field.tag]["subfields"]:
                                if list(subfield.keys())[0] == marc_field.filtering_subfield:
                                    if subfield[marc_field.filtering_subfield].startswith(filter_value):
                                        list_of_fields.append(field[marc_field.tag])
                        else:
                            list_of_fields.append(field[marc_field.tag])
                    
                # For each field to analyze
                for field in list_of_fields:
                    # Retrieves all the subfield mapped
                    subfields_values: List[str] = []
                    for subfield in field["subfields"]:
                        # If specific subfields were mapped
                        if list(subfield.keys())[0] in marc_field.subfields:
                            subfields_values.append(subfield[list(subfield.keys())[0]])
                        # If no specific subfield was mapped
                        elif len(marc_field.subfields) == 0:
                            subfields_values.append(subfield[list(subfield.keys())[0]])
                    # If coded data, retrieve only asked position
                    output.append(self.extract_subfield_values(subfields_values, marc_field))
        return output

    def extract_data_from_marc_field_PYMARC(self, marc_fields: List[Marc_Field], filter_value: Optional[str] = "") -> List[List[Union[str, List[str]]]]:
        """Gets data from PYMARC record"""
        output: List[List[Union[str, List[str]]]] = []
        for marc_field in marc_fields:
            # Control fields
            if marc_field.tag_as_int < 10:
                for field in self.record.get_fields(marc_field.tag):
                    output.append([field.data])
            # Datafields
            else:
                # Gets the field to analyze
                list_of_fields: List[pymarc.field.Field] = []
                for field in self.record.get_fields(marc_field.tag):
                    # If filtering subfield, exclude this field if not correct
                    if marc_field.filtering_subfield:
                        for subfield_value in field.get_subfields(marc_field.filtering_subfield):
                            if subfield_value.startswith(filter_value):
                                list_of_fields.append(field)
                    else:
                        list_of_fields.append(field)
                    
                # For each field to analyze
                for field in list_of_fields:
                    # Retrieves all the subfield mapped
                    subfields_values: List[str] = []
                    # If specific subfields were mapped
                    if len(marc_field.subfields) > 0:
                        # The * unpack the list
                        subfields_values = field.get_subfields(*marc_field.subfields)
                    # If no specific subfield was mapped
                    elif len(marc_field.subfields) == 0:
                        for index, subfield_value in enumerate(field.subfields):
                            # field.subfields return a list with even index = code, odd index = val
                            if index % 2 == 1:
                                subfields_values.append(subfield_value)
                    # If coded data, retrieve only asked position
                    output.append(self.extract_subfield_values(subfields_values, marc_field))
        return output

    # --- Resource methods for the resource methods ---

    def extract_subfield_values(self, values: List[str], marc_field: Marc_Field) -> List[str]:
        """Returns a list of srtings of the ubfield values, only with positions if needed"""
        output = []
        for subfield_value in values:
            # If coded data, retrieve only asked position
            if marc_field.single_line_coded_data and len(marc_field.positions) > 0:
                output.append(self.extract_positions_from_coded_data(subfield_value, marc_field.positions))
            else:
                output.append(subfield_value)
        return output

    def extract_positions_from_coded_data(self, field_text: str, positions: List[str]) -> List[str]:
        """Returns a lsit of string of the asked positions.
        If any problem was too occured, skips"""
        output: List[str] = []
        for position in positions:
            # single character
            if not "-" in position and position.isdigit():
                pos = int(position)
                if pos < len(field_text):
                    output.append(field_text[pos])
            # Range
            else:
                regex_matched = re.search(r"^(\d+)-(\d+)$", position)
                if regex_matched:
                    begining = int(regex_matched.group(1))
                    end = int(regex_matched.group(2)) + 1
                    # End must be > begin and can be equal to the len
                    if begining < len(field_text) and end <= len(field_text) and begining < end:
                        output.append(field_text[begining:end])
        return output

    # --- Get targetted data ---
    def get_by_mapped_field_name(self, mapped_field: FCR_Mapped_Fields, filter_value: Optional[str] = ""):
        """Calls the correct get function based on FCR_Mapped_Fields"""
        if mapped_field == FCR_Mapped_Fields.LEADER:
            return self.get_leader()
        elif mapped_field == FCR_Mapped_Fields.ID:
            return self.get_id(filter_value)
        elif mapped_field == FCR_Mapped_Fields.PPN:
            return self.get_ppn(filter_value)
        elif mapped_field == FCR_Mapped_Fields.EAN:
            return self.get_ean(filter_value)
        elif mapped_field == FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES:
            return self.get_general_processing_data_dates(filter_value)
        elif mapped_field == FCR_Mapped_Fields.ERRONEOUS_ISBN:
            return self.get_erroneous_ISBN(filter_value)
        elif mapped_field == FCR_Mapped_Fields.TITLE:
            return self.get_title(filter_value)
        elif mapped_field == FCR_Mapped_Fields.AUTHORS:
            return self.get_authors(filter_value)
        elif mapped_field == FCR_Mapped_Fields.PUBLISHERS_NAME:
            return self.get_publishers_name(filter_value)
        elif mapped_field == FCR_Mapped_Fields.EDITION_NOTES:
            return self.get_edition_notes(filter_value)
        elif mapped_field == FCR_Mapped_Fields.PUBLICATION_DATES:
            return self.get_publication_dates(filter_value)
        elif mapped_field == FCR_Mapped_Fields.PHYSICAL_DESCRIPTION:
            return self.get_physical_description(filter_value)    
        elif mapped_field == FCR_Mapped_Fields.CONTENTS_NOTES:
            return self.get_contents_notes(filter_value)
        elif mapped_field == FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES:
            return self.get_general_processing_data_dates(filter_value)
        elif mapped_field == FCR_Mapped_Fields.OTHER_ED_IN_OTHER_MEDIUM_BIBG_ID:
            return self.get_other_edition_in_other_medium_bibliographic_id(filter_value)
        elif mapped_field == FCR_Mapped_Fields.OTHER_DB_ID:
            return self.get_other_database_id(filter_value)
        elif mapped_field == FCR_Mapped_Fields.ITEMS:
            return self.get_items(filter_value)
        elif mapped_field == FCR_Mapped_Fields.ITEMS_BARCODE:
            return self.get_items_barcode(filter_value)

    def get_leader(self) -> List[str]:
        """Return the leader field content as a list of string"""
        # List so we avoid crash with the formats who don't display the leader
        output = []
        if self.format == Record_Formats.ET_ELEMENT:
            for field in self.record.findall(f"./{self.xml_namespace}leader", XML_NS):
                output.append(field.text)
        elif self.format == Record_Formats.JSON_DICT:
            output.append(self.record["leader"])
        elif self.format == Record_Formats.PYMARC_RECORD:
            output.append(self.record.leader)
        return output
    
    def get_id(self, filter_value: Optional[str] = "") -> List[str]:
        """Return the ID as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.id, filter_value)

    def get_other_database_id(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all other database id as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.other_database_id, filter_value)

    def get_title(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as title as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.title, filter_value)

    def get_authors(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as authors as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.authors, filter_value)

    def get_general_processing_data_dates(self, filter_value: Optional[str] = "") -> List[List[str]]:
        """Return all publication dates from the general processign data as a list (usually of list containing :
            - Type of date
            - Date 1
            - Date 2)

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_lists(self.marc_fields_mapping.general_processing_data_dates, filter_value)

    def get_publishers_name(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as publisher names as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.publishers_name, filter_value)
        # return self.extract_list_of_strings(self.marc_fields_mapping.publishers_name, filter_value)
    
    def get_ppn(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all PPN as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.ppn, filter_value)

    def get_ean(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all EAN as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.ean, filter_value)

    def get_edition_notes(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as edition notes as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.edition_note, filter_value)

    def get_publication_dates(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as publication dates as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.publication_dates, filter_value)

    def get_physical_description(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as physical descriptions as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.physical_desription, filter_value)
    
    def get_contents_notes(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as contents notes as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.contents_notes, filter_value)

    def get_erroneous_ISBN(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all erroneous ISBN as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.erroneous_isbn, filter_value)

    def get_other_edition_in_other_medium_bibliographic_id(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all of other edition in other medium bibliographic id as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.other_edition_in_other_medium_bibliographic_id, filter_value)

    def get_items_barcode(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all items barcode as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.items_barcode, filter_value)

    def get_items(self, filter_value: Optional[str] = "") -> List[List[str]]:
        """Return all publication dates from the general processign data as a list (usually of list containing :
            - Type of date
            - Date 1
            - Date 2)

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_data_from_marc_field(self.marc_fields_mapping.items, filter_value)
        # return self.extract_list_of_lists(self.marc_fields_mapping.items, filter_value)

    # --- Resources methods to get targetted data ---
    def flatten_list(self, thisList: list, all_layers: bool) -> list:
        """Returns the lsit flattened, only one layer if all_layers is False."""
        if all_layers:
            result = []
            for item in thisList:
                if isinstance(item, list):
                    result.extend(self.flatten_list(item, True))
                else:
                    result.append(item)
            return result
        else:
            return [item for sublist in thisList for item in sublist]
    
    def extract_list_of_ids(self,marc_field: Marc_Fields_Data, filter_value: Optional[str] = "") -> List[str]:
        """Generic funciton to get a list of ID without duplicates"""
        output = []
        extraction = self.extract_data_from_marc_field(marc_field, filter_value)
        output = self.flatten_list(extraction, True)
        return list(set(output))

    def extract_list_of_strings(self,marc_field: Marc_Fields_Data, filter_value: Optional[str] = "") -> List[str]:
        """Generic funciton to get a list of strings merging subfields if needed (with duplicates)"""
        output = []
        extraction = self.extract_data_from_marc_field(marc_field, filter_value)
        for field_value in extraction:
            output.append(" ".join(field_value))
        return output
    
    def extract_list_of_lists(self,marc_field: Marc_Fields_Data, filter_value: Optional[str] = "") -> List[str]:
        """Generic funciton to get a list, merging only one layer, so, supposedly, a list of list"""
        output = []
        extraction = self.extract_data_from_marc_field(marc_field, filter_value)
        output = self.flatten_list(extraction, False)
        return output

# -------------------- MAIN --------------------

class Original_Record(object):
    def __init__(self, line: dict, es:Execution_Settings):
        self.reset_error()
        self.original_line = line
        self.es = es
        self.target_database_data = {}
        self.output = self.Output(self)
    
    def extract_from_original_line(self, headers: List[str]):
        """Extract the first column of the file as the input query and
        the last column as the original UID regardless of the headers name"""
        self.input_query = self.original_line[headers[0]]
        self.original_uid = self.original_line[headers[len(self.original_line)-1]].rstrip()
    
    def get_matched_records_instance(self, mr: Matched_Records):
        """Extract data from the matched_records result."""
        self.matched_record_instance = mr
        self.query_used = mr.query
        self.nb_matched_records = len(mr.returned_ids)
        self.matched_records_ids = mr.returned_ids
        self.matched_records = mr.returned_records
        self.matched_records_include_records = mr.includes_record
    
    def get_origin_database_data(self, processing: FCR_Processings, record: ET.ElementTree | dict | pymarc.record.Record, database: Databases, es: Execution_Settings):
        """Extract data from the origin database record"""
        self.origin_database_data = Database_Record(processing, record, database, False, es)

    def get_target_database_data(self, processing: FCR_Processings, id:str, record: ET.ElementTree | dict | pymarc.record.Record, database: Databases, es: Execution_Settings):
        """Extract data from the origin database record"""
        self.target_database_data[id] = Database_Record(processing, record, database, True, es)

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

    # --- Output methods for other classes / functions ---
    class Output:
        def __init__(self, parent) -> None:
            self.parent = parent

        def to_retro_CSV(self) -> dict:
            """Returns data as the dict for the old output method"""
            par:Original_Record = self.parent
            out = {}
            try:
                # Errors
                out["ERROR"] = par.error
                out["ERROR_MSG"] = par.error_message

                # Data from the original file
                out.update(par.original_line)
                out["INPUT_QUERY"] = par.input_query
                out["INPUT_KOHA_BIB_NB"] = par.original_uid

                # Koha record
                out['KOHA_BIB_NB'] = par.origin_database_data.utils.get_id()
                temp = par.origin_database_data.data[FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]
                out['KOHA_DATE_1'] = temp[0][0]
                out['KOHA_DATE_2'] = temp[0][1]
                out['KOHA_214210c'] = par.origin_database_data.data[FCR_Mapped_Fields.PUBLISHERS_NAME]
                out['KOHA_200adehiv'] = par.origin_database_data.utils.get_first_title_as_string()
                out['KOHA_305'] = fcf.list_as_string(par.origin_database_data.data[FCR_Mapped_Fields.EDITION_NOTES])
                out["KOHA_PPN"] = fcf.list_as_string(par.origin_database_data.data[FCR_Mapped_Fields.PPN])
                out["KOHA_214210a_DATES"] = []
                for date_str in par.origin_database_data.data[FCR_Mapped_Fields.PUBLICATION_DATES]:
                    out["KOHA_214210a_DATES"] += fcf.get_year(date_str)
                out["KOHA_214210a_DATES"] = fcf.list_as_string(out["KOHA_214210a_DATES"])
                out["KOHA_215a_DATES"] = []
                out['KOHA_010z'] = None
                # Better_ITEM specifics
                if par.es.processing_val == FCR_Processings.BETTER_ITEM.name:
                    out['KOHA_010z'] = fcf.list_as_string(par.origin_database_data.data[FCR_Mapped_Fields.ERRONEOUS_ISBN])
                    for desc_str in par.origin_database_data.data[FCR_Mapped_Fields.PHYSICAL_DESCRIPTION]: #AR259
                        out["KOHA_215a_DATES"] += fcf.get_year(desc_str)
                # Better_ITEM DVD specifics
                if par.es.processing_val == FCR_Processings.BETTER_ITEM_DVD.name:
                    out["KOHA_215a_DATES"] = par.origin_database_data.data[FCR_Mapped_Fields.PHYSICAL_DESCRIPTION]
                out["KOHA_215a_DATES"] = fcf.list_as_string(out["KOHA_215a_DATES"])

                # Match records
                out["MATCH_RECORDS_QUERY"] = par.query_used
                out["MATCH_RECORDS_NB_RES"] = par.nb_matched_records
                out["MATCH_RECORDS_RES"] = par.matched_records_ids

                # Matched record
                out["MATCHED_ID"] = par.matched_id

                # Sudoc record
                temp_rec:Database_Record = par.target_database_data[par.matched_id]
                temp_rec_data = temp_rec.data
                temp = temp_rec_data[FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]
                if len(temp) < 1:
                    out['SUDOC_DATE_1'] = None    
                    out['SUDOC_DATE_2'] = None
                else:
                    out['SUDOC_DATE_1'] = temp[0][0]
                    out['SUDOC_DATE_2'] = temp[0][1]
                out['SUDOC_214210c'] = temp_rec_data[FCR_Mapped_Fields.PUBLISHERS_NAME]
                out['SUDOC_200adehiv'] = temp_rec.utils.get_first_title_as_string()
                out['SUDOC_305'] = fcf.list_as_string(temp_rec_data[FCR_Mapped_Fields.EDITION_NOTES])
                out["SUDOC_LOCAL_SYSTEM_NB"] = temp_rec_data[FCR_Mapped_Fields.OTHER_DB_ID]
                # sudoc_record.get_local_system_nb(es.iln)
                out["SUDOC_NB_LOCAL_SYSTEM_NB"] = len(out["SUDOC_LOCAL_SYSTEM_NB"])
                out["SUDOC_LOCAL_SYSTEM_NB"] = fcf.list_as_string(out["SUDOC_LOCAL_SYSTEM_NB"])
                out["SUDOC_ITEMS"] = temp_rec_data[FCR_Mapped_Fields.ITEMS]
                # sudoc_record.get_library_items(es.rcr)
                out["SUDOC_HAS_ITEMS"] = len(out["SUDOC_ITEMS"]) > 0
                if out["SUDOC_NB_LOCAL_SYSTEM_NB"] > 0:
                    out["SUDOC_DIFFERENT_LOCAL_SYSTEM_NB"] = not par.origin_database_data.utils.get_id() in out["SUDOC_LOCAL_SYSTEM_NB"]
                out["SUDOC_ITEMS"] = fcf.list_as_string(out["SUDOC_ITEMS"])
                out['SUDOC_010z'] = None
                # Better_ITEM specifics
                if par.es.processing_val == FCR_Processings.BETTER_ITEM.name:
                    out['SUDOC_010z'] = fcf.list_as_string(temp_rec_data[FCR_Mapped_Fields.ERRONEOUS_ISBN])

                # Analysis
                target_record:Database_Record = par.target_database_data[par.matched_id] # for the IDE
                # Title
                out['MATCHING_TITRE_SIMILARITE'] = temp_rec.title_ratio
                out['MATCHING_TITRE_APPARTENANCE'] = temp_rec.title_partial_ratio
                out['MATCHING_TITRE_INVERSION'] = temp_rec.title_token_sort_ratio
                out['MATCHING_TITRE_INVERSION_APPARTENANCE'] = temp_rec.title_token_set_ratio
                # Dates
                out['MATCHING_DATE_PUB'] = target_record.dates_matched
                # Publishers
                out['MATCHING_EDITEUR_SIMILARITE'] = target_record.publishers_score
                out['SUDOC_CHOSEN_ED'] = target_record.chosen_publisher
                out['KOHA_CHOSEN_ED'] = target_record.chosen_compared_publisher
                # Ids
                out["SUDOC_LOCAL_SYSTEM_NB"] = target_record.list_of_other_db_id
                out["SUDOC_NB_LOCAL_SYSTEM_NB"] = target_record.nb_other_db_id
                out["SUDOC_DIFFERENT_LOCAL_SYSTEM_NB"] = target_record.local_id_in_compared_record.name
                # pretty sure I don't need to do that here anymore but eh, this is just for retro output so who cares
                out['KOHA_214210c'] = fcf.list_as_string(out['KOHA_214210c'])
                out['SUDOC_214210c'] = fcf.list_as_string(out['SUDOC_214210c'])
                # Global validation
                out["FINAL_OK"] = target_record.total_checks.name
                out["NB_OK_CHECKS"] = target_record.passed_check_nb
                out["TITLE_OK"] = target_record.checks[Analysis_Checks.TITLE]
                out["PUBLISHER_OK"] = target_record.checks[Analysis_Checks.PUBLISHER]
                out["DATE_OK"] = target_record.checks[Analysis_Checks.DATE]  
                return out
            except:
                return out

class Report(object):
    def __init__(self):
        self.processed = 0
        self.errors = {}
        for error in Errors:
            self.errors[error.value] = 0
        self.success = {}
        for succ in Success:
            self.success[succ.value] = 0

    def increase_processed(self):
        self.processed += 1
    
    def increase_success(self, step: Success):
        self.success[step.value] += 1
    
    def increase_fail(self, err: Errors):
        self.errors[err.value] += 1