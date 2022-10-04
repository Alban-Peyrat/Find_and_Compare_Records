#!/usr/bin/python3
# -*- coding: utf-8 -*- 
import json
import os
import logging
import logs
import AbesXml
import re
from pymarc import MARCReader
from unidecode import unidecode
from fuzzywuzzy import fuzz

SERVICE = "Alma_CZRecord_To_SUDOC_Record"
FILE_IN = '/media/sf_LouxBox/Notices_Chargees_CZ.mrc'
# FILE_IN = '/media/sf_LouxBox/test2.mrc'
ILE_OUT = '/media/sf_LouxBox/Collection_Electroniques_UB.txt'
LIST_ERROR_ADM = []

#On initialise le logger
logs.init_logs(os.getenv('LOGS_PATH'),SERVICE,'DEBUG')
logger = logging.getLogger(SERVICE)


noise_list = [".", ",", "?", "!", ";","/",":","="]
def prepString(_str, _noise = True, _multiplespaces = True):
    # remove noise (punctuation) if asked (by default yes)
    if _noise:
        for car in noise_list:
            _str = _str.replace(car, " ")
    # replace multiple spaces by ine in string if requested (default yes)
    if _multiplespaces:
        _str = re.sub("\s+", " ", _str).strip()
    return _str.strip().lower()

def nettoie_titre(titre) :
    """Supprime les espace, la ponctuation et les diacritiques transforme & en and

    Args:
        titre (string): une chaîne de caractère
    """
    if titre is not None :
        titre_norm = prepString(titre)
        titre_norm = titre_norm.replace('&', 'and')
        titre_norm = titre_norm.replace('œ', 'oe')
        # out = re.sub(r'[^\w]','',unidecode(titre_norm))
        out = unidecode(titre_norm)
        return out.lower()
    else :
        return titre

def teste_date_pub(date_pub_sudoc,date_pub_alma):
    # si Type de date de pub = reproduction on confronte la date de pub Alma à al date de pub. originale et à la date de reproduction
    for date in date_pub_sudoc :
        logger.debug(date)
        logger.debug(date_pub_alma)
        if date in date_pub_alma:
            return True
    return False

def teste_ppn(ppn_sudoc,ppn_alma):
    if ppn_sudoc == ppn_alma[5:]:
        return True
    else : 
        return False


def zones_multiples(code_champ,code_sous_champ,record):
    liste_valeurs = []
    for champ in record.get_fields(code_champ):
        liste_valeurs.append(champ[code_sous_champ])
    return liste_valeurs

def get_ppn(record):
    ppn_list = []
    champs_035 = zones_multiples('035','a',record)
    logger.debug(champs_035)
    for sys_number in champs_035 :
        if sys_number is not None :
            if sys_number.startswith('(PPN)') :
                ppn_list.append(sys_number[5:14])
    return ppn_list

def teste_editeur(list_ed_sudoc,list_ed_alma):
    score = 0
    return_ed_sudoc = ""
    return_ed_alma = ""
    for ed_sudoc in list_ed_sudoc :
        for ed_alma in list_ed_alma :
            ratio_de_similarite = fuzz.ratio(nettoie_titre(ed_alma),nettoie_titre(ed_sudoc))
            if ratio_de_similarite > score :
                score = ratio_de_similarite
                return_ed_sudoc = ed_sudoc
                return_ed_alma = ed_alma
    return score, return_ed_sudoc, return_ed_alma


results = []
with open(FILE_IN, 'rb') as fh:
    reader = MARCReader(fh)
    for record in reader:
        result = {}
        result['ERROR'] = False
        result['ERROR_MSG'] = ''
        logger.debug(record.title())
        # Récupération des données de la notice CZ
        result['CZ_Leader'] = record.leader
        result['CZ_001'] = record['001'].value() 
        result['CZ_008'] = record['008'].value() 
        result['CZ_DATE_TYPE'] = result['CZ_008'][6:7]
        result['CZ_DATE_1'] = result['CZ_008'][7:11]
        result['CZ_DATE_2'] = result['CZ_008'][11:15]
        # result['CZ_020$a'] = zones_multiples('020','a',record)
        result['CZ_264$b'] = zones_multiples('264','b',record)
        result['CZ_PPN'] = get_ppn(record)
        titre = record['245']
        titre_complet = titre.get_subfields('a','b','n','p')
        result['CZ_245abnp'] = nettoie_titre(' '.join(titre_complet))
        logger.debug(result['CZ_PPN'])
        if len(result['CZ_PPN']) == 0 :
            result['ERROR'] = True
            result['ERROR_MSG'] = 'Pas de PPN dans la notice CZ'
            continue
        # Récupération de la notice SUDOC
        for ppn in result['CZ_PPN'] :
            sudoc_record = AbesXml.AbesXml(ppn,service=SERVICE)
            if sudoc_record.status == 'Error' :
                result['ERROR'] = True
                result['ERROR_MSG'] = sudoc_record.error_msg
                continue
            result['MATCHING_PPN'] = ppn
            result['SUDOC_Leader'] = sudoc_record.get_leader()
            result['SUDOC_200adehiv'] = nettoie_titre(sudoc_record.get_title_info())
            logger.debug(result['SUDOC_200adehiv'])
            result['MATCHING_TITRE_SIMILARITE'] = fuzz.ratio(result['CZ_245abnp'].lower(),result['SUDOC_200adehiv'].lower())
            result['MATCHING_TITRE_APPARTENANCE'] = fuzz.partial_ratio(result['CZ_245abnp'].lower(),result['SUDOC_200adehiv'].lower())
            result['MATCHING_TITRE_INVERSION'] = fuzz.token_sort_ratio(result['CZ_245abnp'],result['SUDOC_200adehiv'])
            result['MATCHING_TITRE_INVERSION_APPARTENANCE'] = fuzz.token_set_ratio(result['CZ_245abnp'],result['SUDOC_200adehiv'])
            result['SUDOC_100a'],result['SUDOC_DATE_TYPE'],result['SUDOC_DATE_1'],result['SUDOC_DATE_2'] = sudoc_record.get_dates_pub()
            result['SUDOC_214210c'] = sudoc_record.get_editeurs()
            result['MATCHING_DATE_PUB'] = teste_date_pub((result['SUDOC_DATE_1'],result['SUDOC_DATE_2']),(result['CZ_DATE_1'],result['CZ_DATE_2']))
            if len(result['CZ_264$b']) > 0 and len(result['SUDOC_214210c']) > 0 : 
                result['MATCHING_EDITEUR_SIMILARITE'],result['SUDOC_214210c'],result['CZ_264$b'] = teste_editeur(result['CZ_264$b'],result['SUDOC_214210c'])
            # Si les dates ne matche pas on va voir si la notice possède un lien vers la version physique pour aller tester cette date
            if not result['MATCHING_DATE_PUB'] :
                result['MATCHING_DATE_PUB_PRINT'] = False
                result['SUDOC_452'] = sudoc_record.get_ppn_autre_support()
                logger.debug("452 : {}".format(result["SUDOC_452"]))
                for ppn_print in result['SUDOC_452'] :
                    if not result['MATCHING_DATE_PUB_PRINT'] :
                        sudoc_record_print = AbesXml.AbesXml(ppn_print,service=SERVICE)
                        result['SUDOC_100a_PRINT'],result['SUDOC_DATE_TYPE_PRINT'],result['SUDOC_DATE_1_PRINT'],result['SUDOC_DATE_2_PRINT'] = sudoc_record_print.get_dates_pub()
                        result['MATCHING_DATE_PUB_PRINT'] = teste_date_pub((result['SUDOC_DATE_1_PRINT'],result['SUDOC_DATE_2_PRINT']),(result['CZ_DATE_1'],result['CZ_DATE_2']))



            results.append(result)
with open('data2.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=4)
            