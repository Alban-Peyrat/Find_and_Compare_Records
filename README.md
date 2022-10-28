# Comparaison des notices Koha et Sudoc avant l'utilisation d'ITEM

À partir de la liste de données extraites de Koha pour ITEM, vérifie que les correspondances PPN / ISBN du [webservice `isbn2ppn` de l'Abes](https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#isbn2ppn) correpondent bien aux documents enregistrés dans Koha.
Le traitement se focalise sur les correspondances uniques (ISBN trouvé et ne correspondant qu'à un seul PPN).

# Fonctionnement

Le script prend 

# Prérequis avant l'exécution du script

## Bibliothèques non incluses dans la Python Standard Library

Ces bibliothèques sont utilisées par le script mais absentes de la [Python Standard Library](https://docs.python.org/3/library/) :
* [`unidecode`](https://pypi.org/project/Unidecode/)
* [`FuzzyWuzzy`](https://pypi.org/project/fuzzywuzzy/)
* [`requests`](https://pypi.org/project/requests/)

## Variables à définir dans `settings.json`

Ces variables doivent avoir été paramétrées dans `settings.json` avant l'exécution du script :
* `MY_PATH` : chemin d'accès au dossier contenant le fichier à analyser, dans lequel seront créé les fichiers de sortie
* `KOHA_URL` : l'URL du Koha à interroger
* `LOGS_PATH` : chemin d'accès au dossier dans lequel sera créé le fichiers contenant les logs

# Analyse des résultats des correspondances

L'analyse des résultats des correspondances se base sur 3 critères :
1. sur les 4 formes du titre étudiée, la correspondance des titres est supérieure à un seuil minimum pour au moins X d'entre eux
1. la correspondance des éditeurs est supérieure à un seuil minimum
1. la correspondance des dates de publication est prise en compte ou non

## Résultats de l'analyse

L'analyse renvoie 4 données :
* `FINAL_OK` : résultat final de l'analyse, prend la valeur :
  * `{chaîne de texte vide}` si aucun des critères n'est sélectionné
  * `OK` si tous les critères sont OK
  * `{chiffre}` : le nombre de critères OK si tous ne le sont pas
* `TITLE_OK` :
  * `True` si le nombre de formes du titre ayant un score supérieur ou égal au seuil minimum requis est supérieur ou égal au nombre minimum requis
  * `False` si ce n'est pas le cas
* `PUB_OK`
  * `True` si le score de correspondance de la pair d'éditeur choisie est supérieur ou égal au seuil minimum requis
  * `False` si ce n'est pas le cas
* `DATE_OK`
  * `True` si l'une des dates de Koha correspond à l'une de celles du Sudoc
  * `False` si ce n'est pas le cas

_Note : `TITLE_OK`, `PUB_OK` et `DATE_OK` renvoient une chaîne de texte vide s'ils ne sont pas sélectionnés._

## Configurations des analyses par défaut

_Si les seuils minimum sont configurés à 0, l'analyse ignorera le critère en question._

### Analyse 0 : Aucune analyse

* Seuil minimum pour la correspondance des titres : `0`
* Nombre minimum de formes du titre devant être supérieur au seuil : `0`
* Seuil minimum pour la correspondance des éditeurs : `0`
* Utilisation de la date de publication : `NON`

### Analyse 1 : Titre 80 (3/4), Editeurs 80, Dates

* Seuil minimum pour la correspondance des titres : `80`
* Nombre minimum de formes du titre devant être supérieur au seuil : `3`
* Seuil minimum pour la correspondance des éditeurs : `80`
* Utilisation de la date de publication : `OUI`

### Analyse 2 : Titre 90

* Seuil minimum pour la correspondance des titres : `90`
* Nombre minimum de formes du titre devant être supérieur au seuil : `4`
* Seuil minimum pour la correspondance des éditeurs : `0`
* Utilisation de la date de publication : `NON`

### Analyse 3 : Titre 95, Editeurs 95

* Seuil minimum pour la correspondance des titres : `95`
* Nombre minimum de formes du titre devant être supérieur au seuil : `4`
* Seuil minimum pour la correspondance des éditeurs : `95`
* Utilisation de la date de publication : `NON`

## Configurer une analyse

Pour ajouter une nouvelle analyse, il faut rajouter à la liste `ANALYSIS` définie dans `settings.json` un dictionnaire avec les clefs suivantes :
* `name` {str}: nom de l'analyse qui s'affichera dans les interfaces
* `TITLE_MIN_SCORE` {int} : seuil minimum requis pour que la correspondances des titres soit considérée comme OK
* `NB_TITLE_OK` {int} : nombre minimum de correspondance de formes de titre requis pour que le critère de correspondance des titres soit considéré comme OK
* `PUBLISHER_MIN_SCORE` {int} : seuil minimum requis pour que la correspondances des éditeurs soit considérée comme OK
* `USE_DATE` {bool} : utilisation du critère correspondance des dates de publication

# Forme des fichiers de sorties

Le script génère 3 fichiers de sortie et 1 fichier de logs :
* [`resultats.csv`](#fichier-csv) : 
* [`resultats.json`](#fichier-json) : 
* [`resultats.txt`](#fichier-txt) : un rapport textuel rappelant les paramétrages sélectionnés et des données chiffrées sur l'analyse
* [`Compare_Koha_Sudoc_records.log`](#logs)

## Fichier CSV

Les données exportées pour chaque ligne sont définies dans la liste `CSV_EXPORT_COLS` définie dans `settings.json`, auxquelles seront forcément rajoutées l'intégralité des colonnes du fichier original, en dernières positions.
Pour les données renseignées dans `CSV_EXPORT_COLS`, l'ordre des colonnes est égal à l'ordre des dictionnaires dans la liste.

Pour les données conservant des listes, toutes les valeurs de la liste sont concaténées en utilisant `|` comme séparateur.
__Les valeurs égale à `None` ne sont pas exportées.__ (voir #38705 et les problèmes de sous-champs vidés en MARCMXL dans Koha)

Pour rajouter une colonne, il faut ajouter à `CSV_EXPORT_COLS` un dictionnaire avec les clefs suivantes :
* `id` {str} : nom de la donnée dans le script
* `name` {str} : nom de la colonne dans le fichier CSV
* `list` {bool} : la donnée est-elle une liste ?

## Fichier JSON

Correspond à l'intégralité de la liste `results`, qui contient pour chaque ligne les informations utilisées pour l'analyse et les résultats de celle-ci.
Toute donnée qui aurait dû être générer après qu'une erreur ait été rencontrée est absente pour la ligne.
Ci dessous, la liste des clefs des dictionnaires compris dans `results` :
* `ERROR` {bool}
* `ERROR_MSG` {str} : chaîne de caractère vide si aucune erreur n'a eu lieu
* `LINE_DIVIDED` {list of str} : chaque colonne du fichier original
* `INPUT_ISBN` {str} : première colonne du fichier original (supposément, l'ISBN)
* `INPUT_KOHA_BIB_NB` {str} : dernière colonne du fichier original (supposément, le biblionumber de Koha)
* `ISBN2PPN_ISBN` {str} : IBSN normalisé renvoyé par `isbn2ppn.py validate_isbn()`, qui a été utilisé pour interroger isbn2ppn
* `ISBN2PPN_NB_RES` {int} : nombre de résultats renvoyés par isbn2ppn
* `ISBN2PPN_RES` {list of str} : chaque PPN renvoyé par isbn2ppn
* `PPN` {str} : le PPN renvoyé par isbn2ppn
* `KOHA_BIB_NB` {str} : le biblionumber de Koha utilisé pour interroger Koha
* || à finir

## Fichier TXT

## Logs

## À faire

* Finir la doc : je suis au fichier JSOn, faut encore faire tout le reste
* Revoir si la comparaison des dates est bonne pour le mathc des éditions surtout
* changer la génération des headers de du fichier original dans le nouveau csv
* Forme du fichier pour l'abes : https://documentation.abes.fr/aideitem/index.html#ConstituerFichierDonneesExemplariser