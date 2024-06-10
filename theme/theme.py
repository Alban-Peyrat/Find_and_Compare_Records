# https://github.com/PySimpleGUI/PySimpleGUI/tree/master/ThemeMaker
from enum import Enum

class ArchiRes_Colors(Enum):
    RED = "#d6441c"
    GREY = "#575551"
    CREME = "#eae8e3"
    BLACK_FONTS = "#001111"
    WHITE = "#ffffff"


theme_name = "ArchiRes_Theme"
theme = {'BACKGROUND': ArchiRes_Colors.GREY.value,
             'TEXT': ArchiRes_Colors.WHITE.value,
             'INPUT': ArchiRes_Colors.CREME.value,
             'TEXT_INPUT': ArchiRes_Colors.BLACK_FONTS.value,
             'SCROLL': ArchiRes_Colors.BLACK_FONTS.value,
             'BUTTON': (ArchiRes_Colors.WHITE.value, ArchiRes_Colors.RED.value),
             'PROGRESS': (ArchiRes_Colors.WHITE.value, ArchiRes_Colors.GREY.value),
             'BORDER': 1, 'SLIDER_DEPTH': 0, 'PROGRESS_DEPTH': 0
             }
font = ("Verdana", 16)
window_location = (0, 0)
