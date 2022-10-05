# Comparaison des notices Koha et Sudoc

À partir de la liste de données extraites de Koha pour ITEM, vérifie que les correspondances PPN / ISBN du [webservice `isbn2ppn` de l'Abes](https://documentation.abes.fr/sudoc/manuels/administration/aidewebservices/index.html#isbn2ppn) correpondent bien aux documents enregistrés dans Koha.
Le traitement se focalise sur les correspondances uniques (ISBN trouvé et ne correspondant qu'à un seul PPN).

# WIP

05/10/2022 : `koha_API_publicBiblio` est quasiment terminé.
Je dois encore décider si je récupère les 210/214$d + adapter le getPPNautre Support en rajoutant un getBibnb avec -> return un tupple avec PPN en 1 et bibNb en 2 -> risque pb de rétrocompatibilité
Je dois aussi faire la doc et voir si je dois reconfigurer le logs + faire le ménage dans le connecteur avec l'API
