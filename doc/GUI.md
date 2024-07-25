# Graphic user interface

_Do not hesitate to check [`FreeSimpleGUI` demos](https://github.com/spyoungtech/FreeSimpleGUI/blob/main/DemoPrograms/Demo_All_Elements.py)_

## Add an element with value

* Chose the input type, then use as a key :
  * The environbment variable name (if it is one)
  * Another name in upper case using underscore as spaces
* Add to the `load_env_values()` method of the `Class Execution_Settings` (in `cl_ES.py`) a new property to handle this element
* If it is a environment variable that can be saved, add it's name to the `values` key of the screen and / or tab it appears in inside the `Enum GUI_Screens`
* __Do not forget to update `UI_update_main_screen_values()` & `UI_update_processing_configuration_values()` methods of `Class Execution_Settings`__

## Add a text element

* Add a member in `Enum GUI_Text` (in `fcr_gui_lang.py`) with an object as value, containing a key for each supported language, with the wanted text.
* In the wanted part of the layout, add a `sg.Text` instance, using as text `GUI_Text.NAME_OF_THE_NEW_TEXT_ELEMENT.value[VALLS.lang]` and as key the name of the `GUI_Text` member

## Hide elements for some processings

* All processing specific elements are hidden by default, you have to specifiy when to show them
* Add a metadata with the key `class` containing a list of :
  * `PROCESSING_CONFIGURATION_MAIN`
  * All FCR_Processings __names__ where the element should de displayed

## Align elements

* Use a `sg.Push()` instance to align elements :
  * On the left to push everything to the right
  * On the right to push everythin to the left
  * On both sides to center

## Add a tab

* Tabs have their own layout, so define one using as variable name `{Name_Of_The_Tab}_TAB_LAYOUT`
* Add a `GUI_Text` member is needed for the tab name, the name should end with `_TAB_TITLE`
  * The name should be consistent between those two
* Add the `GUI_Text` member name as an object to the `tabs` key of the screen it appears in inside the `GUI_Screens` enum, and define the `values` key as a list of environment variable names that can be saved from this tab
* Add a new `sg.Tab` in the `sg.TabGroup` of the wanted screen, using the __`GUI_Text` member name__ as a key
  * Note : tab groups inside a screen must have as a key the screen name + `_TABS`

## Add a save button

* Save buttons names must start with `SAVE_` and only them
* If the data to save can not be saved through the `save_parameters` function, add a condition to the `if` in the event loop

## Add an event

* In the event loop, add a new `if`, using the __`GUI_Text` member name__ for buttons or the input key to detect the event name
* For some elements such as `OptionMenu`, it might be necessary to turn off the event tracker, to prevent endless loops and thus getting stuck in the endless now
  * At the beginning of this event handling, turn off the tracker with the `remove_TKString_trace()` function
  * At the end of this event handling, turn it back on with the `add_TKString_trace()` function

