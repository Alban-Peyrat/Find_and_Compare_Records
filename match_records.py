# -*- coding: utf-8 -*- 

# External imports

# Internal imports
import api.abes.Abes_isbn2ppn as Abes_isbn2ppn
import api.abes.Sudoc_SRU as ssru
import api.koha.Koha_SRU as Koha_SRU
from bi_classes import Execution_Settings, Operations, Actions, Try_Status, Match_Records_Errors, TRY_OPERATIONS, MATCH_RECORDS_ERROR_MESSAGES

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

class Matched_Records(object):
    """
    
    Takes as argument :
        - operation {Operations Instance} (defaults to SEARCH_IN_SUDOC_BY_ISBN)"""
    def __init__(self, operation: Operations, query: str, es: Execution_Settings):
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
        # Action isbn2ppn
        # /!\ THIS PART IS ALSO USED IN Actions.ISBN2PPN_MODIFIED_PPN DO NOT FORGET TO UPDATE
        # THE OTHER ONE IF NECESSARY
        # Sinon je mets des fonction communes du genre : Abes_ISBN2PNN_get_error or something
        elif action == Actions.ISBN2PPN:
            res = Abes_isbn2ppn.Abes_isbn2ppn(self.query)
            thisTry.define_used_query(res.isbn)

        # Action isbn2ppn with changed ISBN
        elif action == Actions.ISBN2PPN_MODIFIED_ISBN:
            #AR226
            # Converting the ISBN to 10<->13
            if len(self.query) == 13:
                new_query = self.query[3:-1]
                new_query += Abes_isbn2ppn.compute_isbn_10_check_digit(list(str(new_query)))
            elif len(self.query) == 10:
                # Doesn't consider 979[...] as the original issue should only concern old ISBN
                new_query = "978" + self.query[:-1]
                new_query += Abes_isbn2ppn.compute_isbn_13_check_digit(list(str(new_query)))
            
            # Same thing as Action ISBN2PPN
            res = Abes_isbn2ppn.Abes_isbn2ppn(self.query)
            thisTry.define_used_query(res.isbn)

        # Action in Koha SRU

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



# multiple PPNs w/ hold only : 2110860723 [06/10/2022]
# multiple PPNs + no hold : 2-07-037026-7 [06/10/2022]
# 1 PPN : 9782862764719 [06/10/2022]
# 0 PPN : 2212064004 [06/10/2022]

# test = Matched_Records(Operations.SEARCH_IN_SUDOC_BY_ISBN, "978-2-84096-539-8")
# print(test)