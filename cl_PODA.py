# -*- coding: utf-8 -*- 

# External import
from enum import Enum, EnumType
from typing import Dict, List

# Internal imports
from cl_UDE import Database_Names, Mapped_Fields

# --------------- Actions ---------------
class Action_Names(Enum):
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
    ISBN2PPN_MODIFIED_ISBN_SAME_KEY = 23
    KOHA_SRU_ANY_TITLE_PUBLISHER_DATE = 24
    KOHA_SRU_TITLE = 25
    SRU_SUDOC_MTI = 26
    SRU_SUDOC_MTI_TDO_B = 27
    SRU_SUDOC_MTI_TDO_K = 28
    SRU_SUDOC_MTI_TDO_V = 29

class Action(object):
    def __init__(self, action:Action_Names, isbn:bool=False, ean:bool=False, title:bool=False, authors:bool=False, publisher:bool=False, date:bool=False, doctype:str="", specific_index:bool=True) -> None:
        """
        By default, all data are off
        By default, will use the specific indexes"""
        self.enum_member = action
        self.name = action.name
        self.id = action.value
        self.use_isbn = isbn
        self.use_ean = ean
        self.use_title = title
        self.use_authors = authors
        self.use_publisher = publisher
        self.use_date = date
        self.use_doctype = False
        self.doctype = doctype
        if doctype != "":
            self.use_doctype = True
        self.specific_index = specific_index

ACTIONS_LIST = {
    Action_Names.ISBN2PPN: Action(
        action=Action_Names.ISBN2PPN,
        isbn=True
    ),
    Action_Names.ISBN2PPN_MODIFIED_ISBN: Action(
        action=Action_Names.ISBN2PPN_MODIFIED_ISBN,
        isbn=True
    ),
    Action_Names.SRU_SUDOC_ISBN: Action(
        action=Action_Names.SRU_SUDOC_ISBN,
        isbn=True
    ),
    Action_Names.EAN2PPN: Action(
        action=Action_Names.EAN2PPN,
        ean=True
    ),
    Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V: Action(
        action=Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V,
        title=True,
        authors=True,
        publisher=True,
        date=True,
        doctype="V"
    ),
    Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_V: Action(
        action=Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_V,
        title=True,
        authors=True,
        date=True,
        doctype="V"
    ),
    Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V: Action(
        action=Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V,
        title=True,
        authors=True,
        publisher=True,
        date=True,
        doctype="V",
        specific_index=False
    ),
    Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_V: Action(
        action=Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_V,
        title=True,
        authors=True,
        date=True,
        doctype="V",
        specific_index=False
    ),
    Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V: Action(
        action=Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V,
        title=True,
        authors=True,
        publisher=True,
        doctype="V",
        specific_index=False
    ),
    Action_Names.KOHA_SRU_IBSN: Action(
        action=Action_Names.KOHA_SRU_IBSN,
        isbn=True
    ),
    Action_Names.KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE: Action(
        action=Action_Names.KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE,
        title=True,
        authors=True,
        publisher=True,
        date=True
    ),
    Action_Names.KOHA_SRU_TITLE_AUTHOR_DATE: Action(
        action=Action_Names.KOHA_SRU_TITLE_AUTHOR_DATE,
        title=True,
        authors=True,
        date=True
    ),
    Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE: Action(
        action=Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE,
        title=True,
        authors=True,
        publisher=True,
        date=True,
        specific_index=False
    ),
    Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_DATE: Action(
        action=Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_DATE,
        title=True,
        authors=True,
        date=True,
        specific_index=False
    ),
    Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B: Action(
        action=Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B,
        title=True,
        authors=True,
        publisher=True,
        date=True,
        doctype="B"
    ),
    Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_B: Action(
        action=Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_B,
        title=True,
        authors=True,
        date=True,
        doctype="B"
    ),
    Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B: Action(
        action=Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B,
        title=True,
        authors=True,
        publisher=True,
        date=True,
        doctype="B",
        specific_index=False
    ),
    Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_B: Action(
        action=Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_B,
        title=True,
        authors=True,
        date=True,
        doctype="B",
        specific_index=False
    ),
    Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_B: Action(
        action=Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_B,
        title=True,
        authors=True,
        publisher=True,
        doctype="B",
        specific_index=False
    ),
    Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K: Action(
        action=Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K,
        title=True,
        authors=True,
        publisher=True,
        date=True,
        doctype="K"
    ),
    Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_K: Action(
        action=Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_K,
        title=True,
        authors=True,
        publisher=True,
        date=True,
        doctype="K"
    ),
    Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K: Action(
        action=Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K,
        title=True,
        authors=True,
        publisher=True,
        date=True,
        doctype="K",
        specific_index=False
    ),
    Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_K: Action(
        action=Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_K,
        title=True,
        authors=True,
        date=True,
        doctype="K",
        specific_index=False
    ),
    Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_K: Action(
        action=Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_K,
        title=True,
        authors=True,
        publisher=True,
        doctype="K",
        specific_index=False
    ),
    Action_Names.ISBN2PPN_MODIFIED_ISBN_SAME_KEY: Action(
        action=Action_Names.ISBN2PPN_MODIFIED_ISBN_SAME_KEY,
        isbn=True
    ),
    Action_Names.KOHA_SRU_ANY_TITLE_PUBLISHER_DATE: Action(
        action=Action_Names.KOHA_SRU_ANY_TITLE_PUBLISHER_DATE,
        title=True,
        publisher=True,
        date=True,
        specific_index=False
    ),
    Action_Names.KOHA_SRU_TITLE: Action(
        action=Action_Names.KOHA_SRU_TITLE,
        title=True
    ),
    Action_Names.SRU_SUDOC_MTI: Action(
        action=Action_Names.SRU_SUDOC_MTI,
        title=True
    ),
    Action_Names.SRU_SUDOC_MTI_TDO_B: Action(
        action=Action_Names.SRU_SUDOC_MTI_TDO_B,
        title=True,
        doctype="B"
    ),
    Action_Names.SRU_SUDOC_MTI_TDO_K: Action(
        action=Action_Names.SRU_SUDOC_MTI_TDO_K,
        title=True,
        doctype="K"
    ),
    Action_Names.SRU_SUDOC_MTI_TDO_V: Action(
        action=Action_Names.SRU_SUDOC_MTI_TDO_V,
        title=True,
        doctype="V"
    )
}

# --------------- Databases ---------------
class Filters(Enum):
    """List of all filters"""
    ILN = 0
    RCR = 1
    FILTER1 = 2
    FILTER2 = 3
    FILTER3 = 4

class Database(object):
    def __init__(self, database:Database_Names, filters:Dict[Mapped_Fields, Filters]) -> None:
        self.enum_member = database
        self.name = database.name
        self.id = database.value
        self.filters = filters

DATABASES_LIST = {
    Database_Names.ABESXML:Database(
        database=Database_Names.ABESXML,
        filters={
            Mapped_Fields.OTHER_DB_ID:Filters.ILN,
            Mapped_Fields.ITEMS:Filters.RCR,
            Mapped_Fields.ITEMS_BARCODE:Filters.RCR
        }
    ),
    Database_Names.SUDOC_SRU:Database(
        database=Database_Names.SUDOC_SRU,
        filters={}
    ),
    Database_Names.KOHA_PUBLIC_BIBLIO:Database(
        database=Database_Names.KOHA_PUBLIC_BIBLIO,
        filters={}
    ),
    Database_Names.KOHA_SRU:Database(
        database=Database_Names.KOHA_SRU,
        filters={
            Mapped_Fields.ITEMS:Filters.FILTER1,
            Mapped_Fields.ITEMS_BARCODE:Filters.FILTER1
            }
    ),
    Database_Names.LOCAL:Database(
        database=Database_Names.LOCAL,
        filters={}
    )
}

# --------------- Operations ---------------
class Operation_Names(Enum):
    SEARCH_IN_SUDOC_BY_ISBN = 0
    SEARCH_IN_KOHA = 1
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN = 2
    SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU = 3
    SEARCH_IN_SUDOC_DVD = 4
    SEARCH_IN_KOHA_SRU_VANILLA = 5
    SEARCH_IN_SUDOC_NO_ISBN = 6
    SEARCH_IN_SUDOC_MAPS = 7

class Operation(object):
    def __init__(self, operation: Operation_Names, actions:List[Action_Names]) -> None:
        """Takes as argument :
            - a Operaion_Nmaes member
            - a list of Action_Names memner (the order is important)"""
        self.enum_member = operation
        self.name = operation.name
        self.id = operation.value
        self.actions = actions

OPERATIONS_LIST = {
    Operation_Names.SEARCH_IN_SUDOC_BY_ISBN:Operation(
        operation=Operation_Names.SEARCH_IN_SUDOC_BY_ISBN,
        actions=[
            Action_Names.ISBN2PPN,
            Action_Names.ISBN2PPN_MODIFIED_ISBN,
            Action_Names.ISBN2PPN_MODIFIED_ISBN_SAME_KEY,
            Action_Names.SRU_SUDOC_ISBN,
            Action_Names.SRU_SUDOC_MTI
        ]
    ),
    Operation_Names.SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN:Operation(
        operation=Operation_Names.SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN,
        actions=[
            Action_Names.ISBN2PPN,
            Action_Names.ISBN2PPN_MODIFIED_ISBN
        ]
    ),
    Operation_Names.SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU:Operation(
        operation=Operation_Names.SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU,
        actions=[
            Action_Names.SRU_SUDOC_ISBN
        ]
    ),
    Operation_Names.SEARCH_IN_SUDOC_DVD:Operation(
        operation=Operation_Names.SEARCH_IN_SUDOC_DVD,
        actions=[
            Action_Names.EAN2PPN,
            Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V,
            Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_V,
            Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V,
            Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V,
            Action_Names.SRU_SUDOC_MTI_TDO_V
        ]
    ),
    Operation_Names.SEARCH_IN_KOHA_SRU_VANILLA:Operation(
        operation=Operation_Names.SEARCH_IN_KOHA_SRU_VANILLA,
        actions=[
            Action_Names.KOHA_SRU_IBSN,
            Action_Names.KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE,
            Action_Names.KOHA_SRU_TITLE_AUTHOR_DATE,
            Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE,
            Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_DATE,
            Action_Names.KOHA_SRU_ANY_TITLE_PUBLISHER_DATE,
            Action_Names.KOHA_SRU_TITLE
        ]
    ),
    Operation_Names.SEARCH_IN_SUDOC_NO_ISBN:Operation(
        operation=Operation_Names.SEARCH_IN_SUDOC_NO_ISBN,
        actions=[
            Action_Names.EAN2PPN,
            Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B,
            Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_B,
            Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B,
            Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_B,
            Action_Names.SRU_SUDOC_MTI_TDO_B
        ]
    ),
    Operation_Names.SEARCH_IN_SUDOC_MAPS:Operation(
        operation=Operation_Names.SEARCH_IN_SUDOC_MAPS,
        actions=[
            Action_Names.EAN2PPN,
            Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K,
            Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_K,
            Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K,
            Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_K,
            Action_Names.SRU_SUDOC_MTI_TDO_K
        ]
    )
}

# --------------- Processings ---------------
class Processing_Names(Enum):
    BETTER_ITEM = 0
    MARC_FILE_IN_KOHA_SRU = 1
    BETTER_ITEM_DVD = 2
    BETTER_ITEM_NO_ISBN = 3
    BETTER_ITEM_MAPS = 4

class Processing_Data_Target(Enum):
    ORIGIN = 0
    TARGET = 1
    BOTH = 2

class Processing(object):
    def __init__(self, processing: Processing_Names, mapped_data:Dict[Mapped_Fields, Processing_Data_Target], operation:Operation, origin_database:Database, target_database:Database, original_file_data_is_csv:bool) -> None:
        """Takes as argument :
            - a Processings_Name member
            - a dict with Mapped_Fields members as key and Processing_Data_Target membres as value
            - a Operation instance"""
        self.enum_member = processing
        self.name = processing.name
        self.id = processing.value
        self.mapped_data = mapped_data
        self.operation = operation
        self.origin_database = origin_database
        self.target_database = target_database
        self.original_file_data_is_csv = original_file_data_is_csv

PROCESSINGS_LIST = {
    Processing_Names.BETTER_ITEM:Processing(
        processing=Processing_Names.BETTER_ITEM,
        mapped_data={
            Mapped_Fields.ID: Processing_Data_Target.ORIGIN,
            Mapped_Fields.PPN: Processing_Data_Target.ORIGIN,
            Mapped_Fields.GENERAL_PROCESSING_DATA_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.ERRONEOUS_ISBN: Processing_Data_Target.BOTH,
            Mapped_Fields.TITLE: Processing_Data_Target.BOTH,
            Mapped_Fields.AUTHORS: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLISHERS_NAME: Processing_Data_Target.BOTH,
            Mapped_Fields.EDITION_NOTES: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLICATION_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.PHYSICAL_DESCRIPTION: Processing_Data_Target.ORIGIN,
            Mapped_Fields.OTHER_DB_ID: Processing_Data_Target.TARGET,
            Mapped_Fields.ITEMS_BARCODE: Processing_Data_Target.TARGET,
            Mapped_Fields.ITEMS: Processing_Data_Target.TARGET
        },
        operation=OPERATIONS_LIST[Operation_Names.SEARCH_IN_SUDOC_BY_ISBN],
        origin_database=DATABASES_LIST[Database_Names.KOHA_PUBLIC_BIBLIO],
        target_database=DATABASES_LIST[Database_Names.ABESXML],
        original_file_data_is_csv=True
    ),
    Processing_Names.MARC_FILE_IN_KOHA_SRU:Processing(
        processing=Processing_Names.MARC_FILE_IN_KOHA_SRU,
        mapped_data={
            Mapped_Fields.ID: Processing_Data_Target.BOTH,
            Mapped_Fields.PPN: Processing_Data_Target.TARGET,
            Mapped_Fields.DOCUMENT_TYPE: Processing_Data_Target.BOTH,
            Mapped_Fields.ISBN:Processing_Data_Target.BOTH,
            Mapped_Fields.GENERAL_PROCESSING_DATA_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.ERRONEOUS_ISBN: Processing_Data_Target.TARGET,
            Mapped_Fields.TITLE: Processing_Data_Target.BOTH,
            Mapped_Fields.AUTHORS: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLISHERS_NAME: Processing_Data_Target.BOTH,
            Mapped_Fields.EDITION_NOTES: Processing_Data_Target.BOTH,
            Mapped_Fields.PHYSICAL_DESCRIPTION: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLICATION_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.LINKING_PIECE: Processing_Data_Target.BOTH,
            Mapped_Fields.EXPORTED_TO_DIGITAL_LIBRARY: Processing_Data_Target.BOTH,
            Mapped_Fields.ITEMS_BARCODE: Processing_Data_Target.BOTH
        },
        operation=OPERATIONS_LIST[Operation_Names.SEARCH_IN_KOHA_SRU_VANILLA],
        origin_database=DATABASES_LIST[Database_Names.LOCAL],
        target_database=DATABASES_LIST[Database_Names.KOHA_SRU],
        original_file_data_is_csv=False
    ),
    Processing_Names.BETTER_ITEM_DVD:Processing(
        processing=Processing_Names.BETTER_ITEM_DVD,
        mapped_data={
            Mapped_Fields.ID: Processing_Data_Target.ORIGIN,
            Mapped_Fields.PPN: Processing_Data_Target.ORIGIN,
            Mapped_Fields.GENERAL_PROCESSING_DATA_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.EAN: Processing_Data_Target.BOTH,
            Mapped_Fields.TITLE: Processing_Data_Target.BOTH,
            Mapped_Fields.AUTHORS: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLISHERS_NAME: Processing_Data_Target.BOTH,
            Mapped_Fields.EDITION_NOTES: Processing_Data_Target.BOTH,
            Mapped_Fields.PHYSICAL_DESCRIPTION: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLICATION_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.CONTENTS_NOTES: Processing_Data_Target.ORIGIN,
            Mapped_Fields.OTHER_DB_ID: Processing_Data_Target.TARGET,
            Mapped_Fields.ITEMS_BARCODE: Processing_Data_Target.TARGET,
            Mapped_Fields.ITEMS: Processing_Data_Target.TARGET    
        },
        operation=OPERATIONS_LIST[Operation_Names.SEARCH_IN_SUDOC_DVD],
        origin_database=DATABASES_LIST[Database_Names.KOHA_PUBLIC_BIBLIO],
        target_database=DATABASES_LIST[Database_Names.ABESXML],
        original_file_data_is_csv=True
    ),
    Processing_Names.BETTER_ITEM_NO_ISBN:Processing(
        processing=Processing_Names.BETTER_ITEM_NO_ISBN,
        mapped_data={
            Mapped_Fields.ID: Processing_Data_Target.ORIGIN,
            Mapped_Fields.PPN: Processing_Data_Target.ORIGIN,
            Mapped_Fields.GENERAL_PROCESSING_DATA_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.EAN: Processing_Data_Target.BOTH,
            Mapped_Fields.ERRONEOUS_ISBN: Processing_Data_Target.BOTH,
            Mapped_Fields.TITLE: Processing_Data_Target.BOTH,
            Mapped_Fields.AUTHORS: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLISHERS_NAME: Processing_Data_Target.BOTH,
            Mapped_Fields.EDITION_NOTES: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLICATION_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.PHYSICAL_DESCRIPTION: Processing_Data_Target.ORIGIN,
            Mapped_Fields.OTHER_DB_ID: Processing_Data_Target.TARGET,
            Mapped_Fields.ITEMS_BARCODE: Processing_Data_Target.TARGET,
            Mapped_Fields.ITEMS: Processing_Data_Target.TARGET
        },
        operation=OPERATIONS_LIST[Operation_Names.SEARCH_IN_SUDOC_NO_ISBN],
        origin_database=DATABASES_LIST[Database_Names.KOHA_PUBLIC_BIBLIO],
        target_database=DATABASES_LIST[Database_Names.ABESXML],
        original_file_data_is_csv=True
    ),
    Processing_Names.BETTER_ITEM_MAPS:Processing(
        processing=Processing_Names.BETTER_ITEM_MAPS,
        mapped_data={
            Mapped_Fields.ID: Processing_Data_Target.ORIGIN,
            Mapped_Fields.PPN: Processing_Data_Target.ORIGIN,
            Mapped_Fields.GENERAL_PROCESSING_DATA_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.EAN: Processing_Data_Target.BOTH,
            Mapped_Fields.TITLE: Processing_Data_Target.BOTH,
            Mapped_Fields.AUTHORS: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLISHERS_NAME: Processing_Data_Target.BOTH,
            Mapped_Fields.EDITION_NOTES: Processing_Data_Target.BOTH,
            Mapped_Fields.PHYSICAL_DESCRIPTION: Processing_Data_Target.BOTH,
            Mapped_Fields.PUBLICATION_DATES: Processing_Data_Target.BOTH,
            Mapped_Fields.CONTENTS_NOTES: Processing_Data_Target.ORIGIN,
            Mapped_Fields.OTHER_DB_ID: Processing_Data_Target.TARGET,
            Mapped_Fields.ITEMS_BARCODE: Processing_Data_Target.TARGET,
            Mapped_Fields.ITEMS: Processing_Data_Target.TARGET,
            Mapped_Fields.MAPS_HORIZONTAL_SCALE: Processing_Data_Target.BOTH,
            Mapped_Fields.MAPS_MATHEMATICAL_DATA: Processing_Data_Target.BOTH,
            Mapped_Fields.SERIES: Processing_Data_Target.BOTH,
            Mapped_Fields.SERIES_LINK: Processing_Data_Target.BOTH,
            Mapped_Fields.GEOGRAPHICAL_SUBJECT: Processing_Data_Target.BOTH,
        },
        operation=OPERATIONS_LIST[Operation_Names.SEARCH_IN_SUDOC_MAPS],
        origin_database=DATABASES_LIST[Database_Names.KOHA_PUBLIC_BIBLIO],
        target_database=DATABASES_LIST[Database_Names.ABESXML],
        original_file_data_is_csv=True
    )
}

# --------------- Function ---------------
def get_PODA_instance(poda:Processing_Names|Operation_Names|Database_Names|str|int, enum:Enum=None) -> Processing|Operation|Database|Action:
    """Returns the wanted instance for the given enum member.
    Argument can either be :
        - Enum member
        - Enum member name
        - Enum member value
    If using the name or value, the second argument must be the enum you want from"""
    # Arg is a member, easy to do
    if type(poda) == Processing_Names:
        return PROCESSINGS_LIST[poda]
    elif type(poda) == Operation_Names:
        return OPERATIONS_LIST[poda]
    elif type(poda) == Database_Names:
        return DATABASES_LIST[poda]
    elif type(poda) == Action_Names:
        return ACTIONS_LIST[poda]
    # Arg is not a memeber, check if we have the 2nd arg
    elif type(enum) == EnumType:
        # Get the LIST for this Enum
        LIST = None
        if enum.__name__ == "Processing_Names":
            LIST = PROCESSINGS_LIST
        elif enum.__name__ == "Operation_Names":
            LIST = OPERATIONS_LIST
        elif enum.__name__ == "Database_Names":
            LIST = DATABASES_LIST
        elif enum.__name__ == "Action_Names":
            LIST = ACTIONS_LIST
        # Leave if Enum is incorrect
        if LIST == None:
            return None
        if type(poda) == str:
            return LIST[enum[poda]]
        elif type(poda) == int:
            for member in enum:
                if member.value == poda:
                    return LIST[member]
    return None
