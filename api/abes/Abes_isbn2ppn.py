# -*- coding: utf-8 -*- 

# Based on Abes_Apis_Intreface/AbesXml by @louxfaure

import logging
import requests
import xml.etree.ElementTree as ET
import json
import re

# Adapted from https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch04s13.html
def validate_isbn(isbn):
    """Return if the ISBN is valid.
    
    Argument : ISBN
    
    Returns a tuple :
    - {str} : [Valid, Invalid, Invalid check]
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
            # val = sum((x + 2) * int(y) for x,y in enumerate(reversed(chars)))
            # check = 11 - (val % 11)
            # if check == 10:
            #     check = "X"
            # elif check == 11:
            #     check = "0"
            check = compute_isbn_10_check_digit(chars)
        else:
            # Compute the ISBN-13 check digit
            # val = sum((x % 2 * 2 + 1) * int(y) for x,y in enumerate(chars))
            # check = 10 - (val % 10)
            # if check == 10:
            #     check = "0"
            check = compute_isbn_13_check_digit(chars)

        if (str(check) == last):
            return "Valid", isbn, "".join(chars)+last
        else:
            return "Invalid check", isbn, "".join(chars)+last
    else:
        return "Invalid", isbn, ""

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

class Abes_isbn2ppn(object):
    """Abes_isbn2ppn
    =======
    A set of function wich handle data returned by Abes webservice isbn2ppn
    https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#isbn2ppn
    On init take as argument :
        - an ISBN
        - (optional) {bool} json ? (else XML)"""

    def __init__(self,isbn,service='Abes_isbn2ppn', json=True):
        self.logger = logging.getLogger(service)
        self.endpoint = "https://www.sudoc.fr/services/isbn2ppn/"
        self.service = service
        self.isbn_validity, self.input_isbn, self.isbn = validate_isbn(str(isbn))
        if json:
            self.format = "text/json"
        else:
            self.format = "application/xml"
        if self.isbn_validity != "Valid":
            # isbn2ppn can take wrong ISBN formats, so this filters them out
            self.status = "Error"
            self.logger.error("{} :: Abes_isbn2ppn :: ISBN {}".format(self.input_isbn, self.isbn_validity))
            self.error_msg = "ISBN " + self.isbn_validity
        else:
            self.url =  '{}/{}'.format(self.endpoint, self.isbn)
            self.payload = {
                
                }
            self.headers = {
                "accept":self.format
                }
            try:
                r = requests.get(self.url, headers=self.headers, params=self.payload)
                r.raise_for_status()  
            except requests.exceptions.HTTPError:
                self.status = 'Error'
                self.logger.error("{} :: Abes_isbn2ppn :: HTTP Status: {} || Method: {} || URL: {} || Response: {}".format(self.input_isbn, r.status_code, r.request.method, r.url, r.text))
                self.error_msg = "ISBN inconnu ou service indisponible"
            except requests.exceptions.RequestException as generic_error:
                self.status = 'Error'
                self.logger.error("{} :: XmlAbes_Init :: Generic exception || URL: {} || {}".format(self.input_isbn, self.url, generic_error))
                self.error_msg = "Exception générique, voir les logs pour plus de détails"
            else:
                self.record = r.content.decode('utf-8')
                self.status = 'Success'
                self.logger.debug("{} :: Abes_isbn2ppn :: Notice trouvée".format(self.input_isbn))

    def get_record(self):
            """Return the entire record as a string of the specified format."""
            return self.record

    def get_init_status(self):
        """Return the init status as a string."""
        return self.status

    def get_error_msg(self):
        """Return the error message as a string."""
        if hasattr(self, "error_msg"):
            return self.error_msg
        else:
            return "Pas de message d'erreur"  

    def get_isbn_no_sep(self):
        """Return the ISBN without separators as a string."""
        return self.isbn

    def get_nb_results(self):
        """Returns the number of results as a tuple of integers :
            - total results
            - results with holdings
            - results without holding"""
        if self.format == "text/json":
            res = []
            res_no_hold = []

            rep = json.loads(self.record)["sudoc"]["query"]
            if "result" in rep:
                res = rep["result"]
            if "resultNoHolding" in rep:
                res_no_hold = rep["resultNoHolding"]
            
        else:
            root = ET.fromstring(self.record)
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

        if self.format == "text/json":
            rep = json.loads(self.record)["sudoc"]["query"]
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
                        res.append(str(ppn["ppn"]))
                    else:
                        res.append(str(rep["resultNoHolding"]["ppn"]))

        else:
            root = ET.fromstring(self.record)
            for ppn in root.findall("./query/result//ppn"):
                res.append(ppn.text)
            for ppn in root.findall("./query/resultNoHolding//ppn"):
                res_no_hold.append(ppn.text)

        if merge:
            return res + res_no_hold
        else:
            return res, res_no_hold 
            
# multiple PPNs w/ hold only : 2110860723 [06/10/2022]
# multiple PPNs + no hold : 2-07-037026-7 [06/10/2022]
# 1 PPN : 9782862764719 [06/10/2022]
# 0 PPN : 2212064004 [06/10/2022]

# Abes_isbn2ppn("978286719")
