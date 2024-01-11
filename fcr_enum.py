# -*- coding: utf-8 -*- 

# External import
from enum import Enum

# ---------- Execution settings (ES) ----------
class FCR_Mapped_Fields(Enum):
    LEADER = "Leader"
    ID = "id"
    PPN = "ppn"
    GENERAL_PROCESSING_DATA_DATES = "general_processing_data_dates"
    ERRONEOUS_ISBN = "erroneous_isbn"
    TITLE = "title"
    PUBLISHERS_NAME = "publishers_name"
    EDITION_NOTES = "edition_note"
    PUBLICATION_DATES = "publication_dates"
    PHYSICAL_DESCRIPTION = "physical_desription"
    CONTENTS_NOTES = "contents_notes"
    OTHER_ED_IN_OTHER_MEDIUM_BIBG_ID = "other_edition_in_other_medium_bibliographic_id"
    OTHER_DB_ID = "other_database_id"
    ITEMS = "items"
    ITEMS_BARCODE = "items_barcode"
    EAN = "ean"
    AUTHORS = "authors"

class FCR_Processing_Data_Target(Enum):
    ORIGIN = 0
    TARGET = 1
    BOTH = 2

class FCR_Processings(Enum):
    BETTER_ITEM = {
        FCR_Mapped_Fields.ID: FCR_Processing_Data_Target.ORIGIN,
        FCR_Mapped_Fields.PPN: FCR_Processing_Data_Target.ORIGIN,
        FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.ERRONEOUS_ISBN: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.TITLE: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.AUTHORS: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PUBLISHERS_NAME: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.EDITION_NOTES: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PUBLICATION_DATES: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PHYSICAL_DESCRIPTION: FCR_Processing_Data_Target.ORIGIN,
        FCR_Mapped_Fields.OTHER_DB_ID: FCR_Processing_Data_Target.TARGET,
        FCR_Mapped_Fields.ITEMS_BARCODE: FCR_Processing_Data_Target.TARGET,
        FCR_Mapped_Fields.ITEMS: FCR_Processing_Data_Target.TARGET
        }
    OTHER_DB_IN_LOCAL_DB = {}
    BETTER_ITEM_DVD = {
        FCR_Mapped_Fields.ID: FCR_Processing_Data_Target.ORIGIN,
        FCR_Mapped_Fields.PPN: FCR_Processing_Data_Target.ORIGIN,
        FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.EAN: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.TITLE: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.AUTHORS: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PUBLISHERS_NAME: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.EDITION_NOTES: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PHYSICAL_DESCRIPTION: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PUBLICATION_DATES: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.CONTENTS_NOTES: FCR_Processing_Data_Target.ORIGIN,
        FCR_Mapped_Fields.OTHER_DB_ID: FCR_Processing_Data_Target.TARGET,
        FCR_Mapped_Fields.ITEMS_BARCODE: FCR_Processing_Data_Target.TARGET,
        FCR_Mapped_Fields.ITEMS: FCR_Processing_Data_Target.TARGET    
    }

class Analysis_Checks(Enum):
    TITLE = 0
    PUBLISHER = 1
    DATE = 2

class Analysis_Final_Results(Enum):
    UNKNOWN = 0
    NO_CHECK = 1
    TOTAL_MATCH = 2
    PARTIAL_MATCH = 3
    NO_MATCH = 4

class Log_Level(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

# ---------- MATCH RECORDS (MR) ----------
class Operations(Enum):
    SEARCH_IN_SUDOC_BY_ISBN = 0
    SEARCH_IN_KOHA = 1
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN = 2
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU = 3
    SEARCH_IN_SUDOC_DVD = 4
    # SEARCH_IN_ISO2701_FILE = 5

class Actions(Enum):
    ISBN2PPN = 0
    ISBN2PPN_MODIFIED_ISBN = 1
    SRU_SUDOC_ISBN = 2
    EAN2PPN = 3
    SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V = 4
    SRU_SUDOC_MTI_AUT_APU_TDO_V = 5
    SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V = 6
    SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_V = 7
    SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V = 8

class Try_Status(Enum):
    UNKNWON = 0
    SUCCESS = 1
    ERROR = 2

class Match_Records_Errors(Enum):
    GENERIC_ERROR = 0
    NOTHING_WAS_FOUND = 1
    NO_EAN_WAS_FOUND = 2
    REQUIRED_DATA_MISSING = 3

class Match_Records_Error_Messages(Enum):
    # Why tf are there 2 enums for errors
    GENERIC_ERROR = "Generic error"
    NOTHING_WAS_FOUND = "Nothing was found"
    NO_EAN_WAS_FOUND = "Original record has no EAN"
    REQUIRED_DATA_MISSING = "Original record was missing one of the required data"


PROCESSING_OPERATION_MAPPING = {
    FCR_Processings.BETTER_ITEM:Operations.SEARCH_IN_SUDOC_BY_ISBN,
    FCR_Processings.BETTER_ITEM_DVD:Operations.SEARCH_IN_SUDOC_DVD
}

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
    SEARCH_IN_SUDOC_DVD = [
        Actions.EAN2PPN,
        Actions.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V,
        Actions.SRU_SUDOC_MTI_AUT_APU_TDO_V,
        Actions.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V,
        Actions.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V
    ]
    


# ---------- UNIVERSAL DATA EXTRACTOR (UDE) ----------
class Databases(Enum):
    """List of databases and their filter field"""
    ABESXML = {
        FCR_Mapped_Fields.OTHER_DB_ID:"ILN",
        FCR_Mapped_Fields.ITEMS:"RCR",
        FCR_Mapped_Fields.ITEMS_BARCODE:"RCR"
    }
    SUDOC_SRU = {}
    KOHA_PUBLIC_BIBLIO = {}
    KOHA_SRU = {}
    LOCAL = {}

class Record_Formats(Enum):
    """List of supported record formats"""
    UNKNOWN = 0
    JSON_DICT = 1
    ET_ELEMENT = 2
    PYMARC_RECORD = 3

class Xml_Namespaces(Enum):
    """List of supported XML namespaces"""
    MARC = "marc"
    ZS2_0 = "zs2.0"
    ZS1_1 = "zs1.1"
    ZS1_2 = "zs1.2"
    SRW = "srw"
    ZR = "zr"
    MG = "mg"
    PPXML = "ppxml"

XML_NS = {
    "marc": "http://www.loc.gov/MARC21/slim",
    "zs2.0": "http://docs.oasis-open.org/ns/search-ws/sruResponse",
    "zs1.1": "http://www.loc.gov/zing/srw/",
    "zs1.2": "http://www.loc.gov/zing/srw/",
    "srw":"http://www.loc.gov/zing/srw/",
    "zr":"http://explain.z3950.org/dtd/2.0/",
    "mg":"info:srw/extension/5/metadata-grouping-v1.0",
    "ppxml":"http://www.oclcpica.org/xmlns/ppxml-1.0"
}

# ---------- MAIN ----------
class Other_Database_Id_In_Target(Enum):
    UNKNOWN = 0
    NO_OTHER_DB_ID = 1
    THIS_ID_INCLUDED = 2
    ONLY_THIS_OTHER_DB_ID = 3
    THIS_ID_NOT_INCLUDED = 4

# ---------- REPORT ----------
class Success(Enum):
    MATCH_RECORD = 0
    GLOBAL = 1

class Errors(Enum):
    MATCH_RECORD = 1
    KOHA = 2
    SUDOC = 3

# ---------- REPORT ----------
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
    MATCH_RECORDS_RESULTS = 5020
    ORIGIN_DB_ID = 6000
    TARGET_DB_ID = 6001
    MATCHED_ID = 7000
    ORIGIN_DB_PPN = 7100
    TARGET_DB_PPN = 7101
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
    ORIGIN_DB_AUTHORS = 20000
    TARGET_DB_AUTHORS = 20001
    ORIGIN_DB_LEADER = 21000
    TARGET_DB_LEADER = 21001
    RESERVED_SLOT1 = 22000
    RESERVED_SLOT2 = 23000
    RESERVED_SLOT3 = 24000
    RESERVED_SLOT4 = 25000
    RESERVED_SLOT5 = 26000
    RESERVED_SLOT6 = 27000
    RESERVED_SLOT7 = 28000
    RESERVED_SLOT8 = 29000
    # 80XXX are reserved
    MATCHING_TITLE_RATIO = 80000
    MATCHING_TITLE_PARTIAL_RATIO = 80010
    MATCHING_TITLE_TOKEN_SORT_RATIO = 80020
    MATCHING_TITLE_TOKEN_SET_RATIO = 80030
    MATCHING_PUBLISHER_RESULT = 80100
    MATCHING_DATES_RESULT = 80200
    # 99XXX are for original file
