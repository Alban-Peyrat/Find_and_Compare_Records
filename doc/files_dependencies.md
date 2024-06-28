# Files dependencies

This document show which other internal files are required to be used.

## `cl_DBR.py`

Needs :

* `cl_PODA.py` for `Processing`, `Processing_Data_Target`, `Filters` & `Mapped_Fields`
* `cl_ES.py` for `Records_Settings`, `Analysis_Checks`
* `cl_UDE.py` for `Universal_Data_Extractor`
* `func_string_manip` for `list_as_string`, `clean_publisher`, `nettoie_titre` & `get_year`

## `cl_error.py`

__None__

## `cl_ES.py`

Needs :

* `cl_PODA.py` for `Processing_Names`, `Processing_Data_Target`, `Mapped_Fields` & `get_PODA_instance()`
  * So `cl_UDE.py` too

## `cl_main.py`

Needs :

* `cl_UDE.py` for `Mapped_Fields`
* `cl_ES.py` for `Execution_Settings`, `Records_Settings`, `CSV_Cols` &`Analysis_Checks`
* `cl_PODA.py` for `Processing`, `Processing_Names`, `Processing_Data_Target` & `Action_Names`
* `cl_DBR.py` for `Database_Record`
* `cl_MR.py` for `Matched_Records` & `Request_Try`
* `func_string_manip.py` for `list_as_string` & `get_year`

## `cl_MR.py`

Needs :

* `cl_error.py` for `Errors` & `get_error_instance()`
* `cl_PODA.py` for `Operation` & `Action_Names`
  * So `cl_UDE.py` too
* `cl_DBR` for `Database_Record`
* `func_string_manip.py` for `delete_for_sudoc()`

## `cl_PODA.py`

Needs :

* `cl_UDE.py` for `Database_Names` & `Mapped_Fields`

## `cl_UDE.py`

__None__

## `func_string_manip.py`

__None__
