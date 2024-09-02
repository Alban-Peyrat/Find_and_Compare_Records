# List & informations about available processings

## `BETTER_ITEM` suite

Based on a list for ITEM, search and check that found records using [`id2ppn` Abes webservice](https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#isbn2ppn) (or [Sudoc SRU service](https://abes.fr/reseau-sudoc/reutiliser-les-donnees-sudoc/service-sru/)) correctly match Koha records.

This suite compute a specific column to show if the Sudoc already has items on for a record for the given RCR.

### `BETTER_ITEM`

This processing mostly searches using the ISBN found in the input file.

It launches up to 5 different actions for the same record :

* If there's a valid ISBN, queries Abes `isbn2ppn` with a cleaned up ISBN
* Converts the ISBN in 10<->13 and, if the new ISBN is valid, queries again Abes `isbn2ppn` with this new ISBN
* Converts the ISBN in 10<->13 __keeping the original control key__, and queries again Abes `isbn2ppn` with this new ISBN (this time, without checking for the ISBN validity)
* Queries Sudoc SRU using the ISBN on its specific index
* Queries Sudoc SRU using only the title (on the title index)

### `BETTER_ITEM_DVD`

This processing only searches based on data from the origin database record retrieved by FCR.

It launches up to 6 different actions for the same record :

* Queries Abes `ean2ppn`
* Queries Sudoc SRU on audiovisual records using title, authors, the publisher & publication dates on their specific index __if they were all found in the record__
* Queries Sudoc SRU on audiovisual records using title, authors & publication dates on their specific index __if they were all found in the record__
* Queries Sudoc SRU on audiovisual records using title, authors, the publisher & publication dates on the _any_ index __if they were all found in the record__
* Queries Sudoc SRU on audiovisual records using title, authors & the publisher on the _any_ index __if they were all found in the record__
* Queries Sudoc SRU on audiovisual records using title on its specific index

### `BETTER_ITEM_NO_ISBN`

This processing only searches based on data from the origin database record retrieved by FCR.

It launches up to 6 different actions for the same record :

* Queries Abes `ean2ppn`
* Queries Sudoc SRU on printed books using title, authors, the publisher & publication dates on their specific index __if they were all found in the record__
* Queries Sudoc SRU on printed books using title, authors & publication dates on their specific index __if they were all found in the record__
* Queries Sudoc SRU on printed books using title, authors, the publisher & publication dates on the _any_ index __if they were all found in the record__
* Queries Sudoc SRU on printed books using title, authors & the publisher on the _any_ index __if they were all found in the record__
* Queries Sudoc SRU on printed books using title on its specific index

### `BETTER_ITEM_MAPS`

This processing only searches based on data from the origin database record retrieved by FCR.

It launches up to 6 different actions for the same record :

* Queries Abes `ean2ppn`
* Queries Sudoc SRU on maps using title, authors, the publisher & publication dates on their specific index __if they were all found in the record__
* Queries Sudoc SRU on maps using title, authors & publication dates on their specific index __if they were all found in the record__
* Queries Sudoc SRU on maps using title, authors, the publisher & publication dates on the _any_ index __if they were all found in the record__
* Queries Sudoc SRU on maps using title, authors & the publisher on the _any_ index __if they were all found in the record__
* Queries Sudoc SRU on maps using title on its specific index

## `MARC_FILE_IN_KOHA_SRU`

This processing only searches based on data from the input file record.

It launches up to 7 different actions for the same record :

* Queries Koha SRU using ISBN on its specific index __if the ISBN was found in the original record__
* Queries Koha SRU using title, authors, the publisher & publication dates on their specific index __if they were all found in the record__
* Queries Koha SRU using title, authors & publication dates on their specific index __if they were all found in the record__
* Queries Koha SRU using title, authors, the publisher & publication dates on the _any_ index __if they were all found in the record__
* Queries Koha SRU using title, authors & publication dates on the _any_ index __if they were all found in the record__
* Queries Koha SRU using title, the publisher & publication dates on the _any_ index __if they were all found in the record__
* Queries Koha SRU using title on its specific index