# -*- coding: utf-8 -*-

# External import
import csv

def generate_csv_output(file_path, results, fieldnames_id, delimiter=";",fieldnames_names=[]):
    """Generates the CSV output file.
    
    Argument :
        - file_path
        - results {dict} : the dict containing all results
        - fieldnames_id {list of str} : name of the keys to export
        - delimiter [optionnal] {str}
        - fieldnames_names [optionnal] {list of str} : header name if different from the key ID"""
    with open(file_path, 'w', newline="", encoding='utf-8') as f_csv:
        writer = csv.DictWriter(f_csv, extrasaction="ignore", fieldnames=fieldnames_id, delimiter=delimiter)
        
        # Headers generation
        if fieldnames_names == []:
            writer.writeheader()
        else:
            new_headers = {}
            for ii, id in enumerate(fieldnames_id):
                new_headers[id] = fieldnames_names[ii]
            writer.writerow(new_headers)

        writer.writerows(results)

def log_fin_traitement(logger, result, success):
    """Log une INFO pour dire que la ligne est terminée.
    Sert à modifier partout le message.
    
    Arguments:
        result {dict} - dict de la ligne en cours de traitement
        success {bool}"""
    if success:
        msg = "SUCCÈS"
    else:
        msg = "ÉCHEC"
    logger.info("{} du traitement de la ligne : ISBN = \"{}\", Koha Bib Nb = \"{}\"".format(msg, result["INPUT_ISBN"],result["INPUT_KOHA_BIB_NB"]))

def generate_report(REPORT_SETTINGS, FILES, KOHA_URL, CHOSEN_ANALYSIS, results_report, logger=None):
    """Génère le rapport. Mettre le logger pour créer le rapport dans le logs aussi.
    
    REPORT_SETTINGS:
        "name" {str} : libellé de la donnée
        "section" {int} : numéro de la section dans le rapport, commence à 0
        "var" : null si c'est juste une ligne de texte, sinon, le nom de la variable"""
    sections = []
    for row in REPORT_SETTINGS:
        line = row["name"]
        if row["var"] != None:
            line += " : " + str(eval(row["var"])) #très très mauvaise idée mais bon
        line += "\n"
        while len(sections) < row["section"]+1:
            sections.append([])
        sections[row["section"]].append(line)

    if logger == None:
        with open(FILES["OUT_RESULTS"], 'w', encoding='utf-8') as f:
            for section in sections:
                f.writelines(section)
                f.write("\n")
    else:
        for section in sections:
            logger.info("----- Nouvelle section -----")
            for line in section:
                logger.info(line[:-1])