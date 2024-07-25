# Computed output data documentation

_Only the computed data is listed here._
_Those who only are a simple extraction from the record are not listed here, please refer to the field configuration in the database mappings._

|Internal Name|Column name (default)|Column name (`BETTER_ITEM`)|Data origin|
|---|---|---|---|
|`INPUT_QUERY`|_Requête originale_|_Requête originale_|Input file first column content for currently analysed row|
|`ORIGIN_DB_INPUT_ID`|_ID fichier original_|_Biblionumber fichier original_|Input file last column content for currently analysed row, stripped of final spaces|
|`ERROR`|_Erreur_|_Erreur_|Did an error occurred ?|
|`ERROR_MSG`|_Message d'erreur_|_Message d'erreur_|If an error occured, the error message, sometimes with informations about the part of FCR that caused the error|
|`GLOBAL_VALIDATION_RESULT`|_Validation globale_|_Validation globale_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`GLOBAL_VALIDATION_NB_SUCCESSFUL_CHECKS`|_Nombre de validations réussies_|_Nombre de validations réussies_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`GLOBAL_VALIDATION_TITLE_CHECK`|_Validation des titres_|_Validation des titres_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`GLOBAL_VALIDATION_PUBLISHER_CHECK`|_Validation des éditeurs_|_Validation des éditeurs_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`GLOBAL_VALIDATION_DATE_CHECK`|_Validation des dates_|_Validation des dates_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`MATCH_RECORDS_QUERY`|_Requête pour recherche de correspondances_|_Requête pour recherche de correspondances_|Query used|
|`FCR_ACTION_USED`|_Action FCR utilisée_|_Action FCR utilisée_|Last action used (so the one who succeeded if records were found)|
|`MATCH_RECORDS_NB_RESULTS`|_Nombre de correspondances_|_Nombre de PPN trouvés_|Number of records found|
|`MATCH_RECORDS_RESULTS`|_IDs correspondants_|_PPN trouvés_|Identifiers of found records|
|`MATCHED_ID`|_ID en cours de traitement_|_PPN en cours de traitement_|Identifier of the target database processed|
|`TARGET_DB_NB_OTHER_ID`|_Nombre d'IDs d'autres bases de données BDD de destination_|_Nombre de biblionumbers dans Sudoc_|Number of other database identifiers found|
|`IS_ORIGIN_ID_IN_TARGET_OTHER_DB_IDS`|_ID BDD d'origine compris dans les IDs d'auters bases de données BDD de destination ?_|_Biblionumber Koha dans le Sudoc ?_|Is the origin database identifier in the other database identifiers from the target database ?|
|`TARGET_DB_HAS_ITEMS`|_Déjà des exemplaires dans BDD de destination ?_|_Déjà des exemplaires dans Sudoc ?_|Has the target database alerady items ?|
|`ORIGIN_DB_TITLE_KEY`|_Clef de titre BDD d'origine_|_Clef de titre Koha_|Origin database title key (notably used in the analysis)|
|`TARGET_DB_TITLE_KEY`|_Clef de titre BDD de destination_|_Clef de titre Sudoc_|Target database title key (notably used in the analysis)|
|`ORIGIN_DB_CHOSEN_PUBLISHER`|_Clef d'éditeur choisi BDD d'origine_|_Clef d'éditeur choisi Koha_|Origin database chosen publisher key (notably used in the analysis)|
|`TARGET_DB_CHOSEN_PUBLISHER`|_Clef d'éditeur choisi BDD de destination_|_Clef d'éditeur choisi Sudoc_|Trget database chosen publisher key (notably used in the analysis)|
|`ORIGIN_DB_DATE_1`|_Date de publication 1 BDD d'origine_|_Date de publication 1 Koha_|First origin database general processing data date|
|`TARGET_DB_DATE_1`|_Date de publication 1 BDD de destination_|_Date de publication 1 Sudoc_|First target database general processing data date|
|`ORIGIN_DB_DATE_2`|_Date de publication 2 BDD d'origine_|_Date de publication 2 Koha_|Second origin database general processing data date|
|`TARGET_DB_DATE_2`|_Date de publication 2 BDD de destination_|_Date de publication 2 Sudoc_|Second target database general processing data date|
|`ORIGIN_DB_PUBLICATION_DATES`|_Dates de publication BDD d'origine_|_Dates de publication Koha_|All 4 number long strings found in data extracted as publication date in the origin database record|
|`TARGET_DB_PUBLICATION_DATES`|_Dates de publication BDD de destination_|_Dates de publication Sudoc_|All 4 number long strings found in data extracted as publication date in the target database record|
|`ORIGIN_DB_PHYSICAL_DESCRIPTION`|__Is not computed in default behaviour__|_Description physique Koha_|Specific to `BETTER_ITEM` suite (as a cumpoted data), all 4 number long strings found in data extracted as physical description in the origin database record|
|`MATCHING_TITLE_RATIO`|_Score de similarité des titres_|_Score de similarité des titres_|Title simple ratio|
|`MATCHING_TITLE_PARTIAL_RATIO`|_Score d'appartenance des titres_|_Score d'appartenance des titres_|Title partial ratio|
|`MATCHING_TITLE_TOKEN_SORT_RATIO`|_Score d'inversion des titres_|_Score d'inversion des titres_|Title token sort ratio|
|`MATCHING_TITLE_TOKEN_SET_RATIO`|_Score d'inversion appartenance des titres_|_Score d'inversion appartenance des titres_|Title token set ratio|
|`MATCHING_DATES_RESULT`|_Correspondance des dates de publications_|_Correspondance des dates de publications_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`MATCHING_PUBLISHER_RESULT`|_Score de similarité des éditeurs choisis_|_Score de similarité des éditeurs choisis_|Chosen publishers simple ratio|