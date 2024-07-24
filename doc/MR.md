# Match records

## Handle data returned from `Matched_Records`

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

## Add a try status

* _In `cl_MR.py`_
* Add a new entry in the `Enum Try_Status`