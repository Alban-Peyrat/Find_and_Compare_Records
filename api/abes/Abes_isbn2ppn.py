# -*- coding: utf-8 -*- 

# Based on Abes_Apis_Intreface/AbesXml by @louxfaure

# External imports
from enum import Enum
import logging
import requests
import xml.etree.ElementTree as ET
import json
import re

# --------------- Enums ---------------

class Isbn2ppn_Status(Enum):
    UNKNOWN = "Unknown"
    SUCCESS = "Success"
    ERROR = "Error"

class Isbn2ppn_Errors(Enum):
    INVALID_ISBN = "ISBN is invalid"
    INVALID_CHECK_ISBN = "ISBN has an invalid check"
    HTTP_GENERIC_ERROR = "Unknown ISBN or unavailable service"
    GENERIC_EXCEPTION = "Generic exception, check logs for more details"
    UNKNOWN_ISBN = "Unknown ISBN"
    UNAVAILABLE_SERVICE = "Unavaible service"
    NO_ERROR = "No error"

class Isbn_Validity(Enum):
    VALID = 0
    INVALID_ISBN = 1
    INVALID_CHECK_ISBN = 2
    SKIPPED = 4

# --------------- Function definition ---------------

# Adapted from https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch04s13.html
def validate_isbn(isbn):
    """Return if the ISBN is valid.
    
    Argument : ISBN
    
    Returns a tuple :
    - {Isbn_Validity} : [VALID, INVALID_ISBN, INVALID_ISBN_CHECK]
    - {as input} : ISBN
    - {str} : ISBN without separators"""
    # `regex` checks for ISBN-10 or ISBN-13 format
    regex = re.compile("^(?:ISBN(?:-1[03])?:? )?(?=[-0-9 ]{17}$|[-0-9X ]{13}$|[0-9X]{10}$)(?:97[89][- ]?)?[0-9]{1,5}[- ]?(?:[0-9]+[- ]?){2}[0-9X]$")

    if regex.search(isbn):
        # Remove non ISBN digits, then split into an array
        chars = list(re.sub("[^0-9X]", "", str(isbn)))
        # Remove the final ISBN digit from `chars`, and assign it to `last`
        last  = chars.pop()

        if len(chars) == 9:
            # Compute the ISBN-10 check digit
            check = compute_isbn_10_check_digit(chars)
        else:
            # Compute the ISBN-13 check digit
            check = compute_isbn_13_check_digit(chars)

        if (str(check) == last):
            return Isbn_Validity.VALID, isbn, "".join(chars)+last
        else:
            return Isbn_Validity.INVALID_CHECK_ISBN, isbn, "".join(chars)+last
    else:
        return Isbn_Validity.INVALID_ISBN, isbn, ""

def compute_isbn_10_check_digit(chars):
    """Returns the check as a string for an ISBN 10.
    
    Argument : {list of str} each digit of the ISBN except the check
    """
    val = sum((x + 2) * int(y) for x,y in enumerate(reversed(chars)))
    check = 11 - (val % 11)
    if check == 10:
        check = "X"
    elif check == 11:
        check = "0"
    return str(check)

def compute_isbn_13_check_digit(chars):
    """Returns the check as a string for an ISBN 13.
    
    Argument : {list of str} each digit of the ISBN except the check
    """
    val = sum((x % 2 * 2 + 1) * int(y) for x,y in enumerate(chars))
    check = 10 - (val % 10)
    if check == 10:
        check = "0"
    return str(check)

# --------------- Launcher Class ---------------

class Abes_isbn2ppn(object):
    """Abes_isbn2ppn
    =======
    A set of function wich handle data returned by Abes webservice isbn2ppn
    https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#isbn2ppn
    On init take as argument :
        - an ISBN
        - (optional) {bool} useJson ? (else XML)"""

    def __init__(self, service='Abes_isbn2ppn', useJson=True):
        self.endpoint = "https://www.sudoc.fr/services/isbn2ppn/"
        self.logger = logging.getLogger(service)
        self.service = service
        if useJson:
            self.format = "text/json"
        else:
            self.format = "application/xml"

    def get_matching_ppn(self, isbn: str, check_isbn_validity=True):
        status = Isbn2ppn_Status.UNKNOWN
        error = Isbn2ppn_Errors.NO_ERROR
        HTTP_status_code = 0
        input_isbn = str(isbn)
        isbn = str(isbn)
        isbn_validity = Isbn_Validity.SKIPPED

        if check_isbn_validity:
            isbn_validity, input_isbn, isbn = validate_isbn(str(isbn))
        
        # If ISBN invalid, returns
        if isbn_validity != Isbn_Validity.VALID and isbn_validity != Isbn_Validity.SKIPPED:
            # isbn2ppn can take wrong ISBN formats, so this filters them out
            status = Isbn2ppn_Status.ERROR
            error = Isbn2ppn_Errors[isbn_validity.name]
            self.logger.error(f"{input_isbn} :: Abes_isbn2ppn ISBN Validity :: {error.value}")
            return Isbn2ppn_Result(status, error, self.format, input_isbn, isbn, isbn_validity=isbn_validity)

        # Requests
        url =  f"{self.endpoint}{isbn}"
        headers = {"accept":self.format}
        try:
            r = requests.get(url, headers=headers)
            r.raise_for_status()  
        # HTTP errors (analysis later)
        except requests.exceptions.HTTPError:
            status = Isbn2ppn_Status.ERROR
            error = Isbn2ppn_Errors.HTTP_GENERIC_ERROR
            HTTP_status_code = r.status_code
            self.logger.error(f"{input_isbn} :: Abes_isbn2ppn Request :: HTTP Status: {HTTP_status_code} || URL: {r.url} || Response: {r.text}")
            return Isbn2ppn_Result(status, error, self.format, input_isbn, isbn, isbn_validity=isbn_validity, url=url, HTTP_status_code=HTTP_status_code)
        # Generic error
        except requests.exceptions.RequestException as generic_error:
            status = Isbn2ppn_Status.ERROR
            error = Isbn2ppn_Errors.GENERIC_EXCEPTION
            # If the error is that no PPN were found for this ISBN
            if status == Isbn2ppn_Status.ERROR and error == Isbn2ppn_Errors.HTTP_GENERIC_ERROR and HTTP_status_code == 404:
                try:
                    real_error_msg = json.loads(r.text)
                    if real_error_msg["sudoc"]["error"] == f"Aucune notice n'est associée à cette valeur {isbn}":
                        error = Isbn2ppn_Errors.UNKNOWN_ISBN
                except:
                    error = Isbn2ppn_Errors.UNAVAILABLE_SERVICE
            self.logger.error(f"{input_isbn} :: Abes_isbn2ppn Request :: {error.value} || URL: {url} || {generic_error}")
            return Isbn2ppn_Result(status, error, self.format, input_isbn, isbn, isbn_validity=isbn_validity, url=url, HTTP_status_code=HTTP_status_code)
        # Success
        else:
            status = Isbn2ppn_Status.SUCCESS
            result = r.content.decode('utf-8')
            self.logger.debug(f"{input_isbn} :: Abes_isbn2ppn Request :: Success")
            return Isbn2ppn_Result(status, error, self.format, input_isbn, isbn, isbn_validity=isbn_validity, url=url, HTTP_status_code=HTTP_status_code, result=result)

# --------------- Result Class ---------------

class Isbn2ppn_Result(object):
    def __init__(self, status: Isbn2ppn_Status, error: Isbn2ppn_Errors, format: str, input_isbn: str, isbn: str, isbn_validity=Isbn_Validity.SKIPPED, url=None, HTTP_status_code=0, result=None):
        self.status = status.value
        self.error = error
        self.error_msg = error.value
        self.format = format
        self.input_isbn = input_isbn
        self.isbn = isbn
        self.isbn_validity = isbn_validity
        self.url = url
        self.HTTP_status_code = HTTP_status_code
        self.result = result
    
    def get_result(self):
        """Return the entire record as a string of the specified format."""
        return self.result

    def get_status(self):
        """Return the init status as a string."""
        return self.status

    def get_error_msg(self):
        """Return the error message as a string."""
        return self.error_msg

    def get_isbn_used(self):
        """Return the ISBN without separators as a string."""
        return self.isbn

    def get_nb_results(self):
        """Returns the number of results as a tuple of integers :
            - total results
            - results with holdings
            - results without holding"""
        if self.status != Isbn2ppn_Status.SUCCESS.value:
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

        if self.status != Isbn2ppn_Status.SUCCESS.value:
            return res, res_no_hold

        if self.format == "text/json":
            rep = json.loads(self.result)["sudoc"]["query"]
            if "result" in rep:
                for ppn in rep["result"]:
                    # ahahahah si ya 1 résultat ça renvoie pas une liste :)
                    if len(rep["result"]) > 1:
                        res.append(str(ppn["ppn"]))
                    else:
                        res.append(str(rep["result"]["ppn"]))
            if "resultNoHolding" in rep:
                for ppn in rep["resultNoHolding"]:
                    if len(rep["resultNoHolding"]) > 1:
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
