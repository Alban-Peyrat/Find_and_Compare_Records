# -*- coding: utf-8 -*- 

# External import
import os
import json
from dotenv import load_dotenv
from enum import Enum

class execution_settings(object):
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
    

class record(object):
    def __init__(self):
        self.a = 1

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

class report(object):
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
        
