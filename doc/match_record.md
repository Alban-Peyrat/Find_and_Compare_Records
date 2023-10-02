# Handle data returned from `Matched_Records`

`Matched_Records` instances always have these properties :

* `error` : a `Enum Match_Records_Errors` entry (or `None` if no error occured)
* `error_msg` : a `string` corresponding to the `error` property (or `None` if no error occured)
* `tries` : a `list` of `Request_Try` class
* `returned_ids` : a `list` of the matched ids as a `string`
* `returned_records` : a `list` of matched records as the type that they were returned
* `includes_record` : a `boolean` property that is set to `True` if records were returned by the connector
* `operation` : the `Enum Operations` entry that was actually used
* `query` : a `string` of the query used

`Request_Try` isntances always have these properties :

* `try_nb` : an `integer` corresponding to which try this was during the operation (starts at `0`)
* `action` : an `Enum Actions` entry
* `status` : an `Enum Try_Status` entry, defaults to `UNKNOWN`
* `error_type` : if an error occured, the type of the error as a `Enum Matched_Records_Error` entry
  * `None` if no error occured
  * If no specific error type was specified, `GENERIC_ERROR`
* `msg` : a `string` containing additional information :
  * `None` if not defined
  * A `string` corresponding to the `error_type` property if an error occured
  * Unless no specific error type was used, then it will be a manually defined string
* `query` : a `string` of the used query
* `returned_ids` : a `list` of the matched ids as a `string`
* `returned_records` : a `list` of matched records as the type that they were returned
* `includes_record` : a `boolean` property that is set to `True` if records were returned by the connector

# Connectors specifications

Connectors, to work with `Find_And_Compare_Records`, need to be able to :

* Return a __`list` of `strings`__ of the matched ids
* If they can return records too, return a __`list`__ of the matched records (types in the `list` do not matter as there is a universal data extractor)
* Detect if an error occured, but this optionnal as the behaviour defined in `request_action` probably can bypass the absence if error detection in the connector

# Add operations or actions (or other) to `Match_Records`

## Add an operation

* `Operations` define where and how `Find_And_Compare_Records` should look for matching records
* First, add a new entry in the `Enum Operations`
* Then, add this entry in the `dict TRY_OPERATIONS` :
  * The key is the `Enum Operations` entry (everything, not only the name or value)
  * The value must be a `list` of `Enum Actions`
    * The order is important as if an action is successful, it will not execute the remaining ones

## Add an action

* `Actions` define where `Find_And_Compare_Records` will be looking for and what will the query be
  * You can have multiple actions requesting from the same API if you want to modify the query : for example, you can have an action that queries `isbn2ppn` without modifying the input query, and another action that still queries `isbn2ppn` but this time the input query is changed into the 13/10 digits form of the ISBN
* First, if needed, import the connector to the webservice or other
* Then, add a new entry in the `Enum Actions`
* Then, add in the `Match_records.request_action()` method a new `elif action == Actions.YOUR_NEW_ACTION`
  * In this `elif`, you call the API or other
  * Call `thistry.define_used_query` with as argument the used query as a `string` 
  * Then, if an error occured, call `thisTry.error_occured()` with as argument :
    * A `Enum Matched_Records_Errors` entry
    * Or a `str` error message
  * If there are other types of status than `Success` or `Error`, call `thisTry.define_special_status()` with :
    * A `Try_Status` entry as first argument (if incorrect, then `Try_Status.UNKNOWN` will be set)
    * A message as second argument
  * If matched ids were returned, call `thisTry.add_returned_ids()` with the list of matched ids as argument
    * Note that this will switch the status to `SUCCESS`, so if you do not want that to happen, assign the list of returned ids directly to `thisTry.returned_ids`
  * If matched records were also returned, call `thistry.add_returned_records` with the list of matched records as argument

## Add a type of error

* First, add a new entry in the `Enum Match_Records_Errors`
* Then, add this entry in the `dict MATCH_RECORDS_ERROR_MESSAGES` :
  * The key is the `Enum Match_Records_Errors` entry (everything, not only the name or value)
  * The value must be a `str`

## Add a try status

* Add a new entry in the `Enum Try_Status`