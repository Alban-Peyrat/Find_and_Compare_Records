# How to install _Find and Compare Records_

Download the application and extract its content.

## Bibliothèques utilisées non incluses dans Python Standard Library

Those libraries are used by the script but are not in the [Python Standard Library](https://docs.python.org/3/library/), all of them should be installed first :

* _Reminder : with Windows, open the command terminal and write the following command lines after `py -m` (or `pyhton -m`). For example, to install `pyisbn`, write `py -m pip install pyisbn==1.3.1`_
* [`unidecode`](https://pypi.org/project/Unidecode/) (`pip install Unidecode==1.3.8`)
* [`FuzzyWuzzy`](https://pypi.org/project/fuzzywuzzy/) (`pip install fuzzywuzzy==0.18.0`)
  * With [`python-Levenshtein`](https://pypi.org/project/python-Levenshtein/) (`pip install python-Levenshtein==0.25.1`), installed with `rapidfuzz` `3.9.3`
* [`FreeSimpleGUI`](https://pypi.org/project/FreeSimpleGUI/) (`pip install FreeSimpleGUI==5.1.0`)
* [`requests`](https://pypi.org/project/requests/) (`pip install requests==2.32.3`)
* [`python-dotenv`](https://pypi.org/project/python-dotenv/) (`pip install python-dotenv==1.0.1`)
* [`pymarc`](https://pypi.org/project/pymarc/) (`pip install pymarc==4.2.2` __(do not use versions `5.X.X` as some functions are not retrocompatible)__)
* [`pyisbn`](https://pypi.org/project/pyisbn) (`pip install pyisbn==1.3.1`)

## Configuration file

At the root of the application is `sample.env` file which needs to be renammed in `.env`.
Or you need to create a new file `.env` with variables :

* General variables :
    * `SERVICE` : name of the service (for logs, including the file name)
    * `LANG` : the user interface language in ISO 639-2 format (`fre` & `eng` are the onyl supported language)
    * `PROCESSING_VAL` : `BETTER_ITEM`, `MARC_FILE_IN_KOHA_SRU`, `BETTER_ITEM_DVD`, `BETTER_ITEM_NO_ISBN` or `BETTER_ITEM_MAPS`
* Database URL :
  * `ORIGIN_URL` : origin database URL (domain name)
  * `TARGET_URL` : target database URL (domain name)
* Processing variables for `BETTER_ITEM` suite :
  * `ILN` : institution ILN for the library
  * `RCR` : library RCR
* Processing variables for `MARC_FILE_IN_KOHA_SRU` :
  * `FILTER1`
  * `FILTER2`
  * `FILTER3`
* Databases mapping :
  * `ORIGIN_DATABASE_MAPPING` : origin database mapping name (`ORIGIN_DATABASE` by default)
  * `TARGET_DATABASE_MAPPING` : target database mapping name (`TARGET_DATABASE` by default)
* Logs configuration :
  * `LOGS_PATH` : full path to the folder containing the log file
  * `LOG_LEVEL` : logging level to use : `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (`INFO` by default)
* Paths to file & folders :
  * `CSV_OUTPUT_JSON_CONFIG_PATH` : CSV export configuration file path
  * `FILE_PATH` : input file path
  * `OUTPUT_PATH` : output folder path
