import csv
import json

with open('./settings.json', "r+", encoding="utf-8") as f:
    settings = json.load(f)

file = settings["OUTPUT_PATH"] + "/test.csv"
fieldnames_id = ["id", "value", "code"]
fieldnames_names = ["Identifiant", "Valeur", "LOVE COLORED MASTER SPARK"]
results = [{"id":1, "value":"ayaya", "code":"IN"},{"id":2, "value":"Ara ara", "code":"EoSD"}]
delimiter = ";"

    # """Generates the CSV output file.
    
    # Argument :
    #     - file_path
    #     - results {dict} : the dict containing all results
    #     - fieldnames_id {list of str} : name of the keys to export
    #     - delimiter [optionnal] {str}
    #     - fieldnames_names [optionnal] {list of str} : header name if different from the key ID"""
with open(file, 'w', newline="", encoding='utf-8') as f_csv:
    writer = csv.DictWriter(f_csv, extrasaction="ignore", fieldnames=fieldnames_id, delimiter=delimiter)
    
    # Headers generation
    if fieldnames_names == []:
        writer.writeheader()
    else:
        new_headers = {}
        for ii, id in enumerate(fieldnames_id):
            new_headers[id] = fieldnames_names[ii]
        writer.writerow(new_headers)

    for data in results:
        writer.writerow(data)
    # writer.writerows(results)

def a():
    print("a")
    print(b("b"))

def b(b):
    return b + "ara ara" 

a()