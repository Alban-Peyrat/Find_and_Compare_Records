# Find and Compare Records between two database

[![Active Development](https://img.shields.io/badge/Maintenance%20Level-Actively%20Developed-brightgreen.svg)](https://gist.github.com/cheerfulstoic/d107229326a01ff0f333a1d3476e068d)

_Documentation not fully updated_

* English user documentation _(not written yet)_
* __[Documentation utilisateur en français](./doc/user/FR)__

This application is used to match records between two databases, perform an automatic comparison of the two records and output a file extracting data from both the record in the original database and all matched records in the target databse.

It was originally a fork of [Alexandre Faure's script to analyze PPN imported in Alma Community Zone](https://github.com/louxfaure/AlmaCZRecord_To_Sudoc_Record).

Version 2.0.0 is developped for :

* Python 3.12
* [`unidecode`](https://pypi.org/project/Unidecode/) : `1.3.8`
* [`FuzzyWuzzy`](https://pypi.org/project/fuzzywuzzy/) : `0.18.0`
  * With [`python-Levenshtein`](https://pypi.org/project/python-Levenshtein/) : `0.25.1`, installed with `rapidfuzz` `3.9.3`
* [`FreeSimpleGUI`](https://pypi.org/project/FreeSimpleGUI/) : `5.1.0`
* [`requests`](https://pypi.org/project/requests/) : `2.32.3`
* [`python-dotenv`](https://pypi.org/project/python-dotenv/) : `1.0.1`
* [`pymarc`](https://pypi.org/project/pymarc/) : `4.2.2` __(do not use versions `5.X.X` as some functions are not retrocompatible)__
* [`pyisbn`](https://pypi.org/project/pyisbn) : `1.3.1`

Version 1.17.5 was developped for :

* Python 3.11
* [`unidecode`](https://pypi.org/project/Unidecode/) : `1.3.6`
* [`FuzzyWuzzy`](https://pypi.org/project/fuzzywuzzy/) : `0.18.0`
  * With [`python-Levenshtein`](https://pypi.org/project/python-Levenshtein/) : `0.23.0`
* [`PySimpleGUI`](https://pypi.org/project/PySimpleGUI/) : `4.60.4`
* [`requests`](https://pypi.org/project/requests/) : `2.28.1`
* [`python-dotenv`](https://pypi.org/project/python-dotenv/) : `1.0.0`
* [`pymarc`](https://pypi.org/project/pymarc/) : `4.2.2`