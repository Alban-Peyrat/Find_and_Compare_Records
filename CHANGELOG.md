# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

_Some previous changes will be added_


## [Unreleased]

### Added

* Documentation now states which library versions were used for development (due to issues with `PySimpleGUI` in this project and `pymarc` in another project)

### Changed

* Now developped for :
  * Python 3.12 (3.11 before)
  * `unidecode 1.3.8` (`1.3.6` before)
  * `python-Levenshtein 0.25.1` (`0.23.0` before)
  * `requests 2.32.3` (`2.28.1` before)
  * `python-dotenv 1.0.1` (`1.0.0` before)
* Changed graphic user interface library from `PySimpleGUI 4.2.2` to `FreeSimpleGUI 5.1.0`

### Fixed

* Put back the mention of Alexandre Faure original script (that I apprently deleted)

## [1.17.5] - 2024-04-11

### Fixed

* `Universal_Data_Extractor.extract_list_of_strings` method does not crash anymore if some subfield had no values
* ASCII range (hexadecimal) `21-2F`, `3A-40`, `5B-60`, `7B-7F` added to the noise list

## [1.17.4] - 2024-03-28

### Added

* New action requesting Koha SRU only using title on the title index

### Changed

* The operation `SEARCH_IN_KOHA_SRU_VANILLA` now queries as a last resort Koha SRU using only the title

## [1.17.3] - 2024-03-20

### Added

* Transformations before request actions using titles, authors or publishers now deletes every word that does not start with a letter or a number

### Changed

* Reordered some columns in CSV output :
  * Document type is now between erroneous ISBN and titles
  * Authors are now between document type and titles
  * Matched IDs, database ID and current ID are moved after FCR prcessed ID

### Fixed

* Added more dahs to the noise deletion process (Unicode 2010 to 2015)

## [1.17.2] - 2024-03-19

### Added

* New exportable data : piece (UNIMARC 463, internal name is `linking_piece`) and document type
* New action : query title, publisher and publication date in the _any_ index in Koha SRU (added to `SEARCH_IN_KOHA_SRU_VANILLA` operation)

### Changed

* Processing `MARC_FILE_IN_KOHA_SRU` now export :
  * Physical descriptions for both records
  * Items barcodes for both records
  * Document type for both records
  * Piece for both records
* Koha SRU now uses _Filter 1_ to filter items and items barcode information
* Mapping `KOHA_ARCHIRES` now uses `b` as filtering subfield for items and items barcode
* Added `collectif` & `collectifs` as empty words to delete

### Fixed

* Added `°` to noise list

## [1.17.1] - 2024-03-14

### Fixed

* Added `UN` to the lsit of empty words deleted
* Added `+` to the list of deleted noise
* Logs now properly write the target database value instead of the origin database twice

## [1.17.0] - 2024-02-28

### Changed

* JSON output exports much mor eprecise data, including raw data from records

### Fixed

* Lists containing one element and empty elements are now properly output in CSV export

## [1.16.2] - 2024-02-28

### Fixed

* CSV output does not replace `D` by spaces anymore

## [1.16.1] - 2024-02-16

### Fixed

* List of list should not crash the CSV output function anymore

## [1.16.0] - 2024-02-14

### Added

* New action `ISBN2PPN_MODIFIED_ISBN_SAME_KEY` was added to `SEARCH_IN_SUDOC_BY_ISBN` operation after `ISBN2PPN_MODIFIED_ISBN` : they behave the same axcept that the new one keeps the original input ISBN check digit instead of recomputing it
* New FCR processed ID with the form : `XXXXXZYYY` :
  * `XXXXX` : record index of the file being processed, with leadings `0` (always 5 character long)
  * `Z` :
    * `Z` : failed before getting origin database record
    * `O` : origin database record retrieved, failed before getting matched records
    * `M` : successfully matched records, failed before looping through matched records
    * `Y` : failed before getting the target database record
    * `T` : failed to analyze the target database record
    * `A` : succesfully did all the checks
  * `YYY` : matched record index, `XXX` if it failed before looping through matched records
* Errors are now translated

### Changed

* Internal changes on the management of processings, operations, databases, UI screens, screen tabs and errors
* Main function and classes are less dependent on the big execution settings variable

### Fixed

* The function exporting lists as strings no longer replaces `1` by a space
* Action `ISBN2PPN_MODIFIED_ISBN` now properly query the modified ISBN instead of the original one
* Actions `ISBN2PPN_MODIFIED_ISBN` and `ISBN2PPN_MODIFIED_ISBN_SAME_KEY` now return a new error if a modified ISBN failed to be created

### Deleted

* Old configuration script `define_default_settings_GUI.py`

## [1.15.0] - 2024-02-07

### Added

* New extractable data : exported to digital library, maps horizontal scales, maps mathematical data, series, series link, geographical subject
* Processing `MARC_FILE_IN_KOHA_SRU` now exports if record was exported to digital library
* New processings : `BETTER_ITEM_NO_ISBN` & `BETTER_ITEM_MAPS`
* Duplicated Sudoc SRU actions limited on `V` document type to query `B` and `K`

### Fixed

* Processing `BETTER_ITEM_DVD` now properly applies `BETTER_ITEM` 's special transformation before exporting data to CSV

## [1.14.3] - 2024-02-05

### Fixed

* Updated `Koha_SRU` & `Abes_SRU` versions, including a fix preventing crashes when the SRU responded with a `numberOfRecords` but data retrieved from it could not be changed to integer

## [1.14.2] - 2024-02-02

### Changed

* `list_as_string()` now returns values separated by `, ` without being enclosed in `[]`

### Fixed

* Fixed records missing general processing data crashing the export to CSV function, thus not exporting every data
* Fixed crashes when trying to use regular expression on some strings containing Unicode format characters after merging them with `list_as_string()`

## [1.14.1] - 2024-01-25

### Changed

* Report is more precise
* Results files are nammed `results` instead of `resultats`, the reprot file is now called `results_report`

### Fixed

* Report is back

### Removed

* `outputing.py` (moved its final function inside `Report` class in `fcr_classes.py`)
* `scripts` folder as nothing was there anymore

## [1.14.0] - 2024-01-25

### Added

* New file in user documentation explaining the exported data (only calculated fields)
* New processing analysing a local MARC file and querying a Koha SRU (`MARC_FILE_IN_KOHA_SRU`)
* Added actions for Koha SRU :
  * ISBN
  * Title, author, publisher and date using their own indexes
  * Title, author and date using their own indexes
  * Title, author, publisher and date using `any` index
  * Title, author and date using `any` index
* Added a new operation to query Koha SRU `SEARCH_IN_KOHA_SRU_VANILLA`
* Added ISBN as extractable data from records
* Added `Utils` methods to `Database_Records` to get the first ISBN and the first EAN as a string
* Added `Utils` methods to `Database_Records` to get the other database IDs
* Added a new default marc field mapping

### Changed

* `OTHER_DB_IN_LOCAL_DB` was renammed in `MARC_FILE_IN_KOHA_SRU`
* Updated `Koha_SRU` and `Koha_API_PublicBiblio` version
* Filters are now properly implanted
* Records are now correctly retrieved from the correct database instead of Koha (origin database) and Sudoc (target database)

### Fixed

* Fixed displayed processing in *Processing configuration* screen, previously not updating properly if selected processing was changed in the main screen
* Fixed `Database_Record.utils` methods crashing the application if some data was not extracted from the record (or if there is no title returned)
* Fixed some errors in main function not logging themselves
* Fixed marc field mapping using only to `ORIGIN_DATABASE` and `TARGET_DATABASE`
* Fixed universal data extractor not extracting anything from single line coded data if positions in a range larger than the max length of the field content
* Fixed crashes if other database IDs were not exported for the target database : a new value `SKIPPED` is used in those cases

## [1.13.1] - 2024-01-15

### Added

* Authors are exported in processing `BETTER_ITEM`

### Changed

* Changed Koha SRU connector version
* ID validation and analysis result now output text instead of internal codes
* Changed some columns names

### Fixed

* Fixed CSV column names configuration file browse type
* Fixed `BETTER_ITEM` target database *has items* not displaying the correct information

## [1.13.0] - 2023-12-22

### Added

* Added changelog file
* New processing `BETTER_ITEM_DVD`
* New actions :
  * EAN to PPN
  * Sudoc SRU using title, authors, publishers and dates using audiovisual document type
  * Sudoc SRU using title, authors and dates using audiovisual document type
  * Sudoc SRU in all indexes using title, authors, publishers and dates using audiovisual document type
  * Sudoc SRU in all indexes using title, authors and dates using audiovisual document type
  * Sudoc SRU in all indexes using title, authors and publishers using audiovisual document type
* New functions to :
  * Delete CBS boolean operators
  * Delete Sudoc empty words
  * Use both of the previous at the same time
  * Delete duplicate words in a string
* `Class Database_Record` now has a `utils` property with methods to return data formatted
* New environment variable `CSV_OUTPUT_JSON_CONFIG_PATH`, selectable in the UI
* Log level is selectable in the UI
* Used action is now exportable
* New `json_configs` file : `csv_cols.json` (and a personnalised `csv_cols_BETTER_ITEM.json`)

### Changed

* Documentation to add actions, operations and processings are more clear
* The noise deletion function deletes more noise
* Authors data defaults to fields `700`, `701`, `702`, `710`, `711` and `712`
* Some output functions have been moved to a new `output` property of `Class Original_Record`
* Internal changes to error management
* Internal changes to logs, notably updated old logged informations and only logging once the query used
* Reworked CSV export

### Fixed

* Changed `id2ppn.py` version to fix incorrect status and incorrect returned value if only one record matched with JSON returned data
* Changed `Sudoc_SRU.py` version to fix XML parse errors when some queries using angle brackets were not properly transformed in Sudoc's response
* Create the output folder if it does not exist
* Output used query display the actual query used

### Removed

* File `csv_export_cols.json`
* `logs.py` (moved its fucntion inside `Logger` subclass in `fcr_classes.py`)

## [1.12.1] - 2023-12-08

### Changed

* Default analysis is now _Titles 80% (3 out of 4), publishers 80%, dates_
* Checking if the ID from the origin database is in the target list of othre database IDs is now more precise ([see `Enum Other_Database_Id_In_Target` in `fcr_enum.py`](./fcr_enum.py "Open the file fcr_enum.py"))
* Global validation has now 2 output columns : the previous one now returns values from [`Enum Analysis_Final_Results` in `fcr_enum.py`](./fcr_enum.py "Open the file fcr_enum.py") and the new one the number of successful checks

### Fixed

* Values filled in the UI without being saved are now properly sent to the main script, instead of using saved values

## [1.12.0] - 2023-12-08

### Added

* Multipe matches are now all retrieved instead of throwing a fake error

### Fixed

* Does not check if the biblionumber is different than those in the Sudoc if no biblionumbers are found in the Sudoc (previous behaviour)

### Removed

* Removed the fake error concept

## [1.11.0] - 2023-11-22

### Changed

* Graphic user interface has been entirely remade and can now configure most configurations
* French user documentation updated

### Fixed

* Fixed an error on unknown ISBN in `isbn2ppn`

## [1.10.0] - 2023-10-20

### Added

* Test files for the universal data extractor

### Changed

* Application name is now _Find and Compare Records_
* List outputing in CSV file is now an emty cell if the list is empty, or just the value if list contains only one value
* Internal changes, notably centralizing data export functions so they are universal
* Technical documentation about the universal data extractor

## [1.9.0] - 2023-10-03

### Added

* Technical documentation for the matching records part
* Can now query Sudoc's SRU
* Now query Sudoc's SRU using ISBN if both query on `isbn2ppn` failed

### Changed

* Internal changes to start implementing classes
* Report is now broken

## [1.8.0] - 2022-09-07

### Added

* Outputs erroneous ISBN from Koha & Sudoc

### Changed

* Part of the settings were moved from `settings.json` to a `.env` file

## [1.7.2] - 2023-04-21

### Fixed

* Changed `Koha_API_PublicBiblio.py` version to fix crashes when Koha record had only empty subfields in the title

## [1.7.1] - 2023-03-17

### Fixed

* Changed `Abes_isbn2ppn.py` version to fix invalid ISBN returned values

## [1.7.0] - 2023-03-01

### Added

* Output years found inside Koha `215$a`

## [1.6.0] - 2023-02-15

### Added

* `Abes_isbn2ppn.py` is now queried with a converted version of ISBN 10 to 13 (or the other way) if the first query did not return result

## [1.5.0] - 2023-02-08

### Added

* Output notes about edition for both Koha and Sudoc

## [1.4.1] - 2023-01-18

### Changed

* Internal changes to the matching records process

### Fixed

* Correctly outputs every lines, even if an error occurred
* Fixed Koha API encoding problem when using JSON

## [1.4.0] - 2023-01-17

### Added

* Added a graphic user interface
* Now outputs :
  * PPN already present in Koha record
  * Items information already present in Sudoc record
* RCR can now be configured

### Changed

* Internal changes (to a lot of things)

### Fixed

* Creatting the report no longer crashes the script

## [1.3.1] - 2022-12-07

### Fixed

* Correctly ctaches all errors instead of just HTTP ones

## [1.3.0] - 2022-11-24

### Added

* Output local system number present in Sudoc record
* ILN can now be configured

## [1.2.0] - 2022-11-02

### Added

* Documentation
* A new configuration file `settings.json`

### Changed

* Internal changes, notably in the CSV export and better error handling

## [1.1.0] - 2022-10-19

### Fixed

* Prevent crashes if no publisher was found in Koha or Sudoc record
* Correctly increases ISBN to PPN success for the report
* Correctly compute ht enumber of unique matching in the report

## [1.0.0] - 2022-10-19

* Realeased version for first executions
