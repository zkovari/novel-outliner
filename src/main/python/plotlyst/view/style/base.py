"""
Plotlyst
Copyright (C) 2021-2024  Zsolt Kovari

This file is part of Plotlyst.

Plotlyst is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Plotlyst is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from typing import Union

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QWidget
from qtmenu import MenuWidget

from plotlyst.view.style.theme import BG_PRIMARY_COLOR, BG_SECONDARY_COLOR

style = f'''
* {{
    icon-size: 20px;
}}

QToolTip {{
    border: 0px;
    font-size: 14pt;
    padding: 5px;
    background-color: {BG_PRIMARY_COLOR};
}}

QMenuBar {{
    background-color: {BG_PRIMARY_COLOR};
}}

QToolBar {{
    spacing: 1px;
}}

QWidget[bg=true] {{
    background-color: {BG_PRIMARY_COLOR};
}}

QWidget[darker-bg=true] {{
    background-color: #E5E5EE;
}}

QWidget[white-bg=true] {{
    background-color: #FcFcFc;
}}

QWidget[relaxed-white-bg=true] {{
    background-color: {BG_SECONDARY_COLOR};
}}

QWidget[banner-bg=true] {{
    background-color: #2B0548;
}}

QWidget[transparent=true] {{
    border: 0px;
    background-color: rgba(0, 0, 0, 0);
}}

QWidget[navbar=true] {{
    background-color: #622675;
}}

QFrame[bottom-bar=true] {{
    background-color: {BG_PRIMARY_COLOR};
}}

QFrame[relaxed-white-bg=true] {{
    background-color: {BG_SECONDARY_COLOR};
}}

QFrame[white-bg=true] {{
    background-color: #FcFcFc;
}}

QFrame[rounded=true] {{
    border: 1px solid lightgrey;
    border-radius: 6px;
}}

QFrame[revision-badge=true] {{
    border: 3px solid #622675;
    background: {BG_SECONDARY_COLOR};
    padding: 6px;
    border-radius: 12px;
}}

QFrame[large-rounded=true] {{
    border: 1px solid lightgrey;
    border-radius: 15px;
}}

QDialog[relaxed-white-bg] {{
    background-color: {BG_SECONDARY_COLOR};
}}

QToolBox::tab[conflict-selector=true] {{
    background: #f3a712;
    border-radius: 5px;
    color: black;
    font: italic;
}}

QToolBox::tab:selected[conflict-selector=true] {{
    font: bold;
    color: black;
}}

QToolBox[conflict-selector=true] {{
    background-color: white;
}}
        
QScrollArea[transparent=true] {{
    border: 0px;
    background-color: rgba(0, 0, 0, 0);
}}

QScrollArea[relaxed-white-bg=true] {{
    background-color: {BG_SECONDARY_COLOR};
}}

TaskWidget {{
    background-color: {BG_SECONDARY_COLOR};
    border: 1px solid lightGrey;
    border-radius: 6px;
}}

QSplitter::handle:horizontal {{
    width: 20px;
    border: 0px;
    background-color: rgba(0, 0, 0, 0);
}}

QSplitter[framed=true]::handle:horizontal {{
    border-left: 1px solid grey;
}}

QSplitter::handle:horizontal:hover {{
    border-left: 2px dashed #4B0763;
}}

QSplitter::handle:horizontal:pressed {{
    border-left: 2px solid #4B0763;
}}

'''


def apply_color(wdg: QWidget, color: Union[str, QColor, Qt.GlobalColor]):
    if isinstance(color, QColor):
        color = color.name()
    wdg.setStyleSheet(f'color: {{color}}')


def apply_bg_image(wdg: QWidget, resource_url: str):
    wdg.setStyleSheet(f'.QWidget[bg-image=true] {{background-image: url({resource_url});}}')


def apply_border_image(wdg: QWidget, resource_url: str):
    wdg.setStyleSheet(
        f'.QWidget[border-image=true] {{border-image: url({resource_url}) 0 0 0 0 stretch stretch;}}')


def apply_white_menu(menu: MenuWidget):
    menu.setStyleSheet(f'''
                        MenuWidget {{
                            background-color: {{RELAXED_WHITE_COLOR}};
                        }}
                        .QFrame {{
                            background-color: {{RELAXED_WHITE_COLOR}};
                            padding-left: 2px;
                            padding-right: 2px;
                            border-radius: 5px;
                        }}
                        MenuItemWidget:hover {{
                            background-color: #F0E6F4;
                        }}
                        MenuItemWidget[pressed=true] {{
                            background-color: #DCDCDC;
                        }}
                        SubmenuWidget:hover {{
                            background-color: #F0E6F4;
                        }}
                        SubmenuWidget[pressed=true] {{
                            background-color: #DCDCDC;
                        }}
                        ''')
