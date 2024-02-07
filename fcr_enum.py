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
    ISBN = "isbn"
    EXPORTED_TO_DIGITAL_LIBRARY = "exported_to_digital_library"
    MAPS_HORIZONTAL_SCALE = "maps_horizontal_scale"
    MAPS_MATHEMATICAL_DATA = "maps_mathematical_data"
    SERIES = "series"
    SERIES_LINK = "series_link"
    GEOGRAPHICAL_SUBJECT = "geographical_subject"

class FCR_Processing_Data_Target(Enum):
    ORIGIN = 0
    TARGET = 1
    BOTH = 2

class Processing_Names(Enum):
    BETTER_ITEM = 0
    MARC_FILE_IN_KOHA_SRU = 1
    BETTER_ITEM_DVD = 2
    BETTER_ITEM_NO_ISBN = 3
    BETTER_ITEM_MAPS = 4

class Analysis_Checks(Enum):
    TITLE = 0
    PUBLISHER = 1
    DATE = 2

class Analysis_Final_Results(Enum):
    UNKNOWN = {
        "eng":"Unknown final result",
        "fre":"Vérification inconnue"
    }
    NO_CHECK = {
        "eng":"No checks",
        "fre":"Pas de vérification"
    }
    TOTAL_MATCH = {
        "eng":"All checks were successful",
        "fre":"Vérications complètes"
    }
    PARTIAL_MATCH = {
        "eng":"Checks partially successful",
        "fre":"Vérifications partielles"
    }
    NO_MATCH = {
        "eng":"All checks failed",
        "fre":"Vérifications KO"
    }

class Log_Level(Enum):
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4

# ---------- MATCH RECORDS (MR) ----------

class Operation_Names(Enum):
    SEARCH_IN_SUDOC_BY_ISBN = 0
    SEARCH_IN_KOHA = 1
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN = 2
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU = 3
    SEARCH_IN_SUDOC_DVD = 4
    SEARCH_IN_KOHA_SRU_VANILLA = 5
    SEARCH_IN_SUDOC_NO_ISBN = 6
    SEARCH_IN_SUDOC_MAPS = 7

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
    KOHA_SRU_IBSN = 9
    KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE = 10
    KOHA_SRU_TITLE_AUTHOR_DATE = 11
    KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE = 12
    KOHA_SRU_ANY_TITLE_AUTHOR_DATE = 13
    SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B = 14
    SRU_SUDOC_MTI_AUT_APU_TDO_B = 15
    SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B = 16
    SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_B = 17
    SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_B = 18
    SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K = 19
    SRU_SUDOC_MTI_AUT_APU_TDO_K = 20
    SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K = 21
    SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_K = 21
    SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_K = 22
    
class Try_Status(Enum):
    UNKNWON = 0
    SUCCESS = 1
    ERROR = 2

class Match_Records_Errors(Enum):
    GENERIC_ERROR = 0
    NOTHING_WAS_FOUND = 1
    NO_EAN_WAS_FOUND = 2
    REQUIRED_DATA_MISSING = 3
    NO_ISBN_WAS_FOUND = 4

class Match_Records_Error_Messages(Enum):
    # Why tf are there 2 enums for errors
    GENERIC_ERROR = "Generic error"
    NOTHING_WAS_FOUND = "Nothing was found"
    NO_EAN_WAS_FOUND = "Original record has no EAN"
    REQUIRED_DATA_MISSING = "Original record was missing one of the required data"
    NO_ISBN_WAS_FOUND = "Original record has no ISBN"

# ---------- UNIVERSAL DATA EXTRACTOR (UDE) ----------
class FCR_Filters(Enum):
    """List of all filters"""
    ILN = 0
    RCR = 1
    FILTER1 = 2
    FILTER2 = 3
    FILTER3 = 4

class Database_Names(Enum):
    ABESXML = 0
    SUDOC_SRU = 1
    KOHA_PUBLIC_BIBLIO = 2
    KOHA_SRU = 3
    LOCAL = 4

# ↓ A del
# class Databases(Enum):
#     """List of databases and their filter field"""
#     ABESXML = {
#         FCR_Mapped_Fields.OTHER_DB_ID:FCR_Filters.ILN,
#         FCR_Mapped_Fields.ITEMS:FCR_Filters.RCR,
#         FCR_Mapped_Fields.ITEMS_BARCODE:FCR_Filters.RCR
#     }
#     SUDOC_SRU = {}
#     KOHA_PUBLIC_BIBLIO = {}
#     KOHA_SRU = {
#     }
#     LOCAL = {FCR_Mapped_Fields.LEADER:FCR_Filters.FILTER3}

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
    UNKNOWN = {
        "eng":"Unknown",
        "fre":"Inconnu"
    }
    SKIPPED = {
        "eng":"Skipped",
        "fre":"Ignoré"
    }
    NO_OTHER_DB_ID = {
        "eng":"No ID in the list",
        "fre":"Aucun ID dans la liste"
    }
    THIS_ID_INCLUDED = {
        "eng":"Included in list",
        "fre":"Présent dans la liste"
    }
    ONLY_THIS_OTHER_DB_ID = {
        "eng":"List includes only this ID",
        "fre":"Liste comportant que cet ID"
    }
    THIS_ID_NOT_INCLUDED = {
        "eng":"Missing from list",
        "fre":"Absent de la liste"
    }

# ---------- REPORT ----------
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
