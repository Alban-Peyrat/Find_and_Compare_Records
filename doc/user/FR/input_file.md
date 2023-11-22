# Documentation sur le fichier à traiter

Le fichier à traiter varie selon le traitement sélectionné :

* [`BETTER_ITEM`](#better_item)
* `OTHER_DB_IN_LOCAL_DB` _(non supporté au 22/11/2023)_

## `BETTER_ITEM`

Le fichier utilisé est un fichier `.csv` contenant les informations d'un exemplaire ainsi que l'ISBN et l'identifiant dans la base de donnée d'origine.

La première colonne du fichier doit __forcément__ être la colonne contenant l'ISBN, la dernière colonne doit __forcément__ être celle contenant l'identifiant de la base de donnée d'origine.

Toutes les colonnes du fichier seront exportées à la fin du fichier de sortie.