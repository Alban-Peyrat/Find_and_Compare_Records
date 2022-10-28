# Notes sur le premier test concluant (500 notices)

* Analyse choisie : 1
* 500 lignes dans le fichier choisi

* resultats.json : 721ko, 23081 lignes
* resultats.csv : 153ko
* logs : 662ko, 5636 lignes

Le `résultats.txt` a un problème dans le Nombre de correspondance unique sur isbn2ppn.
Il y en a 388 en réalité.
Sur les 388, 19 requêtes Koha ont échouées, soit 4,9%.

Le format JSON dans Koha semble avoir corriger le problème pour les éditeurs

* Premier log : 2022-10-19 15:26:35,399
* Dernier log : 2022-10-19 15:33:09,249
* ~6 min 30 pour l'exécution sur 500 documents

Validation globale :
* 335 OK
* 18 2
* 13 1
* 3 0

# Notes sur le second test concluant (500 notices)

* Analyse choisie : 3
* 500 lignes dans le fichier choisi

* resultats.json : 719ko, 23049 lignes
* resultats.csv : 152ko
* logs : 660ko, 5626 lignes

Le `résultats.txt` a un problème dans le Nombre de correspondance unique sur isbn2ppn.
Il y en a 387 en réalité.
Sur les 387, 19 requête Koha ont échouées, soit 4,9%.
__Ce sont les mêmes biblionumbers qui ont échoué :__
226753
226767
226781
226782
226783
226784
226812
226895
226936
226946
226972
227012
227127
227163
227329
227845
227887
228100
228197

__Ces notices n'existent plus dans Koha, il n'y a donc pas de problème au niveau du script__, c'est juste l'âge du fichier qui en est la cause.

__Les mêmes ISBN ont échoué sur isbn2ppn.__
L'isbn `211085457X` a eu un résultat de plus de la part de isbn2ppn dans le second essai.
Le RCR 751165107 l'a bien modifié à 15:58:02 le même jour que les exécutions, pas de problème à ce niveau là.

* Premier log : 2022-10-19 15:57:05,440
* Dernier log : 2022-10-19 16:03:25,322
* ~6 min 30 pour l'exécution sur 500 documents

Validation globale :
* 339 OK
* 22 1
* 7 0