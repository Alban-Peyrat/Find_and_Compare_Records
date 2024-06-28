# -*- coding: utf-8 -*- 

# External import
import pyisbn
import re
from enum import Enum
from typing import List

# Internal imports
from cl_error import Errors, get_error_instance
from cl_PODA import Operation, Action_Names, get_PODA_instance
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

        # To avoid redundance
        # Extract data
        title = delete_for_sudoc(self.local_record.utils.get_titles_as_string())
        author = delete_for_sudoc(self.local_record.utils.get_authors_as_string())
        publisher = delete_for_sudoc(self.local_record.utils.get_all_publishers_as_string())
        dates, oldest_date, newest_date = self.local_record.utils.get_all_publication_dates()
        ean = self.local_record.utils.get_first_ean_as_string()
        isbn = self.local_record.utils.get_first_isbn_as_string()

        # Action Sudoc's id2ppn webservice
        if action in [
                Action_Names.ISBN2PPN,
                Action_Names.ISBN2PPN_MODIFIED_ISBN,
                Action_Names.ISBN2PPN_MODIFIED_ISBN_SAME_KEY,
                Action_Names.EAN2PPN
            ]:
            action_instance = get_PODA_instance(action, Action_Names)
            # Leaves if it does nto find the action 
            if action_instance == None:
                thisTry.error_occured(Errors.ACTION_IS_NOT_CORRECTLY_DEFINED)
                return

            # Action specific checks
            new_query = ""
            # Throw an error if it uses EAN2PPN & no EAN was found
            if action == Action_Names.EAN2PPN and ean == "":
                thisTry.error_occured(Errors.NO_EAN_WAS_FOUND)
                return
            # Edit the ISBN if it uses ISBN2PPN_MODIFIED_ISBN
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
            # Edit the ISBN if it uses ISBN2PPN_MODIFIED_ISBN_SAME_KEY
            elif action == Action_Names.ISBN2PPN_MODIFIED_ISBN_SAME_KEY:
                # Converting the ISBN to 10<->13 
                if len(self.query) == 13:
                    new_query = self.query[3:]
                elif len(self.query) == 10:
                    # Doesn't consider 979[...] as the original issue should only concern old ISBN
                    new_query = "978" + self.query
            # Throw an error if ISBN modification end up in empty variable
            if not new_query and action in [
                    Action_Names.ISBN2PPN_MODIFIED_ISBN,
                    Action_Names.ISBN2PPN_MODIFIED_ISBN_SAME_KEY
                ]:
                thisTry.error_occured(Errors.ISBN_MODIFICATION_FAILED)
                return

            # Defines the correct webservice (defautls to ISBN)
            webservice = id2ppn.Webservice.ISBN
            if action_instance.use_isbn:
                webservice = id2ppn.Webservice.ISBN
            elif action_instance.use_ean:
                webservice = id2ppn.Webservice.EAN
            
            # Sets up the class
            i2p = id2ppn.Abes_id2ppn(webservice=webservice, useJson=True)

            # Defines the correct query
            query = self.query
            if action in [Action_Names.ISBN2PPN]:
                query = self.query # I know it's useless but that way I'm don't have a doubt reading the code fast
            elif action in [
                    Action_Names.ISBN2PPN_MODIFIED_ISBN,
                    Action_Names.ISBN2PPN_MODIFIED_ISBN_SAME_KEY
                ]:
                query = new_query
            elif action in [Action_Names.EAN2PPN]:
                query = ean

            # Defines if it should valdiate ISBN
            check_isbn_validity = True
            if action in [
                    Action_Names.ISBN2PPN_MODIFIED_ISBN_SAME_KEY,
                    Action_Names.EAN2PPN
                ]:
                check_isbn_validity = False

            res = i2p.get_matching_ppn(query, check_isbn_validity=check_isbn_validity)
            thisTry.define_used_query(res.get_id_used())
            # Tbh Idk why this one is different, but eh
            if action == Action_Names.EAN2PPN:
                thisTry.define_used_query(ean)
            if res.status != id2ppn.Id2ppn_Status.SUCCESS:
                thisTry.error_occured(res.get_error_msg())
            else:
                thisTry.add_returned_ids(res.get_results(merge=True))

        # Action SRU Sudoc on data fields (ISBN, Title, Author, Publisher, Date or DocType)
        elif action in [
                Action_Names.SRU_SUDOC_ISBN,
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
            action_instance = get_PODA_instance(action, Action_Names)
            # Leaves if it does nto find the action 
            if action_instance == None:
                thisTry.error_occured(Errors.ACTION_IS_NOT_CORRECTLY_DEFINED)
                return
            sru = ssru.Sudoc_SRU()
            sru_request = []
            # ISBN
            if action_instance.use_isbn:
                # Leave if empty
                if self.query.strip() == "":
                    thisTry.error_occured(Errors.NO_ISBN_WAS_FOUND)
                    return
                # Defines the right index
                isbn_index = ssru.SRU_Indexes.ISB
                if not action_instance.specific_index:
                    isbn_index = ssru.SRU_Indexes.TOU
                # Append to query
                sru_request.append(ssru.Part_Of_Query(
                    isbn_index,
                    ssru.SRU_Relations.EQUALS,
                    self.query,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # TITLE
            if action_instance.use_title:
                # Leave if empty
                if title.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_TITLE_MISSING)
                    return
                # Defines the right index
                title_index = ssru.SRU_Indexes.MTI
                if not action_instance.specific_index:
                    title_index = ssru.SRU_Indexes.TOU
                # Append to query
                sru_request.append(ssru.Part_Of_Query(
                    title_index,
                    ssru.SRU_Relations.EQUALS,
                    title,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # AUTHORS
            if action_instance.use_authors:
                # Leave if empty
                if author.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_AUTHORS_MISSING)
                    return
                # Defines the right index
                authors_index = ssru.SRU_Indexes.AUT
                if not action_instance.specific_index:
                    authors_index = ssru.SRU_Indexes.TOU
                # Append to query
                sru_request.append(ssru.Part_Of_Query(
                    authors_index,
                    ssru.SRU_Relations.EQUALS,
                    author,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # PUBLISHER
            if action_instance.use_publisher:
                # Leave if empty
                if publisher.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_PUBLISHER_MISSING)
                    return
                # Defines the right index
                publisher_index = ssru.SRU_Indexes.EDI
                if not action_instance.specific_index:
                    publisher_index = ssru.SRU_Indexes.TOU
                # Append to query
                sru_request.append(ssru.Part_Of_Query(
                    publisher_index,
                    ssru.SRU_Relations.EQUALS,
                    publisher,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # DATES        
            if action_instance.use_date:
                # Leave if empty
                if len(dates) < 1:
                    thisTry.error_occured(Errors.REQUIRED_DATE_MISSING)
                    return
                # Defines the right index & append to query
                if action_instance.specific_index:
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
                else:
                    f" AND (tou={' or tou='.join([str(num) for num in dates])})",
            # Doctype filter
            if action_instance.use_doctype:
                doctype_auth_val = None
                if action_instance.doctype == "B":
                    doctype_auth_val = ssru.SRU_Filter_TDO.B
                elif action_instance.doctype == "K":
                    doctype_auth_val = ssru.SRU_Filter_TDO.K
                elif action_instance.doctype == "V":
                    doctype_auth_val = ssru.SRU_Filter_TDO.V
                else:
                    # Leave if doctype is not supported
                    thisTry.error_occured(Errors.UNSUPPORTED_DOCTYPE)
                    return
                # Append to query
                sru_request.append(ssru.Part_Of_Query(
                    ssru.SRU_Filters.TDO,
                    ssru.SRU_Relations.EQUALS,
                    doctype_auth_val,
                    ssru.SRU_Boolean_Operators.AND
                ))
            # Launch search
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

        # Action SRU Koha on data fields (ISBN, Title, Author, Publisher, Date)
        elif action in [
                    Action_Names.KOHA_SRU_IBSN,
                    Action_Names.KOHA_SRU_TITLE_AUTHOR_PUBLISHER_DATE,
                    Action_Names.KOHA_SRU_TITLE_AUTHOR_DATE,
                    Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_PUBLISHER_DATE,
                    Action_Names.KOHA_SRU_ANY_TITLE_AUTHOR_DATE,
                    Action_Names.KOHA_SRU_ANY_TITLE_PUBLISHER_DATE,
                    Action_Names.KOHA_SRU_TITLE
                ]:
            action_instance = get_PODA_instance(action, Action_Names)
            # Leaves if it does nto find the action 
            if action_instance == None:
                thisTry.error_occured(Errors.ACTION_IS_NOT_CORRECTLY_DEFINED)
                return
            sru = ksru.Koha_SRU(self.target_url, ksru.SRU_Version.V1_1)
            sru_request = []
            # ISBN
            if action_instance.use_isbn:
                # Leave if empty
                if isbn.strip() == "":
                    thisTry.error_occured(Errors.NO_ISBN_WAS_FOUND)
                    return
                # Defines the right index
                isbn_index = ksru.SRU_Indexes.ISBN
                if not action_instance.specific_index:
                    isbn_index = ksru.SRU_Indexes.ANY
                # Append to query
                sru_request.append(ksru.Part_Of_Query(
                    isbn_index,
                    ksru.SRU_Relations.EQUALS,
                    isbn,
                    ksru.SRU_Boolean_Operators.AND
                ))
            # TITLE
            if action_instance.use_title:
                # Leave if empty
                if title.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_TITLE_MISSING)
                    return
                # Defines the right index
                title_index = ksru.SRU_Indexes.TITLE
                if not action_instance.specific_index:
                    title_index = ksru.SRU_Indexes.ANY
                # Append to query
                sru_request.append(ksru.Part_Of_Query(
                    title_index,
                    ksru.SRU_Relations.EQUALS,
                    title,
                    ksru.SRU_Boolean_Operators.AND
                ))
            # AUTHORS
            if action_instance.use_authors:
                # Leave if empty
                if author.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_AUTHORS_MISSING)
                    return
                # Defines the right index
                authors_index = ksru.SRU_Indexes.AUTHOR
                if not action_instance.specific_index:
                    authors_index = ksru.SRU_Indexes.ANY
                # Append to query
                sru_request.append(ssru.Part_Of_Query(
                    authors_index,
                    ksru.SRU_Relations.EQUALS,
                    author,
                    ksru.SRU_Boolean_Operators.AND
                ))
            # PUBLISHER
            if action_instance.use_publisher:
                # Leave if empty
                if publisher.strip() == "":
                    thisTry.error_occured(Errors.REQUIRED_PUBLISHER_MISSING)
                    return
                # Defines the right index
                publisher_index = ksru.SRU_Indexes.PUBLISHER
                if not action_instance.specific_index:
                    publisher_index = ksru.SRU_Indexes.ANY
                # Append to query
                sru_request.append(ksru.Part_Of_Query(
                    publisher_index,
                    ksru.SRU_Relations.EQUALS,
                    publisher,
                    ksru.SRU_Boolean_Operators.AND
                ))
            # DATES        
            if action_instance.use_date:
                # Leave if empty
                if len(dates) < 1:
                    thisTry.error_occured(Errors.REQUIRED_DATE_MISSING)
                    return
                # Defines the right index
                date_index = ksru.SRU_Indexes.DATE
                if not action_instance.specific_index:
                    date_index = ksru.SRU_Indexes.ANY
                # Append to query
                sru_request.append(f" and ({date_index.value}={f' or {date_index.value}='.join([str(num) for num in dates])})")
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
