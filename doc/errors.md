# Errors

## Add a type of error

* _In `cl_error.py`_
* First, add a new entry in the `Enum Errors`
* Then, add this entry in the `dict ERRORS_LIST` :
  * The key is the `Enum Errors` entry (everything, not only the name or value)
  * The value must be a `str`