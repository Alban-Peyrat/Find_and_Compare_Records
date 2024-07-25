# Procédure d'installation de _Find and Compare Records_

Téléchargez l'application puis extrayez le contenu.

## Bibliothèques utilisées non incluses dans Python Standard Library

Ces bibliothèques sont utilisées par le script mais absentes de la [Python Standard Library](https://docs.python.org/3/library/), il est donc nécessaire de les installer dans un premier temps :

* _Rappel : sous Windows, ouvrir l'invite de commande, et taper les lignes de commandes suivantes après `py -m` (ou `pyhton -m`)_
* [`unidecode`](https://pypi.org/project/Unidecode/) (`pip install Unidecode==1.3.8`)
* [`FuzzyWuzzy`](https://pypi.org/project/fuzzywuzzy/) (`pip install fuzzywuzzy==0.18.0`)
  * With [`python-Levenshtein`](https://pypi.org/project/python-Levenshtein/) (`pip install python-Levenshtein==0.25.1`), installé avec `rapidfuzz` `3.9.3`
* [`FreeSimpleGUI`](https://pypi.org/project/FreeSimpleGUI/) (`pip install FreeSimpleGUI==5.1.0`)
* [`requests`](https://pypi.org/project/requests/) (`pip install requests==2.32.3`)
* [`python-dotenv`](https://pypi.org/project/python-dotenv/) (`pip install python-dotenv==1.0.1`)
* [`pymarc`](https://pypi.org/project/pymarc/) (`pip install pymarc==4.2.2` __(ne pas utiliser les versions `5.X.X` parce que certaines fonctions ne sont pas rétrocompatibles)__)
* [`pyisbn`](https://pypi.org/project/pyisbn) (`pip install pyisbn==1.3.1`)

## Fichier de configuration

À la racine du dossier se trouve un fichier `sample.env`, qu'il faut renommer en `.env`.
Ou il faut créer un fichier `.env` avec les variables :

* Variables générales :
    * `SERVICE` : nom du service (pour les journaux, dont le nom du fichier)
    * `LANG` : la langue de l'interface au format ISO 639-2 (seuls `fre` et `eng` sont supportés)
    * `PROCESSING_VAL` : `BETTER_ITEM`, `MARC_FILE_IN_KOHA_SRU`, `BETTER_ITEM_DVD`, `BETTER_ITEM_NO_ISBN` ou `BETTER_ITEM_MAPS`
* URL des bases de données :
  * `ORIGIN_URL` : URL (nom de domaine) de la base de donnée d'origine
  * `TARGET_URL` : URL (nom de domaine) de la base de donnée de destination
* Variables des traitements de la suite `BETTER_ITEM` :
  * `ILN` : ILN de l'établissement voulu
  * `RCR` : RCR de la bibliothèque voulue
* Variables du traitement `MARC_FILE_IN_KOHA_SRU` :
  * `FILTER1`
  * `FILTER2`
  * `FILTER3`
* Mapping des bases de données :
  * `ORIGIN_DATABASE_MAPPING` : nom du mapping de la base de données d'origine (`ORIGIN_DATABASE` par défaut)
  * `TARGET_DATABASE_MAPPING` : nom du mapping de la base de données de destination (`TARGET_DATABASE` par défaut)
* Configuration des journaux :
  * `LOGS_PATH` : chemin d'accès au dossier pour le fichiers des journaux
  * `LOG_LEVEL` : niveau de journalisation utilisé : `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (`INFO` par défaut)
* Chemin d'accès aux fichiers & dossiers :
  * `CSV_OUTPUT_JSON_CONFIG_PATH` : fichier de configuration de l'export CSV
  * `FILE_PATH` : chemin d'accès vers le fichier à traiter
  * `OUTPUT_PATH` : chemin d'accès vers le dossier qui contiendra les résultats
