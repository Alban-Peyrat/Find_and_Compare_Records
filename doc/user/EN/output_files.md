# Results file documentation

The script creates 3 output files & 1 log file :

* [`results.csv`](#csv-file)
* [`results.json`](#json-file)
* [`results_report`](#text-file)
* [`{Service_nae}.log`](#logs)

## CSV file

Exported data for each processing is defined inside the code.

For data containing lists, every value inside them are concatenated and separated by a comma followed by a space.

## JSON file

Contains a more complete version of the processing informations, more representative of FCR internal data than the CSV export..

For example :

* Data containing lists still contain lists
* If multiple records are found in the target database, they all are gathered inside the same proporty of the origin database (whereas the CSV export has to duplicate the origin database record information)
* Every action tried are present, ntoably containing the query used or the failing cause

## Text file

This file contains a report of the analysis, reminding the configuration used & some statistics about the analysis results (number of processed records, number of fullt processed records, number of times an action was used and it succeeded, etc.)

## Logs

The file contains a reminder of the configuration used, the final report & some informations extarcted during the data retrieval or the analysis.

It is mostly used to find out why some logged errors happened or find clues on what part of FCR could have bugged.