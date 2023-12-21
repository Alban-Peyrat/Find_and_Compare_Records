
## Add a new data from records

* In `fcr_enum.py`, add two new entries in `Enum CSV_Cols` :
  * Use `ORIGIN_DB_` / `TARGET_DB_` followed by the name of the eleemnt in `Enum FCR_Mapped_Fields`
  * The value is used to determine the order of the columns in the CSV file
  * Usually, if both origin and target databases are displayed, display first the origin database then the target database next to each other
* In `csv_cols.json`, add a new object :
  * Use as key in the parent object the name of the element in `Enum FCR_Mapped_Fields`
  * Inside the new object, use a key the langauge as ISO 
  * For those names, usually write what it is followed by `origin DB` / `target DB` (`BDD d'origine`, `BDD de destination`)

### Add special modifications to data from records

* If the standard way of outputing data from records does not suit, add code to `Original_Record.CSV.__special_data` method in `fcr_classes.py`
* If those are special to a processing, add a new `Original_Record.CSV.__special_` method (or edit the existant one), and add a `elif` to `Original_Record.CSV.to_csv` method (__for both *Origin database record* and *Target database record* if needed__)

## Add new data (not from the record)

* In `fcr_enum.py`, add two new entries in `Enum CSV_Cols` :
  * Use `ORIGIN_DB_` / `TARGET_DB_` followed by the name of the eleemnt in `Enum FCR_Mapped_Fields`
  * The value is used to determine the order of the columns in the CSV file
* In `fcr_classes.py`, add code to `Original_Record.CSV.to_csv` method :
  * Add to `out` dictionnary the value, using the `Enum CSV_Cols` __name__ as a key
* In `csv_cols.json`, add a new object :
  * Use as key in the parent object the name of the element in `Enum FCR_Mapped_Fields`
  * Inside the new object, use a key the langauge as ISO 