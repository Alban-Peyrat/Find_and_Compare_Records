# -*- coding: utf-8 -*- 

# External import
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler
import json
import pymarc
import csv
from enum import Enum
from typing import List, Dict

# Internal imports
from cl_PODA import Processing_Names, Processing_Data_Target, Mapped_Fields, get_PODA_instance

# --------------- Enums ---------------
class Log_Level(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

class Analysis_Checks(Enum):
    TITLE = 0
    PUBLISHER = 1
    DATE = 2

class CSV_Cols(Enum):
    INPUT_QUERY = 1000
    ORIGIN_DB_INPUT_ID = 2000
    ERROR = 3000
    ERROR_MSG = 3010
    GLOBAL_VALIDATION_RESULT = 4000
    GLOBAL_VALIDATION_NB_SUCCESSFUL_CHECKS = 4010
    GLOBAL_VALIDATION_TITLE_CHECK = 4020
    GLOBAL_VALIDATION_PUBLISHER_CHECK = 4030
    GLOBAL_VALIDATION_DATE_CHECK = 4040
    MATCH_RECORDS_QUERY = 5000
    FCR_ACTION_USED = 5005
    MATCH_RECORDS_NB_RESULTS = 5010
    # MATCH_RECORDS_RESULTS = 5020
    # ORIGIN_DB_ID = 6000
    # TARGET_DB_ID = 6001
    # MATCHED_ID = 7000
    OLD_SLOT_3 = 6000
    OLD_SLOT_4 = 7000
    ORIGIN_DB_PPN = 7100
    TARGET_DB_PPN = 7101
    ORIGIN_DB_ISBN = 7200
    TARGET_DB_ISBN = 7201
    ORIGIN_DB_OTHER_DB_ID = 7900
    TARGET_DB_OTHER_DB_ID = 7901
    TARGET_DB_NB_OTHER_ID = 8000
    IS_ORIGIN_ID_IN_TARGET_OTHER_DB_IDS = 8010
    ORIGIN_DB_ITEMS = 9000
    TARGET_DB_ITEMS = 9001
    TARGET_DB_HAS_ITEMS = 9100
    ORIGIN_DB_ITEMS_BARCODE = 9200
    TARGET_DB_ITEMS_BARCODE = 9201
    ORIGIN_DB_ERRONEOUS_ISBN = 10000
    TARGET_DB_ERRONEOUS_ISBN = 10001
    ORIGIN_DB_DOCUMENT_TYPE = 10300
    TARGET_DB_DOCUMENT_TYPE = 10301
    ORIGIN_DB_AUTHORS = 10600
    TARGET_DB_AUTHORS = 10601
    ORIGIN_DB_TITLE = 11000
    TARGET_DB_TITLE = 11001
    ORIGIN_DB_TITLE_KEY = 11010
    TARGET_DB_TITLE_KEY = 11011
    ORIGIN_DB_PUBLISHERS_NAME = 12000
    TARGET_DB_PUBLISHERS_NAME = 12001
    ORIGIN_DB_CHOSEN_PUBLISHER = 12010
    TARGET_DB_CHOSEN_PUBLISHER = 12011
    ORIGIN_DB_GENERAL_PROCESSING_DATA_DATES = 13000
    TARGET_DB_GENERAL_PROCESSING_DATA_DATES = 13001
    ORIGIN_DB_DATE_1 = 13200
    TARGET_DB_DATE_1 = 13201
    ORIGIN_DB_DATE_2 = 13250
    TARGET_DB_DATE_2 = 13251
    ORIGIN_DB_EDITION_NOTES = 14000
    TARGET_DB_EDITION_NOTES = 14001
    ORIGIN_DB_PUBLICATION_DATES = 15000
    TARGET_DB_PUBLICATION_DATES = 15001
    ORIGIN_DB_PHYSICAL_DESCRIPTION = 16000
    TARGET_DB_PHYSICAL_DESCRIPTION = 16001
    ORIGIN_DB_CONTENTS_NOTES = 17000
    TARGET_DB_CONTENTS_NOTES = 17001
    ORIGIN_DB_OTHER_ED_IN_OTHER_MEDIUM_BIBG_ID = 18000
    TARGET_DB_OTHER_ED_IN_OTHER_MEDIUM_BIBG_ID = 18001
    ORIGIN_DB_EAN = 19000
    TARGET_DB_EAN = 19001
    OLD_SLOT_1 = 20000
    ORIGIN_DB_LEADER = 21000
    TARGET_DB_LEADER = 21001
    ORIGIN_DB_EXPORTED_TO_DIGITAL_LIBRARY = 22000
    TARGET_DB_EXPORTED_TO_DIGITAL_LIBRARY = 22001
    ORIGIN_DB_MAPS_HORIZONTAL_SCALE = 23000
    TARGET_DB_MAPS_HORIZONTAL_SCALE = 23001
    ORIGIN_DB_MAPS_MATHEMATICAL_DATA = 23100
    TARGET_DB_MAPS_MATHEMATICAL_DATA = 23101
    ORIGIN_DB_SERIES = 24000
    TARGET_DB_SERIES = 24001
    ORIGIN_DB_SERIES_LINK = 24100
    TARGET_DB_SERIES_LINK = 24101
    RESERVED_SLOT4 = 25000
    ORIGIN_DB_GEOGRAPHICAL_SUBJECT = 25600
    TARGET_DB_GEOGRAPHICAL_SUBJECT = 25601
    ORIGIN_DB_LINKING_PIECE = 26000
    TARGET_DB_LINKING_PIECE = 26001
    OLD_SLOT_2 = 27000
    RESERVED_SLOT7 = 28000
    RESERVED_SLOT8 = 29000
    # 80XXX are reserved
    MATCHING_TITLE_RATIO = 80000
    MATCHING_TITLE_PARTIAL_RATIO = 80010
    MATCHING_TITLE_TOKEN_SORT_RATIO = 80020
    MATCHING_TITLE_TOKEN_SET_RATIO = 80030
    MATCHING_PUBLISHER_RESULT = 80100
    MATCHING_DATES_RESULT = 80200
    # 
    FCR_PROCESSED_ID = 98000
    MATCH_RECORDS_RESULTS = 98100
    ORIGIN_DB_ID = 98400
    TARGET_DB_ID = 98401
    MATCHED_ID = 98700
    # 99XXX are for original file


# --------------- Classes ---------------
class Records_Settings(object):
    def __init__(self, rcr:str, iln: str, filter1:str, filter2:str, filter3:str, chosen_analysis:int, chosen_analysis_checks:dict, origin_db_marc_fields_json:dict, target_db_marc_fields_json:dict) -> None:
        self.rcr = rcr
        self.iln = iln
        self.filter1 = filter1
        self.filter2 = filter2
        self.filter3 = filter3
        self.chosen_analysis = chosen_analysis
        self.chosen_analysis_checks = chosen_analysis_checks
        self.origin_db_marc_fields_json = origin_db_marc_fields_json
        self.target_db_marc_fields_json = target_db_marc_fields_json

class Execution_Settings(object):
    def __init__(self, dir: str):
        # Load analysis settings
        with open(dir + "/json_configs/analysis.json", "r+", encoding="utf-8") as f:
            self.analysis_json = json.load(f)

        # Load marc fields
        with open(dir + "/json_configs/marc_fields.json", "r+", encoding="utf-8") as f:
            self.marc_fields_json = json.load(f)
        
        # Set up subclasses
        self.csv = self.CSV(self)
    
    def load_env_values(self):
        load_dotenv()
        # General
        self.lang = os.getenv("SERVICE")
        if self.lang not in ["eng", "fre"]:
            self.lang = "eng"
        self.service = os.getenv("SERVICE")
        self.file_path = os.getenv("FILE_PATH")
        self.output_path = os.getenv("OUTPUT_PATH")
        self.csv_cols_config_path = os.getenv("CSV_OUTPUT_JSON_CONFIG_PATH")
        self.logs_path = os.getenv("LOGS_PATH")
        self.log_level = os.getenv("LOG_LEVEL")
        # Processing & operations
        self.change_processing(os.getenv("PROCESSING_VAL"))
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
    
    # ----- Methods to pass some properties -----
    def get_records_settings(self) -> Records_Settings:
        return Records_Settings(
            rcr=self.rcr,
            iln=self.iln,
            filter1=self.filter1,
            filter2=self.filter2,
            filter3=self.filter3,
            chosen_analysis=self.chosen_analysis,
            chosen_analysis_checks=self.chosen_analysis_checks,
            origin_db_marc_fields_json=self.marc_fields_json[self.origin_database_mapping],
            target_db_marc_fields_json=self.marc_fields_json[self.target_database_mapping]
        )

    # ----- Methods for main -----
    def generate_files_path(self):
        self.file_path_out_results = self.output_path + "/results_report"
        self.file_path_out_json = self.output_path + "/results.json"
        self.file_path_out_csv = self.output_path + "/results.csv"
    
    def change_processing(self, processing: Processing_Names|str|int):
        """Updates the current dataabse mapping.
        Takes as argument the processing as a Processing_Nmaes member, the member name or the memeber value"""
        self.processing = get_PODA_instance(processing, Processing_Names)

    def get_operation(self):
        self.operation = self.processing.operation

    def define_chosen_analysis(self, nb: int):
        self.chosen_analysis = self.analysis_json[nb]
        self.chosen_analysis_checks = {}
        if self.chosen_analysis["TITLE_MIN_SCORE"] > 0:
            self.chosen_analysis_checks[Analysis_Checks.TITLE] = None
        if self.chosen_analysis["PUBLISHER_MIN_SCORE"] > 0:
            self.chosen_analysis_checks[Analysis_Checks.PUBLISHER] = None
        if self.chosen_analysis["USE_DATE"]:
            self.chosen_analysis_checks[Analysis_Checks.DATE] = None
    
    def load_original_file_data(self):
        self.original_file_data = {}
        # CSV handling
        if self.processing.enum_member in [
                Processing_Names.BETTER_ITEM,
                Processing_Names.BETTER_ITEM_DVD,
                Processing_Names.BETTER_ITEM_NO_ISBN,
                Processing_Names.BETTER_ITEM_MAPS
            ]:
            with open(self.file_path, 'r', newline="", encoding="utf-8") as fh:
                csvdata = csv.DictReader(fh, delimiter=";")
                self.original_file_headers = csvdata.fieldnames
                for index, line in enumerate(csvdata):
                    self.original_file_data[index] = line
        # MARC handling
        elif self.processing.enum_member == Processing_Names.MARC_FILE_IN_KOHA_SRU:
            self.original_file_headers = []
            with open(self.file_path, 'rb') as fh:
                marcreader = pymarc.MARCReader(fh, to_unicode=True, force_utf8=True)
                for index, record in enumerate(marcreader):
                    self.original_file_data[index] = record

    # ----- Methods for UI -----
    def UI_get_log_levels(self) -> List[str]:
        """Returns log levels as a list of str"""
        return [lvl.name for lvl in Log_Level]
    
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

    def UI_update_main_screen_values(self, val:dict):
        """Updates all data from the UI inside this instance"""
        self.service = val["SERVICE"]
        self.log_level = val["LOG_LEVEL"]
        self.file_path = val["FILE_PATH"]
        self.output_path = val["OUTPUT_PATH"]
        self.csv_cols_config_path = val["CSV_OUTPUT_JSON_CONFIG_PATH"]
        self.logs_path = val["LOGS_PATH"]
        self.change_processing(val["PROCESSING_VAL"])
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
    
    # --- Logger methods for other classes / functions ---
    def init_logger(self):
        """Init the logger"""
        self.log = self.Logger(self)

    class Logger(object):
        def __init__(self, parent) -> None:
            self.parent:Execution_Settings = parent
            par = self.parent
            self.__init_logs(par.logs_path, par.service, par.log_level)
            self.logger = logging.getLogger(par.service)

        def __init_logs(self, logsrep,programme,niveau):
            # logs.py by @louxfaure, check file for more comments
            # D'aprés http://sametmax.com/ecrire-des-logs-en-python/
            logsfile = logsrep + "/" + programme + ".log"
            logger = logging.getLogger(programme)
            logger.setLevel(getattr(logging, niveau))
            # Formatter
            formatter = logging.Formatter(u'%(asctime)s :: %(levelname)s :: %(message)s')
            file_handler = RotatingFileHandler(logsfile, 'a', 10000000, 1, encoding="utf-8")
            file_handler.setLevel(getattr(logging, niveau))
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            # For console
            stream_handler = logging.StreamHandler()
            stream_handler.setLevel(getattr(logging, niveau))
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)

            logger.info('Logger initialised')

        def critical(self, msg:str):
            """Basic log critical function"""
            self.logger.critical(f"{msg}")

        def debug(self, msg:str):
            """Log a debug statement logging first the service then the message"""
            self.logger.debug(f"{self.parent.service} :: {msg}")

        def info(self, msg:str):
            """Basic log info function"""
            self.logger.info(f"{msg}")

        def simple_info(self, msg:str, data):
            """Log an info statement separating msg and data by :"""
            self.logger.info(f"{msg} : {data}")

        def big_info(self, msg:str):
            """Logs a info statement encapsuled between ----"""
            self.logger.info(f"--------------- {msg} ---------------")

        def error(self, msg:str):
            """Log a error statement logging first the service then the message"""
            self.logger.error(f"{self.parent.service} :: {msg}")

    # --- CSV methods for other classes / functions ---
    class CSV(object):
        def __init__(self, parent) -> None:
            self.parent:Execution_Settings = parent
        
        def create_file(self, original_file_cols:List[str]):
            """Create the CSV file and the DictWriter.
            
            Takes as argument the list of columns from the original file"""
            self.file_path = self.parent.file_path_out_csv
            self.file = open(self.file_path, "w", newline="", encoding='utf-8')
            with open(self.parent.csv_cols_config_path, "r+", encoding="utf-8") as f:
                self.csv_cols = json.load(f)
            self.__define_headers(original_file_cols)
            self.writer = csv.DictWriter(self.file, extrasaction="ignore", fieldnames=self.headers_ordered, delimiter=";")
            self.writer.writerow(self.headers)

        def __define_headers(self, original_file_cols:List[str]):
            """Defines the headers for the CSV file"""
            self.headers = {}
            par:Execution_Settings = self.parent
            # Common columns     
            for col in [
                    CSV_Cols.ERROR,
                    CSV_Cols.ERROR_MSG,
                    CSV_Cols.INPUT_QUERY,
                    CSV_Cols.ORIGIN_DB_INPUT_ID,
                    CSV_Cols.MATCH_RECORDS_QUERY,
                    CSV_Cols.FCR_ACTION_USED,
                    CSV_Cols.MATCH_RECORDS_NB_RESULTS,
                    CSV_Cols.MATCH_RECORDS_RESULTS,
                    CSV_Cols.MATCHED_ID,
                    CSV_Cols.MATCHING_TITLE_RATIO,
                    CSV_Cols.MATCHING_TITLE_PARTIAL_RATIO,
                    CSV_Cols.MATCHING_TITLE_TOKEN_SORT_RATIO,
                    CSV_Cols.MATCHING_TITLE_TOKEN_SET_RATIO,
                    CSV_Cols.MATCHING_DATES_RESULT,
                    CSV_Cols.MATCHING_PUBLISHER_RESULT,
                    CSV_Cols.ORIGIN_DB_CHOSEN_PUBLISHER,
                    CSV_Cols.TARGET_DB_CHOSEN_PUBLISHER,
                    CSV_Cols.TARGET_DB_NB_OTHER_ID,
                    CSV_Cols.IS_ORIGIN_ID_IN_TARGET_OTHER_DB_IDS,
                    CSV_Cols.GLOBAL_VALIDATION_RESULT,
                    CSV_Cols.GLOBAL_VALIDATION_NB_SUCCESSFUL_CHECKS,
                    CSV_Cols.GLOBAL_VALIDATION_TITLE_CHECK,
                    CSV_Cols.GLOBAL_VALIDATION_PUBLISHER_CHECK,
                    CSV_Cols.GLOBAL_VALIDATION_DATE_CHECK,
                    CSV_Cols.FCR_PROCESSED_ID,
                    # special data
                    CSV_Cols.ORIGIN_DB_DATE_1,
                    CSV_Cols.TARGET_DB_DATE_1,
                    CSV_Cols.ORIGIN_DB_DATE_2,
                    CSV_Cols.TARGET_DB_DATE_2,
                    CSV_Cols.ORIGIN_DB_TITLE_KEY,
                    CSV_Cols.TARGET_DB_TITLE_KEY
                ]:
                self.headers[col.name] = self.csv_cols[col.name][par.lang]
            # Columns from records
            processing_fields:Dict[Mapped_Fields, Processing_Data_Target] = par.processing.mapped_data
            for data in processing_fields:
                if processing_fields[data] in [Processing_Data_Target.BOTH, Processing_Data_Target.ORIGIN]:
                    self.headers[f"ORIGIN_DB_{data.name}"] = self.csv_cols[f"ORIGIN_DB_{data.name}"][par.lang]
                # NOT A ELIF
                if processing_fields[data] in [Processing_Data_Target.BOTH, Processing_Data_Target.TARGET]:
                    self.headers[f"TARGET_DB_{data.name}"] = self.csv_cols[f"TARGET_DB_{data.name}"][par.lang]
            # Special processing cols
            if par.processing in [
                    Processing_Names.BETTER_ITEM,
                    Processing_Names.BETTER_ITEM_DVD,
                    Processing_Names.BETTER_ITEM_NO_ISBN,
                    Processing_Names.BETTER_ITEM_MAPS
                ]:
                self.headers[CSV_Cols.TARGET_DB_HAS_ITEMS.name] = self.csv_cols[CSV_Cols.TARGET_DB_HAS_ITEMS.name][par.lang]
                del self.headers[CSV_Cols.ORIGIN_DB_GENERAL_PROCESSING_DATA_DATES.name]
                del self.headers[CSV_Cols.TARGET_DB_GENERAL_PROCESSING_DATA_DATES.name]
            elif par.processing == Processing_Names.MARC_FILE_IN_KOHA_SRU:
                del self.headers[CSV_Cols.ORIGIN_DB_GENERAL_PROCESSING_DATA_DATES.name]
                del self.headers[CSV_Cols.TARGET_DB_GENERAL_PROCESSING_DATA_DATES.name]
                del self.headers[CSV_Cols.INPUT_QUERY.name]
                del self.headers[CSV_Cols.TARGET_DB_NB_OTHER_ID.name]
                del self.headers[CSV_Cols.IS_ORIGIN_ID_IN_TARGET_OTHER_DB_IDS.name]
            # Order columns by their index
            self.headers_ordered = sorted(self.headers.keys(), key=lambda x: CSV_Cols[x].value)
            # Columns from the original file
            for col in original_file_cols:
                self.headers[col] = col
                self.headers_ordered.append(col)

        def write_line(self, rec, success):
            """Write this record line to the CSV file"""
            self.writer.writerow(rec.output.to_csv())
            if success:
                msg = "SUCCESSFULLY processed"
            else:
                msg = "FAILED to process"
            self.parent.log.info(f"{msg} line input query = \"{rec.input_query}\", origin database ID = \"{rec.original_uid}\"")

        def close_file(self):
            """Closes the CSV file"""
            self.file.close()