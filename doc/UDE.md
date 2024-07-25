# Universal Data Extractor

## Setting up `marc_fields.json`

This file contains an object with at least two keys, `ORIGIN_DATABASE` and `TARGET_DATABASE`.
Extra keys can be added, like `SUDOC` or `KOHA_ARCHIRES` in order to save a database setting under a specific name.
__Every database must share the exact same list of extracted data__ (but the configuration of the data can be different).

The value of those database keys are another object containing a list of objects representing the data extracted.
Each one has a `label` and `fields` key.

`label` key : use the language code in ISO 639-2 as key, the value will be displayed in the user interface.

`fields` key : use a string as key, value is a list of objects with :

* `tag` (`str`) : MARC field tag containing the data to extract
  * For control fields (00X), all other properties of this object are ignored
* `single_line_coded_data` (`bool`) : if set to `True`, allows to extract only part of the subfields
* `filtering_subfield` (`str`) : the subfield on which to use the filter on
  * Checks if the subfield __starts with__ the given value
  * To ignore, assign an empty string
* `subfields` (`list` of `str`) : list of the subfields to extract as this data
  * To retrieve every subfield, set to an empty array
* `positions` (`list` of `str`) : if `single_line_coded_data` is set to `True`, which position to extract
  * MARC position always start at `0`
  * For multiple characters positions, separate the start and end (included) by `-` (`"13-17"`)

``` mermaid
---
title: marc_fields.json
---
flowchart TD

%% Définition des styles
  classDef Archires fill:#FF0000, color:#000;
  classDef imvt fill:#00FF00, color:#000;
  classDef ENSAMSP fill:#FFFF00, color:#000;
  classDef IUAR fill:#0000FF, color:#FFF;

%% Origin DB
subgraph db_od ["Database ORIGIN_DATABASE"]

  subgraph db_od_d1 ["Data 1 (ex : <i>id</i>)"]
    db_od_d1_label["<i>Label</i> property"]
    subgraph db_od_d1_fields ["Fields"]
      direction TB
      db_od_d1_field1["First MARC field"]
      db_od_d1_field2["Second MARC field"]
    end
    %% Aligning
    db_od_d1_label ~~~ db_od_d1_fields
    db_od_d1_field1 ~~~ db_od_d1_field2
  end

  subgraph db_od_d2 ["Data 2 (ex : <i>title</i>)"]
    db_od_d2_label["<i>Label</i> property"]
    subgraph db_od_d2_fields ["Fields"]
      db_od_d2_field1["First MARC field"]
    end
    %% Aligning
    db_od_d2_label ~~~ db_od_d2_fields
  end

end

subgraph db_td ["Database TARGET_DATABASE"]

  subgraph db_td_d1 ["Data 1 (ex : <i>id</i>)"]
    db_td_d1_label["<i>Label</i> property"]
    subgraph db_td_d1_fields ["Fields"]
      db_td_d1_field1["First MARC field"]
      db_td_d1_field2["Second MARC field"]
      db_td_d1_field3["Third MARC field"]
    end
    
    %% Aligning
    db_td_d1_label ~~~ db_td_d1_fields
    db_td_d1_field1 ~~~ db_td_d1_field2
    db_td_d1_field2 ~~~ db_td_d1_field3
  end

  subgraph db_td_d2 ["Data 2 (ex : <i>title</i>)"]
    db_td_d2_label["<i>Label</i> property"]
    subgraph db_td_d2_fields ["Fields"]
      direction TB
      db_td_d2_field1["First MARC field"]
      db_td_d2_field2["Second MARC field"]
    end
    %% Aligning
    db_td_d2_label ~~~ db_td_d2_fields
    db_td_d2_field1 ~~~ db_td_d2_field2
  end

end

%% Aligning
db_od ~~~~ db_td

```

A few example of extarcted data configuration :

``` JSON
// Basic data extarcted only from 1 control field
"id": {
    "label": {
        "eng": "Database ID",
        "fre": "ID base de donn\u00e9es"
    },
    "fields": [
        {
            "tag": "001",
            "single_line_coded_data": false,
            "filtering_subfield": "",
            "subfields": "",
            "positions": ""
        }
    ]
}
// Data extracted from two specific subfield in two different fields
"authors": {
    "label": {
        "eng": "Authors",
        "fre": "Auteurs"
    },
    "fields": [
        {
            "tag": "700",
            "single_line_coded_data": false,
            "filtering_subfield": "",
            "subfields": [
                "a",
                "b"
            ],
            "positions": []
        },
        {
            "tag": "701",
            "single_line_coded_data": false,
            "filtering_subfield": "",
            "subfields": [
                "a",
                "b"
            ],
            "positions": [
                ""
            ]
        }
    ]
}
// Extract only part of the fields
"general_processing_data_dates": {
    "label": {
        "eng": "Dates from general processing data",
        "fre": "Dates (donn\u00e9es g\u00e9n\u00e9rales de traitement)"
    },
    "fields": [
        {
            "tag": "100",
            "single_line_coded_data": true,
            "filtering_subfield": "",
            "subfields": [],
            "positions": [
                "9-12",
                "13-16"
            ]
        }
    ]
}
// Use filter to only extracted data from those matching
"other_database_id": {
    "label": {
        "eng": "IDs in other database",
        "fre": "IDs dans d'autres bases de donn\u00e9es"
    },
    "fields": [
        {
            "tag": "035",
            "single_line_coded_data": false,
            "filtering_subfield": "1",
            "subfields": [
                "a"
            ],
            "positions": []
        }
    ]
}
```

## Add a database

In the universal data extractor, they are only used to configure the XML namespace to use if necessary.
In FCR as a whole, they have more usage, but this is detailed in [`PODAs.md`](./PODAs.md#database)

* Add a new member in the `Enum Database_Names`

## Add an XML data source with new namespaces

If a new database is using XML with a specific namespace :

* If necessary, add a new member in `Enum Xml_Namespaces`, using the namespace prefix as a value
* If necessary, add a new entry in `XML_NS`, using the prefix as key and the URI as value
* Add a new `elif` to `Universal_Data_Extractor.get_xml_namespace()` method and configure it so it returns `/{prefix}:`

## Add data to extract

* In `marc_fields.json`, [add an object](#setting-up-marc_fieldsjson) __to every mapping__ _(otherwise FCR will not boot up as it will crash trying to load existing mappings)_
* In `cl_UDE.py` :
  * Add a new member to `Mapped_Fields`, using as a value the key used in `marc_fields.json`
  * Add a property in `Marc_Fields_Mapping` by assigning it is value in `load_mapping`
  * Add a `get_` function in `Universal_Data_Extractor` :
    * A simple `return self.extract_list_of_ids()` to get a flatten list of strings without duplicates
    * A simple `return self.extract_list_of_strings()` to get a one layer flatten list of strings (merges subfield by separating them by a space)
    * A simple `return self.extract_list_of_lists()` to get a one layer flatten list (handy if you want to return a list of list)
    * Or code something if those 3 do not do what you want
  * Add a case in `Universal_Data_Extractor.get_by_mapped_field_name()`
* See [output.md](./output.md#add-a-new-data-from-records) to add it to the output
