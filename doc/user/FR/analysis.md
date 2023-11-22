__Documentation non à jour__

# Fonctionnement

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