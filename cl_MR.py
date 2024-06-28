# -*- coding: utf-8 -*- 

# External import
import pyisbn
import re
from enum import Enum
from typing import List

# Internal imports
from cl_error import Errors, get_error_instance
from cl_PODA import Operation, Action_Names
from cl_DBR import Database_Record
from func_string_manip import delete_for_sudoc

# ----- Match Records imports -----
# Internal imports
import api.abes.Abes_id2ppn as id2ppn
import api.abes.Sudoc_SRU as ssru
import api.koha.Koha_SRU as ksru

class Try_Status(Enum):
    UNKNWON = 0
    SUCCESS = 1
    ERROR = 2

class Request_Try(object):
    """"""
    def __init__(self, try_nb: int, action: Action_Names, lang:str):
        self.try_nb = try_nb
        self.action = action
        self.lang = lang
        self.status = Try_Status.UNKNWON
        self.error_type = None
        self.msg = None
        self.query = None
        self.returned_ids = []
        self.returned_records = []
        self.includes_records = False
    
    def error_occured(self, msg: Errors | str):
        if type(msg) == Errors:
            self.error_type = msg
            self.msg = get_error_instance(self.error_type).get_msg(self.lang)
        else:
            self.error_type = Errors.GENERIC_ERROR
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
    
    def to_json(self) -> dict:
        """Retuns the data ready for a JSON export"""
        error_type = None
        if type(self.error_type) == Errors:
            error_type = self.error_type.name
        return {
            "try_nb":self.try_nb,
            "action":self.action.name,
            "status":self.status.name,
            "error_type":error_type,
            "msg":self.msg,
            "query":self.query,
            "returned_ids":self.returned_ids
        }
    
class Matched_Records(object):
    """
    
    Takes as argument :
        - operation {Operation Instance}"""
    def __init__(self, operation: Operation, query: str, local_record:Database_Record, target_url:str, lang:str):
        self.error = None
        self.error_msg = None
        self.tries:List[Request_Try] = []
        self.returned_ids = []
        self.returned_records = []
        self.includes_record = False
        self.operation = operation # Removed default operation, I'd rather it threw an error
        self.query = query
        self.local_record = local_record
        self.target_url = target_url
        self.lang = lang

        # Calls the operation
        self.execute_operation()
        last_try:Request_Try = self.tries[-1]
        self.query = last_try.query
        self.action = last_try.action

    def execute_operation(self):
        """Searches in the Sudoc with 3 possibles tries :
            - isbn2ppn
            - if failed, isbn2ppn after ISBN conversion
            - if failed again, Sudoc SRU on ISB index
        
        Requires match_records query to be an ISBN"""
        for index, action in enumerate(self.operation.actions):
            thisTry = Request_Try(index, action, self.lang)
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
            self.error = Errors.NOTHING_WAS_FOUND
            self.error_msg = get_error_instance(self.error).get_msg(self.lang)

    def tries_to_json(self) -> dict:
        """Returns the tries as a dict ready for JSON export"""
        out = {}
        for this_try in self.tries:
            out[this_try.try_nb] = this_try.to_json()
        return out

    def request_action(self, action: Action_Names, thisTry: Request_Try):
        """Makes the request for this specific action and returns a list of IDs as a result"""
        # Action_Names based on the same connector are siilar, do not forget to udate all of them

        #to avoid redundance
        # Extract data
        title = delete_for_sudoc(self.local_record.utils.get_titles_as_string())
        author = delete_for_sudoc(self.local_record.utils.get_authors_as_string())
        publisher = delete_for_sudoc(self.local_record.utils.get_all_publishers_as_string())
        dates, oldest_date, newest_date = self.local_record.utils.get_all_publication_dates()
        ean = self.local_record.utils.get_first_ean_as_string()
        isbn = self.local_record.utils.get_first_isbn_as_string()

        # Action SRU SUdoc ISBN
        if action == Action_Names.SRU_SUDOC_ISBN:
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
        elif action == Action_Names.ISBN2PPN:
            i2p = id2ppn.Abes_id2ppn(webservice=id2ppn.Webservice.ISBN, useJson=True)
            res = i2p.get_matching_ppn(self.query, check_isbn_validity=True)
            thisTry.define_used_query(res.get_id_used())
            if res.status != id2ppn.Id2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action isbn2ppn with changed ISBN
        elif action == Action_Names.ISBN2PPN_MODIFIED_ISBN:
            # Converting the ISBN to 10<->13
            isbn_validity, temp, new_query = id2ppn.validate_isbn(re.sub("[^0-9X]", "", str(self.query)))
            if isbn_validity != id2ppn.Isbn_Validity.VALID:
                thisTry.error_occured(Errors.ISBN_MODIFICATION_FAILED)
                return
            if new_query[:3] != "978" and len(new_query) == 13:
                thisTry.error_occured(Errors.ISBN_979_CAN_NOT_BE_CONVERTED)
                return
            new_query = pyisbn.Isbn(re.sub("[^0-9X]", "", str(new_query))).convert()

            # Ensure ISBN is not empty 
            if not new_query:
                thisTry.error_occured(Errors.ISBN_MODIFICATION_FAILED)
                return

            # Same thing as Action ISBN2PPN
            i2p = id2ppn.Abes_id2ppn(useJson=True)
            res = i2p.get_matching_ppn(new_query, check_isbn_validity=True)
            thisTry.define_used_query(res.get_id_used())
            if res.status != id2ppn.Id2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action isbn2ppn with changed ISBN without recomputing th ekey
        elif action == Action_Names.ISBN2PPN_MODIFIED_ISBN_SAME_KEY:
            # Converting the ISBN to 10<->13 
            new_query = None
            if len(self.query) == 13:
                new_query = self.query[3:]
            elif len(self.query) == 10:
                # Doesn't consider 979[...] as the original issue should only concern old ISBN
                new_query = "978" + self.query
            
            # Ensure ISBN is not empty 
            if not new_query:
                thisTry.error_occured(Errors.ISBN_MODIFICATION_FAILED)
                return
            
            # Same thing as Action ISBN2PPN
            i2p = id2ppn.Abes_id2ppn(useJson=True)
            res = i2p.get_matching_ppn(new_query, check_isbn_validity=False)
            thisTry.define_used_query(res.get_id_used())
            if res.status != id2ppn.Id2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action SRU SUdoc EAN
        elif action == Action_Names.EAN2PPN:
            # No EAN was found, throw an error
            if ean == "":
                thisTry.error_occured(Errors.NO_EAN_WAS_FOUND)
                return
            i2p = id2ppn.Abes_id2ppn(webservice=id2ppn.Webservice.EAN, useJson=True)
            res = i2p.get_matching_ppn(ean)
            thisTry.define_used_query(ean)
            if res.status != id2ppn.Id2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action SRU Sudoc on data fields (Title, Author, Publisher, Date or DocType)
        elif action in [
                Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V,
                Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_V,
                Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V,
                Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_V,
                Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V,
                Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B,
                Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_B,
                Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B,
                Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_B,
                Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_B,
                Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K,
                Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_K,
                Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K,
                Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_K,
                Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_K,
                Action_Names.SRU_SUDOC_MTI,
                Action_Names.SRU_SUDOC_MTI_TDO_B,
                Action_Names.SRU_SUDOC_MTI_TDO_K,
                Action_Names.SRU_SUDOC_MTI_TDO_V
                ]:
            sru = ssru.Sudoc_SRU()
            sru_request = []
            # TITLE
            if action in [
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V,
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_K,
                        Action_Names.SRU_SUDOC_MTI,
                        Action_Names.SRU_SUDOC_MTI_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_TDO_K,
                        Action_Names.SRU_SUDOC_MTI_TDO_V
                    ]:
                # Leave if empty
                if title.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_DATA_MISSING)
                    return
                # Else, append to query
                sru_request.append(ssru.Part_Of_Query(
                    ssru.SRU_Indexes.MTI,
                    ssru.SRU_Relations.EQUALS,
                    title,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # AUTHORS
            if action in [
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V,
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_K
                    ]:
                # Leave if empty
                if author.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_DATA_MISSING)
                    return
                # Else, append to query
                sru_request.append(ssru.Part_Of_Query(
                    ssru.SRU_Indexes.AUT,
                    ssru.SRU_Relations.EQUALS,
                    author,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # PUBLISHER
            if action in [
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V,
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_K
                    ]:
                # Leave if empty
                if publisher.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_DATA_MISSING)
                    return
                # Else, append to query
                sru_request.append(ssru.Part_Of_Query(
                    ssru.SRU_Indexes.EDI,
                    ssru.SRU_Relations.EQUALS,
                    publisher,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # DATES        
            if action in [
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_V,
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_K
                    ]:
                # Leave if empty
                if len(dates) < 1:
                    thisTry.error_occured(Errors.REQUIRED_DATA_MISSING)
                    return
                # Else, append to query
                sru_request.append(ssru.Part_Of_Query(
                    ssru.SRU_Filters.APU,
                    ssru.SRU_Relations.SUPERIOR_OR_EQUAL,
                    oldest_date,
                    ssru.SRU_Boolean_Operators.AND
                ))
                sru_request.append(ssru.Part_Of_Query(
                    ssru.SRU_Filters.APU,
                    ssru.SRU_Relations.INFERIOR_OR_EQUAL,
                    newest_date,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # FILTERS We can use a IF - ELIF here
            # TDO B
            if action in [
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_B,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_B,
                        Action_Names.SRU_SUDOC_MTI_TDO_B
                    ]:
                sru_request.append(ssru.Part_Of_Query(
                    ssru.SRU_Filters.TDO,
                    ssru.SRU_Relations.EQUALS,
                    ssru.SRU_Filter_TDO.B,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # TDO K
            elif action in [
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_K,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_K,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_K,
                        Action_Names.SRU_SUDOC_MTI_TDO_K
                    ]:
                sru_request.append(ssru.Part_Of_Query(
                    ssru.SRU_Filters.TDO,
                    ssru.SRU_Relations.EQUALS,
                    ssru.SRU_Filter_TDO.K,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # TDO V
            elif action in [
                        Action_Names.SRU_SUDOC_MTI_AUT_EDI_APU_TDO_V,
                        Action_Names.SRU_SUDOC_MTI_AUT_APU_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_DATE_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_DATE_TDO_V,
                        Action_Names.SRU_SUDOC_TOU_TITLE_AUTHOR_PUBLISHER_TDO_V,
                        Action_Names.SRU_SUDOC_MTI_TDO_V
                    ]:
                sru_request.append(ssru.Part_Of_Query(
                    ssru.SRU_Filters.TDO,
                    ssru.SRU_Relations.EQUALS,
                    ssru.SRU_Filter_TDO.V,
                    ssru.SRU_Boolean_Operators.AND
                )) 
            # launch search
            thisTry.define_used_query(sru.generate_query(sru_request))
            res = sru.search(
                thisTry.query,
                record_schema=ssru.SRU_Record_Schemas.UNIMARC,
                record_packing=ssru.SRU_Record_Packings.XML,
                maximum_records=100,
                start_record=1
            )
            # Interpret results
            if (res.status == "Error"):
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_records_id())
                thisTry.add_returned_records(res.get_records())

        # Action Koha SRU ISBN
        elif action == Action_Names.KOHA_SRU_IBSN:
            # No ISBN was found, throw an error
            if isbn == "":
                thisTry.error_occured(Errors.NO_ISBN_WAS_FOUND)
                return
            sru = ksru.Koha_SRU(self.target_url, ksru.SRU_Version.V1_1)
            sru_request = ksru.Part_Of_Query(
                ksru.SRU_Indexes.ISBN,
                ksru.SRU_Relations.EQUALS,
                isbn
            )
            thisTry.define_used_query(sru.generate_query([sru_request]))
            res = sru.search(
                thisTry.query,
                record_schema=ksru.SRU_Record_Schemas.MARCXML,
                start_record=1,
                maximum_records=100
            )
            if (res.status == "Error"):
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_records_id())
                thisTry.add_returned_records(res.get_records())

        # Action SRU Koha on data fields (Title, Author, Publisher, Date)
        elif action in [
                    Action_Names.KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE,
                    Action_Names.KOHA_SRU_TITLE_AUTHOR_DATE,
                    Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE,
                    Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_DATE,
                    Action_Names.KOHA_SRU_ANY_TITLE_PUBLISHER_DATE,
                    Action_Names.KOHA_SRU_TITLE
                ]:
            sru = ksru.Koha_SRU(self.target_url, ksru.SRU_Version.V1_1)
            sru_request = []
            # TITLE
            if action in [
                        Action_Names.KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE,
                        Action_Names.KOHA_SRU_TITLE_AUTHOR_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_PUBLISHER_DATE,
                        Action_Names.KOHA_SRU_TITLE
                    ]:
                # Leave if empty
                if title.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_DATA_MISSING)
                    return
                # Else, append to query
                sru_request.append(ksru.Part_Of_Query(
                    ksru.SRU_Indexes.TITLE,
                    ksru.SRU_Relations.EQUALS,
                    title,
                    ksru.SRU_Boolean_Operators.AND
                ))
            # AUTHORS
            if action in [
                        Action_Names.KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE,
                        Action_Names.KOHA_SRU_TITLE_AUTHOR_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_DATE
                    ]:
                # Leave if empty
                if author.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_DATA_MISSING)
                    return
                # Else, append to query
                sru_request.append(ksru.Part_Of_Query(
                    ksru.SRU_Indexes.AUTHOR,
                    ksru.SRU_Relations.EQUALS,
                    author,
                    ksru.SRU_Boolean_Operators.AND
                ))
            # PUBLISHER
            if action in [
                        Action_Names.KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_PUBLISHER_DATE
                    ]:
                # Leave if empty
                if publisher.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_DATA_MISSING)
                    return
                # Else, append to query
                sru_request.append(ksru.Part_Of_Query(
                    ksru.SRU_Indexes.PUBLISHER,
                    ksru.SRU_Relations.EQUALS,
                    publisher,
                    ksru.SRU_Boolean_Operators.AND
                ))
            # DATES        
            if action in [
                        Action_Names.KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE,
                        Action_Names.KOHA_SRU_TITLE_AUTHOR_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_DATE,
                        Action_Names.KOHA_SRU_ANY_TITLE_PUBLISHER_DATE
                    ]:
                # Leave if empty
                if len(dates) < 1:
                    thisTry.error_occured(Errors.REQUIRED_DATA_MISSING)
                    return
                # Else, append to query
                sru_request.append(f" and ({ksru.SRU_Indexes.DATE.value}={f' or {ksru.SRU_Indexes.DATE.value}='.join([str(num) for num in dates])})")
            
            # launch search
            thisTry.define_used_query(sru.generate_query(sru_request))
            res = sru.search(
                thisTry.query,
                record_schema=ksru.SRU_Record_Schemas.MARCXML,
                start_record=1,
                maximum_records=100
            )
            if (res.status == "Error"):
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_records_id())
                thisTry.add_returned_records(res.get_records())