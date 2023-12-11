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
        FCR_Mapped_Fields.LEADER: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.ID: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PPN: FCR_Processing_Data_Target.ORIGIN,
        FCR_Mapped_Fields.GENERAL_PROCESSING_DATA_DATES: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.ERRONEOUS_ISBN: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.TITLE: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PUBLISHERS_NAME: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.EDITION_NOTES: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PUBLICATION_DATES: FCR_Processing_Data_Target.BOTH,
        FCR_Mapped_Fields.PHYSICAL_DESCRIPTION: FCR_Processing_Data_Target.ORIGIN,
        FCR_Mapped_Fields.OTHER_DB_ID: FCR_Processing_Data_Target.TARGET,
        FCR_Mapped_Fields.ITEMS_BARCODE: FCR_Processing_Data_Target.TARGET,
        FCR_Mapped_Fields.ITEMS: FCR_Processing_Data_Target.TARGET
        }
    OTHER_DB_IN_LOCAL_DB = {}

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

# ---------- MATCH RECORDS (MR) ----------
class Operations(Enum):
    SEARCH_IN_SUDOC_BY_ISBN = 0
    SEARCH_IN_KOHA = 1
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN = 2
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU = 3
    SEARCH_IN_SUDOC_DVD = 4
    # SEARCH_IN_ISO2701_FILE = 4

class Actions(Enum):
    ISBN2PPN = 0
    ISBN2PPN_MODIFIED_ISBN = 1
    SRU_SUDOC_ISBN = 2
    EAN2PPN = 3
    SRU_SUDOC_MTI_AUT_EDI_APU = 4
    SRU_SUDOC_MTI_AUT_APU = 5
    SRU_SUDOC_MTI_AUT = 6

class Try_Status(Enum):
    UNKNWON = 0
    SUCCESS = 1
    ERROR = 2

class Match_Records_Errors(Enum):
    GENERIC_ERROR = 0
    NOTHING_WAS_FOUND = 1

PROCESSING_OPERATION_MAPPING = {
    FCR_Processings.BETTER_ITEM:Operations.SEARCH_IN_SUDOC_BY_ISBN
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
        Actions.SRU_SUDOC_MTI_AUT_EDI_APU,
        Actions.SRU_SUDOC_MTI_AUT_APU,
        Actions.SRU_SUDOC_MTI_AUT
    ]
    

class Match_Records_Error_Messages(Enum):
    GENERIC_ERROR = "Generic error"
    NOTHING_WAS_FOUND = "Nothing was found"

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