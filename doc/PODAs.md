# Add a new Processing, Operation, Database or Action

## Action

Actions define where `Find_And_Compare_Records` will be looking for and what will the query be.

You can have multiple actions requesting from the same API if you want to modify the query : for example, you can have an action that queries `isbn2ppn` without modifying the input query, and another action that still queries `isbn2ppn` but this time the input query is changed into the 13/10 digits form of the ISBN.

To add an action :

* In `cl_PODA.py` :
  * Add a new member in the `Enum Action_Names`
  * Added a new entry in `dict ACTIONS_LIST`
    * Use the `Action_Names` member as the key
    * As a value, create a `class Action` instance :
      * Define `action` as the `Action_Names` member
      * Then, you're free to set some optional values :
        * _Those values are used inside MR `request_action()` for some actions, but a new action can be used without them_
        * `isbn` (`bool`, `false` by default) : the action uses ISBN for the query
        * `ean` (`bool`, `false` by default) : the action uses EAN for the query
        * `title` (`bool`, `false` by default) : the action uses a title for the query
        * `authors` (`bool`, `false` by default) : the action uses authors for the query
        * `publisher` (`bool`, `false` by default) : the action uses the publisher for the query
        * `date` (`bool`, `false` by default) : the action uses the date for the query
        * `doctype` (`str`, `""` by default) : the action uses a document type for the query, needs to be set on specific values _(to be used in `request_action()`)_
        * `specific_index` (`bool`, `true` by default) : the action uses specific indexes instead of a more general index like `any`
* In `cl_MR.py` :
  * First, if needed, import the connector to the webservice or other
  * If the action can already be performed by current big `elif`, so just add the new action isnide the `elif action in []`
    * Those use the optionnal values set in `cl_PODA.py`
    * Currently, both Sudoc & Koha SRU can be used by defautl with ISBN, title, authors, dates and publisher (Sudoc can also use document type, but they need to be added to the code if they're not : `B`, `K` or `V`)
  * Else, add in the `Match_records.request_action()` method a new `elif action == Actions.YOUR_NEW_ACTION`
    * In this `elif`, you call the API or other
    * Call `thisTry.define_used_query()` with as argument the used query as a `string` 
    * Then, if an error occured, call `thisTry.error_occured()` with as argument :
      * A `Enum Matched_Records_Errors` entry
      * Or a `str` error message
    * If there are other types of status than `Success` or `Error`, call `thisTry.define_special_status()` with :
      * A `Try_Status` entry as first argument (if incorrect, then `Try_Status.UNKNOWN` will be set)
      * A message as second argument
    * If matched ids were returned, call `thisTry.add_returned_ids()` with the list of matched ids as argument
      * Note that this will switch the status to `SUCCESS`, so if you do not want that to happen, assign the list of returned ids directly to `thisTry.returned_ids`
    * If matched records were also returned, call `thistry.add_returned_records` with the list of matched records as argument

## Database

Database are a weirdly nammed thing but defines a type of database, part of how to connect to them and if they can be filtered.
They are without a doubt a messy part of the code that evolved the wrong way, so the part on _How to add one_ might be incomplete.
But they're somehow vital, so R.I.P.

Also, they are dependant of UDE.

To add a new database name :

* _In `cl_UDE.py`_ :
  * Add a new database ([_explained in `UDE.md`, part dedicated to adding a database_](./UDE.md#add-a-database))
  * If the new database is using XML with a specific namespace, check how to configure it ([_explained in `UDE.md`, part dedicated to adding an XML data source with a new namespace_](./UDE.md#add-an-xml-data-source-with-new-namespaces))
* _In `cl_PODA.py`_ :
  * Added a new entry in `dict DATABASES_LIST`
    * Use the `Database_Names` member as the key
    * As a value, create a `class Database` instance :
      * Define `database` as the `Database_Names` member
      * Define `filters` as a `dict` :
        * Use a `Mapped_Fields` (in `cl_UDE.py`) member as a key
        * Use a `Filters` member as value
        * _List all fields that should be filtered, the `Filters` member is which filter in the execution settings that will be used_

### Adding new filters

* _In `cl_PODA.py`_ :
  * Add a new member to `Enum Filters`
* _In `.env`_ :
  * Add a new entry in `.env`, using the name of the `Enum Filters` member
* _In `cl_ES.py`_ :
  * In `Records_Settings.__init__()` :
    * Add a new argument to the constructor
    * Add a new property using the `Enum Filters` member name in lower case
  * In `Execution_Settings` :
    * In `load_env_values()`, add a new property using the `Enum Filters` member name in lower case that loads the environment variable set up earlier
    * In `get_record_settings()`, change the `Records_Settings` call by adding the argument as configured earlier
    * In `UI_update_processing_configuration_values()`, add a new property using the `Enum Filters` member name in lower case that loads the `val` property assigned to the environment variable set up earlier
* In `main_gui.py` : see [in GUI documentation to add the new element](./GUI.md)

## Operation

Operations define where and how `Find_And_Compare_Records` should look for matching records.
They are kind of a parent class of actions, as they are mostly a list of action to perform until one or more records match.

To add an operation :

* _In `cl_PODA.py`_ :
  * Add a new member in the `Enum Operation_Names`
  * Added a new entry in `dict OPERATIONS_LIST`
    * Use the `Operation_Names` member as the key
    * As a value, create a `class Operation` instance :
      * Define `operation` as the `Operation_Names` member
      * Define `actions` as a `list` of `Enum Action_Names`
      * _Note : the order of the actions is important as if an action is successful, the remaining ones will not be executed_

## Processing

Processings are the biggest parameter as they use all other PODAs concept.
They define which data will be extracted from records, which operation will be performed (and by extension, which actions to use) and which database they should query.

They also are what shifted *Better_ITEM* to FCR, as the application was originally only supposed to do what the current *BETTER_ITEM* processing does.

To add a processing :

* In `cl_PODA.py` :
  * Add a new member in the `Enum Processing_Names`
  * Added a new entry in `dict PROCESSINGS_LIST`
    * Use the `Processing_Names` member as the key
    * As a value, create a `class Processing` instance :
      * Define `processing` as the `Processing_Names` member
      * Define `mapped_data` as a `dict`, using UDE's `Enum Mapped_Fields` member as keys and `Enum Processing_Data_Target` member as value :
        * This defines which data to extarct from record and from which database (origin, target or both)
      * Define `operation` as the instance of the operation you want to use (use `OPERATIONS_LIST[Operation_Names.WANTED_OEPRATION`)
      * Define `origin_database` as the instance of the database you want to use as origin database (use `DATABASES_LIST[Database_Names.WANTED_DATABASE]`)
      * Define `target_database` as the instance of the database you want to use as target database (use `DATABASES_LIST[Database_Names.WANTED_DATABASE]`)
      * Define `original_file_data_is_csv` as `False` if the original file is a MARC records, else define as `True` (so FCR correctly queries the origin database to get the records)
* In `cl_ES.py` :
  * In `Execution_Settings.load_original_file_data()` method, connect to an already existing behaviour or add one
  * If needed, remove some exported columns inside `Execution_Settings.CSV.__define_headers()` method
* In `cl_main.py` :
  * If needed, add a `__special_` method to subclass `Original_Record.Output` and call it inside the `to_csv()` method
  * If needed, remove some exported columns inside `Report.generate_report_output_lines()` method
* In `main_gui.py` : see [in GUI doc](./GUI.md#hide-elements-for-some-processings)
* In `main.py`, add the processing to :
  * The logger init part
  * The origin database part
  * The matched_records part if needed
  * The target database part