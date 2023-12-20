# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

_Some previous changes will be added_


## [Unreleased]

### Added

* Changelog file
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

### Changed

* Documentation to add actions, operations and processings are more clear
* The noise deletion function deletes more noise
* Authors data defaults to fields `700`, `701`, `702`, `710`, `711` and `712`
* Some output functions have been moved to a new `output` property of `Class Original_Record`
* Internal changes to error management
* Slight changes to logs, notably only logging once the query used

### Fixed

* Changed `id2ppn.py` version to fix incorrect status and incorrect returned value if only one record matched with JSON returned data
* Changed `Sudoc_SRU.py` version to fix XML parse errors when some queries using angle brackets were not properly transformed in Sudoc's response
* Create the output folder if it doe snot exist
* Output used query display the actual query used

## [1.12.1] - 2023-12-08

### Changed

* Default analysis is now _Titles 80% (3 out of 4), publishers 80%, dates_
* Checking if the ID from the origin database is in the target list of othre database IDs is now more precise ([see `Enum Other_Database_Id_In_Target` in `fcr_enum.py`](./fcr_enum.py "Open the file fcr_enum.py"))
* Global validation has now 2 output columns : the previous one now returns values from [`Enum Analysis_Final_Results` in `fcr_enum.py`](./fcr_enum.py "Open the file fcr_enum.py") and the new one the number of successful checks

### Fixed

* Values filled in the UI without being saved are now properly sent to the main script, instead of using saved values

## [1.12.0] - 2023-12-18

### Added

* Multipe matches are now all retrieved instead of throwing a fake error

### Removed

* Removed the fake error concept

## [1.11.0] - 2023-11-22



## [1.10.0] - 2023-10-20



## [1.8.0] - 2023-10-03

## [1.7.2] - 2023-04-21

### Fixed

* Changed `Koha_API_PublicBiblio.py` version to fix crashes when Koha record had only empty subfields in the title

## [1.7.1] - 2023-03-17

### Fixed

* Changed `Abes_isbn2ppn.py` version to fix invalid ISBN returned values

## [1.7.0] - 2023-03-01

### Added

* Output years found inside Koha `215$a`