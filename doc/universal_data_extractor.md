add things :

add to marc_feilds
(add to UI)

add to get_xml_namespace if the action is based on xml depending on how you call in actions

the filter value checks if it __starts with__

Sudoc SRU PICA XML is not supported 

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