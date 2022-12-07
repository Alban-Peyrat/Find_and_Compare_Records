# -*- coding: utf-8 -*- 

# External import
from fuzzywuzzy import fuzz

# Internal import
from scripts.prep_data import * # pour éviter de devoir réécrire tous les appels de fonctions

# Titles
# directly in the main loop

# Publishers
def teste_editeur(list_ed_sudoc, list_ed_koha):
    """Confront every Sudoc publishers with every Koha publishers and returns the pair with the higher matching ratio as a tuple :
            - score
            - chosen Sudoc publisher
            - chosen Koha publisher

    Args:
        list_ed_sudoc (list of strings): all 210/4$c of the Sudoc record
        list_ed_koha (list of strings): all 210/4$c of the Koha record
    """
    score = 0
    return_ed_sudoc = ""
    return_ed_koha = ""
    for ed_sudoc in list_ed_sudoc :
        ed_sudoc = clean_publisher(ed_sudoc)
        for ed_koha in list_ed_koha :
            ed_koha = clean_publisher(ed_koha)
            ratio_de_similarite = fuzz.ratio(ed_koha,ed_sudoc)
            if ratio_de_similarite > score :
                score = ratio_de_similarite
                return_ed_sudoc = ed_sudoc
                return_ed_koha = ed_koha
    return score, return_ed_sudoc, return_ed_koha

# Dates
def teste_date_pub(date_pub_sudoc, date_pub_koha):
    """Checks if one of Sudoc publication date matches on of Koha's and returns True if it's the case.

    Args:
        date_pub_sudoc (tuple of strings): 1st and 2nd publication date in the Sudoc record
        date_pub_koha (tuple of strings): 1st and 2nd publication date in the Koha record
    """
    # si Type de date de pub = reproduction on confronte la date de pub Alma à al date de pub. originale et à la date de reproduction
    # ↑ AlP : j'ai un doute sur ce commentaire du code original

    for date in date_pub_sudoc :
        if date in date_pub_koha and date != "    ": # excludes empty dates
            return True
    return False

# Koha bibnb dans ceux déjà présents dans la notice Koha
# Directly in the mainloop

# Global analysis
def analysis_checks(CHOSEN_ANALYSIS, check, res):
    """Launches each check for the analysis, returns the result as a boolean.
    
    Args:
        CHOSEN_ANALYSIS (dict) : the analysis chosen from settings.json["ANALYSIS"]
        check (string) : name of the check to perform
        res (dict) : the result dict of the record to check"""
    # Titles
    if check == "TITLE":
        res["TITLE_OK_NB"] = 0
        # for each matching score, checks if it's high enough
        title_score_list = ["SIMILARITE", "APPARTENANCE", "INVERSION", "INVERSION_APPARTENANCE"]
        for title_score in title_score_list:
            if res["MATCHING_TITRE_"+title_score] >= CHOSEN_ANALYSIS["TITLE_MIN_SCORE"]:
                res["TITLE_OK_NB"] += 1
        return (res["TITLE_OK_NB"] >= CHOSEN_ANALYSIS["NB_TITLE_OK"])
    # Publishers
    elif check == "PUB":
        return (res["MATCHING_EDITEUR_SIMILARITE"] >= CHOSEN_ANALYSIS["PUBLISHER_MIN_SCORE"])
    # Dates
    elif check == "DATE":
        return res["MATCHING_DATE_PUB"]