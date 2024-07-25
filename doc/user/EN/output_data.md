# Computed output data documentation

_Only the computed data is listed here._
_Those who only are a simple extraction from the record are not listed here, please refer to the field configuration in the database mappings._

|Internal Name|Column name (default)|Column name (`BETTER_ITEM`)|Data origin|
|---|---|---|---|
|`INPUT_QUERY`|_Input query_|_Input query_|Input file first column content for currently analysed row|
|`ORIGIN_DB_INPUT_ID`|_Original file ID_|_Original file biblionumber_|Input file last column content for currently analysed row, stripped of final spaces|
|`ERROR`|_Error_|_Error_|Did an error occurred ?|
|`ERROR_MSG`|_Error message_|_Error message_|If an error occured, the error message, sometimes with informations about the part of FCR that caused the error|
|`GLOBAL_VALIDATION_RESULT`|_Global validation result_|_Global validation result_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`GLOBAL_VALIDATION_NB_SUCCESSFUL_CHECKS`|_Number of successful checks_|_Number of successful checks_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`GLOBAL_VALIDATION_TITLE_CHECK`|_Title check_|_Title check_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`GLOBAL_VALIDATION_PUBLISHER_CHECK`|_Publishers check_|_Publishers check_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`GLOBAL_VALIDATION_DATE_CHECK`|_Dates check_|_Dates check_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`MATCH_RECORDS_QUERY`|_Query used to match records_|_Query used to match records_|Query used|
|`FCR_ACTION_USED`|_FCR action used_|_FCR action used_|Last action used (so the one who succeeded if records were found)|
|`MATCH_RECORDS_NB_RESULTS`|_Number of matches_|_Number of found PPN_|Number of records found|
|`MATCH_RECORDS_RESULTS`|_Matched IDs_|_Matched PPN_|Identifiers of found records|
|`MATCHED_ID`|_Current ID_|_Current PPN_|Identifier of the target database processed|
|`TARGET_DB_NB_OTHER_ID`|_Number of IDs in other databases target DB_|_Number of biblionumbers in Sudoc_|Number of other database identifiers found|
|`IS_ORIGIN_ID_IN_TARGET_OTHER_DB_IDS`|_Is origin DB ID in target DB IDs in other databases ?_|_Koha biblionumber in Sudoc ?_|Is the origin database identifier in the other database identifiers from the target database ?|
|`TARGET_DB_HAS_ITEMS`|_Already items in target DB ?_|_Already items in Sudoc ?_|Has the target database alerady items ?|
|`ORIGIN_DB_TITLE_KEY`|_Title key origin DB_|_Title key Koha_|Origin database title key (notably used in the analysis)|
|`TARGET_DB_TITLE_KEY`|_Title key target DB_|_Title key Sudoc_|Target database title key (notably used in the analysis)|
|`ORIGIN_DB_CHOSEN_PUBLISHER`|_Chosen publisher key origin DB_|_Chosen publisher key Koha_|Origin database chosen publisher key (notably used in the analysis)|
|`TARGET_DB_CHOSEN_PUBLISHER`|_Chosen publisher key target DB_|_Chosen publisher key Sudoc_|Trget database chosen publisher key (notably used in the analysis)|
|`ORIGIN_DB_DATE_1`|_Publication date 1 origin DB_|_Publication date 1 Koha_|First origin database general processing data date|
|`TARGET_DB_DATE_1`|_Publication date 1 target DB_|_Publication date 1 Sudoc_|First target database general processing data date|
|`ORIGIN_DB_DATE_2`|_Publication date 2 origin DB_|_Publication date 2 Koha_|Second origin database general processing data date|
|`TARGET_DB_DATE_2`|_Publication date 2 target DB_|_Publication date 2 Sudoc_|Second target database general processing data date|
|`ORIGIN_DB_PUBLICATION_DATES`|_Publication dates origin DB_|_Publication dates Koha_|All 4 number long strings found in data extracted as publication date in the origin database record|
|`TARGET_DB_PUBLICATION_DATES`|_Publication dates target DB_|_Publication dates Sudoc_|All 4 number long strings found in data extracted as publication date in the target database record|
|`ORIGIN_DB_PHYSICAL_DESCRIPTION`|__Is not computed in default behaviour__|_Physical description Koha_|Specific to `BETTER_ITEM` suite (as a cumpoted data), all 4 number long strings found in data extracted as physical description in the origin database record|
|`MATCHING_TITLE_RATIO`|_Matching title ratio_|_Matching title ratio_|Title simple ratio|
|`MATCHING_TITLE_PARTIAL_RATIO`|_Matching title partial ratio_|_Matching title partial ratio_|Title partial ratio|
|`MATCHING_TITLE_TOKEN_SORT_RATIO`|_Matching title token sort ratio_|_Matching title token sort ratio_|Title token sort ratio|
|`MATCHING_TITLE_TOKEN_SET_RATIO`|_Matching title token set ratio_|_Matching title token set ratio_|Title token set ratio|
|`MATCHING_DATES_RESULT`|_Matching dates result_|_Matching dates result_|[See file dedicated to the analysis](./analysis.md#analysis-results)|
|`MATCHING_PUBLISHER_RESULT`|_Matching publishers result_|_Matching publishers result_|Chosen publishers simple ratio|