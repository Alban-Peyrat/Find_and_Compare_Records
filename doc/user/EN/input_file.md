# Input file documentation

The input file changes depending on the processing :

* [`BETTER_ITEM` suite](#better_item-suite) (`BETTER_ITEM`, `BETTER_ITEM_DVD`, `BETTER_ITEM_NO_ISBN`, `BETTER_ITEM_MAPS`)
* [`MARC_FILE_IN_KOHA_SRU`](#marc_file_in_koha_sru)

## `BETTER_ITEM` suite

The file used is a CSV like, using `;` as separator.

This file contains informations about an item, the origin database identifier and (sometimes) an identifier used in some queries.
This last identifer is only used in the `BETTER_ITEM` processing and must be an ISBN.

The file __has to__ have as :

* First column the column using the identifier for queries (ISBN for `BETTER_ITEM`, empty columns or with another data for the other processings)
* Last column is the one containing origin database identifier

Every column of the file will be exported at the end of the CSV export.

## `MARC_FILE_IN_KOHA_SRU`

File used is a simple records file in ISO 2709, containing items.