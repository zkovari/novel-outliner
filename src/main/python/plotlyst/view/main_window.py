"""
Plotlyst
Copyright (C) 2021  Zsolt Kovari

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
import typing
from typing import List

import qtawesome
from PyQt5 import QtGui, QtCore
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QMainWindow, QToolButton, QWidget, QApplication, QWidgetAction, QProxyStyle, \
    QStyle, QStyleOption, QTabBar, QStyleOptionTab
from overrides import overrides

from src.main.python.plotlyst.common import EXIT_CODE_RESTART
from src.main.python.plotlyst.core.client import client
from src.main.python.plotlyst.core.domain import Novel
from src.main.python.plotlyst.event.core import event_log_reporter
from src.main.python.plotlyst.event.handler import EventAuthorizationHandler, EventLogHandler
from src.main.python.plotlyst.view.characters_view import CharactersView
from src.main.python.plotlyst.view.common import EditorCommand, spacer_widget, EditorCommandType, busy
from src.main.python.plotlyst.view.dialog.about import AboutDialog
from src.main.python.plotlyst.view.generated.main_window_ui import Ui_MainWindow
from src.main.python.plotlyst.view.home_view import HomeView
from src.main.python.plotlyst.view.icons import IconRegistry
from src.main.python.plotlyst.view.notes_view import NotesView
from src.main.python.plotlyst.view.novel_view import NovelView
from src.main.python.plotlyst.view.reports_view import ReportsView
from src.main.python.plotlyst.view.scenes_view import ScenesOutlineView, DraftScenesView
from src.main.python.plotlyst.view.tasks_view import TasksWidget
from src.main.python.plotlyst.view.timeline_view import TimelineView


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.resize(1000, 630)
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle('Plotlyst')

        self.novel = client.fetch_novel(1)

        self._init_menubar()
        self._init_toolbar()

        self._tabstyle = TabStyle()
        self.tabWidget.tabBar().setStyle(self._tabstyle)
        self._init_tabs()
        self.tabWidget.currentChanged.connect(self._on_current_tab_changed)

        EventAuthorizationHandler.parent = self
        self.event_log_handler = EventLogHandler(self.statusBar())
        event_log_reporter.info.connect(self.event_log_handler.on_info_event)
        event_log_reporter.warning.connect(self.event_log_handler.on_warning_event)
        event_log_reporter.error.connect(self.event_log_handler.on_error_event)

    def _init_tabs(self):
        self.home_view = HomeView()
        self.novel_view = NovelView(self.novel)
        self.characters_view = CharactersView(self.novel)
        self.scenes_outline_view = ScenesOutlineView(self.novel)
        self.scenes_outline_view.commands_sent.connect(self._on_received_commands)

        self.timeline_view = TimelineView(self.novel)
        self.notes_view = NotesView(self.novel)
        self.reports_view = ReportsView(self.novel)
        self.draft_scenes_view = DraftScenesView(self.novel)

        self.tabWidget.addTab(self.home_view.widget, IconRegistry.home_icon(), '')
        self.tabWidget.addTab(self.novel_view.widget, IconRegistry.book_icon(), '')
        self.tabWidget.addTab(self.characters_view.widget, IconRegistry.character_icon(), '')
        self.tabWidget.addTab(self.scenes_outline_view.widget, IconRegistry.scene_icon(), '')
        self.tabWidget.addTab(self.timeline_view.widget, IconRegistry.timeline_icon(), '')
        self.tabWidget.addTab(self.notes_view.widget, IconRegistry.notes_icon(), '')
        self.tabWidget.addTab(self.reports_view.widget, IconRegistry.reports_icon(), '')
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.home_view.widget), 'Home')
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.novel_view.widget), 'Novel')
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.characters_view.widget), 'Characters')
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.scenes_outline_view.widget), 'Scenes')
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.timeline_view.widget), 'Timeline & events')
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.notes_view.widget), 'Notes')
        self.tabWidget.setTabToolTip(self.tabWidget.indexOf(self.reports_view.widget), 'Reports')
        self.tabWidget.setCurrentWidget(self.scenes_outline_view.widget)

        self.home_view.loadNovel.connect(self._load_new_novel)

    def _init_menubar(self):
        self.actionRestart.setIcon(qtawesome.icon('mdi.restart'))
        self.actionRestart.triggered.connect(lambda: QApplication.instance().exit(EXIT_CODE_RESTART))
        self.actionAbout.triggered.connect(lambda: AboutDialog().exec())

    def _init_toolbar(self):
        tasks_button = QToolButton(self.toolBar)
        tasks_button.setPopupMode(QToolButton.InstantPopup)
        tasks_button.setIcon(IconRegistry.tasks_icon())
        tasks_button.setToolTip('Tasks')
        tasks_action = QWidgetAction(tasks_button)
        self._distribution_widget = TasksWidget(self.novel)
        self._distribution_widget.setMinimumWidth(700)
        self._distribution_widget.setMinimumHeight(400)
        tasks_action.setDefaultWidget(self._distribution_widget)
        tasks_button.addAction(tasks_action)
        self.toolBar.addWidget(spacer_widget(5))
        self.toolBar.addWidget(tasks_button)
        self.toolBar.addWidget(spacer_widget())

    def _on_add(self):
        self._on_character_edition(None)

    def _on_character_creation(self):
        self._on_character_edition(None)

    def _on_current_tab_changed(self, index: int):
        pass

    @busy
    def _load_new_novel(self, novel: Novel):
        if self.novel.id == novel.id:
            return
        self.novel = client.fetch_novel(novel.id)
        self.tabWidget.clear()
        self._init_tabs()

    def _on_received_commands(self, widget: QWidget, commands: List[EditorCommand]):
        for cmd in commands:
            if cmd.type == EditorCommandType.CLOSE_CURRENT_EDITOR:
                index = self.tabWidget.indexOf(widget)
                self.tabWidget.removeTab(index)
            elif cmd.type == EditorCommandType.DISPLAY_CHARACTERS:
                self.tabWidget.setCurrentWidget(self.characters_view.widget)
                self.characters_view.refresh()
            elif cmd.type == EditorCommandType.DISPLAY_SCENES:
                self.tabWidget.setCurrentWidget(self.scenes_tab)
                self.scenes_outline_view.refresh()
            elif cmd.type == EditorCommandType.EDIT_SCENE:
                if cmd.value is not None and cmd.value < len(self.novel.scenes):
                    self._on_scene_edition(self.novel.scenes[cmd.value])
            elif cmd.type == EditorCommandType.UPDATE_SCENE_SEQUENCES:
                for index, scene in enumerate(self.novel.scenes):
                    scene.sequence = index
                client.update_scene_sequences(self.novel)


class TabStyle(QProxyStyle):
    @overrides
    def sizeFromContents(self, type: QStyle.ContentsType, option: QStyleOption, size: QtCore.QSize,
                         widget: QWidget) -> QtCore.QSize:
        size: QSize = super(TabStyle, self).sizeFromContents(type, option, size, widget)
        if type == QStyle.CT_TabBarTab:
            size.transpose()
        return size

    @overrides
    def drawControl(self, element: QStyle.ControlElement, option: QStyleOption, painter: QtGui.QPainter,
                    widget: typing.Optional[QWidget] = ...) -> None:
        if element == QStyle.CE_TabBarTabLabel:
            opt = QStyleOptionTab(option)
            opt.shape = QTabBar.RoundedNorth
            super(TabStyle, self).drawControl(element, opt, painter, widget)
            return
        super(TabStyle, self).drawControl(element, option, painter, widget)
