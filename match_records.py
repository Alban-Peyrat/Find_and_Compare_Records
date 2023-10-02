# -*- coding: utf-8 -*- 

# External imports
import types
from enum import Enum

# Internal imports
import api.abes.Abes_isbn2ppn as Abes_isbn2ppn
import api.abes.Sudoc_SRU as ssru
import api.koha.Koha_SRU as Koha_SRU

class Match_Records_Errors(Enum):
    GENERIC_ERROR = 0
    NOTHING_WAS_FOUND = 1

MATCH_RECORDS_ERROR_MESSAGES = {
    Match_Records_Errors.GENERIC_ERROR: "Generic error",
    Match_Records_Errors.NOTHING_WAS_FOUND: "Nothing was found"
}

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
            self.msg = MATCH_RECORDS_ERROR_MESSAGES[self.error_type]
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

# TRY_OPERATIONS defines for each Operations a lsit of Actions to execute
# The order in the list is the order of execution
TRY_OPERATIONS = {
    Operations.SEARCH_IN_SUDOC_BY_ISBN: [
        Actions.ISBN2PPN,
        Actions.ISBN2PPN_MODIFIED_ISBN,
        Actions.SRU_SUDOC_ISBN
    ],
    Operations.SEARCH_IN_SUDOC_BY_ISBN_ONLY_ISBN2PPN: [
        Actions.ISBN2PPN,
        Actions.ISBN2PPN_MODIFIED_ISBN
    ],
    Operations.SEARCH_IN_SUDOC_BY_ISBN_ONLY_SRU: [
        Actions.SRU_SUDOC_ISBN
    ]
}

class Matched_Records(object):
    """
    
    Takes as argument :
        - operation {Operations Instance} (defaults to SEARCH_IN_SUDOC_BY_ISBN)"""
    def __init__(self, operation: Operations, query: str):
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
        
        for index, action in enumerate(TRY_OPERATIONS[self.operation]):
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
            self.error_msg = MATCH_RECORDS_ERROR_MESSAGES[self.error]


    def request_action(self, action: Actions, thisTry: Request_Try):
        """Makes the request for this specific action and returns a list of IDs as a result"""

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



def main(api: Operations, query: str, return_records=False, service="match_records", args={}):
    """Main function.
    
    Takes as argument :
        - api {Operations instance}
        - query {str}
        - service {str}
        - args {dict}
    
    Returns a tupple :
        error {bool}
        error_msg {str}
        output {list}
            """

    # Do not return records or IDS, return records with IDS (see SRU_Abes)

    output = {}
    
    # General part
    result = call_api(api=api, query=query, service=service, args=args)
    output["ERROR"], output["ERROR_MSG"] = is_error(result, api)

    #AR226
    # If error on isbn2ppn, try again converting the ISBN to 10<->13
    if output["ERROR"] and api == "Abes_isbn2ppn" and (len(result.isbn) == 13 or len(result.isbn) == 10):
        if len(result.isbn) == 13:
            new_query = result.isbn[3:-1]
            new_query += Abes_isbn2ppn.compute_isbn_10_check_digit(list(str(new_query)))
        else:
            # Doesn't consider 979[...] as the original issue should only concern old ISBN
            new_query = "978" + result.isbn[:-1]
            new_query += Abes_isbn2ppn.compute_isbn_13_check_digit(list(str(new_query)))

        result = call_api(api=api, query=new_query, service=service, args=args)
        output["ERROR"], output["ERROR_MSG"] = is_error(result, api)

    # Leaves if there was an error
    if output["ERROR"]:
        return output

    # Specific actions
    output.update(specific_actions(api=api, result=result, return_records=return_records))

    return output

def call_api(api, query, service, args):
    """Calls the API.
    
    Returns the object"""
    if api == "Abes_isbn2ppn":
        return Abes_isbn2ppn.Abes_isbn2ppn(query, service=service)
    elif api == "Koha_SRU":
        # checks if a Koha URL was provided
        if not "KOHA_URL" in args:
            return types.SimpleNamespace(status="Error", error_msg="Koha_SRU called in match_records without specifying a Koha URL in args.")
        elif args["KOHA_URL"] == "":
            return types.SimpleNamespace(status="Error", error_msg="Koha_SRU called in match_records with empty string as Koha URL in args.")
        return Koha_SRU.Koha_SRU(query, kohaUrl=args["KOHA_URL"], service=service) #VERSION QUE POUR NANTES

def specific_actions(api, result, return_records=False):
    """
    """
    output = {}
    if api == "Abes_isbn2ppn":
        output["MATCH_RECORDS_QUERY"] = result.get_isbn_no_sep()
        output["MATCH_RECORDS_NB_RES"] = result.get_nb_results()[0] # We take every result
        output["MATCH_RECORDS_RES"] = result.get_results(merge=True)
        if output["MATCH_RECORDS_NB_RES"] != 1:
            output["ERROR"] = True
            output["FAKE_ERROR"] = True
            output['ERROR_MSG'] = "{} : trop de résultats".format(str(api))
        if output["MATCH_RECORDS_NB_RES"] == 1: # Only 1 match : gets the PPN
            output["MATCHED_ID"] = output["MATCH_RECORDS_RES"][0]
    elif api == "Koha_SRU":
        output["MATCH_RECORDS_QUERY"] = result.query
        output["MATCH_RECORDS_NB_RES"] = result.get_nb_results()
        if return_records:
            output["MATCH_RECORDS_RES"] = result.get_records()
        else:
            output["MATCH_RECORDS_RES"] = result.get_records_id()
        if int(output["MATCH_RECORDS_NB_RES"]) != 1:
            output["ERROR"] = True
            output["FAKE_ERROR"] = True
            if int(output["MATCH_RECORDS_NB_RES"]) == 0:
                output['ERROR_MSG'] = "{} : aucun résultat".format(str(api))
            else:
                output['ERROR_MSG'] = "{} : trop de résultats".format(str(api))
        if output["MATCH_RECORDS_NB_RES"] == 1 and not return_records:
            output["MATCHED_ID"] = output["MATCH_RECORDS_RES"][0]

    return output

# ready to del
# def is_error(request_object, service):
#     """Returns if the request response was an error.
    
#     Returns a tupple :
#         {bool}
#         {str} : the error message, starting with the service name"""
#     if request_object.status == 'Error':
#         return True, "{} : {}".format(str(service), str(request_object.error_msg))
#     return False, ""

# multiple PPNs w/ hold only : 2110860723 [06/10/2022]
# multiple PPNs + no hold : 2-07-037026-7 [06/10/2022]
# 1 PPN : 9782862764719 [06/10/2022]
# 0 PPN : 2212064004 [06/10/2022]

# test = Matched_Records(Operations.SEARCH_IN_SUDOC_BY_ISBN, "978-2-84096-539-8")
# print(test)