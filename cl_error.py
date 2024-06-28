# -*- coding: utf-8 -*- 

# External import
from enum import Enum
from typing import Dict

# Internal imports

class Errors(Enum):
    GENERIC_ERROR = 0
    NOTHING_WAS_FOUND = 1
    NO_EAN_WAS_FOUND = 2
    REQUIRED_DATA_MISSING = 3
    NO_ISBN_WAS_FOUND = 4
    ISBN_MODIFICATION_FAILED = 5
    MARC_CHUNK_RAISED_EXCEPTION = 6
    OPERATION_NO_RESULT = 7
    ISBN_979_CAN_NOT_BE_CONVERTED = 8

class Error(object):
    def __init__(self, error:Errors, msg:Dict[str, str]) -> None:
        """Takes as argument :
            - an Errors member
            - a dict using lang ISO code as key and error message as value"""
        self.enum_member = error
        self.name = error.name
        self.id = error.value
        self.msg = msg
    
    def get_msg(self, lang:str) -> str:
        """Returns the message in wanted lagnuage (return an empty string if nothing was found)"""
        if lang in self.msg:
            return self.msg[lang]
        return ""

ERRORS_LIST = {
    Errors.GENERIC_ERROR:Error(
        error=Errors.GENERIC_ERROR,
        msg={
            "eng":"Generic error",
            "fre":"Erreur générique"
        }
    ),
    Errors.NOTHING_WAS_FOUND:Error(
        error=Errors.NOTHING_WAS_FOUND,
        msg={
            "eng":"Nothing was found",
            "fre":"Aucun résultat"
        }
    ),
    Errors.NO_EAN_WAS_FOUND:Error(
        error=Errors.NO_EAN_WAS_FOUND,
        msg={
            "eng":"Original record has no EAN",
            "fre":"Notice originale sans EAN"
        }
    ),
    Errors.REQUIRED_DATA_MISSING:Error(
        error=Errors.REQUIRED_DATA_MISSING,
        msg={
            "eng":"Original record was missing one of the required data",
            "fre":"Données requises absentes dans la notice oringinale"
        }
    ),
    Errors.NO_ISBN_WAS_FOUND:Error(
        error=Errors.NO_ISBN_WAS_FOUND,
        msg={
            "eng":"Original record has no ISBN",
            "fre":"Notice originale sans ISBN"
        }
    ),
    Errors.ISBN_MODIFICATION_FAILED:Error(
        error=Errors.ISBN_MODIFICATION_FAILED,
        msg={
            "eng":"Failed to create a modified ISBN",
            "fre":"Échec de la création d'un ISBN modifié"
        }
    ),
    Errors.MARC_CHUNK_RAISED_EXCEPTION:Error(
        error=Errors.MARC_CHUNK_RAISED_EXCEPTION,
        msg={
            "eng":"Record was ignored because its chunk raised an exception",
            "fre":"Notice ignorée car une erreur s'est produite en l'interprétant"
        }
    ),
    Errors.OPERATION_NO_RESULT:Error(
        error=Errors.OPERATION_NO_RESULT,
        msg={
            "eng":"No results fot this operation",
            "fre":"Aucun résultat pour cette opération"
        }
    ),
    Errors.ISBN_979_CAN_NOT_BE_CONVERTED:Error(
        error=Errors.ISBN_979_CAN_NOT_BE_CONVERTED,
        msg={
            "eng":"Can only convert ISBN 13 starting with 978",
            "fre":"Seuls les ISBN 13 commençant par 978 peuvent être convertis"
        }
    )
}

def get_error_instance(err:Errors|str|int) -> Error:
    """Returns the wanted instance for the given Errors member.
    Argument can either be :
        - Enum member
        - Enum member name
        - Enum member value
    If using the name or value, the second argument must be the enum you want from"""
    # Arg is a member, easy to do
    if type(err) == Errors:
        return ERRORS_LIST[err]
    LIST = ERRORS_LIST
    if type(err) == str:
        return ERRORS_LIST[Errors[err]]
    elif type(err) == int:
        for member in Errors:
            if member.value == err:
                return LIST[member]
    return None