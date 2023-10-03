# -*- coding: utf-8 -*- 

# External import
import os
import json
from dotenv import load_dotenv
from enum import Enum

# ----- Match Records imports -----
# Internal imports
import api.abes.Abes_isbn2ppn as isbn2ppn
import api.abes.Sudoc_SRU as ssru
import api.koha.Koha_SRU as Koha_SRU

# -------------------- Execution settings --------------------

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
class Try_Operations(Enum):
    SEARCH_IN_SUDOC_BY_ISBN = [
        Actions.ISBN2PPN,
        Actions.ISBN2PPN_MODIFIED_ISBN,
        Actions.SRU_SUDOC_ISBN
    ]
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN = [
        Actions.ISBN2PPN,
        Actions.ISBN2PPN_MODIFIED_ISBN
    ]
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU = [
        Actions.SRU_SUDOC_ISBN
    ]

class Match_Records_Error_Messages(Enum):
    GENERIC_ERROR = "Generic error"
    NOTHING_WAS_FOUND = "Nothing was found"

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
    def __init__(self, operation: Operations, query: str, es: Execution_Settings):
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

        # Calls the operation
        # if self.operation == Operations.SEARCH_IN_SUDOC_BY_ISBN:
        #     return self.search_in_sudoc_by_isbn()
        self.execute_operation()

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
        # /!\ THIS PART IS ALSO USED IN Actions.ISBN2PPN_MODIFIED_PPN DO NOT FORGET TO UPDATE
        # THE OTHER ONE IF NECESSARY
        # Sinon je mets des fonction communes du genre : Abes_ISBN2PNN_get_error or something
        elif action == Actions.ISBN2PPN:
            i2p = isbn2ppn.Abes_isbn2ppn(useJson=True)
            res = i2p.get_matching_ppn(self.query)
            thisTry.define_used_query(res.get_isbn_used())
            if res.status != isbn2ppn.Isbn2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action isbn2ppn with changed ISBN
        elif action == Actions.ISBN2PPN_MODIFIED_ISBN:
            #AR226
            # Converting the ISBN to 10<->13
            if len(self.query) == 13:
                new_query = self.query[3:-1]
                new_query += isbn2ppn.compute_isbn_10_check_digit(list(str(new_query)))
            elif len(self.query) == 10:
                # Doesn't consider 979[...] as the original issue should only concern old ISBN
                new_query = "978" + self.query[:-1]
                new_query += isbn2ppn.compute_isbn_13_check_digit(list(str(new_query)))
            
            # Same thing as Action ISBN2PPN
            i2p = isbn2ppn.Abes_isbn2ppn(useJson=True)
            res = i2p.get_matching_ppn(self.query)
            thisTry.define_used_query(res.get_isbn_used())
            if res.status != isbn2ppn.Isbn2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action in Koha SRU


# -------------------- MAIN --------------------

class Original_Record(object):
    def __init__(self, line: dict):
        self.error = None
        self.error_message = None
        self.original_line = line
    
    def extract_from_original_line(self, headers: list):
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