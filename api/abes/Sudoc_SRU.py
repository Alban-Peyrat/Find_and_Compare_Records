# -*- coding: utf-8 -*- 

# External imports
from enum import Enum
import logging
import requests
import urllib.parse
import xml.etree.ElementTree as ET
import re

# See README.md for more informations

# --------------- Enums ---------------

XML_NS = {
    "srw":"http://www.loc.gov/zing/srw/",
    "zr":"http://explain.z3950.org/dtd/2.0/",
    "mg":"info:srw/extension/5/metadata-grouping-v1.0",
    "ppxml":"http://www.oclcpica.org/xmlns/ppxml-1.0"
}

class SRU_Operations(Enum):
    SCAN = "scan"
    EXPLAIN = "explain"
    SEARCH = "searchRetrieve"

class SRU_Record_Schemas(Enum):
    DUBLIN_CORE = "dc"
    PICA = "pica"
    PICA_XML = "ppxml"
    UNIMARC = "unimarc"
    UNIMARC_SHORT = "uni_b"
    PICA_SHORT = "pica_b"
    PICA_SHORT_FCV_XML = "picaxml_b"
    MARC21 = "marc21"
    ISNI_BASIC = "isni-b"
    ISNI_EXTENDED = "isni-e"

class SRU_Record_Packings(Enum):
    XML = "xml"
    STRING = "string"

class Status(Enum):
    ERROR = "Error"
    SUCCESS = "Success"

class Errors(Enum):
    HTTP_ERROR = "Service unavailable"
    GENERIC = "Generic exception, read logs for more information"

class SRU_Indexes(Enum):
    # Index on numbers
    NUMERO_DE_NOTICE_SUDOC = "ppn"
    PPN = "ppn"
    TOUS_NUMEROS = "num"
    NUM = "num"
    ISBN_LIVRES = "isb"
    ISB = "isb"
    ISSN_PERIODIQUES = "isn"
    ISN = "isn"
    NUMERO_NATIONAL_DE_THESE = "nnt"
    NNT = "nnt"
    NUMERO_SOURCE = "sou"
    SOU = "sou"
    NUMERO_DE_NOTICE_WORLDCAT = "ocn"
    OCN = "ocn"
    # Index on title
    MOTS_DU_TITRE = "mti"
    MTI = "mti"
    TITRE_COMPLET = "tco"
    TCO = "tco"
    TITRE_ABREGE_PERIODIQUES = "tab"
    TAB = "tab"
    COLLECTION = "col"
    COL = "col"
    # Index on authors
    MOTS_AUTEUR = "aut"
    AUT = "aut"
    NOM_PERSONNE = "per"
    PER = "per"
    ORGANISME_AUTEUR = "org"
    ORG = "org"
    # Index on subject
    MOTS_SUJETS = "msu"
    MSU = "msu"
    POINT_DACCES_SUJET = "vma"
    VMA = "vma"
    FORME_GENRE = "fgr"
    FGR = "fgr"
    MOTS_SUJETS_ANGLAIS = "msa"
    MSA = "msa"
    SUJET_MESH_ANGLAIS = "mee"
    MEE = "mee"
    # Index on note fields
    NOTE_DE_THESE = "nth"
    NTH = "nth"
    RESUME_SOMMAIRE = "res"
    RES = "res"
    NOTE_DE_LIVRE_ANCIEN = "lva"
    LVA = "lva"
    SOURCE_DU_FINANCEMENT_DE_LA_RESSOURCE = "fir"
    FIR = "fir"
    NOTE_DE_RECOMPENSE = "rec"
    REC = "rec"
    # Index on item fields
    NUMERO_RCR = "rbc"
    RBC = "rbc"
    PLAN_DE_CONSERVATION_PARTAGEE = "pcp"
    PCP = "pcp"
    RELIURE_PROVENANCE_CONSERVATION = "rpc"
    RPC = "rpc"
    BOUQUET_DE_RESSOURCES_EN_LIGNE = "bqt"
    BQT = "bqt"
    # Other index
    TOUS_LES_MOTS = "tou"
    TOU = "tou"
    EDITEUR = "edi"
    EDI = "edi"

class SRU_Filters(Enum):
    TYPE_DE_DOCUMENT = "tdo"
    TDO = "tdo"
    LANGUE_DE_LA_RESSOURCE = "lan"
    LAN = "lan"
    LANGUE_RARE_DE_LA_RESSOURCE = "lai"
    LAI = "lai"
    PAYS_DE_LENTITE_DECRITE = "pay"
    PAY = "pay"
    PAYS_RARE_DE_LENTITE_DECRITE = "pai"
    PAI = "pai"
    ANNEE_DE_PUBLICATION = "apu"
    APU = "apu"

class SRU_Filter_TDO(Enum):
    ARTICLES = "a"
    A = "a"
    MONOGRAPHIES_IMPRIMEES = "b"
    B = "b"
    MANUSCRITS = "f"
    F = "f"
    ENREGISTREMENTS_SONORES_MUSICAUX = "g"
    G = "g"
    IMAGES_FIXES = "i"
    I = "i"
    CARTES_IMPRIMEES_ET_MANUSCRITES = "k"
    K = "k"
    PARTITIONS_MANUSCRITES_ET_IMPRIMEES = "m"
    M = "m"
    ENREGISTREMENTS_SONORES_NON_MUSICAUX = "n"
    N = "n"
    MONOGRAPHIES_ELECTRONIQUES = "o"
    O = "o"
    PERIODIQUES_ET_COLLECTIONS_TOUS_TYPES_DE_SUPPORT = "t"
    T = "t"
    DOCUMENTS_AUDIOVISUELS = "v"
    V = "v"
    OBJETS_DOCUMENTS_MULTIMEDIAS_MULTISUPPORTS = "x"
    X = "x"
    THESE_VERSION_DE_SOUTENANCE_IMPRIMEES_ET_ELECTRONIQUES = "y"
    Y = "y"

class SRU_Filter_LAN(Enum):
    ALLEMAND = "ger"
    GER = "ger"
    ANGLAIS = "eng"
    ENG = "eng"
    ESPAGNOL = "spa"
    SPA = "spa"
    FRANCAIS = "fre"
    FRE = "fre"
    ITALIEN = "ita"
    ITA = "ita"
    LATIN = "lat"
    LAT = "lat"
    NEERLANDAIS = "dut"
    DUT = "dut"
    POLONAIS = "pol"
    POL = "pol"
    PORTUGAIS = "por"
    POR = "por"
    RUSSIE = "rus"
    RUS = "rus"

# Ye LAI is a pain, maybe one day

class SRU_Filter_PAY(Enum):
    ALLEMAGNE = "de"
    DE = "de"
    BELGIQUE = "be"
    BE = "be"
    CANDA = "ca"
    CA = "ca"
    ESPAGNE = "es"
    ES = "es"
    ETATS_UNIS = "us"
    US = "us"
    FRANCE = "fr"
    FR = "fr"
    ITALIE = "it"
    IT = "it"
    PAYS_BAS = "nl"
    NL = "nl"
    ROYAUME_UNI = "gb"
    GB = "gb"
    RUSSIE = "ru"
    RU = "ru"
    SUISSE = "ch"
    CH = "ch"

# Ye PAI is a pain, maybe one day

class SRU_Relations(Enum):
    EQUALS = "="
    EXACT = " exact "
    ANY = " any "
    ALL = " all "
    STRITCLY_INFERIOR = "<"
    STRITCLY_SUPERIOR = ">"
    INFERIOR_OR_EQUAL = "<="
    SUPERIOR_OR_EQUAL = ">="
    NOT = " not "

class SRU_Boolean_Operators(Enum):
    AND = " and "
    OR = " or "
    NOT = " not "

# --------------- Class Objects ---------------

# ---------- SRU Query ----------

class Part_Of_Query(object):
    """Part_Of_Query
    =======
    Generate a Part_Of_Query that can be used in Sudoc_SRU.generate_query() or Sudoc_SRU.generate_scan_clause().
    On init, takes as argument (must provide the right data type) :
        - index {SRU_Indexes or SRU_Filters} : the index to use
        - relation {SRU_Relations} : the relation to use
        - value {str, int, SRU_Filter_TDO, SRU_Filter_LAN or SRU_Filter_PAY} : the value to search in the index
        - [optional] bool_operator {SRU_Boolean_Operators} : the boolean operator to use, defauts to AND"""
    
    def __init__(self, index: SRU_Indexes | SRU_Filters, relation: SRU_Relations, value: str | int | SRU_Filter_TDO | SRU_Filter_LAN | SRU_Filter_PAY, bool_operator=SRU_Boolean_Operators.AND):
        self.bool_operator = bool_operator
        self.index = index
        self.relation = relation
        self.value = value 
        self.invalid = False
        if (
                type(self.bool_operator) != SRU_Boolean_Operators
                or type(self.relation) != SRU_Relations
            ):
            self.invalid = True
        # Checks if it's a filter
        self.is_filter = False
        self.filter_value_is_manual = False
        if type(self.index) == SRU_Filters:
            self.is_filter = True
            # Checks if filters value are OK
            self.is_filter_valid()
        elif type(self.index) != SRU_Indexes:
            self.invalid = True
        
        # Calculated infos
        self.as_string_with_operator = self.to_string(True)
        self.as_string_without_operator = self.to_string(False)

    def is_filter_valid(self):
        """Checks if filters value are valid"""
        # Document type filter
        if self.index.value == SRU_Filters.TDO.value:
            self.is_valid_filter_TDO()
        # Language filter
        elif self.index.value == SRU_Filters.LAN.value:
            self.is_valid_filter_LAN()
        # Rrare languages filter, no Enum so only a form check
        elif self.index.value == SRU_Filters.LAI.value:
            self.is_valid_filter_LAI()
        # Country filter
        elif self.index.value == SRU_Filters.PAY.value:
            self.is_valid_filter_PAY()
        # Rare countries filter, no Enum so only a form check
        elif self.index.value == SRU_Filters.PAI.value:
            self.is_valid_filter_PAI()
        # Publication date filter
        elif self.index.value == SRU_Filters.APU.value:
            self.is_valid_filter_APU()

    def is_valid_filter_TDO(self):
        """Checks if TDO filter value is valid"""
        if type(self.value) != SRU_Filter_TDO:
            if self.value not in [e.value for e in SRU_Filter_TDO]:
                self.invalid = True
            else:
                self.filter_value_is_manual = True

    def is_valid_filter_LAN(self):
        """Checks if LAN filter value is valid"""
        if type(self.value) != SRU_Filter_LAN:
            if self.value not in [e.value for e in SRU_Filter_LAN]:
                self.invalid = True
            else:
                self.filter_value_is_manual = True
    
    def is_valid_filter_LAI(self):
        """Checks if LAI filter value is valid"""
        if not re.search("^[a-zA-Z]{3}$", self.value):
            self.invalid = True
    
    def is_valid_filter_PAY(self):
        """Checks if PAY filter value is valid"""
        if type(self.value) != SRU_Filter_LAN:
            if self.value not in [e.value for e in SRU_Filter_PAY]:
                self.invalid = True
            else:
                self.filter_value_is_manual = True

    def is_valid_filter_PAI(self):
        """Checks if PAI filter value is valid"""
        if not re.search("^[a-zA-Z]{2}$", self.value):
                self.invalid = True

    def is_valid_filter_APU(self):
        """Checks if APU filter value is valid"""
        try:
            int(self.value) # Works with 2000-2023
        except ValueError:
            self.invalid = True
        # Only if ot's not already invalid
        # Inf/sup or equal is not valid absed on APU doc : https://documentation.abes.fr/sudoc/manuels/interrogation/interrogation_professionnelle/index.html#apu
        # Well, WinIBW is fine with it soooooooooo
        if not self.invalid:
            if self.relation.value not in [
                    SRU_Relations.EQUALS.value,
                    SRU_Relations.STRITCLY_SUPERIOR.value,
                    SRU_Relations.STRITCLY_INFERIOR.value,
                    SRU_Relations.SUPERIOR_OR_EQUAL.value,
                    SRU_Relations.INFERIOR_OR_EQUAL.value
                ]:
                self.invalid = True

    def to_string(self, include_operator=True):
        """Returns the Part_Of_Query as a string.
        Takes as parameter :
            - [optional] incule_operator {bool} : include the operator in the output. Defaults to True"""
        
        val = self.value
        # If the filter value was set manually
        if not self.filter_value_is_manual and type(val) not in [str, int]:
            val = val.value
        if not include_operator:
            return f"{self.index.value}{self.relation.value}{val}"
        else:
            return f"{self.bool_operator.value}{self.index.value}{self.relation.value}{val}"

# ---------- SRU ----------

class Sudoc_SRU(object):
    """Sudoc_SRU
    =======
    A set of function to query Sudoc's SRU
    On init take as arguments :
        - [optional] service {str} : Name of the service for the logs"""
    def __init__(self, service="Sudoc_SRU"):
        # Const
        self.endpoint = "https://www.sudoc.abes.fr/cbs/sru/"
        self.version = "1.1" # no choice possible
        # self.record_schema = "unimarc" # no choice possible (says the doc)
        # logs
        self.logger = logging.getLogger(service)
        self.service = service


    def explain(self):
        """GET an explain request from the SRU and returns a SRU_Result_Explain instance"""

        url = f'{self.endpoint}?operation={SRU_Operations.EXPLAIN.value}&version={self.version}'
        status = None
        error_msg = None
        result = ""

        # Request
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            status = Status.ERROR
            error_msg = Errors.HTTP_ERROR
            self.logger.error(f"Explain :: Sudoc_SRU Explain :: HTTP Status: {r.status_code} || Method: {r.request.method} || URL: {r.url} || Response: {r.text}")
        except requests.exceptions.RequestException as generic_error:
            status = Status.ERROR
            self.error_msg = Errors.GENERIC
            self.logger.error(f"Explain :: Sudoc_SRU Explain :: Generic exception || URL: {url} || {generic_error}")
        else:
            status = Status.SUCCESS
            self.logger.debug(f"Explain :: Sudoc_SRU Explain :: Success")
            result = r.content.decode('utf-8')
        
        return SRU_Result_Explain(status, error_msg, result, url)

    def search(self, query: str, record_schema=SRU_Record_Schemas.UNIMARC, record_packing=SRU_Record_Packings.XML, maximum_records=100, start_record=1):
        """GET a search retrieve request from the SRU and returns a SRU_Result_Search instance
        Takes as arguments :
            - query {str} : the query
            - [optional] record_schema {SRU_Record_Schema} : the record schema
            - [optional] record_packing {SRU_Record_packings} : the record packing
            - [optional] maximum_records {int} : the maximum records to be returned (between 1 and 1000)
            - [optional] start_record {int} : the position of the first result in the query result list (> 0)"""
        
        # Query part
        query = urllib.parse.quote(query)
        
        # Convert record schema and record packing to their value
        if type(record_schema) == SRU_Record_Schemas:
            record_schema = record_schema.value
        if type(record_packing) == SRU_Record_Packings:
            record_packing = record_packing.value
        # Checks some input values validity
        if record_schema not in [e.value for e in SRU_Record_Schemas]:
                record_schema = SRU_Record_Schemas.UNIMARC.value
        if record_packing not in [e.value for e in SRU_Record_Packings]:
                record_packing = SRU_Record_Packings.XML.value
        maximum_records = self.to_int(maximum_records)
        if not maximum_records:
            maximum_records = 100
        elif maximum_records > 1001:
            maximum_records = 1000
        elif maximum_records < 1:
            maximum_records = 10
        start_record = self.to_int(start_record)
        if not start_record:
            start_record = 1
        elif start_record < 1:
            start_record = 1

        # Defines the URL
        url = f'{self.endpoint}?operation={SRU_Operations.SEARCH.value}&version={self.version}'\
            f'&recordSchema={record_schema}&recordPacking={record_packing}'\
            f'&startRecord={start_record}&maximumRecords={maximum_records}&query={query}'
        status = None
        error_msg = None
        result = ""

        # Request
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            status = Status.ERROR
            error_msg = Errors.HTTP_ERROR
            self.logger.error(f"{query} :: Sudoc_SRU Search Retrieve :: HTTP Status: {r.status_code} || Method: {r.request.method} || URL: {r.url} || Response: {r.text}")
        except requests.exceptions.RequestException as generic_error:
            status = Status.ERROR
            self.error_msg = Errors.GENERIC
            self.logger.error(f"{query} :: Sudoc_SRU Search Retrieve :: Generic exception || URL: {url} || {generic_error}")
        else:
            status = Status.SUCCESS
            self.logger.debug(f"{query} :: Sudoc_SRU Search Retrieve :: Success")
            result = r.content.decode('utf-8')
        
        return SRU_Result_Search(status, error_msg, result,
                record_schema, record_packing, maximum_records,
                start_record, query, url)

    def scan(self, scan_clause: str, maximum_terms=25, response_position=1):
        """GET a scan request from the SRU and returns a SRU_Result_Scan instance
        Takes as arguments :
            - scan_clause {str} : the query
            - [optional] maximum_terms {int} : the number of returned terms (between 1 and 1000)
            - [optional] response_position {int} : the position of the scanned term in the returned list (> 0)"""
        
        # Query part
        scan_clause = urllib.parse.quote(scan_clause)

        # Checks some input values validity
        maximum_terms = self.to_int(maximum_terms)
        if not maximum_terms:
            maximum_terms = 25
        elif maximum_terms > 1001: # Doc does not say that there's a limit, but better safe than sorry
            maximum_terms = 1000
        elif maximum_terms < 1:
            maximum_terms = 10
        response_position = self.to_int(response_position)
        if not response_position:
            response_position = 1
        elif response_position < 1:
            response_position = 1
        elif response_position > maximum_terms:
            response_position = maximum_terms

        # Defines the URL
        url = f'{self.endpoint}?operation={SRU_Operations.SCAN.value}&version={self.version}'\
            f"&responsePosition={response_position}&maximumTerms={maximum_terms}&scanClause={scan_clause}"
        status = None
        error_msg = None
        result = ""
        
        # request
        try:
            r = requests.get(url)
            r.raise_for_status()
        except requests.exceptions.HTTPError:
            status = Status.ERROR
            error_msg = Errors.HTTP_ERROR
            self.logger.error(f"{scan_clause} :: Sudoc_SRU Scan :: HTTP Status: {r.status_code} || Method: {r.request.method} || URL: {r.url} || Response: {r.text}")
        except requests.exceptions.RequestException as generic_error:
            status = Status.ERROR
            self.error_msg = Errors.GENERIC
            self.logger.error(f"{scan_clause} :: Sudoc_SRU Scan :: Generic exception || URL: {url} || {generic_error}")
        else:
            status = Status.SUCCESS
            self.logger.debug(f"{scan_clause} :: Sudoc_SRU Scan :: Success")
            result = r.content.decode('utf-8')
        
        return SRU_Result_Scan(status, error_msg, result,
                maximum_terms, response_position, scan_clause, url)
        
    def generate_query(self, list: list):
        """Returns a query from multiple parts of query as a string.
        Takes as arguments :
            - list {list of strings or Part_Of_Query instances} : all parts of query to merge
        Any non string or Part_Of_Query instance will be ignored
        Can be use to add parenthesis to a list of Part_Of_Query."""

        output = ""
        for index, query_part in enumerate(list):
            if type(query_part) == str:
                output += query_part
            elif type(query_part) == Part_Of_Query:
                if not query_part.invalid:
                    output += query_part.to_string(bool(index))
        return output

    def generate_scan_clause(self, clause: Part_Of_Query):
        """Returns a scan clause as a string.
        Takes as arguments :
            - clause {Part_Of_Query instance} : the Part_Of_Query instance to return as a string
        Only useful if the scan clause is to be created from a Part_Of_Query instance"""
        return clause.to_string(False)

    def to_int(self, val):
        """Returns None if val can't be a int, else return an int"""
        try:
            int(val) # Works with 2000-2023
        except TypeError:
            return None

        return int(val)

# ---------- SRU Explain Result ----------

class SRU_Result_Explain(object):
    """SRU_Result_Explain
    =======
    A set of function to handle an explain request response from Sudoc's SRU"""

    def __init__(self, status: Status, error: Errors, result: str, url: str):
        self.operation = SRU_Operations.EXPLAIN.value
        self.url = url
        self.status = status.value
        if error:
            self.error = error.value
            return
        else:
            self.error = None
        self.result_as_string = result

        # Generate the result property
        self.result = ET.fromstring(result)

        # Calculated infos
        self.grouping_indexes = self.get_grouping_indexes()
        self.indexes = self.get_indexes()
        self.record_schemas = self.get_record_schemas()
        self.sort_keys = self.get_sort_keys()

    def get_result(self):
            """Return the result as an ET Element."""
            return self.result

    def get_status(self):
        """Return the init status as a string."""
        return self.status

    def get_error_msg(self):
        """Return the error message."""
        return str(self.error)
    
    def get_grouping_indexes(self):
        """Returns a list of all groupings indexes as SRU_Index_From_Explain"""
        output = []
        for sru_index in self.result.find(".//srw:record/srw:recordData/zr:explain/zr:metaInfo/mg:supportedGroupings", XML_NS).findall(".//index"):
            title = sru_index.find("title").text
            index_set = sru_index.find("map/name").attrib["indexSet"]
            key = sru_index.find("map/name").text
            output.append(SRU_Index_From_Explain(title, index_set, key))
        return output
    
    def get_indexes(self):
        """Returns a list of all indexes as SRU_Index_From_Explain"""
        output = []
        for sru_index in self.result.find(".//srw:record/srw:recordData/zr:explain/indexInfo", XML_NS).findall(".//index"):
            title = sru_index.find("title").text
            index_set = sru_index.find("map/name").attrib["indexSet"]
            key = sru_index.find("map/name").text
            output.append(SRU_Index_From_Explain(title, index_set, key))
        return output

    def get_record_schemas(self):
        """Returns a list of all recordSchema as SRU_Record_Schema_From_Explain"""
        output = []
        for record_schema in self.result.find(".//srw:record/srw:recordData/zr:explain/schemaInfo", XML_NS).findall(".//schema"):
            title = record_schema.find("title").text
            uri = record_schema.attrib["uri"]
            sort = record_schema.attrib["sort"]
            retrieve = record_schema.attrib["retrieve"]
            key = record_schema.attrib["name"]
            output.append(SRU_Record_Schema_From_Explain(title, uri, sort, retrieve, key))
        return output

    def get_sort_keys(self):
        """Returns a list of all sortkeys as SRU_Sort_Key_From_Explain"""
        output = []
        for record_schema in self.result.find(".//srw:record/srw:recordData/zr:explain/sortkeyInfo", XML_NS).findall(".//sortkey"):
            title = record_schema.find("title").text
            uri = record_schema.attrib["uri"]
            sort = record_schema.attrib["sort"]
            retrieve = record_schema.attrib["retrieve"]
            key = record_schema.attrib["name"]
            output.append(SRU_Record_Schema_From_Explain(title, uri, sort, retrieve, key))
        return output

# ----- SRU Explain sub-classes -----

class SRU_Index_From_Explain(object):
    """SRU_Index_From_Explain
    =======
    A simple class that extracts data from XML objects"""
    def __init__(self, title: str, index_set: str, key: str):
        self.title = title
        self.index_set = index_set
        self.key = key
        self.as_string = self.to_string()
    
    def to_string(self):
        """Returns all this instance property as a string"""
        return f"{self.index_set}.{self.key} : {self.title}"

class SRU_Record_Schema_From_Explain(object):
    """SRU_Record_Schema_From_Explain
    =======
    A simple class that extracts data from XML objects"""
    def __init__(self, title: str, uri: str, sort: str, retrieve: str, key: str):
        self.title = title
        self.uri = uri
        self.sort = sort
        self.retrieve = retrieve
        self.key = key
        self.as_string = self.to_string()
    
    def to_string(self):
        """Returns all this instance property as a string"""
        return f"{self.title} ({self.key}) : sort={self.sort}, "\
                f"retrieve={self.retrieve}, uri={self.uri}"

class SRU_Sort_Key_From_Explain(object):
    """SRU_Sort_Key_From_Explain
    =======
    A simple class that extracts data from XML objects"""
    def __init__(self, title: str, uri: str, sort: str, retrieve: str, key: str):
        self.title = title
        self.uri = uri
        self.sort = sort
        self.retrieve = retrieve
        self.key = key
        self.as_string = self.to_string()
    
    def to_string(self):
        """Returns all this instance property as a string"""
        return f"{self.title} ({self.key}) : sort={self.sort}, "\
                f"retrieve={self.retrieve}, uri={self.uri}"

# ---------- SRU Search Retrieve Result ----------

class SRU_Result_Search(object):
    """SRU_Result_Search
    =======
    A set of function to handle a search retrieve request response from Sudoc's SRU"""

    closing_tags_fix = "</record></srw:recordData></srw:record>"

    def __init__(self, status: Status, error: Errors, result: str, record_schema: str, record_packing: str, maximum_records: int, start_record: int, query: str, url: str):
        self.operation = SRU_Operations.SEARCH.value
        self.url = url
        self.status = status.value
        if error:
            self.error = error.value
            return
        else:
            self.error = None
        self.result_as_string = result

        # Fix records schemas that can't be parsed [14/09/2023]
        # Pica Xml
        if record_schema in [SRU_Record_Schemas.PICA_XML.value]:
            result = self.fix_angle_brackets()
            # result = re.sub("(?<=<\/ppxml:record>)\s*(?=[<srw:record>|<\/srw:records>])", "</record></srw:recordData></srw:record>", result)
            result = re.sub("(?<=<\/ppxml:record>)\s*(?=(<srw:record>|<\/srw:records>))", self.closing_tags_fix, result)
        # Pica short (fcv XML)
        elif record_schema in [SRU_Record_Schemas.PICA_SHORT_FCV_XML.value]:
            result = re.sub("(?<!<srw:records)>\s*(?=(<srw:record>|<\/srw:records>))", self.closing_tags_fix, result)
            result = re.sub("(?<=<record>)\s*<", "", result)
            result = re.sub(">\s*(?=<\/record>)", "", result) # useless ?
        # Marc 21
        if record_schema in [SRU_Record_Schemas.MARC21.value]:
            result = re.sub("(?<=<leader>)\s*R>", "", result)
            result = re.sub("(<TD>|<TR>)", "", result)
            result = re.sub("(?<=<\/leader>)\s*<\/record>\s*<\/srw:recordData>\s*<srw:recordPosition>\s*leader\s*<\/srw:recordPosition>\s*<\/srw:record>\s*(?!\s*(<srw:record>|<\/srw:records>))", "", result)
        # ISNI Basic & ISNI Extended
        elif record_schema in [SRU_Record_Schemas.ISNI_BASIC.value,
                SRU_Record_Schemas.ISNI_EXTENDED.value,]:
            result = self.fix_angle_brackets()
            result = re.sub("</a>\s*<TR>", "</a></TD></TR>", result)
            result = re.sub("(?<=</TR>)\s*(?=(<srw:record>|<\/srw:records>))", self.closing_tags_fix, result)
        # Fix srw:query not correcting < and > and failing parsing
        fix_srw_query_pattern = r"(<srw:query>.*<\/srw:query>)"
        has_matched = re.search(fix_srw_query_pattern, result)
        if has_matched:
            fixed_query = f"<srw:query>{has_matched.group(1)[11:-12].replace('<', '&lt;').replace('>', '&gt;')}</srw:query>"
            result = re.sub(fix_srw_query_pattern, fixed_query, result)
        self.result_as_parsed_xml = ET.fromstring(result)

        # Generate the result property
        if record_packing == SRU_Record_Packings.XML.value:
            self.result = self.result_as_parsed_xml
        elif record_packing == SRU_Record_Packings.STRING.value:
            self.result = self.result_as_string
        else:
            self.result = "Invalid recordPacking"
        
        # Original query parameters
        self.record_schema = record_schema
        self.record_packing = record_packing
        self.maximum_records = maximum_records
        self.start_record = start_record
        self.query = query
        
        # Calculated infos
        self.nb_results = self.get_nb_results()
        self.records = self.get_records()
        self.records_id = self.get_records_id()

    def get_result(self):
            """Return the result as a string or ET Element depending the chosen recordPacking"""
            return self.result

    def get_status(self):
        """Return the init status as a string."""
        return self.status

    def get_error_msg(self):
        """Return the error message."""
        return str(self.error)

    def get_nb_results(self):
        """Return the number of results as an int."""
        if self.result_as_parsed_xml.findall("srw:numberOfRecords", XML_NS):
            # Somehow FCR crashed because the text was None
            try:
                return int(self.result_as_parsed_xml.find("srw:numberOfRecords", XML_NS).text)
            except:
                return 0
        else: # Prbly not encessary in this SRU
            return 0

    def get_records(self):
        """Returns all records as a list"""
        records = self.result_as_parsed_xml.findall(".//srw:record", XML_NS)
        if self.record_packing == SRU_Record_Packings.XML.value:
            return records
        elif self.record_packing == SRU_Record_Packings.STRING.value:
            output = []
            for record in records:
                output.append(ET.tostring(record))
            return output
        else:
            return []
    
    def get_records_id(self):
        """Returns all records as a list of strings"""
        # Don't have values (or can't be parsed)
        if self.record_schema in [
            SRU_Record_Schemas.DUBLIN_CORE.value,
            SRU_Record_Schemas.PICA_SHORT_FCV_XML.value, # also can't be parsed
            # ↓ those can't be parsed
            # SRU_Record_Schemas.PICA_XML.value,
            # SRU_Record_Schemas.MARC21.value,
            # SRU_Record_Schemas.ISNI_BASIC.value,
            # SRU_Record_Schemas.ISNI_EXTENDED.value
        ]:
            return []
        
        records = self.get_records()
        output = []
        for record in records:
            if self.record_packing == SRU_Record_Packings.STRING.value:
                record = ET.fromstring(record)
            # Controlfield 001 search
            if self.record_schema in [
                SRU_Record_Schemas.UNIMARC.value,
                SRU_Record_Schemas.UNIMARC_SHORT.value,
            ]:
                output.append(record.find(".//controlfield[@tag='001']").text)
            # Datafield 003@ $0 search
            elif self.record_schema in [
                SRU_Record_Schemas.PICA.value,
                SRU_Record_Schemas.PICA_SHORT.value,
            ]:
                output.append(record.find(".//datafield[@tag='003@']/subfield[@code='0']").text)
            # Tag 003@ $0 search
            elif self.record_schema in [
                SRU_Record_Schemas.PICA_XML.value,
                SRU_Record_Schemas.PICA_SHORT_FCV_XML.value,
            ]:
                output.append(record.find(".//ppxml:tag[@id='003@']/ppxml:subf[@id='0']", XML_NS).text)
            # TR TD a href search
            elif self.record_schema in [
                SRU_Record_Schemas.ISNI_BASIC.value,
                SRU_Record_Schemas.ISNI_EXTENDED.value
            ]:
                output.append(re.findall("(?<=https:\/\/www\.sudoc\.fr\/)\d{8}[\d|X]", record.find(".//TR/TD/a").attrib["href"])[0])
            elif self.record_schema in [SRU_Record_Schemas.MARC21.value]:
                output.append(re.findall("(?<=https:\/\/www\.sudoc\.fr\/)\d{8}[\d|X]", record.find(".//leader/a").attrib["href"])[0])
        return output

    def fix_angle_brackets(self):
        """Returns the result_as_string property deleting double brackets"""
        output = re.sub("<\s*<+", "<", self.result_as_string)
        output = re.sub(">\s*>+", ">", output)
        return output

# ---------- SRU Scan Result ----------

class SRU_Result_Scan(object):
    """SRU_Result_Scan
    =======
    A set of function to handle a scan request response from Sudoc's SRU"""
    def __init__(self, status: Status, error: Errors, result: str, maximum_terms: int, response_position: int, scan_clause: str, url: str):
        self.operation = SRU_Operations.SCAN.value
        self.url = url
        self.status = status.value
        if error:
            self.error = error.value
            return
        else:
            self.error = None
        self.result_as_string = result

        # Generate the result property
        self.result = ET.fromstring(result)

        # Original query parameters
        self.maximum_terms = maximum_terms
        self.response_position = response_position
        self.scan_clause = scan_clause

        # Calculated infos
        self.terms = self.get_terms()

    def get_result(self):
            """Return the result as an ET Element."""
            return self.result

    def get_status(self):
        """Return the init status as a string."""
        return self.status

    def get_error_msg(self):
        """Return the error message."""
        return str(self.error)

    def get_terms(self):
        """Returns a list of all terms as SRU_Scanned_Term"""
        output = []
        for term_container in self.result.findall(".//srw:terms/srw:term", XML_NS):
            term = term_container.find("srw:displayTerm", XML_NS).text
            nb_records = term_container.find("srw:numberOfRecords", XML_NS).text
            extra_term_data = term_container.find("srw:extraTermData", XML_NS).text
            value = term_container.find("srw:value", XML_NS).text
            output.append(SRU_Scanned_Term(term, value, nb_records, extra_term_data))
        return output

# ----- SRU Explain sub-classes -----
class SRU_Scanned_Term(object):
    """SRU_Scanned_Term
    =======
    A simple class that extracts data from XML objects"""
    def __init__(self, term: str, value: str, nb_records: str, extra_term_data: str):
        self.term = term
        self.value = value
        self.nb_records = int(nb_records)
        self.extra_term_data = extra_term_data
        self.as_string = self.to_string()
    
    def to_string(self):
        """Returns all this instance property as a string"""
        return f"{self.term} : {self.nb_records}, "\
                f"value={self.value}, extra term data={self.extra_term_data}"
