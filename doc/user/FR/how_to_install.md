# Procédure d'installation de _Find and Compare Records_

Téléchargez l'application puis extrayez le contenu.

## Bibliothèques utilisées non incluses dans Python Standard Library

Ces bibliothèques sont utilisées par le script mais absentes de la [Python Standard Library](https://docs.python.org/3/library/), il ets donc nécessaire de les installer dans un premier temps :
* [`unidecode`](https://pypi.org/project/Unidecode/)
* [`FuzzyWuzzy`](https://pypi.org/project/fuzzywuzzy/)
  * With [`python-Levenshtein`](https://pypi.org/project/python-Levenshtein/)
* [`PySimpleGUI`](https://pypi.org/project/PySimpleGUI/)
* [`requests`](https://pypi.org/project/requests/)
* [`python-dotenv`](https://pypi.org/project/python-dotenv/)
* [`pymarc`](https://pypi.org/project/pymarc/)

## Fichier de configuration

À la racine du dossier se trouve un fichier `sample.env`, qu'il faut renommer en `.env`.
Ou il faut créer un fichier `.env` avec les variables :

* Variables générales :
    * `SERVICE` : nom du service (pour les journaux, dont le nom du fichier)
    * `LANG` : la langue de l'interface au format ISO 639-2 (seuls `fre` et `eng` sont supportés)
    * `PROCESSING_VAL` : `BETTER_ITEM` ou `OTHER_DB_IN_LOCAL_DB` (au 22/11/2023, seul `BETTER_ITEM` est supporté)
* URL des bases de données :
  * `ORIGIN_URL` : URL (nom de domaine) de la base de donnée d'origine
  * `TARGET_URL` : URL (nom de domaine) de la base de donnée de destination
* Variables du traitement `BETTER_ITEM` :
  * `ILN` : ILN de l'établissement voulu
  * `RCR` : RCR de la bibliothèque voulue
* Variables du traitement `OTHER_DB_IN_LOCAL_DB` :
  * `FILTER1`
  * `FILTER2`
  * `FILTER3`
* Mapping des bases de données :
  * `ORIGIN_DATABASE_MAPPING` : nom du mapping de la base de données d'origine
  * `TARGET_DATABASE_MAPPING` : nom du mapping de la base de données de destination
* Configuration des journaux :
  * `LOGS_PATH` : chemin d'accès au dossier pour le fichiers des journaux
  * `LOGGER_LEVEL` : niveau de journalisation utilisé, __uniquement configurable directement dans ce fichier__. Prend les valeurs `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`, avec `INFO` par défaut
* Configuration des chemins d'accès aux fichiers et dossiers :
  * `FILE_PATH` : chemin d'accès vers le fichier à traiter
  * `OUTPUT_PATH` : chemin d'accès vers le dossier qui contiendra les résultats
