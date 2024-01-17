# Add a new processing

* In `fcr_enum.py` :
  * Add a new entry in the `Enum FCR_Processings`, using as value a dict :
    * Use as keys `FCR_Mapped_Fields` entries you want to export at the end
    * Use as value for those keys `FCR_Processing_Data_Target` entries to specify from which base you want the data to be extracted
  * Add a new key in `PROCESSING_OPERATION_MAPPING` using :
    * A `FCR_Processings` entry as a key
    * A `Operations` entry as a value
* In `fcr_classes.py` :
  * In `Execution_Settings`, define the databases in `define_databases()` methods
  * In `Execution_Settings`, add a behaviour at the beginning of `load_original_file_data()` method
* In `main_gui.py` : see [in GUI doc](./GUI.md#hide-elements-for-some-processings)


<!-- in database_record, add a case with the processig, calling for ude gets wanted -->
