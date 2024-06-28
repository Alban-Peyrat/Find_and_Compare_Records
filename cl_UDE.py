# -*- coding: utf-8 -*- 

# External import
import re
import pymarc
import xml.etree.ElementTree as ET
from enum import Enum
from typing import List, Optional, Union

# Internal imports

# --------------- Enums ---------------
class Mapped_Fields(Enum):
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
    DOCUMENT_TYPE = "document_type"
    LINKING_PIECE = "linking_piece"

class Record_Formats(Enum):
    """List of supported record formats"""
    UNKNOWN = 0
    JSON_DICT = 1
    ET_ELEMENT = 2
    PYMARC_RECORD = 3

class Database_Names(Enum):
    ABESXML = 0
    SUDOC_SRU = 1
    KOHA_PUBLIC_BIBLIO = 2
    KOHA_SRU = 3
    LOCAL = 4

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

# --------------- Classes ---------------
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
    def __init__(self, marc_fields_json:dict):
        """Loads the marc field mapping"""
        # Just throw an error if is_target_db is not a bool
        self.marc_fields_json = marc_fields_json
        self.load_mapping()
    
    def load_mapping(self):
        """Loads a marc field mappig by name from marc_fields.json (debgging)"""
        self.id = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.ID.value])
        self.ppn = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.PPN.value])
        self.document_type = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.DOCUMENT_TYPE.value])
        self.ean = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.EAN.value])
        self.isbn = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.ISBN.value])
        self.general_processing_data_dates = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.GENERAL_PROCESSING_DATA_DATES.value])
        self.erroneous_isbn = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.ERRONEOUS_ISBN.value])
        self.title = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.TITLE.value])
        self.authors = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.AUTHORS.value])
        self.publishers_name = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.PUBLISHERS_NAME.value])
        self.edition_note = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.EDITION_NOTES.value])
        self.publication_dates = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.PUBLICATION_DATES.value])
        self.contents_notes = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.CONTENTS_NOTES.value])
        self.physical_desription = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.PHYSICAL_DESCRIPTION.value])
        self.other_edition_in_other_medium_bibliographic_id = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.OTHER_ED_IN_OTHER_MEDIUM_BIBG_ID.value])
        self.other_database_id = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.OTHER_DB_ID.value])
        self.linking_piece = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.LINKING_PIECE.value])
        self.items = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.ITEMS.value])
        self.items_barcode = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.ITEMS_BARCODE.value])
        self.exported_to_digital_library = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.EXPORTED_TO_DIGITAL_LIBRARY.value])
        self.maps_horizontal_scale = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.MAPS_HORIZONTAL_SCALE.value])
        self.maps_mathematical_data = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.MAPS_MATHEMATICAL_DATA.value])
        self.series = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.SERIES.value])
        self.series_link = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.SERIES_LINK.value])
        self.geographical_subject = Marc_Fields_Data(self.marc_fields_json[Mapped_Fields.GEOGRAPHICAL_SUBJECT.value])

class Universal_Data_Extractor(object):
    """Central class to extract data from a record.
    
    Takes as argument :
        - the parsed record
        - Database_Names member
        - is_target_db {bool} : determines if the database is ORIGIN_DATABSE/TARGET_DATABASE
    in marc_fields.json
        - es : execution settings"""
    def __init__(self, record: ET.ElementTree | dict | pymarc.record.Record, database: Database_Names, marc_fields_json: dict):
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
        self.marc_fields_mapping = Marc_Fields_Mapping(marc_fields_json)
    
    # --- Resources methods ---

    def get_xml_namespace(self) -> str:
        """Returns the namespace code with a "/" at the beginning and a ":" at the end"""
        if self.database == Database_Names.KOHA_PUBLIC_BIBLIO:
            return "/" + Xml_Namespaces.MARC.value + ":"
        elif self.database == Database_Names.KOHA_SRU:
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
                    # Restrict beginning and end to the max length if they're too high
                    if begining > len(field_text):
                        begining = len(field_text)
                    if end > len(field_text):
                        end = len(field_text)
                    # End must be > begin and can be equal to the len
                    if begining < len(field_text) and end <= len(field_text) and begining < end:
                        output.append(field_text[begining:end])
        return output

    # --- Get targetted data ---
    def get_by_mapped_field_name(self, mapped_field: Mapped_Fields, filter_value: Optional[str] = ""):
        """Calls the correct get function based on Mapped_Fields"""
        if mapped_field == Mapped_Fields.LEADER:
            return self.get_leader()
        elif mapped_field == Mapped_Fields.ID:
            return self.get_id(filter_value)
        elif mapped_field == Mapped_Fields.PPN:
            return self.get_ppn(filter_value)
        elif mapped_field == Mapped_Fields.DOCUMENT_TYPE:
            return self.get_document_type(filter_value)
        elif mapped_field == Mapped_Fields.EAN:
            return self.get_ean(filter_value)
        elif mapped_field == Mapped_Fields.ISBN:
            return self.get_isbn(filter_value)
        elif mapped_field == Mapped_Fields.GENERAL_PROCESSING_DATA_DATES:
            return self.get_general_processing_data_dates(filter_value)
        elif mapped_field == Mapped_Fields.ERRONEOUS_ISBN:
            return self.get_erroneous_ISBN(filter_value)
        elif mapped_field == Mapped_Fields.TITLE:
            return self.get_title(filter_value)
        elif mapped_field == Mapped_Fields.AUTHORS:
            return self.get_authors(filter_value)
        elif mapped_field == Mapped_Fields.PUBLISHERS_NAME:
            return self.get_publishers_name(filter_value)
        elif mapped_field == Mapped_Fields.EDITION_NOTES:
            return self.get_edition_notes(filter_value)
        elif mapped_field == Mapped_Fields.PUBLICATION_DATES:
            return self.get_publication_dates(filter_value)
        elif mapped_field == Mapped_Fields.PHYSICAL_DESCRIPTION:
            return self.get_physical_description(filter_value)    
        elif mapped_field == Mapped_Fields.CONTENTS_NOTES:
            return self.get_contents_notes(filter_value)
        elif mapped_field == Mapped_Fields.GENERAL_PROCESSING_DATA_DATES:
            return self.get_general_processing_data_dates(filter_value)
        elif mapped_field == Mapped_Fields.OTHER_ED_IN_OTHER_MEDIUM_BIBG_ID:
            return self.get_other_edition_in_other_medium_bibliographic_id(filter_value)
        elif mapped_field == Mapped_Fields.LINKING_PIECE:
            return self.get_linking_piece(filter_value)
        elif mapped_field == Mapped_Fields.OTHER_DB_ID:
            return self.get_other_database_id(filter_value)
        elif mapped_field == Mapped_Fields.ITEMS:
            return self.get_items(filter_value)
        elif mapped_field == Mapped_Fields.ITEMS_BARCODE:
            return self.get_items_barcode(filter_value)
        elif mapped_field == Mapped_Fields.EXPORTED_TO_DIGITAL_LIBRARY:
            return self.get_exported_to_digital_library(filter_value)
        elif mapped_field == Mapped_Fields.MAPS_HORIZONTAL_SCALE:
            return self.get_maps_horizontal_scale(filter_value)
        elif mapped_field == Mapped_Fields.MAPS_MATHEMATICAL_DATA:
            return self.get_maps_mathematical_data(filter_value)
        elif mapped_field == Mapped_Fields.SERIES:
            return self.get_series(filter_value)
        elif mapped_field == Mapped_Fields.SERIES_LINK:
            return self.get_series_link(filter_value)
        elif mapped_field == Mapped_Fields.GEOGRAPHICAL_SUBJECT:
            return self.get_geographical_subject(filter_value)

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

    def get_document_type(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all document types as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.document_type, filter_value)
    
    def get_ean(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all EAN as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.ean, filter_value)

    def get_isbn(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all ISBN as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.isbn, filter_value)
    
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

    def get_linking_piece(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all of pieces (link) as a list of str.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.linking_piece, filter_value)

    def get_items_barcode(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all items barcode as a list of str, without duplicates.

        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_ids(self.marc_fields_mapping.items_barcode, filter_value)
    
    def get_exported_to_digital_library(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as exported to digital library as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.exported_to_digital_library, filter_value)
    
    def get_maps_horizontal_scale(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as maps horizontal scales as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.maps_horizontal_scale, filter_value)
    
    def get_maps_mathematical_data(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as maps mathematical data as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.maps_mathematical_data, filter_value)
    
    def get_series(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as series as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.series, filter_value)

    def get_series_link(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as series link as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.series_link, filter_value)

    def get_geographical_subject(self, filter_value: Optional[str] = "") -> List[str]:
        """Return all fields mapped as geographical subject as a list of strings
        Each subfield is separated by a space
        
        Takes filter_value as argument if mapped to have a filtering subfield."""
        return self.extract_list_of_strings(self.marc_fields_mapping.geographical_subject, filter_value)    

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
            valid_values = []
            for value in field_value:
                if value:
                    valid_values.append(value)
            output.append(" ".join(valid_values))
        return output
    
    def extract_list_of_lists(self,marc_field: Marc_Fields_Data, filter_value: Optional[str] = "") -> List[str]:
        """Generic funciton to get a list, merging only one layer, so, supposedly, a list of list"""
        output = []
        extraction = self.extract_data_from_marc_field(marc_field, filter_value)
        output = self.flatten_list(extraction, False)
        return output