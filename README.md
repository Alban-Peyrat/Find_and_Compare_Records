# Comparaison des notices Koha et Sudoc avant l'utilisation d'ITEM

À partir de la liste de données extraites de Koha pour ITEM, vérifie que les correspondances PPN / ISBN du [webservice `isbn2ppn` de l'Abes](https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#isbn2ppn) correpondent bien aux documents enregistrés dans Koha.
Le traitement se focalise sur les correspondances uniques (ISBN trouvé et ne correspondant qu'à un seul PPN).

# Fonctionnement

## Validation de l'ISBN

Pour chaque ligne dans le document à traiter, le script vérifie [si l'ISBN est valide](https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch04s13.html).
S'il ne l'est pas, soit par sa forme, soit car la clef de contrôle est erronée, renvoie une erreur et passe à la prochaine ligne.

## Interrogation de `isbn2ppn`

Si l'ISBN est valide, interroge le [webservice `isbn2ppn` de l'Abes](https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#isbn2ppn) avec l'ISBN nettoyé (seul les chiffres et `X` sont conservés) pour récupérer le ou les PPNs associés à cet ISBN.
Si le script ne parvient pas à sa connecter au service, si aucun PPN n'est renvoyé ou si trop de PPN sont renvoyés, renvoie une erreur et passe à la prochaine ligne

## Récupération des informations des notices

Si un seul PPN est renvoyé par `isbn2ppn`, le script interroge alors l'[API `getBiblioPublic` de Koha](https://api.koha-community.org/20.11.html#operation/getBiblioPublic) et le [webservice `MARCXML` de l'Abes](https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#SudocMarcXML).
Il récupère de chacune de ces notices les informations suivantes :
* le titre du document : une chaîne de caractère formée par le contenu de chaque sous-champ dont le code est `a`, `d`, `e`, `h`, `i` ou `v` du premier 200, séparé par un espace
* les dates de publications : la première et la seconde date de publication contenu dans la 100$a
* le nom de chaque éditeur : une liste contenant le contenu de chaque 210$c ou 214$c présent dans la notice

Si l'interrogation à l'une des bases échoue, renvoie une erreur et passe à la prochaine ligne.

## Nettoyage des titres

Une fois le titre récupéré, le nettoie :
* en remplaçant `.`, `,`, `?`, `!`, `;`, `/`, `:`, `=` par un espace
* en suprimant les doubles espaces
* en retirant les espaces en début en fin de titre
* en le passant en minuscule
* en remplaçant `&` par `et`
* en remplaçant `œ` par `oe`
* en ASCIIisant le titre (retirant les accents, cédilles, etc.)
* en le passant à nouveau en minuscule

## Nettoyage des éditeurs

Les éditeurs sont également nettoyés avant d'être comparés :
* en suprimant les doubles espaces
* en retirant les espaces en début en fin de titre
* en le passant en minuscule
* en le passant à nouveau en minuscule
* en remplaçant `&` par `et`
* en remplaçant `œ` par `oe`
* en ASCIIisant le titre (retirant les accents, cédilles, etc.)
* en remplaçant par un espace, __dans l'ordre__ :
  * `les editions`
  * `les ed.`
  * `les ed`
  * `editions`
  * `edition`
  * `ed`
* en remplaçant `.`, `,`, `?`, `!`, `;`, `/`, `:`, `=` par un espace
* en suprimant les doubles espaces
* en retirant les espaces en début en fin de titre
* en le passant en minuscule

## Comparaison des données entre les bases

Une fois toutes les informations récupérées, compare les données entre les deux bases :
* pour le titre : génère un score de similarité, d'appartenance, d'inversion et d'inversion appartenance à l'aide de [la distance de Levenshtein](https://fr.wikipedia.org/wiki/Distance_de_Levenshtein)
* pour les dates de publication : vérifie si l'un des dates de Koha est comprise dans l'une des dates du Sudoc (ne compare pas si les dates ne sont pas renseignées)
* pour les éditeurs : compare chaque éditeur de Koha avec chaque éditeur du Sudoc en génèrant un score de similarité, puis renvoie la paire avec le score le plus élevé.

## Validation des critères de comparaisons

Enfin, le script valide ou non chaque critère de comparaison de l'analyse choisie puis passe à la ligne suivante

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
* `ILN` : l'ILN à utiliser pour vérifier la présence de numéros de système locaux au sein de la notice Sudoc
* `LOGS_PATH` : chemin d'accès au dossier dans lequel sera créé le fichiers contenant les logs

Ces variables peuvent être modifiées si voulu :
* `SERVICE` : nom du service, apparaît notamment dans les logs (et définit le nom du fichier de logs)
* `ANALYSIS` : les analyses disponibles dans le script. [Voir comment configurer une analyse](#configurer-une-analyse)
* `CSV_EXPORT_COLS` : les colonnes exportées dans le fichier CSV (hors colonnes du fichier original qui sont forcément exportées). [Voir comment ajouter des colonnes exportées](#fichier-csv)
* `REPORT_SETTINGS` : les lignes affichées dans le rapport final. [Voir comment ajouter des lignes au rapport](#fichier-txt)

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
* [`resultats.csv`](#fichier-csv)
* [`resultats.json`](#fichier-json)
* [`resultats.txt`](#fichier-txt)
* [`Compare_Koha_Sudoc_records.log`](#logs)

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
Ci-dessous, la liste des clefs des dictionnaires compris dans `results` :
* `ERROR` {bool}
* `ERROR_MSG` {str} : chaîne de caractère vide si aucune erreur n'a eu lieu
* chaque colonne du fichier original : chaque en-tête est une clef
* `INPUT_ISBN` {str} : première colonne du fichier original (supposément, l'ISBN)
* `INPUT_KOHA_BIB_NB` {str} : dernière colonne du fichier original (supposément, le biblionumber de Koha)
* `ISBN2PPN_ISBN` {str} : IBSN normalisé renvoyé par `isbn2ppn.py validate_isbn()`, qui a été utilisé pour interroger isbn2ppn
* `ISBN2PPN_NB_RES` {int} : nombre de résultats renvoyés par isbn2ppn
* `ISBN2PPN_RES` {list of str} : chaque PPN renvoyé par isbn2ppn
* `PPN` {str} : le PPN renvoyé par isbn2ppn
* `SUDOC_LOCAL_SYSTEM_NB` {list of str} : les numéros de système présents dans la notice Sudoc __dédoublonnés__
* `SUDOC_NB_LOCAL_SYSTEM_NB` {int} : le nombre de numéros de système présents dans la notice Sudoc __dédoublonnés__
* `SUDOC_DIFFERENT_LOCAL_SYSTEM_NB` {bool} : si le nombre de numéros de système présents dans la notice Sudoc __dédoublonnés__ est supérieur à 0, est-ce que le biblionumber de Koha utilisé pour interroger Koha est compris dans la liste
* `KOHA_BIB_NB` {str} : le biblionumber de Koha utilisé pour interroger Koha
* `KOHA_Leader` {str} : le label de la notice Koha
* `KOHA_100a` {str} : le contenu de la 100$a de la notice Koha
* `KOHA_DATE_TYPE` {str} : le type de la date de publication en 100$a de la notice Koha (caractère en position 8)
* `KOHA_DATE_1` {str} : première date de publication en 100$a de la notice Koha (caractères en position 9-12)
* `KOHA_DATE_2` {str} : seconde date de publication en 100$a de la notice Koha (caractères en position 13-16)
* `KOHA_214210c` {list of str} : chaque contenu des 210$c ou 214$c de la notice Koha
* `KOHA_200adehiv` {str} : renvoie [le titre nettoyé](#nettoyage-des-titres) présent en 200 de la notice Koha
* `KOHA_Leader` {str} : le label de la notice Sudoc
* `KOHA_100a` {str} : le contenu de la 100$a de la notice Sudoc
* `KOHA_DATE_TYPE` {str} : le type de la date de publication en 100$a de la notice Sudoc (caractère en position 8)
* `KOHA_DATE_1` {str} : première date de publication en 100$a de la notice Sudoc (caractères en position 9-12)
* `KOHA_DATE_2` {str} : seconde date de publication en 100$a de la notice Sudoc (caractères en position 13-16)
* `KOHA_214210c` {list of str} : chaque contenu des 210$c ou 214$c de la notice Sudoc
* `KOHA_200adehiv` {str} : renvoie [le titre nettoyé](#nettoyage-des-titres) présent en 200 de la notice Sudoc
* `MATCHING_TITRE_SIMILARITE` {int} : score de similarité des titres
* `MATCHING_TITRE_APPARTENANCE` {int} : score d'appartenance des titres
* `MATCHING_TITRE_INVERSION` {int} : score d'inversion des titres
* `MATCHING_TITRE_INVERSION_APPARTENANCE` {int} : score d'inversion appartenance des titres
* `MATCHING_DATE_PUB` {bool} : résultat de la comparaison des dates de publication
* `MATCHING_EDITEUR_SIMILARITE` {int} : score de similarité des éditeurs choisis
* `SUDOC_CHOSEN_ED` {str} : [nom de l'éditeur nettoyé](#nettoyage-des-éditeurs) choisi dans la notice Sudoc
* `KOHA_CHOSEN_ED` {str} : [nom de l'éditeur nettoyé](#nettoyage-des-éditeurs) choisi dans la notice Koha
* `TITLE_OK_NB` {int} : nombre de formes de titre ayant un score supéreieur ou égal au seuil minimum
* `TITLE_OK` {bool} : [voir les résultats de l'analyse](#résultats-de-lanalyse)
* `PUB_OK` {bool} : [voir les résultats de l'analyse](#résultats-de-lanalyse)
* `DATE_OK` {bool} : [voir les résultats de l'analyse](#résultats-de-lanalyse)
* `FINAL_OK` {str} : [voir les résultats de l'analyse](#résultats-de-lanalyse)

## Fichier TXT

Ce fichier contient un rapport sur l'analyse, rappelant les paramétrages et des résultats de l'analyse.

Les données exportées dans le rapport sont définies dans la liste `REPORT_SETTINGS` définie dans `settings.json`.
L'ordre d'apparition au sein d'une même section est égal à l'ordre des dictionnaires dans la liste.

Pour rajouter une ligne, il faut ajouter à `REPORT_SETTINGS` un dictionnaire avec les clefs suivantes :
* `name` {str} : texte à afficher. Si une `var` est renseignée, ` : ` sera ajouté entre `name` et la valeur de `var`
* `section` {int} : numéro de la section dans laquelle afficher la ligne
* `var` {str} :
  * `null` si l'on souhaite uniquement afficher du texte
  * le nom de la variable dont l'on veut afficher le contenu

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

## À faire

* Revoir si la comparaison des dates est bonne pour le mathc des éditions surtout
* Forme du fichier pour l'abes : https://documentation.abes.fr/aideitem/index.html#ConstituerFichierDonneesExemplariser

# Fait 

* Utiliser MARCXML plutôt que JSON (#AR141 - #MT38705)