# -*- coding: utf-8 -*- 

# External imports
import types

# Internal imports
import api.abes.Abes_isbn2ppn as Abes_isbn2ppn
import api.koha.Koha_SRU as Koha_SRU

def main(api, query, return_records=False, service="match_records", args={}):
    """Main function.
    
    Takes as argument :
        - api {str} :
            - "Abes_isbn2ppn"
            - "Koha_SRU"
        - query {str}
        - return_records {bool} : returns IDs or complete records (default to false)
        - service {str}
        - args {dict}
    
    Returns a tupple :
        error {bool}
        error_msg {str}
        output {list}
            """

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

def is_error(request_object, service):
    """Returns if the request response was an error.
    
    Returns a tupple :
        {bool}
        {str} : the error message, starting with the service name"""
    if request_object.status == 'Error':
        return True, "{} : {}".format(str(service), str(request_object.error_msg))
    return False, ""

# multiple PPNs w/ hold only : 2110860723 [06/10/2022]
# multiple PPNs + no hold : 2-07-037026-7 [06/10/2022]
# 1 PPN : 9782862764719 [06/10/2022]
# 0 PPN : 2212064004 [06/10/2022]