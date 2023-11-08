To add a textual elemnts, add an entry in fcr_gui_lang.GUI_Text

In an element without value, text comes from GUI_Text.ELEM.value[lang], key comes from GUI_Text.ELEM.name
In an element with value, text comes from ELEMS_WITH_VAL.ELEM, key is the ELEM attribute as a string

Add save buttons names must start with `SAVE_` and only them
In the screens definition, the values key contains all environment variables that are present in this screen
If there are tabs inside the screens, environment variables specific to a tab should be in the tabs[{nameOfTheTab}] key.

Tab groups inside a screen must have as a key the screen name + `_TABS`

All elements in the PROCESSING_CONFIGURATION must have a metadate with the key `class` containging a list of :

* "PROCESSING_CONFIGURATION_MAIN"
* All FCR_Processings __names__ in which it shouldbe displayed
* _They are used to oly display relevent fields_

Elements to add new field must have the `` class in metadata

In order to remove a field in a MARC data, you have to manually delete it in the JSON file