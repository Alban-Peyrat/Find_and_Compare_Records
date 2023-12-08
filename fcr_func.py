# -*- coding: utf-8 -*- 

# External imports
import re
from unidecode import unidecode

# ---------- Start of old prep_data ----------

def prep_string(_str:str, _noise = True, _multiplespaces = True) -> str:
    """Returns a string without punctuation and/or multispaces stripped and in lower case.

    Takes as arguments :
        - _str : the string to edit
        - _noise [optional] {bool} : remove punctuation ?
        - _multispaces [optional] {bool} : remove multispaces ?
    """
    # remove noise (punctuation) if asked (by default yes)
    if _noise:
        noise_list = [".", ",", "?", "!", ";","/",":","="]
        for car in noise_list:
            _str = _str.replace(car, " ")
    # replace multiple spaces by ine in string if requested (default yes)
    if _multiplespaces:
        _str = re.sub("\s+", " ", _str).strip()
    return _str.strip().lower()

def nettoie_titre(titre:str) -> str:
    """Supprime les espaces, la ponctuation et les diacritiques transforme "&" en "et" et renvoie le résultat en minuscule.

    Args:
        titre (string): une chaîne de caractères
    """
    if titre is not None :
        titre_norm = prep_string(titre)
        titre_norm = titre_norm.replace('&', 'et')
        titre_norm = titre_norm.replace('œ', 'oe')
        # out = re.sub(r'[^\w]','',unidecode(titre_norm))
        out = unidecode(titre_norm)
        return out.lower()
    else :
        return titre

def clean_publisher(pub:str) -> str:
    """Deletes from the publisher name a list of words and returns the result as a string.

    Takes as an argument the publisher name as a string."""
    if pub is not None :
        pub_noise_list = ["les editions", "les ed.", "les ed", "editions", "edition", "ed."] # this WILL probably delete too much things but we take the risk
        # pas "ed" parce que c'est vraiment trop commun
        pub_norm = prep_string(pub, _noise=False) # We keep punctuation for the time being
        pub_norm = pub_norm.lower()
        pub_norm = pub_norm.replace('&', 'et')
        pub_norm = pub_norm.replace('œ', 'oe')
        pub_norm = unidecode(pub_norm)
        
        for car in pub_noise_list:
            pub_norm = pub_norm.replace(car, " ")
        
        return prep_string(pub_norm) # we don't need punctuation anymore
    else :
        return pub

def get_year(txt:str) -> str:
    """Returns all 4 consecutive digits included in the string as a list of strings.
    
    Takes as an argument a string."""
    return re.findall("\d{4}", txt)

# ---------- End of old prep_data ----------

def delete_control_char(txt: str) -> str:
    """Returns the string without control characters"""
    return re.sub(r"[\x00-\x1F]", " ", str(txt))

def list_as_string(this_list: list) -> str:
    """Returns the list as a string :
        - "" if the lsit is empty
        - the first element as a string if there's only one element
        - if after removing empty elements there is only one element, thsi element as a string
        - the lsit a string if there are multiple elements.
    Takes as argument a list"""
    if len(this_list) == 0:
        return ""
    elif len(this_list) == 1:
        return delete_control_char(str(this_list[0]))
    else:
        if type(this_list) != list:
            return delete_control_char(str(this_list))
        non_empty_elements = []
        for elem in this_list:
            if elem:
                non_empty_elements.append(elem)
        if len(non_empty_elements) == 0:
            return ""
        elif len(non_empty_elements) == 1:
            return delete_control_char(str(non_empty_elements[0]))
        else:
            return delete_control_char(str(non_empty_elements))
