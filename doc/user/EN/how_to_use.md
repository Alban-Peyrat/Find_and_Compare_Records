# How to use _Find and Compare Records_

Once the application downloaded et the `sample.env` file renammed to `.env`, you can execute the application.

To do it :

* Execute the file `FCR.bat` found at the root of the application
* Or, using the command terminal, go to the application folder (using `cd`) and execute with Python the file `main_gui.py`

## Step 1 : main configuration

![_Find and Compare Records_ main screen](./img/UI_main_screen.png)

_The top-right button allows to switch language between french and english._

This screen is used to configure the main settings of the application :

* The processing to use _([see more about available processings](./processings.md))_
* Files path :
  * To the input file _([see more about the input file](./input_file.md))_
  * To the output folder
  * To the folder containing the log file
* The service name (only used for logs, notable namming the file)
* The log level

The _Save these executon settigs_ button can be used to save the settings currently displayed for a future execution (including language).

Once this screen correctly configured (and possibly saved), the _Next (processing configuration)_ button is used to go to nest step.

## Step 2 : processing configuration

This new screen has 3 tabs :

* _Processing main configuration_
* _Mapping configuration_
* _Chose database mappings_

A text under the screen title reminds which processing will be used.

Once every tab is correctly configured, the _Start analysis_ button is used to go to the third and last step.

### _Processing main configuration_ tab

This tab displayes settings is based on the chosen processing.

The _Save main processing configuration settings_ button is used to saved currently displayed settings for a fututre execution.


#### `BETTER_ITEM` suite

![Processing configuration screen, main configuration tab for `BETTER_ITEM`](./img/UI_processing_conf_main_tab_better_item.png)

* Origin database URL : this processing retrieve data from the origin database through its APIs, the URL should be the __domain name for API exution__
* ILN : library ILN _(used to filter identifiers in other databases)_
* RCR : library RCR _(used to filter items & items barcodes)_

#### `MARC_FILE_IN_KOHA_SRU`

![Processing configuration screen, main configuration tab for `MARC_FILE_IN_KOHA_SRU`](./img/UI_processing_conf_main_tab_marc_file_in_koha_sru.png)

* Target database URL : this processing retrieve data from the origin database through its APIs, the URL should be the __domain name for API exution__ (or the SRU if it is used)
* Filter 1, 2 & 3 : free filters, configurable based on target database (or origin)
  * Filter 1 is used to filter items & items barcodes
  * To link filters to data, the code in `cl_PODA.py` needs to be edited ([see developper documentation about PODAs on that subject](../../PODAs.md#database))

### _Mapping configuration_ tab

![Processing configuration screen, mapping configuration tab](./img/UI_processing_conf_db_conf_tab.png)

This tab is the most complex one, but also the one who does not need to be reconfigured once it is saved.

It is used to configure which data will be retrieved from records (graphic interface to configure `json_configs/marc_fields.json`).
For more information on how to configure those mapping, see [universal data extractor docuemention](../../../doc/UDE.md).

Firstly, you need to select which ampping to edit.
It is possible to add a new mapping using the _Save this mpping as a new one_ button, which will copy the whole curent mapping under a new name.
The button will open a dialog window asking for the name of the new mapping, which is saved using the _OK_ button.

![Dialog window to save a new mapping](./img/UI_save_new_mapping.png)

Secondly, you need to chose which data to configure.
This data can be renammed for the current langauge using the _Rename_ button.
The button will open a new dialog window asking for the new name, which then needs to be confirmed using the _OK_ button to save.
To make sure which data is currently being renammed, its internal id is written between parenthesis.

![Dialog window to save the data rename](./img/UI_save_new_data_name.png)

Thirdly, you need to chose a MARC field to configure.
For each field, 4 data can be set up (or not) :

* Is single line coded data : is used if the field is a coded data in only one subfield (example : UNIMARC `100`)
* Filtering subfield : is used to set up which subfield must be used to rule out unwanted fields (example : keeping only items for a library)
* Subfields to export : the subfield list to export, separated with commas (spaces bewteen commas will be deleted)
* Positions to export :
  * Positions list to export, separated with commas (spaces bewteen commas will be deleted)
  * This information is only used if the field is set as a single line coded data
  * To extract only 1 character, write it's position
  * Ro extract a strinf of characters, write the first position to export and the last position to export, separated by a dash

To add new fields, select the field _Add new field_, which will make a new completable data appear next to it.
Input the field tag in that new text input.

![New field configuration](./img/UI_add_new_field.png)

To save a modification on a field, clic on the _Save this MARC field button_
This operation is needed __for every field__, otherwise the modifications will not be saved.

### _Chose database mappings_ tab

![Processing configuration screen, chosing database mappings tab](./img/UI_processing_conf_chose_mapping_tab.png)

This tab is the easiest as it only requires to chose the mapping we want to use for the origin database & for the target database.

The _Save chosen database mappings_ button is used to save currently displayed settings for future execution.

## Step 3 : chosing the analysis

![Chosing the analysis screen](./img/UI_chose_analysis.png)

This last screen is used to chose the analysis we want to execute, from the ones defined in the `json_configs/analysis.json` file.

The _Start main script_ button is used to start the script.