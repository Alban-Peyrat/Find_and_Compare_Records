# Documentation sur le fichier à traiter

Le fichier à traiter varie selon le traitement sélectionné :

* [Suite `BETTER_ITEM`](#suite-better_item) (`BETTER_ITEM`, `BETTER_ITEM_DVD`, `BETTER_ITEM_NO_ISBN`, `BETTER_ITEM_MAPS`)
* `MARC_FILE_IN_KOHA_SRU`

||| Vérifier comment fonctionne les autres avec la première colonne

## Suite `BETTER_ITEM`

Le fichier utilisé est un fichier `.csv` contenant les informations d'un exemplaire ainsi que l'ISBN et l'identifiant dans la base de donnée d'origine.

La première colonne du fichier doit __forcément__ être la colonne contenant l'ISBN, la dernière colonne doit __forcément__ être celle contenant l'identifiant de la base de donnée d'origine.

Toutes les colonnes du fichier seront exportées à la fin du fichier de sortie.

## `MARC_FILE_IN_KOHA_SRU`

Le fichier utilisé est un fichier de notices en ISO 2709, contenant les exemplaires.