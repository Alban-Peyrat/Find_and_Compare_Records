# Liste des traitements

## `BETTER_ITEM`

À partir d'une liste de données pour ITEM, recherche et vérifie que les correspondances PPN / ISBN du [webservice `isbn2ppn` de l'Abes](https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#isbn2ppn) (ou du [service SRU du Sudoc](https://abes.fr/reseau-sudoc/reutiliser-les-donnees-sudoc/service-sru/)) correpondent bien aux documents enregistrés dans Koha.

### Validation de l'ISBN

Pour chaque ligne dans le document à traiter, le script vérifie [si l'ISBN est valide](https://www.oreilly.com/library/view/regular-expressions-cookbook/9780596802837/ch04s13.html).
S'il ne l'est pas, soit par sa forme, soit car la clef de contrôle est erronée, renvoie une erreur et passe à la prochaine ligne.

### Recherche des notices correspondantes

Si l'ISBN est valide, interroge le webservice `isbn2ppn` de l'Abesavec l'ISBN nettoyé (seul les chiffres et `X` sont conservés) pour récupérer le ou les PPNs associés à cet ISBN.
Si le script ne parvient pas à se connecter au service ou si aucun PPN n'est renvoyé, transforme l'ISBN 10/13 en son équivalent 13/10 et ralnce la requête.
En cas de nouvel échec, interroge le service SRU du Sudoc sur l'index `ISB`, ce qui permet également d'interroger les ISBN erronnés.
En cas de nouvel échec, renvoie une erreur et passe à la prochaine ligne.

## `MARC_FILE_IN_KOHA_SRU`

Le filtre 1 est utilisé pour filtrer les données d'exemplaires dans le SRU de Koha (`995$b`)