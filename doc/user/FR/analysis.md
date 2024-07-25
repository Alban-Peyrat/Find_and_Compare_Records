# Fonctionnement des analyses effectuées

## Comparaison des données entre les bases

Une fois toutes les informations récupérées, compare les données entre les deux bases :

* Pour le titre : génère un score de similarité, d'appartenance, d'inversion et d'inversion appartenance à l'aide de [la distance de Levenshtein](https://fr.wikipedia.org/wiki/Distance_de_Levenshtein)
* Pour les dates de publication : vérifie si l'un des dates de la base de données d'origine est comprise dans l'une des dates de la base de données de destination (ne compare pas si les dates ne sont pas renseignées)
* Pour les éditeurs : compare chaque éditeur de la base de données d'origine avec chaque éditeur de la base de donnée de destination en génèrant un score de similarité, puis renvoie la paire avec le score le plus élevé.

Ensuite, le script valide ou non chaque critère de comparaison de l'analyse choisie et indique un degré de validation pour cette comparaison.

## Analyse des résultats des correspondances

L'analyse des résultats des correspondances se base sur 3 critères :

1. Sur les 4 formes du titre étudiée, la correspondance des titres est supérieure à un seuil minimum pour au moins X d'entre eux
1. La correspondance des éditeurs est supérieure à un seuil minimum
1. La correspondance des dates de publication est prise en compte ou non

## Résultats de l'analyse

L'analyse renvoie 5 données :

* _Validation globale_ : résultat final de l'analyse, prend la valeur :
  * _Vérifications complètes_ : tous les critères sélectionnés sont validés
  * _Vérifications partielles_ : une partie des critères sélectionnés sont validés
  * _Vérifications KO_ : aucun des critères sélectionnés n'a été validé
  * _Pas de vérification_ : l'analyse choisie n'effectue aucune vérification
  * Si rien ne s'affiche, l'analyse n'a pas eu lieu
* _Nombre de validations réussies_ : le nombre de critéères sélectionnés qui ont été validés
* _Validation des titres_ :
  * `True` si le nombre de formes du titre ayant un score supérieur ou égal au seuil minimum requis est supérieur ou égal au nombre minimum requis
  * `False` si ce n'est pas le cas
* _Validation des éditeurs_
  * `True` si le score de correspondance de la pair d'éditeur choisie est supérieur ou égal au seuil minimum requis
  * `False` si ce n'est pas le cas
* _Validation des dates_
  * `True` si l'une des dates de la base de données d'origine correspond à l'une de celles de la base de données de destination
  * `False` si ce n'est pas le cas

_Note : les détails (notamment les scores de similarités) sont disponibles à la fin des colonnes du fichier de sortie_

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

Pour ajouter une nouvelle analyse, il faut rajouter un nouvel objet dans `analysis.json` avec les clefs suivantes :

* `name` `(str)`: nom de l'analyse qui s'affichera dans les interfaces
* `TITLE_MIN_SCORE` (`int`) : seuil minimum requis pour que la correspondances des titres soit considérée comme OK
* `NB_TITLE_OK` (`int`) : nombre minimum de correspondance de formes de titre requis pour que le critère de correspondance des titres soit considéré comme OK
* `PUBLISHER_MIN_SCORE` (`int`) : seuil minimum requis pour que la correspondances des éditeurs soit considérée comme OK
* `USE_DATE` (`bool`) : utilisation du critère correspondance des dates de publication