# -*- coding: utf-8 -*- 

# External import
import xml.etree.ElementTree as ET
import pymarc
from fuzzywuzzy import fuzz
from enum import Enum
from typing import List, Tuple


# Internal imports
from cl_PODA import Processing, Processing_Data_Target, Filters, Mapped_Fields
from cl_ES import Records_Settings, Analysis_Checks
from cl_UDE import Universal_Data_Extractor
from func_string_manip import list_as_string, clean_publisher, nettoie_titre, get_year

# -------------------- Enums --------------------
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

# -------------------- Classes --------------------
class Database_Record(object):
    """Contains extracted data from the record.
    The data property contains every mapped data for the chosen processing"""
    def __init__(self, processing: Processing, record: ET.ElementTree | dict | pymarc.record.Record, fcr_processed_id:str, is_target_db: bool, settings:Records_Settings):
        self.processing = processing
        self.record = record
        self.fcr_processed_id = fcr_processed_id
        self.database = self.processing.origin_database
        if is_target_db:
            self.database = self.processing.target_database
        self.is_target_db = is_target_db
        # Temp var for easyness
        marc_fields_json = settings.origin_db_marc_fields_json
        if self.is_target_db:
            marc_fields_json = settings.target_db_marc_fields_json
        self.ude = Universal_Data_Extractor(self.record, self.database.enum_member, marc_fields_json)
        self.data = {}
        for data in processing.mapped_data:
            if (
                (processing.mapped_data[data] == Processing_Data_Target.BOTH)
                or (self.is_target_db and processing.mapped_data[data] == Processing_Data_Target.TARGET)
                or (not self.is_target_db and processing.mapped_data[data] == Processing_Data_Target.ORIGIN)
            ):
                if data in self.database.filters:
                    filter_value = ""
                    if self.database.filters[data] == Filters.RCR:
                        filter_value = settings.rcr
                    elif self.database.filters[data] == Filters.ILN:
                        filter_value = settings.iln
                    elif self.database.filters[data] == Filters.FILTER1:
                        filter_value = settings.filter1
                    elif self.database.filters[data] == Filters.FILTER2:
                        filter_value = settings.filter2
                    elif self.database.filters[data] == Filters.FILTER3:
                        filter_value = settings.filter3
                    self.data[data] = self.ude.get_by_mapped_field_name(data, filter_value)
                else:
                    self.data[data] = self.ude.get_by_mapped_field_name(data)
        self.chosen_analysis = settings.chosen_analysis
        self.chosen_analysis_checks = settings.chosen_analysis_checks
        self.utils = self.Utils(self)

    def __compare_titles(self, compared_to):
        """Compares the titles and sets their keys"""
        self.compared_title_key = compared_to.utils.get_first_title_as_string()
        self.title_key = self.utils.get_first_title_as_string()
        self.title_ratio = fuzz.ratio(self.title_key, self.compared_title_key)
        self.title_partial_ratio = fuzz.partial_ratio(self.title_key, self.compared_title_key)
        self.title_token_sort_ratio = fuzz.token_sort_ratio(self.title_key, self.compared_title_key)
        self.title_token_set_ratio = fuzz.token_set_ratio(self.title_key, self.compared_title_key)
    
    def __compare_dates(self, compared_to) -> None:
        """Compares if one of the record dates matches on one of the compared record."""
        self.dates_matched = False
        # Merge dates lists
        this_dates = []
        for dates in self.data[Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]:
            this_dates.extend(dates)
        compared_dates = []
        for dates in compared_to.data[Mapped_Fields.GENERAL_PROCESSING_DATA_DATES]:
            compared_dates.extend(dates)
        for date in this_dates:
            if date in compared_dates and date != "    ": # excludes empty dates
                self.dates_matched = True
                return
    
    def __compare_publishers(self, compared_to) -> None:
        """Compares every publishers in this record with every publishers in comapred record"""
        self.publishers_score = -1
        self.chosen_publisher = ""
        self.chosen_compared_publisher = ""
        # I fboth don't have results, comparison can't be done
        if len(self.data[Mapped_Fields.PUBLISHERS_NAME]) == 0 or len(compared_to.data[Mapped_Fields.PUBLISHERS_NAME]) == 0:
            return
        for publisher in self.data[Mapped_Fields.PUBLISHERS_NAME]:
            publisher = clean_publisher(publisher)
            for compared_publisher in compared_to.data[Mapped_Fields.PUBLISHERS_NAME]:
                compared_publisher = clean_publisher(compared_publisher)
                ratio = fuzz.ratio(publisher, compared_publisher)
                if ratio > self.publishers_score:
                    self.publishers_score = ratio
                    self.chosen_publisher = publisher
                    self.chosen_compared_publisher = compared_publisher

    def __compare_other_db_id(self, compared_to):
        """Checks if this record id is in the comapred other database IDs"""
        self.local_id_in_compared_record = Other_Database_Id_In_Target.UNKNOWN
        self.list_of_other_db_id = self.utils.get_other_db_id()
        # Other DB IDs are not extracted
        if self.list_of_other_db_id == None:
            self.local_id_in_compared_record = Other_Database_Id_In_Target.SKIPPED
            self.nb_other_db_id = 0
            return
        # They were extracted
        self.nb_other_db_id = len(self.list_of_other_db_id)
        id = list_as_string(compared_to.data[Mapped_Fields.ID])
        if self.nb_other_db_id == 0:
            self.local_id_in_compared_record = Other_Database_Id_In_Target.NO_OTHER_DB_ID
        elif self.nb_other_db_id == 1 and id in self.list_of_other_db_id:
            self.local_id_in_compared_record = Other_Database_Id_In_Target.ONLY_THIS_OTHER_DB_ID
        elif self.nb_other_db_id > 1 and id in self.list_of_other_db_id:
            self.local_id_in_compared_record = Other_Database_Id_In_Target.THIS_ID_INCLUDED
        elif id not in self.list_of_other_db_id:
            self.local_id_in_compared_record = Other_Database_Id_In_Target.THIS_ID_NOT_INCLUDED

    def __analysis_check_title(self):
        self.check_title_nb_valids = 0
        # for each matching score, checks if it's high enough
        title_score_list = [
            self.title_ratio,
            self.title_partial_ratio,
            self.title_token_sort_ratio,
            self.title_token_set_ratio
            ]
        for title_score in title_score_list:
            if title_score >= self.chosen_analysis["TITLE_MIN_SCORE"]:
                self.check_title_nb_valids += 1
        self.checks[Analysis_Checks.TITLE] = (self.check_title_nb_valids >= self.chosen_analysis["NB_TITLE_OK"])

    def __analysis_checks(self, check):
        """Launches the check for the provided analysis"""
        # Titles
        if check == Analysis_Checks.TITLE:
            self.__analysis_check_title()
        # Publishers
        elif check == Analysis_Checks.PUBLISHER:
            self.checks[Analysis_Checks.PUBLISHER] = (self.publishers_score >= self.chosen_analysis["PUBLISHER_MIN_SCORE"])
        # Dates
        elif check == Analysis_Checks.DATE:
            self.checks[Analysis_Checks.DATE] = self.dates_matched

    def __finalize_analysis(self):
        """Summarizes all checks"""
        self.total_checks = Analysis_Final_Results.UNKNOWN
        self.passed_check_nb = 0
        self.checks = {}
        for check in Analysis_Checks:
            self.checks[check] = None
        if len(self.chosen_analysis_checks) == 0:
            self.total_checks = Analysis_Final_Results.NO_CHECK
        else:
            for check in self.chosen_analysis_checks:
                self.__analysis_checks(check)
                if self.checks[check] == True:
                    self.passed_check_nb += 1
            if self.passed_check_nb == len(self.chosen_analysis_checks):
                self.total_checks = Analysis_Final_Results.TOTAL_MATCH
            elif self.passed_check_nb > 0:
                self.total_checks = Analysis_Final_Results.PARTIAL_MATCH
            else:
                self.total_checks = Analysis_Final_Results.NO_MATCH

    def compare_to(self, compared_to):
        """Execute the analysis processs
        Takes as argument:
        - compared_to {Database_Record instance} : the record from origin database"""
        self.__compare_titles(compared_to)
        self.__compare_dates(compared_to)
        self.__compare_publishers(compared_to)
        self.__compare_other_db_id(compared_to)
        self.__finalize_analysis()

    def data_to_json(self) -> dict:
        """Returns the data for a JSOn export, using Mapped_Fields names as keys"""
        out = {}
        for data in self.data:
            out[data.name] = self.data[data]
        return out

    def analysis_to_json(self) -> dict:
        """Returns the analysis data as a dict for a JSON export"""
        if type(self.total_checks) == Analysis_Final_Results:
            return {
                "title":{
                    "title_ratio":self.title_ratio,
                    "title_partial_ratio":self.title_partial_ratio,
                    "title_token_sort_ratio":self.title_token_sort_ratio,
                    "title_token_set_ratio":self.title_token_set_ratio,
                },
                "dates":self.dates_matched,
                "publishers":{
                    "score":self.publishers_score,
                    "target_db":self.chosen_publisher,
                    "origin_db":self.chosen_compared_publisher
                },
                "other_ids":{
                    "nb":self.nb_other_db_id,
                    "result":self.local_id_in_compared_record.name
                },
                "global":{
                    "result":self.total_checks.name,
                    "nb_succesful_checks":self.passed_check_nb,
                    "title":self.checks[Analysis_Checks.TITLE],
                    "publisher":self.checks[Analysis_Checks.PUBLISHER],
                    "date":self.checks[Analysis_Checks.DATE]
                }
            }
        else:
            return None
    
    # --- Utils methods for other classes / functions ---
    class Utils:
        def __init__(self, parent) -> None:
            self.parent = parent
            self.data: dict = self.parent.data

        def get_id(self) -> str:
            """Returns the record ID as a string"""
            if not Mapped_Fields.ID in self.data:
                return ""
            return list_as_string(self.data[Mapped_Fields.ID])

        def get_first_title_as_string(self) -> str:
            """Returns the first title cleaned up as a string"""
            if not Mapped_Fields.TITLE in self.data:
                return ""
            if len(self.data[Mapped_Fields.TITLE]) < 1:
                return ""
            return nettoie_titre(list_as_string(self.data[Mapped_Fields.TITLE][0]))

        def get_titles_as_string(self) -> str:
            """Returns all titles cleaned up as a str"""
            if not Mapped_Fields.TITLE in self.data:
                return ""
            return nettoie_titre(list_as_string(self.data[Mapped_Fields.TITLE]))

        def get_authors_as_string(self) -> str:
            """Returns all authors cleaned up as a str"""
            if not Mapped_Fields.AUTHORS in self.data:
                return ""
            return nettoie_titre(list_as_string(self.data[Mapped_Fields.AUTHORS]))

        def get_all_publishers_as_string(self) -> str:
            """Returns all authors cleaned up as a str"""
            if not Mapped_Fields.PUBLISHERS_NAME in self.data:
                return ""
            return clean_publisher(list_as_string(self.data[Mapped_Fields.PUBLISHERS_NAME]))

        def get_all_publication_dates(self) -> Tuple[List[int], int, int]:
            """Returns a tuple :
                - all publication dates as a list of int
                - the oldest date as a int (None if no date)
                - the newest date as a int (None if no date)"""
            dates = []
            if not Mapped_Fields.PUBLICATION_DATES in self.data:
                return dates, None, None
            for date_str in self.data[Mapped_Fields.PUBLICATION_DATES]:
                dates += get_year(date_str)
            # Intifies
            for date in dates:
                date = int(date)
            if dates == []:
                return dates, None, None
            return dates, min(dates), max(dates)
        
        def get_first_ean_as_string(self) -> str:
            """Returns the first EAN as a str"""
            ean = ""
            if not Mapped_Fields.EAN in self.data:
                return ean
            for val in self.data[Mapped_Fields.EAN]:
                if type(val) == str and val != "":
                    ean = val
                    break
            return ean

        def get_first_isbn_as_string(self) -> str:
            """Returns the first ISBN as a str"""
            isbn = ""
            if not Mapped_Fields.ISBN in self.data:
                return isbn
            for val in self.data[Mapped_Fields.ISBN]:
                if type(val) == str and val != "":
                    isbn = val
                    break
            return isbn
        
        def get_other_db_id(self) -> List[str]|None:
            """Returns the other DB IDs as a list of str.
            Returns None if data was not extracted"""
            if not Mapped_Fields.OTHER_DB_ID in self.data:
                return None
            return self.data[Mapped_Fields.OTHER_DB_ID]