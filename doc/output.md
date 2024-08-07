
## Define headers

## Add a new data from records

* In `cl_ES.py`, add two new entries in `Enum CSV_Cols` :
  * Use `ORIGIN_DB_` / `TARGET_DB_` followed by the name of the element in `Enum Mapped_Fields` (in `cl_UDE.py`)
  * The value is used to determine the order of the columns in the CSV file
  * Usually, if both origin and target databases are displayed, display first the origin database then the target database next to each other
* In `csv_cols.json`, add a new object :
  * Use as key in the parent object the name of the element in `Enum Mapped_Fields` (in `cl_UDE.py`)
  * Inside the new object, use as key the language code in ISO 639-2
  * As a value, usually write __at the end__ `origin DB` / `target DB` (`BDD d'origine`, `BDD de destination`)

### Add special modifications to data from records

* If the standard way of outputing data from records does not suit, add code to `Original_Record.CSV.__special_data` method in `cl_main.py`
* If those are specific to a processing, add a new `Original_Record.CSV.__special_` method (or edit the existant one) and add a `elif` to `Execution_Settings.CSV.to_csv` method (__for both *Origin database record* and *Target database record* if needed__)
* In `Execution_Settings.CSV.__define_headers` method, be sure to add or delete the header in the part for special processing columns

## Add new data (not from the record)

* In `cl_ES.py`, add one or two new entries in `Enum CSV_Cols` :
  * Use `ORIGIN_DB_` / `TARGET_DB_` followed by the name of the element in `Enum Mapped_Fields` (in `cl_UDE.py`) if it's for both database
  * The value is used to determine the order of the columns in the CSV file
* In `fcr_classes.py` :
  * If it is not a database specific element, add it to the list in `Execution_Settings.CSV.__define_headers` method
  * Add code to `Original_Record.Output.to_csv` method : add to `out` dictionnary the value, using the `Enum CSV_Cols` __name__ as a key
* In `csv_cols.json`, add a new object :
  * Inside the new object, use as key the language code in ISO 639-2
  * As a value, usually write __at the end__ `origin DB` / `target DB` (`BDD d'origine`, `BDD de destination`)
