# -*- coding: utf-8 -*- 

# Based on Abes_Apis_Intreface/AbesXml by @louxfaure

# External imports
from enum import Enum
import logging
import requests
import xml.etree.ElementTree as ET
import json
import pyisbn
import re
from typing import Tuple, List

# --------------- Enums ---------------

class Id2ppn_Status(Enum):
    UNKNOWN = "Unknown"
    SUCCESS = "Success"
    ERROR = "Error"

class Id2ppn_Errors(Enum):
    INVALID_ISBN = "ISBN is invalid"
    INVALID_CHECK_ISBN = "ISBN has an invalid check"
    HTTP_GENERIC_ERROR = "Unknown ISBN or unavailable service"
    GENERIC_EXCEPTION = "Generic exception, check logs for more details"
    UNKNOWN_ID = "Unknown ID"
    UNAVAILABLE_SERVICE = "Unavaible service"
    NO_ERROR = "No error"

class Isbn_Validity(Enum):
    VALID = 0
    INVALID_ISBN = 1
    INVALID_CHECK_ISBN = 2
    SKIPPED = 4

class Webservice(Enum):
    ISBN = "isbn"
    ISSN = "issn"
    EAN = "ean"
    FRBN = "frbn"
    OCN = "ocn"
    DNB = "dnb"
    UCATB = "ucatb"
    FRCAIRN = "frcairninfo"
    SPRINGERLN = "springerln"

# --------------- Function definition ---------------

# Adapted from https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch04s13.html
def validate_isbn(isbn:str) -> Tuple[Isbn_Validity, str, str]:
    """Return if the ISBN is valid.
    
    Argument : ISBN
    
    Returns a tuple :
    - {Isbn_Validity} : [VALID, INVALID_ISBN, INVALID_ISBN_CHECK]
    - {as input} : ISBN
    - {str} : ISBN without separators"""
    # `regex` checks for ISBN-10 or ISBN-13 format
    regex = re.compile("^(?:ISBN(?:-1[03])?:? )?(?=[-0-9 ]{17}$|[-0-9X ]{13}$|[0-9X]{10}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?(?:[0-9]+[- ]?){2}[0-9X]$")

    if regex.search(str(isbn)):
        # Remove non ISBN digits
        normalised = re.sub("[^0-9X]", "", str(isbn))
        # Leave if it's an ISBN 13 with a X as a checksum
        if normalised[-1:] == "X" and len(normalised) == 13:
            return Isbn_Validity.INVALID_CHECK_ISBN, isbn, normalised
        
        isbn_inst = pyisbn.Isbn(normalised)
        if (isbn_inst.validate()):
            return Isbn_Validity.VALID, isbn, isbn_inst.isbn
        else:
            return Isbn_Validity.INVALID_CHECK_ISBN, isbn, isbn_inst.isbn
    else:
        return Isbn_Validity.INVALID_ISBN, isbn, ""


def compute_isbn_10_check_digit(chars:List[str]) -> str:
    """DEPRACTED, use pyisbn library directly
    
    Returns the check as a string for an ISBN 10.
    
    Argument : {list of str} each digit of the ISBN except the check
    """
    return pyisbn.Isbn("".join(chars) + "0").calculate_checksum()

def compute_isbn_13_check_digit(chars:List[str]) -> str:
    """DEPRACTED, use pyisbn library directly
    
    Returns the check as a string for an ISBN 13.
    
    Argument : {list of str} each digit of the ISBN except the check
    """
    return pyisbn.Isbn("".join(chars) + "0").calculate_checksum()

# --------------- Result Class ---------------

class Id2ppn_Result(object):
    def __init__(self, status: Id2ppn_Status, error: Id2ppn_Errors, format: str, id: str, mod_id: str, isbn_validity=Isbn_Validity.SKIPPED, url=None, HTTP_status_code=0, result=None):
        self.status = status
        self.error = error
        self.error_msg = error.value
        self.format = format
        self.id = id
        self.mod_id = mod_id
        self.isbn_validity = isbn_validity
        self.url = url
        self.HTTP_status_code = HTTP_status_code
        self.result = result
    
    def get_result(self):
        """Return the entire record as a string of the specified format."""
        return self.result

    def get_status(self):
        """Return the init status as a string."""
        return self.status.value

    def get_error_msg(self):
        """Return the error message as a string."""
        return self.error_msg

    def get_id_used(self):
        """Return the ID used (ex : ISBN without separators) as a string."""
        return self.mod_id

    def get_nb_results(self):
        """Returns the number of results as a tuple of integers :
            - total results
            - results with holdings
            - results without holding"""
        if self.status != Id2ppn_Status.SUCCESS:
            return 0, 0, 0
        if self.format == "text/json":
            res = []
            res_no_hold = []

            rep = json.loads(self.result)["sudoc"]["query"]
            if "result" in rep:
                res = rep["result"]
            if "resultNoHolding" in rep:
                res_no_hold = rep["resultNoHolding"]
            
        else:
            root = ET.fromstring(self.result)
            res = root.findall("./query/result//ppn")
            res_no_hold = root.findall("./query/resultNoHolding//ppn")

        return len(res) + len(res_no_hold), len(res), len(res_no_hold)

    def get_results(self, merge=False):
        """Returns all the results as a list of strings.
        
        Takes as an optional argument {bool} merge, to merge both list.
        If set to False, returns a tuple of the two lists :
            - results with holdings
            - results without holding"""
        res = []
        res_no_hold = []

        if self.status != Id2ppn_Status.SUCCESS:
            return res, res_no_hold

        if self.format == "text/json":
            rep = json.loads(self.result)["sudoc"]["query"]
            if "result" in rep:
                # Returns an object if only one match
                if len(rep["result"]) > 1:
                    for ppn in rep["result"]:
                        res.append(str(ppn["ppn"]))
                else:
                    res.append(str(rep["result"]["ppn"]))
            if "resultNoHolding" in rep:
                if len(rep["resultNoHolding"]) > 1:
                    for ppn in rep["resultNoHolding"]:
                        res_no_hold.append(str(ppn["ppn"]))
                else:
                    res_no_hold.append(str(rep["resultNoHolding"]["ppn"]))

        else:
            root = ET.fromstring(self.result)
            for ppn in root.findall("./query/result//ppn"):
                res.append(ppn.text)
            for ppn in root.findall("./query/resultNoHolding//ppn"):
                res_no_hold.append(ppn.text)

        if merge:
            return res + res_no_hold
        else:
            return res, res_no_hold 


# --------------- Launcher Class ---------------

class Abes_id2ppn(object):
    """Abes_id2ppn
    =======
    A set of function wich handle data returned by Abes webservices to get a PPN from IDs
    https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#IdentifiantSudoc
    https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#IdentifiantSudocExterne
    On init take as argument :
        - a Webservice entry, defaults to ISBN
        - (optional) {bool} useJson ? (else XML)"""

    def __init__(self, webservice:Webservice=Webservice.ISBN, useJson:bool=True, service:str='Abes_isbn2ppn'):
        self.webservice = webservice
        # If webservice is provided as a string
        if type(self.webservice) == str:
            if self.webservice in [w.value for w in Webservice]:
                self.webservice = next(w for w in Webservice if w.value == self.webservice)
        # Defaults webservice to isbn2ppn if incorrect data is provided
        if type(self.webservice) != Webservice:
            self.webservice = Webservice.ISBN
        self.endpoint = f"https://www.sudoc.fr/services/{self.webservice.value}2ppn/"
        self.logger = logging.getLogger(service)
        self.service = service
        if useJson:
            self.format = "text/json"
        else:
            self.format = "application/xml"

    def get_matching_ppn(self, id: str, check_isbn_validity=True) -> Id2ppn_Result:
        """Calls the webservice"""
        status = Id2ppn_Status.UNKNOWN
        error = Id2ppn_Errors.NO_ERROR
        HTTP_status_code = 0
        id = str(id)
        mod_id = id
        isbn_validity = Isbn_Validity.SKIPPED
        # do not check ISBN validity unless it's isbn2ppn
        if check_isbn_validity and self.webservice == Webservice.ISBN:
            isbn_validity, id, mod_id = validate_isbn(mod_id)
        
        # If ISBN invalid, returns
        if isbn_validity != Isbn_Validity.VALID and isbn_validity != Isbn_Validity.SKIPPED:
            # isbn2ppn can take wrong ISBN formats, so this filters them out
            status = Id2ppn_Status.ERROR
            error = Id2ppn_Errors[isbn_validity.name]
            self.logger.error(f"{id} :: Abes_id2ppn ISBN Validity :: {error.value}")
            return Id2ppn_Result(status, error, self.format, id, mod_id, isbn_validity=isbn_validity)

        # Requests
        url =  f"{self.endpoint}{mod_id}"
        headers = {"accept":self.format}
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()  
        # HTTP errors (analysis later)
        except requests.exceptions.HTTPError:
            status = Id2ppn_Status.ERROR
            error = Id2ppn_Errors.HTTP_GENERIC_ERROR
            HTTP_status_code = r.status_code
            # If the error is that no PPN were found for this id
            if status == Id2ppn_Status.ERROR and error == Id2ppn_Errors.HTTP_GENERIC_ERROR and HTTP_status_code == 404:
                try:
                    real_error_msg = json.loads(r.text)
                    if real_error_msg["sudoc"]["error"] == f"No record was found for this {mod_id}":
                        error = Id2ppn_Errors.UNKNOWN_ID
                except:
                    error = Id2ppn_Errors.UNAVAILABLE_SERVICE
                self.logger.error(f"{id} :: Abes_id2ppn Request :: {error.value}")
                return Id2ppn_Result(status, error, self.format, id, mod_id, isbn_validity=isbn_validity, url=url, HTTP_status_code=HTTP_status_code)
            self.logger.error(f"{id} :: Abes_id2ppn Request :: HTTP Status: {HTTP_status_code} || URL: {r.url} || Response: {r.text}")
            return Id2ppn_Result(status, error, self.format, id, mod_id, isbn_validity=isbn_validity, url=url, HTTP_status_code=HTTP_status_code)
        # Generic error
        except requests.exceptions.RequestException as generic_error:
            status = Id2ppn_Status.ERROR
            error = Id2ppn_Errors.GENERIC_EXCEPTION
            self.logger.error(f"{id} :: Abes_id2ppn Request :: {error.value} || URL: {url} || {generic_error}")
            return Id2ppn_Result(status, error, self.format, id, mod_id, isbn_validity=isbn_validity, url=url, HTTP_status_code=HTTP_status_code)
        # Success
        else:
            status = Id2ppn_Status.SUCCESS
            result = r.content.decode('utf-8')
            self.logger.debug(f"{id} :: Abes_id2ppn Request :: Success")
            return Id2ppn_Result(status, error, self.format, id, mod_id, isbn_validity=isbn_validity, url=url, HTTP_status_code=HTTP_status_code, result=result)
