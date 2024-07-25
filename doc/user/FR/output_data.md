# Données exportées

_Sont listées ici uniquement les données calculées dans le programme._
_Les données qui ne sont qu'un simple export de la notice ne sont pas renseignées ici, il faut se référer à la configuration des champs dans les mappings sélectionnés._

|Nom interne|Nom de la colonne (défaut)|Nom de la colonne (`BETTER_ITEM`)|Provenance de la donnée|
|---|---|---|---|
|`INPUT_QUERY`|_Requête originale_|_Requête originale_|Contenu de la première colonne du fichier à analyser pour la ligne en cours d'analyse|
|`ORIGIN_DB_INPUT_ID`|_ID fichier original_|_Biblionumber fichier original_|Contenu de la dernière colonne du fichier à analyser pour la ligne en cours d'analyse, en retirant les espaces finaux|
|`ERROR`|_Erreur_|_Erreur_|Une erreur a-t-elle eu lieu ?|
|`ERROR_MSG`|_Message d'erreur_|_Message d'erreur_|En cas d'erreur, le message d'erreur, avec parfois une information sur le module qui a causé l'erreur|
|`GLOBAL_VALIDATION_RESULT`|_Validation globale_|_Validation globale_|[Voir le fichier dédié à l'analyse](./analysis.md#résultats-de-lanalyse)|
|`GLOBAL_VALIDATION_NB_SUCCESSFUL_CHECKS`|_Nombre de validations réussies_|_Nombre de validations réussies_|[Voir le fichier dédié à l'analyse](./analysis.md#résultats-de-lanalyse)|
|`GLOBAL_VALIDATION_TITLE_CHECK`|_Validation des titres_|_Validation des titres_|[Voir le fichier dédié à l'analyse](./analysis.md#résultats-de-lanalyse)|
|`GLOBAL_VALIDATION_PUBLISHER_CHECK`|_Validation des éditeurs_|_Validation des éditeurs_|[Voir le fichier dédié à l'analyse](./analysis.md#résultats-de-lanalyse)|
|`GLOBAL_VALIDATION_DATE_CHECK`|_Validation des dates_|_Validation des dates_|[Voir le fichier dédié à l'analyse](./analysis.md#résultats-de-lanalyse)|
|`MATCH_RECORDS_QUERY`|_Requête pour recherche de correspondances_|_Requête pour recherche de correspondances_|Requête utilisée pour rechercher une correspondance|
|`FCR_ACTION_USED`|_Action FCR utilisée_|_Action FCR utilisée_|Dernière action utilisée (donc, celle qui a réussi en cas de correspondance trouvée)|
|`MATCH_RECORDS_NB_RESULTS`|_Nombre de correspondances_|_Nombre de PPN trouvés_|Nombre de correspondances trouvées|
|`MATCH_RECORDS_RESULTS`|_IDs correspondants_|_PPN trouvés_|Liste des identifiants des notices correspondantes trouvées|
|`MATCHED_ID`|_ID en cours de traitement_|_PPN en cours de traitement_|Identifiant de la notice de la base de destination traitée|
|`TARGET_DB_NB_OTHER_ID`|_Nombre d'IDs d'autres bases de données BDD de destination_|_Nombre de biblionumbers dans Sudoc_|Nombre d'identifiants d'autres bases de données trouvés|
|`IS_ORIGIN_ID_IN_TARGET_OTHER_DB_IDS`|_ID BDD d'origine compris dans les IDs d'auters bases de données BDD de destination ?_|_Biblionumber Koha dans le Sudoc ?_|L'identifiant de la base de données d'origine est-il présent dans la liste des identifiants d'autres bases de données trouvées ?|
|`TARGET_DB_HAS_ITEMS`|_Déjà des exemplaires dans BDD de destination ?_|_Déjà des exemplaires dans Sudoc ?_|La base de données de destination possède-t-elle déjà des exemplaires ?|
|`ORIGIN_DB_TITLE_KEY`|_Clef de titre BDD d'origine_|_Clef de titre Koha_|Clef de titre de la base de données d'origine (notamment utilisé pour l'analyse)|
|`TARGET_DB_TITLE_KEY`|_Clef de titre BDD de destination_|_Clef de titre Sudoc_|Clef de titre de la base de données de destination (notamment utilisé pour l'analyse)|
|`ORIGIN_DB_CHOSEN_PUBLISHER`|_Clef d'éditeur choisi BDD d'origine_|_Clef d'éditeur choisi Koha_|Clef de l'éditeur choisi de la base de données d'origine (notamment utilisé pour l'analyse)|
|`TARGET_DB_CHOSEN_PUBLISHER`|_Clef d'éditeur choisi BDD de destination_|_Clef d'éditeur choisi Sudoc_|Clef de l'éditeur choisi de la base de données de destination (notamment utilisé pour l'analyse)|
|`ORIGIN_DB_DATE_1`|_Date de publication 1 BDD d'origine_|_Date de publication 1 Koha_|Première date des données générales de traitement de la base de données d'origine|
|`TARGET_DB_DATE_1`|_Date de publication 1 BDD de destination_|_Date de publication 1 Sudoc_|Première date des données générales de traitement de la base de données de destination|
|`ORIGIN_DB_DATE_2`|_Date de publication 2 BDD d'origine_|_Date de publication 2 Koha_|Seconde date des données générales de traitement de la base de données d'origine|
|`TARGET_DB_DATE_2`|_Date de publication 2 BDD de destination_|_Date de publication 2 Sudoc_|Seconde date des données générales de traitement de la base de données de destination|
|`ORIGIN_DB_PUBLICATION_DATES`|_Dates de publication BDD d'origine_|_Dates de publication Koha_|Toutes les suites de 4 chiffres présentes dans les données extraites en tant que dates de publications dans la base de données d'origine|
|`TARGET_DB_PUBLICATION_DATES`|_Dates de publication BDD de destination_|_Dates de publication Sudoc_|Toutes les suites de 4 chiffres présentes dans les données extraites en tant que dates de publications dans la base de données de destination|
|`ORIGIN_DB_PHYSICAL_DESCRIPTION`|__Pas un champ un calculé par défaut__|_Description physique Koha_|Spécifique à la suite `BETTER_ITEM` (en tant que champ calculé), toutes les suites de 4 chiffres présentes dans les données extraites en tant que description dans la base de données d'origine|
|`MATCHING_TITLE_RATIO`|_Score de similarité des titres_|_Score de similarité des titres_|Score de similarité des titres|
|`MATCHING_TITLE_PARTIAL_RATIO`|_Score d'appartenance des titres_|_Score d'appartenance des titres_|Score d'appartenance des titres|
|`MATCHING_TITLE_TOKEN_SORT_RATIO`|_Score d'inversion des titres_|_Score d'inversion des titres_|Score d'inversion des titres|
|`MATCHING_TITLE_TOKEN_SET_RATIO`|_Score d'inversion appartenance des titres_|_Score d'inversion appartenance des titres_|Score d'inversion appartenance des titres|
|`MATCHING_DATES_RESULT`|_Correspondance des dates de publications_|_Correspondance des dates de publications_|[Voir le fichier dédié à l'analyse](./analysis.md#résultats-de-lanalyse)|
|`MATCHING_PUBLISHER_RESULT`|_Score de similarité des éditeurs choisis_|_Score de similarité des éditeurs choisis_|Score de similarité des éditeurs choisis|