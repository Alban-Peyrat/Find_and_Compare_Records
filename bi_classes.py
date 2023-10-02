# -*- coding: utf-8 -*- 

# External import
import os
import json
from dotenv import load_dotenv
from enum import Enum

# -------------------- MAIN --------------------

class Execution_Settings(object):
    def __init__(self):
        # Load settings file
        with open('./settings.json', "r+", encoding="utf-8") as f:
            settings = json.load(f)
            self.analysis = settings["ANALYSIS"]
            self.csv_export_cols = settings["CSV_EXPORT_COLS"]
            self.report_settings = settings["REPORT_SETTINGS"]
    
    def get_values_from_GUI(self, val: dict):
        self.service = val["SERVICE"]
        self.file_path = val["FILE_PATH"]
        self.output_path = val["OUTPUT_PATH"]
        self.logs_path = val["LOGS_PATH"]
        self.koha_url = val["KOHA_URL"]
        self.koha_ppn_field = val["KOHA_PPN_FIELD"]
        self.koha_ppn_subfield = val["KOHA_PPN_SUBFIELD"]
        self.koha_report_nb = val["KOHA_REPORT_NB"]
        self.koha_userid = val["KOHA_USERID"]
        self.koha_password = val["KOHA_PASSWORD"]
        self.iln = val["ILN"]
        self.rcr = val["RCR"]
    
    def get_values_from_env(self):
        load_dotenv()
        self.service = os.getenv("SERVICE")
        self.file_path = os.getenv("FILE_PATH")
        self.output_path = os.getenv("OUTPUT_PATH")
        self.logs_path = os.getenv("LOGS_PATH")
        self.koha_url = os.getenv("KOHA_URL")
        self.koha_ppn_field = os.getenv("KOHA_PPN_FIELD")
        self.koha_ppn_subfield = os.getenv("KOHA_PPN_SUBFIELD")
        self.koha_report_nb = os.getenv("KOHA_REPORT_NB")
        self.koha_userid = os.getenv("KOHA_USERID")
        self.koha_password = os.getenv("KOHA_PASSWORD")
        self.ILN = os.getenv("ILN")
        self.RCR = os.getenv("RCR")
    
    def generate_files_path(self):
        self.file_path_out_results = self.output_path + "/resultats.txt"
        self.file_path_out_json = self.output_path + "/resultats.json"
        self.file_path_out_csv = self.output_path + "/resultats.csv"
    
    def define_chosen_analysis(self, nb: int):
        self.chosen_analysis = self.analysis[nb]
    

class Record(object):
    def __init__(self, line: dict):
        self.error = None
        self.error_message = None
        self.original_line = line
    
    def extract_from_original_line(self, headers: list):
        """Extract the first column of the file as the input query and
        the last column as the original UID regardless of the headers name"""
        self.input_query = self.original_line[headers[0]]
        self.original_uid = self.original_line[headers[len(self.original_line)-1]].rstrip()

# Used in report class
class Success(Enum):
    MATCH_RECORD = 0
    GLOBAL = 1

# Used in report class
class Errors(Enum):
    MATCH_RECORD_FAKE = 0
    MATCH_RECORD_REAL = 1
    KOHA = 2
    SUDOC = 3

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
        
# -------------------- MATCH RECORDS --------------------

class Operations(Enum):
    SEARCH_IN_SUDOC_BY_ISBN = 0
    SEARCH_IN_KOHA = 1
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN = 2
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU = 3
    # SEARCH_IN_ISO2701_FILE = 4

class Actions(Enum):
    ISBN2PPN = 0
    ISBN2PPN_MODIFIED_ISBN = 1
    SRU_SUDOC_ISBN = 2

class Try_Status(Enum):
    UNKNWON = 0
    SUCCESS = 1
    ERROR = 2

class Match_Records_Errors(Enum):
    GENERIC_ERROR = 0
    NOTHING_WAS_FOUND = 1

# TRY_OPERATIONS defines for each Operations a lsit of Actions to execute
# The order in the list is the order of execution
TRY_OPERATIONS = {
    Operations.SEARCH_IN_SUDOC_BY_ISBN: [
        Actions.ISBN2PPN,
        Actions.ISBN2PPN_MODIFIED_ISBN,
        Actions.SRU_SUDOC_ISBN
    ],
    Operations.SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN: [
        Actions.ISBN2PPN,
        Actions.ISBN2PPN_MODIFIED_ISBN
    ],
    Operations.SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU: [
        Actions.SRU_SUDOC_ISBN
    ]
}

MATCH_RECORDS_ERROR_MESSAGES = {
    Match_Records_Errors.GENERIC_ERROR: "Generic error",
    Match_Records_Errors.NOTHING_WAS_FOUND: "Nothing was found"
}