# Analysis documentation

## Comparing data bewteen databases

Once all data is retrieved, compares data between the two databases :

* Title : generate a simple ratio, a partial ratio, a token sort ratio and a token set ratio using [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
* Publication dates : checks if one of the origin database date is equal to one of the target databes date (does not check if no dates are found)
* Publisher : compares every publisher from the origin database record to every publisher from the target database record using a simple ratio, then returns the couple with the highest ratio

Then, the script validate or not every comparison criteria for the chosen analysis and outputs a validation grade for this comparison.

## Matching results analysis

The matching results analysis is based on 3 criterias :

1. Of the 4 title ratios used, at least X of them meet the required floor
1. The publishers ratio meet the required floor
1. The publication date is used

## Analysis results

The analysis output 5 data :

* _Global validation result_ : analysis final result, can be :
  * _All checks were successful_
  * _Checks partially successful_ : only some checks were succesful
  * _All checks failed_
  * _No checks_ : chosen analysis does not check any criteria
  * If nothing is displayed, the analysis did not happen
* _Number of successful checks_ : the number of checks that were OK
* _Title check_ :
  * `True` if the number of title checks was superir or aquel to the minimum required
  * `False` if it was nto the case
* _Publishers check_
  * `True` if the publishers ratio is superior or equal to the required floor
  * `False` if it was nto the case
* _Dates check_
  * `True` if one of the origin database date matches one of the target database ones
  * `False` if it was nto the case

_Note : details (notably ratios) are available at the end of CSV export columns_

## Default analysis configuration

_If the floor are configured to `0`, the critera will be ignored_

### Analysis 0 : Aucune analyse

* Floor ratio for title match : `0`
* Minimum ratio number matching : `0`
* Floor ratiofor publisher match : `0`
* Use publication date : `NON`

### Analysis 1 : Titre 80 (3/4), Editeurs 80, Dates

* Floor ratio for title match : `80`
* Minimum ratio number matching : `3`
* Floor ratiofor publisher match : `80`
* Use publication date : `OUI`

### Analysis 2 : Titre 90

* Floor ratio for title match : `90`
* Minimum ratio number matching : `4`
* Floor ratiofor publisher match : `0`
* Use publication date : `NON`

### Analysis 3 : Titre 95, Editeurs 95

* Floor ratio for title match : `95`
* Minimum ratio number matching : `4`
* Floor ratiofor publisher match : `95`
* Use publication date : `NON`

## Configure an analysis

To add a new analysis, add a new object in `analysis.json` with the following keys :

* `name` `(str)`: interface displayed analysis name
* `TITLE_MIN_SCORE` (`int`) : floor ratio for title matching to be OK
* `NB_TITLE_OK` (`int`) : minimum number of title matches for considering the entire title criteria to be OK
* `PUBLISHER_MIN_SCORE` (`int`) : floor ratio for publishers matching to be OK
* `USE_DATE` (`bool`) : use publication date