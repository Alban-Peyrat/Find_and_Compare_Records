# -*- coding: utf-8 -*- 

# External imports

# Internal imports
import api.abes.Abes_isbn2ppn as Abes_isbn2ppn

def main(api, query, return_records=False, service="match_records"):
    """Main function.
    
    Takes as argument :
        - api {str} :
            - "Abes_isbn2ppn"
            - "Koha_SRU"
        - query {str}
        - return_records {bool} : returns IDs or complete records (default to false)
        - servie {str}
    
    Returns a tupple :
        error {bool}
        error_msg {str}
        output {list}
            """

    output = {}
    
    # General part
    result = call_api(api=api, query=query, service=service)
    output["ERROR"], output["ERROR_MSG"] = is_error(result, api)

    # Leaves if there was an error
    if output["ERROR"]:
        return output

    # Specific actions
    output.update(specific_actions(api=api, result=result))

    return output

def call_api(api, query, service):
    """Calls the API.
    
    Returns the object"""
    if api == "Abes_isbn2ppn":
        return Abes_isbn2ppn.Abes_isbn2ppn(query, service=service)
    elif api == "Koha_SRU":
        return "a"

def is_error(request_object, service):
    """Returns if the request response was an error.
    
    Returns a tupple :
        {bool}
        {str} : the error message, starting with the service name"""
    if request_object.status == 'Error':
        return True, "{} : {}".format(str(service), str(request_object.error_msg))
    return False, ""

def specific_actions(api, result):
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

    return output

# multiple PPNs w/ hold only : 2110860723 [06/10/2022]
# multiple PPNs + no hold : 2-07-037026-7 [06/10/2022]
# 1 PPN : 9782862764719 [06/10/2022]
# 0 PPN : 2212064004 [06/10/2022]