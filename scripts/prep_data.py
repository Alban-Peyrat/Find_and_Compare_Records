# -*- coding: utf-8 -*- 

# External import
import re
from unidecode import unidecode

def prepString(_str, _noise = True, _multiplespaces = True):
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

def nettoie_titre(titre) :
    """Supprime les espaces, la ponctuation et les diacritiques transforme "&" en "et" et renvoie le résultat en minuscule.

    Args:
        titre (string): une chaîne de caractères
    """
    if titre is not None :
        titre_norm = prepString(titre)
        titre_norm = titre_norm.replace('&', 'et')
        titre_norm = titre_norm.replace('œ', 'oe')
        # out = re.sub(r'[^\w]','',unidecode(titre_norm))
        out = unidecode(titre_norm)
        return out.lower()
    else :
        return titre

def clean_publisher(pub):
    """Deletes from the publisher name a list of words and returns the result as a string.

    Takes as an argument the publisher name as a string."""
    if pub is not None :
        pub_noise_list = ["les editions", "les ed.", "les ed", "editions", "edition", "ed."] # this WILL probably delete too much things but we take the risk
        # pas "ed" parce que c'est vraiment trop commun
        pub_norm = prepString(pub, _noise=False) # We keep punctuation for the time being
        pub_norm = pub_norm.lower()
        pub_norm = pub_norm.replace('&', 'et')
        pub_norm = pub_norm.replace('œ', 'oe')
        pub_norm = unidecode(pub_norm)
        
        for car in pub_noise_list:
            pub_norm = pub_norm.replace(car, " ")
        
        return prepString(pub_norm) # we don't need punctuation anymore
    else :
        return pub

def get_year(txt):
    """Returns all 4 consecutive digits included in the string as a list of strings.
    
    Takes as an argument a string."""
    return re.findall("\d{4}", txt)