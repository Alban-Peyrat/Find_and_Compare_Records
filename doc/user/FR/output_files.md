__Documentation non à jour__

# Forme des fichiers de sorties

Le script génère 3 fichiers de sortie et 1 fichier de logs :
* [`resultats.csv`](#fichier-csv)
* [`resultats.json`](#fichier-json)
* [`resultats.txt`](#fichier-txt)
* [`{Nom_du_service}.log`](#logs)

## Fichier CSV

Les données exportées pour chaque ligne sont définies dans la liste `CSV_EXPORT_COLS` définie dans `settings.json`, auxquelles seront forcément rajoutées l'intégralité des colonnes du fichier original, en dernières positions.
Pour les données renseignées dans `CSV_EXPORT_COLS`, l'ordre des colonnes est égal à l'ordre des dictionnaires dans la liste.

Pour les données conservant des listes, toutes les valeurs de la liste sont concaténées au sein d'un `[]` en utilisant `,` comme séparateur et `'` comme délimiteur de texte (ou `"` si un `'` est présent dans la chaîne de texte).

Pour rajouter une colonne, il faut ajouter à `CSV_EXPORT_COLS` un dictionnaire avec les clefs suivantes :
* `id` {str} : nom de la donnée dans le script
* `name` {str} : nom de la colonne dans le fichier CSV
* __[inutile dans cette version]__`list` {bool} : la donnée est-elle une liste ?

## Fichier JSON

Correspond à l'intégralité de la liste `results`, qui contient pour chaque ligne les informations utilisées pour l'analyse et les résultats de celle-ci.
Toute donnée qui aurait dû être générer après qu'une erreur ait été rencontrée est absente pour la ligne.

## Fichier TXT

Ce fichier contient un rapport sur l'analyse, rappelant les paramétrages et des résultats de l'analyse.

## Logs

Le fichier contient les logs de niveau `DEBUG` et plus élevés (seuls `INFO` et `ERROR` sont utilisés au-dessus).
Il suit l'exécution du script et se divise donc en plusieurs étapes, qui sont généralement signalées par des `INFO` entre `---------------`

Les messages suivent la même mise en forme, chaque information étant séparée par ` :: `, les sous-informations étant généralement séparées par ` || ` :
* le moment du log (`AAAA-MM-JJ HH:MM:SS:MMM`)
* le niveau du log
* _pour les DEBUG_ :
  * l'identifiant utilisé
  * le nom du service qui a généré le log
  * l'information loggée
* _pour les `INFO`_ :
  * le message à afficher
* _pour les `ERROR`_ :
  * la donnée utilisée comme identifiant
  * le nom du service qui a généré l'erreur
  * _selon la cause de l'erreur_ :
    * le nom de l'erreur
    * des informations sur la requête HTTP qui a entraîné l'erreur :
      * Statut de la réponse
      * Méthode de la requête
      * URL de la requête
      * Réponse à la requête