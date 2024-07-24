# Universal Data Extractor

## Add a database

[_Explained in `PODAs.md`, part dedicated to databases_](./PODAs.md#database)

## Adding an XML data source with new namespaces

[_Explained in `PODAs.md`, part dedicated to databases_](./PODAs.md#database)

## Add data to extract

* In `marc_fields.json`, [add an object](#setting-up-marc_fieldsjson) __to every mapping__ _(otherwise FCR will not boot up as it will crash trying to load existing mappings)_
* In `cl_UDE.py` :
  * Add a new member to `Mapped_Fields`, using as a value the key used in `marc_fields.json`
  * Add a property in `Marc_Fields_Mapping` by assigning it is value in `load_mapping`
  * Add a `get_` function in `Universal_Data_Extractor`
  * Add a case in `Universal_Data_Extractor.get_by_mapped_field_name()`
* See [output.md](./output.md#add-a-new-data-from-records) to add it to the output

## Add data to extract for a processing

[_Explained in `PODAs.md`, part dedicated to processings_](./PODAs.md#processing)

# Adding a `get_{data}` function

* Add another wanted data in Mapped_Fields and `marc_fields.json` + add dans FCR_procesings
* Inside the _class_ `Marc_Fields_Mapping`, add a property loading this new wanted data in `load_mapping` + get_by_mapped_field_name
* Add the `get_{data}` function, with :
  * A simple `return self.extract_list_of_ids()` to get a flatten list of strings without duplicates
  * A simple `return self.extract_list_of_strings()` to get a one layer flatten list of strings (merges subfield by separating them by a space)
  * A simple `return self.extract_list_of_lists()` to get a one layer flatten list (handy if you want to return a list of list)
  * Or code something if those 3 do not do what you want

## Setting up `marc_fields.json`

This file contains an object with at least two keys, `ORIGIN_DATABASE` and `TARGET_DATABASE`.
Extra keys can be added, like `SUDOC` or `KOHA_ARCHIRES` in order to save a database setting under a specific name.

Inside those database keys, there is another object containing a list of objects representing the wanted data.
Each one has a `label` and `fields` key, the last one being an object with :

* `tag` as a string
* `single_line_coded_data` as a boolean
* `filtering_subfield` as a string
* `subfields` and `positions` as arrays
  * For control fields (00X), all other data is ignored
  * If `filtering_subfield` is an empty string, is ignored
  * If `subfields` is an empty array, every subfield will be retrieved
  * `positions` is only used for single line coded data
  * `positions` must contain strings
  * MARC position always start at `0`
  * For multiple characters positions, separate the start and end (included) by `-` (`"13-17"`)

``` JSON
// New object example for marc_fields.json
"items": {
    "label": {
        "eng": "Items",
        "fre": "Exemplaires"
    },
    "fields": [
        {
            "tag": "995",
            "single_line_coded_data": false,
            "filtering_subfield": "",
            "subfields": [],
            "positions": []
        }
    ]
}
```