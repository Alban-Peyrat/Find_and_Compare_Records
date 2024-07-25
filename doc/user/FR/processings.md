# Liste des traitements

## Suite `BETTER_ITEM`

À partir d'une liste de données pour ITEM, recherche et vérifie que les correspondances trouvées via les [webservice `id2ppn` de l'Abes](https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#isbn2ppn) (ou du [service SRU du Sudoc](https://abes.fr/reseau-sudoc/reutiliser-les-donnees-sudoc/service-sru/)) correpondent bien aux documents enregistrés dans Koha.

Cette suite calcule une colonne particulière pour indiquer si le Sudoc possède déjà des exemplaires sur une notice pour le RCR renseigné.

### `BETTER_ITEM`

Ce traitement recherche majoritairement à l'aide de l'ISBN renseigné dans le fichier à traiter.

Il lance jusqu'à 5 actions différentes pour un même document :

* Si l'ISBN est valide, il interroge le webservice `isbn2ppn` de l'Abes avec un ISBN nettoyé
* Il convertit l'ISBN en 10<->13 et, si ce nouvel ISBN est valide, il réinterroge le webservice `isbn2ppn` de l'Abes avec
* Il convertit l'ISBN en 10<->13 __en conservant la clef de contrôle originale__, et il réinterroge le webservice `isbn2ppn` de l'Abes avec (cette fois-ci, il ne vérifie pas si l'ISBN est valide)
* Il interroge le SRU du Sudoc sur l'index dédié aux ISBN
* Il interroge le SRU du Sudoc en utilisant uniquement le titre (sur l'index du titre)

### `BETTER_ITEM_DVD`

Ce traitement recherche uniquement à partir des informations contenues dans la notice de la base de données d'origine récupérée par FCR.

Il lance jusqu'à 6 actions différentes pour un même document :

* Il interroge le webservice `ean2ppn` de l'Abes
* Il interroge le SRU du Sudoc sur les documents audio-visuels avec le titre, les auteurs, l'éditeur et les dates de publications sur leurs index spécifiques __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les documents audio-visuels avec le titre, les auteurs et les dates de publications sur leurs index spécifiques __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les documents audio-visuels avec le titre, les auteurs, l'éditeur et les dates de publications sur l'index général __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les documents audio-visuels avec le titre, les auteurs et l'éditeur sur l'index général __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les documents audio-visuels avec le titre sur son index spécifique

### `BETTER_ITEM_NO_ISBN`

Ce traitement recherche uniquement à partir des informations contenues dans la notice de la base de données d'origine récupérée par FCR.

Il lance jusqu'à 6 actions différentes pour un même document :

* Il interroge le webservice `ean2ppn` de l'Abes
* Il interroge le SRU du Sudoc sur les monographies imprimées avec le titre, les auteurs, l'éditeur et les dates de publications sur leurs index spécifiques __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les monographies imprimées avec le titre, les auteurs et les dates de publications sur leurs index spécifiques __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les monographies imprimées avec le titre, les auteurs, l'éditeur et les dates de publications sur l'index général __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les monographies imprimées avec le titre, les auteurs et l'éditeur sur l'index général __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les monographies imprimées avec le titre sur son index spécifique

### `BETTER_ITEM_NO_MAPS`

Ce traitement recherche uniquement à partir des informations contenues dans la notice de la base de données d'origine récupérée par FCR.

Il lance jusqu'à 6 actions différentes pour un même document :

* Il interroge le webservice `ean2ppn` de l'Abes
* Il interroge le SRU du Sudoc sur les cartes avec le titre, les auteurs, l'éditeur et les dates de publications sur leurs index spécifiques __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les cartes avec le titre, les auteurs et les dates de publications sur leurs index spécifiques __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les cartes avec le titre, les auteurs, l'éditeur et les dates de publications sur l'index général __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les cartes avec le titre, les auteurs et l'éditeur sur l'index général __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU du Sudoc sur les cartes avec le titre sur son index spécifique

## `MARC_FILE_IN_KOHA_SRU`

Ce traitement recherche uniquement à partir des informations contenues dans la notice du fichier à traiter.

Il lance jusqu'à 7 actions différentes pour un même document :

* Il interroge le SRU de Koha avec l'ISBN sur son index spécifique __si l'ISBN est présent dans la notice d'origine__
* Il interroge le SRU de Koha avec le titre, les auteurs, l'éditeur et les dates de publications sur leurs index spécifiques __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU de Koha avec le titre, les auteurs et les dates de publications sur leurs index spécifiques __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU de Koha avec le titre, les auteurs, l'éditeur et les dates de publications sur l'index général __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU de Koha avec le titre, les auteurs et les dates de publications sur l'index général __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU de Koha avec le titre, l'éditeur et les dates de publications sur l'index général __si toutes ces données sont présentes dans la notice__
* Il interroge le SRU de Koha avec le titre sur son index spécifique