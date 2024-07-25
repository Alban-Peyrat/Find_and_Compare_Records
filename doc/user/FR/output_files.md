# Forme des fichiers de sorties

Le script génère 3 fichiers de sortie et 1 fichier de logs :

* [`results.csv`](#fichier-csv)
* [`results.json`](#fichier-json)
* [`results_report`](#fichier-texte)
* [`{Nom_du_service}.log`](#journaux)

## Fichier CSV

Les données exportées pour chaque traitement sont définies dans le code.

Pour les données conservant des listes, toutes les valeurs de la liste sont concaténées et séparées par une virgule suivie d'un espace.

## Fichier JSON

Contient les informations du traitement d'une manière plus complète et représentative du fonctionnement de FCR que l'export CSV.

Entre autres :

* Les données conservant des listes contiennent toujours des listes
* Dans le cas où plusieurs notices sont trouvées dans la base de données de destination, elles sont toutes rassemblées au sein d'une propriété de la notice dans la base de données d'origine (là où l'export CSV est obligé de dupliquer les informations de la base de données d'origine)
* Toutes les actions qui ont été essayées sont renseignées, notamment avec la requête utilisée ou la cause de l'échec

## Fichier texte

Ce fichier contient un rapport sur l'analyse, rappelant les paramétrages et quelques statistiques sur résultats de l'analyse (nombre de documents traités, nombre de documents traités jusqu'au bout, nombre de fois qu'une action a été utilisée et qu'elle a réussi, etc.).

## Journaux

Le fichier contient un rappel des informations paramétrées, le rapport final et des informations extraites durant la récupération de données ou l'analyse.

L'utilité première est de consulter pourquoi certaines erreurs journalisées ont eu lieu ou obtenir des pistes sur la partie de FCR qui aurait dysfonctionné.