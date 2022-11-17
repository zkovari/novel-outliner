"""
Plotlyst
Copyright (C) 2021-2022  Zsolt Kovari

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
APP_STYLESHEET = '''

* {
    icon-size: 20px;
}

QToolTip {
    border: 0px;
}

QPushButton[base=true] {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #dadbde);
    border: 2px solid #8f8f91;
    border-radius: 6px;
    padding: 2px;
}

QPushButton:hover[base=true] {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #c3c4c7, stop: 1 #f6f7fa);
}

QPushButton:pressed[base=true] {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #d7d8db, stop: 1 #f6f7fa);
    border: 2px solid darkGrey;
}

QPushButton:checked[base=true] {
    background-color: lightgrey;
}

QPushButton:disabled[base=true] {
    opacity: 0.65;
}

QPushButton[positive=true]:!disabled {
    background-color: #4fb477;
    color: #fff;
    font: bold;
}

QPushButton[positive=true]:hover {
    background-color: #27ae60;
}

QPushButton[highlighted=true]:!disabled {
    background-color: #384e77;
    color: #fff;
    font: bold;
}

QPushButton[highlighted=true]:hover {
    background-color: #18314f;
}

QPushButton[deconstructive=true]:!disabled {
    background-color: #e74c3c;
    color: #fff;
    font: bold;
}

QPushButton[deconstructive=true]:hover {
    background-color: #c0392b;
}

QToolButton::menu-indicator {
    width:0px;
}

QToolButton[transparent=true] {
    border: 0px;
    background-color: rgba(0, 0, 0, 0);
}

QToolButton[base=true] {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #f6f7fa, stop: 1 #dadbde);
    border: 1px solid #8f8f91;
    border-radius: 6px;
    padding: 2px;
}

QToolButton:hover[base=true] {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #c3c4c7, stop: 1 #f6f7fa);
}

QToolButton:pressed[base=true] {
    background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                      stop: 0 #d7d8db, stop: 1 #f6f7fa);
}

QToolButton:checked[base=true] {
    background-color: lightgrey;
}

QToolButton:disabled[base=true] {
    opacity: 0.65;
}

QToolButton[transparent=true] {
    border: 0px;
    border-radius: 4px;
}

QToolButton:pressed[transparent=true] {
    border: 1px solid grey
}

QDockWidget::float-button {
    subcontrol-position: top left;
    subcontrol-origin: margin;
    position: absolute;
    top: 0px; left: 4px; bottom: 0px;
    width: 16px;
}

QHeaderView::section {
    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                      stop:0 #2177b0, stop: 0.5 #185b87,
                                      stop: 0.6 #124669, stop:1 #1d608c);
    color: white;
    padding-left: 4px;
    border: 1px solid #6c6c6c;
    border-radius: 6px;
    font-size: 16px;
    font: bold;
}

QToolBar {
    spacing: 1px;
}

QTreeView {
    background-color: rgb(244, 244, 244);
}

QTreeView::branch {
    background-color: rgb(244, 244, 244);
    border: 0px;
}

QTreeView::branch:selected {
    background-color: #D8D5D5;
    border: 0px;
}

QTreeView::branch:hover:!selected {
    background-color: #D8D5D5;
    border: 0px;
}

QTreeView::item:hover:!selected {
    background-color: #D8D5D5;
    border: 0px;
}

QTreeView::item:selected:active {
    background-color: #D8D5D5;
    color: black;
}

QTreeView::item:selected:!active {
    background-color: #D8D5D5;
    color: black;
}

QTabWidget::pane {
    border: 1px solid black;
    background: white;
}

QTabWidget::tab-bar:top {
    top: 1px;
}

QTabWidget::tab-bar:bottom {
    bottom: 1px;
}

QTabWidget::tab-bar:left {
    right: 1px;
}

QTabWidget::tab-bar:right {
    left: 1px;
}

QTabBar::tab {
    border: 1px solid black;
}

QTabBar::tab:selected {
    background: white;
}

QTabBar::tab:!selected {
    background: lightGrey;
}

QTabBar::tab:!selected:hover {
    background: #999;
}

QTabBar::tab:top:!selected {
    margin-top: 3px;
}

QTabBar::tab:bottom:!selected {
    margin-bottom: 3px;
}

QTabBar::tab:top, QTabBar::tab:bottom {
    margin-right: -1px;
    padding: 5px 10px 5px 10px;
}

QTabBar::tab:top:selected {
    border-bottom-color: none;
}

QTabBar::tab:bottom:selected {
    border-top-color: none;
}

QTabBar::tab:top:last, QTabBar::tab:bottom:last,
QTabBar::tab:top:only-one, QTabBar::tab:bottom:only-one {
    margin-right: 0;
}

QTabBar::tab:left:!selected {
    margin-right: 3px;
}

QTabBar::tab:right:!selected {
    margin-left: 3px;
}

QTabBar::tab:left, QTabBar::tab:right {
    min-height: 8ex;
    margin-bottom: -1px;
    padding: 10px 5px 10px 5px;
}

QTabBar::tab:left:selected {
    border-left-color: none;
}

QTabBar::tab:right:selected {
    border-right-color: none;
}

QTabBar::tab:left:last, QTabBar::tab:right:last,
QTabBar::tab:left:only-one, QTabBar::tab:right:only-one {
    margin-bottom: 0;
}

'''
