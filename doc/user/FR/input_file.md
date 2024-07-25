# Documentation sur le fichier à traiter

Le fichier à traiter varie selon le traitement sélectionné :

* [Suite `BETTER_ITEM`](#suite-better_item) (`BETTER_ITEM`, `BETTER_ITEM_DVD`, `BETTER_ITEM_NO_ISBN`, `BETTER_ITEM_MAPS`)
* [`MARC_FILE_IN_KOHA_SRU`](#marc_file_in_koha_sru)

## Suite `BETTER_ITEM`

Le fichier utilisé est un fichier de type CSV utilisant un `;` comme délimiteur.

Celui-ci contient les informations d'un exemplaire, l'identifiant dans la base de donnée d'origine et (parfois) un identifiant pour certaines requêtes.
Ce dernier identifiant est utilisé unisuement pour le traitement `BETTER_ITEM` et doit être un ISBN.

Le fichier doit __forcément__ avoir comme :

* Première colonne la colonne contenant l'identifiant pour les reqûetes (l'ISBN pour `BETTER_ITEM`, une colonne vide ou avec un autre donnée pour les autres)
* Dernière colonne celle contenant l'identifiant de la base de donnée d'origine

Toutes les colonnes du fichier seront exportées à la fin du fichier de sortie.

## `MARC_FILE_IN_KOHA_SRU`

Le fichier utilisé est un simple fichier de notices en ISO 2709, contenant les exemplaires.