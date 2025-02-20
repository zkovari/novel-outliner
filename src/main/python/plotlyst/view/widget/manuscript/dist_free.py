"""
Plotlyst
Copyright (C) 2021-2025  Zsolt Kovari

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
from typing import Optional

import qtanim
from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSignal, QTimer, QObject, QEvent, Qt
from PyQt6.QtGui import QMouseEvent, QScreen
from PyQt6.QtWidgets import QWidget, QApplication
from overrides import overrides
from qthandy import decr_font, clear_layout

from plotlyst.common import PLOTLYST_TERTIARY_COLOR
from plotlyst.core.sprint import TimerModel
from plotlyst.view.generated.distraction_free_manuscript_editor_ui import Ui_DistractionFreeManuscriptEditor
from plotlyst.view.icons import IconRegistry
from plotlyst.view.widget.display import WordsDisplay
from plotlyst.view.widget.manuscript import SprintWidget
from plotlyst.view.widget.manuscript.editor import ManuscriptEditor


class DistractionFreeManuscriptEditor(QWidget, Ui_DistractionFreeManuscriptEditor):
    exitRequested = pyqtSignal()

    def __init__(self, parent=None):
        super(DistractionFreeManuscriptEditor, self).__init__(parent)
        self.setupUi(self)
        self.editor: Optional[ManuscriptEditor] = None
        self.lblWords: Optional[WordsDisplay] = None
        self._firstInit: bool = True

        self.wdgSprint = SprintWidget(self)
        self.wdgSprint.setCompactMode(True)
        self.wdgHeader.layout().insertWidget(0, self.wdgSprint, alignment=Qt.AlignmentFlag.AlignLeft)

        self.wdgDistractionFreeEditor.installEventFilter(self)
        self.wdgBottom.installEventFilter(self)
        self.btnReturn.setIcon(IconRegistry.from_name('mdi.arrow-collapse', 'white'))
        self.btnReturn.clicked.connect(self.exitRequested.emit)
        self.btnFocus.setIcon(IconRegistry.from_name('mdi.credit-card', 'lightgrey', color_on=PLOTLYST_TERTIARY_COLOR))
        self.btnFocus.toggled.connect(self._toggle_manuscript_focus)
        self.btnTypewriterMode.setIcon(
            IconRegistry.from_name('mdi.typewriter', 'lightgrey', color_on=PLOTLYST_TERTIARY_COLOR))
        self.btnTypewriterMode.toggled.connect(self._toggle_typewriter_mode)
        self.btnWordCount.setIcon(IconRegistry.from_name('mdi6.counter', 'lightgrey', color_on=PLOTLYST_TERTIARY_COLOR))
        self.btnWordCount.clicked.connect(self._wordCountClicked)

        decr_font(self.btnFocus, 2)
        decr_font(self.btnTypewriterMode, 2)
        decr_font(self.btnWordCount, 2)

    def activate(self, editor: ManuscriptEditor, timer: Optional[TimerModel] = None):
        self.editor = editor
        self.editor.installEventFilter(self)
        # editor.setTitleVisible(False)
        clear_layout(self.wdgDistractionFreeEditor.layout())
        if timer and timer.isActive():
            self.wdgSprint.setModel(timer)
            self.wdgSprint.setVisible(True)
        else:
            self.wdgSprint.setHidden(True)
        self.wdgDistractionFreeEditor.layout().addWidget(self.editor)
        self.editor.setFocus()
        # self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.wdgBottom.setVisible(True)
        # self.editor.initSentenceHighlighter()
        if self._firstInit:
            self.btnTypewriterMode.setChecked(True)
            self._firstInit = False
        else:
            self._toggle_manuscript_focus(self.btnFocus.isChecked())
            self._toggle_typewriter_mode(self.btnTypewriterMode.isChecked())

        self._wordCountClicked(self.btnWordCount.isChecked())
        self.setMouseTracking(True)
        self.wdgDistractionFreeEditor.setMouseTracking(True)
        QTimer.singleShot(5000, self._autoHideBottomBar)

    def deactivate(self):
        # self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        # self.editor.setTitleVisible(True)
        self.editor.removeEventFilter(self)
        # self.editor.setMargins(30, 30, 30, 30)
        # self.editor.clearSentenceHighlighter()
        self.editor = None
        self.setMouseTracking(False)
        self.wdgDistractionFreeEditor.setMouseTracking(False)
        if self.lblWords:
            self.lblWords.setNightModeEnabled(False)

    def setWordDisplay(self, words: WordsDisplay):
        words.setNightModeEnabled(True)
        self.lblWords = words
        self.wdgHeader.layout().addWidget(self.lblWords, alignment=Qt.AlignmentFlag.AlignRight)
        self._wordCountClicked(self.btnWordCount.isChecked())

    @overrides
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.wdgBottom and event.type() == QEvent.Type.Leave:
            self.wdgBottom.setHidden(True)
        if event.type() == QEvent.Type.MouseMove and isinstance(event, QMouseEvent):
            if self.wdgBottom.isHidden() and event.pos().y() > self.height() - 25:
                self.wdgBottom.setVisible(True)
        return super().eventFilter(watched, event)

    @overrides
    def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
        if self.wdgBottom.isHidden() and event.pos().y() > self.height() - 15:
            self.wdgBottom.setVisible(True)

    def _wordCountClicked(self, checked: bool):
        if self.lblWords:
            if checked:
                qtanim.fade_in(self.lblWords, 150)
            else:
                qtanim.fade_out(self.lblWords, 150, teardown=lambda: self.lblWords.setGraphicsEffect(None))

    def _toggle_manuscript_focus(self, toggled: bool):
        return
        self.editor.setSentenceHighlighterEnabled(toggled)

    def _toggle_typewriter_mode(self, toggled: bool):
        return
        viewportMargins = self.editor.textEdit.viewportMargins()
        if toggled:
            screen: QScreen = QApplication.screenAt(self.editor.pos())
            viewportMargins.setBottom(screen.size().height() // 2)
        else:
            viewportMargins.setBottom(30)

        self.editor.textEdit.setViewportMargins(viewportMargins.left(), viewportMargins.top(),
                                                viewportMargins.right(), viewportMargins.bottom())
        self.editor.textEdit.ensureCursorVisible()

    def _autoHideBottomBar(self):
        if not self.wdgBottom.underMouse():
            self.wdgBottom.setHidden(True)
