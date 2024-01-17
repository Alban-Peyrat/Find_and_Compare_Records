Sudoc PICA XML is not supported

# Add a database

* In `fcr_classes.py` :
  * Add an entry to the _Enum_ `Databases` with as value :
    * Name = `FCR_Mapped_Fields` entry
    * Value = as a string, value of the filtered field||| but I don't know yet how to correctly configure this

# Adding an XML data source with new namespaces

* In `fcr_classes.py` :
  * Add the key / value to the _dict_ `XML_NS`
  * Add an entry to the _Enum_ `Xml_Namespaces` :
    * Name : the name inside the code
    * Value : the prefix code
  * Add a case to `Universal_Data_Extractor.get_xml_namespace()`

# Add data to extract :

* In `fcr_enum.py`, add an entry in `FCR_Mapped_Fields`
* In `marc_fields.json`, add an object in each mapping
* In `fcr_classes.py` :
  * Add a property in `Marc_Fields_Mapping` by assigning it is value in `load_mapping`
  * Add a `get_` function in `Universal_Data_Extractor`
  * Add a case in `Universal_Data_Extractor.get_by_mapped_field_name()`
* See [output.md](./output.md) to add it to the output

# Add data to extract for a processing

* In `fcr_enum.py` :
  * Add a key for the processing entry in `FCR_Processings`, using as key a `FCR_Mapped_Fields` entry and as value a `FCR_Processing_Data_Target` entry

# For filtered fields

* In `fcr_enum.py` :
  * If needed, add a new entry in `FCR_Filters`, `Execution_Settings.__init__()` inside the `if` for filters (you're supposed to already ahve added an environmental variable in `Execution_Settings` and the UI)
  * In `Databases`, add an element using as key a `FCR_Mapped_Fields` entry and as value a `FCR_Filters` entry

The filter value checks if it __starts with__.

# Adding a `get_{data}` function

* Add another wanted data in FCR_Mapped_Fields and `marc_fields.json` + add dans FCR_procesings
* Inside the _class_ `Marc_Fields_Mapping`, add a property loading this new wanted data in `load_mapping` + get_by_mapped_field_name
* Add the `get_{data}` function, with :
  * A simple `return self.extract_list_of_ids()` to get a flatten list of strings without duplicates
  * A simple `return self.extract_list_of_strings()` to get a one layer flatten list of strings (merges subfield by separating them by a space)
  * A simple `return self.extract_list_of_lists()` to get a one layer flatten list (handy if you want to return a list of list)
  * Or code something if those 3 do not do what you want

# Setting up `marc_fields.json`

This file contains an object with at least two keys, `ORIGIN_DATABASE` and `TARGET_DATABASE`.
Extra keys can be added, like `SUDOC` or `KOHA_ARCHIRES` in order to save a database setting under a specific name.

Inside those database keys, there is another object containing a list of objects representing the wanted data.
Each one has a `label` and `fields` key, the last one being an object with :

* `tag` as a string
* `single_line_coded_data` as a boolean
* `filtering_subfield` as a string
* `subfields` and `positions` as arrays
  * For control fields (00X), all pother data is ignored
  * If `filtering_subfield` is an empty string, is ignored
  * If `subfields` is an empty array, every subfield will be retrieved
  * `positions` is only used for single line coded data
  * `positions` must contain strings
  * MARC position always start at `0`
  * For multiple characters positions, separate the start and end (included) by `-` (`"13-17"`)