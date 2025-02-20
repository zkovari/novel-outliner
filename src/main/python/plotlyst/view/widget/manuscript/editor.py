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
import math
from functools import partial
from typing import Optional, List

from PyQt6 import QtGui
from PyQt6.QtCore import pyqtSignal, QTextBoundaryFinder, Qt, QSize, QTimer, QEvent
from PyQt6.QtGui import QFont, QResizeEvent, QShowEvent, QTextCursor, QTextCharFormat, QSyntaxHighlighter, QColor, \
    QTextBlock, QFocusEvent
from PyQt6.QtWidgets import QWidget, QApplication, QTextEdit, QLineEdit, QToolButton, QFrame, QPushButton
from overrides import overrides
from qthandy import vbox, clear_layout, vspacer, margins, transparent, gc, hbox, italic, translucent, sp, spacer, \
    decr_font, retain_when_hidden
from qthandy.filter import OpacityEventFilter
from qttextedit import remove_font, TextBlockState, DashInsertionMode, AutoCapitalizationMode
from qttextedit.ops import Heading1Operation, Heading2Operation, Heading3Operation, InsertListOperation, \
    InsertNumberedListOperation, BoldOperation, ItalicOperation, UnderlineOperation, StrikethroughOperation, \
    AlignLeftOperation, AlignCenterOperation, AlignRightOperation

from plotlyst.common import RELAXED_WHITE_COLOR, DEFAULT_MANUSCRIPT_LINE_SPACE, DEFAULT_MANUSCRIPT_INDENT, \
    PLACEHOLDER_TEXT_COLOR, PLOTLYST_TERTIARY_COLOR
from plotlyst.core.client import json_client
from plotlyst.core.domain import DocumentProgress, Novel, Scene, TextStatistics, DocumentStatistics, FontSettings
from plotlyst.env import app_env
from plotlyst.service.manuscript import daily_progress, daily_overall_progress
from plotlyst.service.persistence import RepositoryPersistenceManager
from plotlyst.view.common import push_btn, tool_btn, fade_in, fade
from plotlyst.view.icons import IconRegistry
from plotlyst.view.style.text import apply_text_color
from plotlyst.view.style.theme import BG_DARK_COLOR
from plotlyst.view.widget.display import WordsDisplay
from plotlyst.view.widget.input import BasePopupTextEditorToolbar, TextEditBase, GrammarHighlighter, \
    GrammarHighlightStyle
from plotlyst.view.widget.manuscript.settings import ManuscriptEditorSettingsWidget


class DistFreeDisplayBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        hbox(self, 4, 6)
        margins(self, left=15, right=15)
        self.setStyleSheet(f'QWidget {{background-color: {BG_DARK_COLOR};}}')
        sp(self).v_max()

        self.btnExitDistFreeMode = tool_btn(IconRegistry.from_name('mdi.arrow-collapse', RELAXED_WHITE_COLOR),
                                            transparent_=True, tooltip='Exit distraction-free mode')
        self.btnExitDistFreeMode.installEventFilter(OpacityEventFilter(self.btnExitDistFreeMode, leaveOpacity=0.8))
        retain_when_hidden(self.btnExitDistFreeMode)

        self.layout().addWidget(self.btnExitDistFreeMode, alignment=Qt.AlignmentFlag.AlignRight)

    def activate(self):
        self.btnExitDistFreeMode.setVisible(True)
        QTimer.singleShot(5000, self._hideItems)

    @overrides
    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        if not self.btnExitDistFreeMode.isVisible():
            fade_in(self.btnExitDistFreeMode)

    @overrides
    def leaveEvent(self, event: QEvent) -> None:
        self.btnExitDistFreeMode.setHidden(True)

    def _hideItems(self):
        if not self.underMouse():
            self.btnExitDistFreeMode.setHidden(True)


class DistFreeControlsBar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        hbox(self, 4, 6)
        margins(self, left=15, right=15)
        self.setStyleSheet(f'QWidget {{background-color: {BG_DARK_COLOR};}}')
        sp(self).v_max()
        self.lblWords: Optional[WordsDisplay] = None

        self.btnFocus = self._initButton('mdi.credit-card', 'Highlight')
        self.btnTypewriterMode = self._initButton('mdi.typewriter', 'Centered')
        self.btnWordCount = self._initButton('mdi6.counter', 'Word count')
        self.btnWordCount.clicked.connect(self._wordCountClicked)

        self.layout().addWidget(self.btnFocus)
        self.layout().addWidget(self.btnTypewriterMode)
        self.layout().addWidget(self.btnWordCount)
        self.layout().addWidget(spacer())

    def activate(self):
        self.btnFocus.setVisible(True)
        self.btnTypewriterMode.setVisible(True)
        self.btnWordCount.setVisible(True)
        QTimer.singleShot(5000, self._hideItems)

    @overrides
    def enterEvent(self, event: QtGui.QEnterEvent) -> None:
        if not self.btnFocus.isVisible():
            fade_in(self.btnFocus)
            fade_in(self.btnTypewriterMode)
            fade_in(self.btnWordCount)

    @overrides
    def leaveEvent(self, event: QEvent) -> None:
        self.btnFocus.setHidden(True)
        self.btnTypewriterMode.setHidden(True)
        self.btnWordCount.setHidden(True)

    def setWordDisplay(self, words: WordsDisplay):
        words.setNightModeEnabled(True)
        self.lblWords = words
        self.layout().addWidget(self.lblWords)
        self.lblWords.setVisible(self.btnWordCount.isChecked())

    def _hideItems(self):
        if not self.underMouse():
            self.btnFocus.setHidden(True)
            self.btnTypewriterMode.setHidden(True)
            self.btnWordCount.setHidden(True)

    def _wordCountClicked(self, checked: bool):
        if self.lblWords:
            fade(self.lblWords, checked)

    def _initButton(self, icon: str, text: str) -> QToolButton:
        btn = tool_btn(
            IconRegistry.from_name(icon, 'lightgrey', color_on=PLOTLYST_TERTIARY_COLOR), checkable=True,
            properties=[
                'base', 'dark-mode-toggle'
            ])
        btn.setIconSize(QSize(22, 22))
        decr_font(btn, 2)
        btn.setText(text)
        retain_when_hidden(btn)
        btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)

        return btn


class SentenceHighlighter(QSyntaxHighlighter):
    DEFAULT_FOREGROUND_COLOR = '#dee2e6'

    def __init__(self, textedit: QTextEdit):
        super(SentenceHighlighter, self).__init__(textedit.document())
        self._editor = textedit
        self._sentenceEnabled: bool = False

        self._hidden_format = QTextCharFormat()
        self._hidden_format.setForeground(QColor(self.DEFAULT_FOREGROUND_COLOR))

        self._visible_format = QTextCharFormat()
        self._visible_format.setForeground(QColor(RELAXED_WHITE_COLOR))

        self._prevBlock: Optional[QTextBlock] = None
        self._editor.cursorPositionChanged.connect(self.rehighlight)

    def sentenceHighlightEnabled(self) -> bool:
        return self._sentenceEnabled

    def setSentenceHighlightEnabled(self, enabled: bool):
        self._sentenceEnabled = enabled
        self._hidden_format.setForeground(QColor('#38414A' if enabled else self.DEFAULT_FOREGROUND_COLOR))
        self.rehighlight()

    @overrides
    def highlightBlock(self, text: str) -> None:
        self.setFormat(0, len(text), self._hidden_format)
        if self._sentenceEnabled and self._editor.hasFocus() and self._editor.textCursor().block() == self.currentBlock():
            text = self._editor.textCursor().block().text()
            finder = QTextBoundaryFinder(QTextBoundaryFinder.BoundaryType.Sentence, text)
            pos = self._editor.textCursor().positionInBlock()
            boundary = finder.toNextBoundary()
            prev_boundary = 0
            while -1 < boundary < pos:
                prev_boundary = boundary
                boundary = finder.toNextBoundary()

            self.setFormat(prev_boundary, boundary - prev_boundary, self._visible_format)


class ManuscriptPopupTextEditorToolbar(BasePopupTextEditorToolbar):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setProperty('rounded', True)
        self.setProperty('relaxed-white-bg', True)
        margins(self, 5, 5, 5, 5)

        self.addTextEditorOperation(BoldOperation)
        self.addTextEditorOperation(ItalicOperation)
        self.addTextEditorOperation(UnderlineOperation)
        self.addTextEditorOperation(StrikethroughOperation)
        self.addSeparator()
        self.addTextEditorOperation(AlignLeftOperation)
        self.addTextEditorOperation(AlignCenterOperation)
        self.addTextEditorOperation(AlignRightOperation)
        self.addSeparator()
        self.addTextEditorOperation(InsertListOperation)
        self.addTextEditorOperation(InsertNumberedListOperation)


class ManuscriptTextEdit(TextEditBase):
    sceneSeparatorClicked = pyqtSignal(Scene)

    def __init__(self, parent=None):
        super(ManuscriptTextEdit, self).__init__(parent)
        self._pasteAsOriginalEnabled = False
        self._resizedOnShow: bool = False
        self._minHeight = 40
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setTabChangesFocus(True)

        self.highlighter = GrammarHighlighter(self.document(), checkEnabled=False,
                                              highlightStyle=GrammarHighlightStyle.BACKGOUND)

        self._sentenceHighlighter: Optional[SentenceHighlighter] = None

        toolbar = ManuscriptPopupTextEditorToolbar()
        toolbar.activate(self)
        self.setPopupWidget(toolbar)

        # self._sceneSepBlockFormat = QTextBlockFormat()
        # self._sceneSepBlockFormat.setTextIndent(40)
        # self._sceneSepBlockFormat.setTopMargin(20)
        # self._sceneSepBlockFormat.setBottomMargin(20)

        # self._sceneTextObject = SceneSeparatorTextObject(self)
        # self.document().documentLayout().registerHandler(SceneSeparatorTextFormat, self._sceneTextObject)

        self._setDefaultStyleSheet()
        self.setCommandOperations([Heading1Operation, Heading2Operation, Heading3Operation, InsertListOperation,
                                   InsertNumberedListOperation])

        self.textChanged.connect(self.resizeToContent)

    @overrides
    def setFocus(self) -> None:
        super().setFocus()
        self.moveCursor(QTextCursor.MoveOperation.Start)

    @overrides
    def focusOutEvent(self, event: QFocusEvent):
        super().focusOutEvent(event)
        if self._sentenceHighlighter and self._sentenceHighlighter.sentenceHighlightEnabled():
            self._sentenceHighlighter.rehighlight()

    @overrides
    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        cursor: QTextCursor = self.textCursor()
        if cursor.atBlockEnd() and event.key() == Qt.Key.Key_Space:
            cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor)
            if cursor.selectedText() == ' ':
                self.textCursor().deletePreviousChar()
                self.textCursor().insertText('.')
        super(ManuscriptTextEdit, self).keyPressEvent(event)

    # @overrides
    # def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
    #     anchor = self.anchorAt(event.pos())
    #     if anchor and anchor.startswith(SceneSeparatorTextFormatPrefix):
    #         if QApplication.overrideCursor() is None:
    #             QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)
    #         synopsis = self._sceneTextObject.sceneSynopsis(anchor.replace(SceneSeparatorTextFormatPrefix, ''))
    #         self.setToolTip(synopsis)
    #         return
    #     else:
    #         QApplication.restoreOverrideCursor()
    #         self.setToolTip('')
    #     super(ManuscriptTextEdit, self).mouseMoveEvent(event)

    # @overrides
    # def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
    #     anchor = self.anchorAt(event.pos())
    #     if anchor and anchor.startswith(SceneSeparatorTextFormatPrefix):
    #         scene = self._sceneTextObject.scene(anchor.replace(SceneSeparatorTextFormatPrefix, ''))
    #         if scene:
    #             self.sceneSeparatorClicked.emit(scene)
    #         return
    #
    #     super(ManuscriptTextEdit, self).mouseReleaseEvent(event)

    def setGrammarCheckEnabled(self, enabled: bool):
        self.highlighter.setCheckEnabled(enabled)

    def checkGrammar(self):
        self.highlighter.rehighlight()

    def asyncCheckGrammar(self):
        self.highlighter.asyncRehighlight()

    def initSentenceHighlighter(self):
        transparent(self)
        self._sentenceHighlighter = SentenceHighlighter(self)

    def clearSentenceHighlighter(self):
        if self._sentenceHighlighter is not None:
            gc(self._sentenceHighlighter)
            self._sentenceHighlighter = None

        self._setDefaultStyleSheet()

    def setSentenceHighlighterEnabled(self, enabled: bool):
        self._sentenceHighlighter.setSentenceHighlightEnabled(enabled)

    def setScene(self, scene: Scene):
        # self._sceneTextObject.setScenes([scene])

        self._addScene(scene)
        self.setUneditableBlocksEnabled(False)
        self.document().clearUndoRedoStacks()
        self.resizeToContent()

    # def setScenes(self, scenes: List[Scene]):
    #     def sceneCharFormat(scene: Scene) -> QTextCharFormat:
    #         sceneSepCharFormat = QTextCharFormat()
    #         sceneSepCharFormat.setObjectType(SceneSeparatorTextFormat)
    #         sceneSepCharFormat.setToolTip(scene.synopsis)
    #         sceneSepCharFormat.setAnchor(True)
    #         sceneSepCharFormat.setAnchorHref(f'{SceneSeparatorTextFormatPrefix}{scene.id}')
    #
    #         return sceneSepCharFormat
    #
    #     self.setUneditableBlocksEnabled(True)
    #     self._sceneTextObject.setScenes(scenes)
    #
    #     for i, scene in enumerate(scenes):
    #         self.textCursor().insertBlock(self._sceneSepBlockFormat)
    #         self.textCursor().insertText(f'{OBJECT_REPLACEMENT_CHARACTER}', sceneCharFormat(scene))
    #         self.textCursor().block().setUserState(TextBlockState.UNEDITABLE.value)
    #         self.insertNewBlock()
    #         self._addScene(scene)
    #
    #     self._deleteBlock(0, force=True)
    #
    #     self.document().clearUndoRedoStacks()
    #     self.resizeToContent()

    # def insertNewBlock(self):
    #     self.textCursor().insertBlock(self._defaultBlockFormat, QTextCharFormat())

    @overrides
    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        if not self._resizedOnShow:
            self.resizeToContent()
            self._resizedOnShow = True

    @overrides
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)
        if self._resizedOnShow:
            self.resizeToContent()

    def resizeToContent(self):
        padding = self.contentsMargins().top() + self.contentsMargins().bottom() + 2 * self.document().documentMargin()
        size = self.document().size()
        self.setFixedHeight(max(self._minHeight, math.ceil(size.height() + padding)))

    def _addScene(self, scene: Scene):
        if not scene.manuscript.loaded:
            json_client.load_document(app_env.novel, scene.manuscript)

        first_scene_block = self.textCursor().block()
        self.textCursor().insertHtml(remove_font(scene.manuscript.content))
        if first_scene_block.userState() == TextBlockState.UNEDITABLE.value:
            first_scene_block.setUserState(-1)

    def _transparent(self):
        border = 0
        self.setStyleSheet(f'border-top: {border}px dashed {RELAXED_WHITE_COLOR}; background-color: rgba(0, 0, 0, 0);')

    def _setDefaultStyleSheet(self):
        self.setStyleSheet(
            f'ManuscriptTextEdit {{background-color: {RELAXED_WHITE_COLOR};}}')


class ManuscriptEditor(QWidget):
    textChanged = pyqtSignal()
    progressChanged = pyqtSignal(DocumentProgress)
    sceneTitleChanged = pyqtSignal(Scene)
    sceneSeparatorClicked = pyqtSignal(Scene)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._novel: Optional[Novel] = None
        self._margins: int = 30
        self._scenes: List[ManuscriptTextEdit] = []
        self._sceneLabels: List[QPushButton] = []
        self._scene: Optional[Scene] = None
        self._font = self.defaultFont()
        self._characterWidth: int = 40
        self._settings: Optional[ManuscriptEditorSettingsWidget] = None

        vbox(self, 0, 0)

        self.textTitle = QLineEdit()
        self.textTitle.setProperty('transparent', True)
        self.textTitle.setFrame(False)
        self.textTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        apply_text_color(self.textTitle, QColor(PLACEHOLDER_TEXT_COLOR))
        self.textTitle.textEdited.connect(self._titleEdited)

        self.wdgTitle = QWidget()
        hbox(self.wdgTitle).addWidget(self.textTitle)
        margins(self.wdgTitle, bottom=15)

        # self.divider = DividerWidget()
        # effect = QGraphicsColorizeEffect(self.divider)
        # effect.setColor(QColor(PLACEHOLDER_TEXT_COLOR))
        # self.divider.setGraphicsEffect(effect)
        # self._textTitle.returnPressed.connect(self.textEdit.setFocus)
        # self._textTitle.textEdited.connect(self._titleChanged)

        self.wdgEditor = QWidget()
        vbox(self.wdgEditor, 0, 0)
        margins(self.wdgEditor, left=15, top=40, bottom=40, right=15)

        self.layout().addWidget(self.wdgTitle)
        self.layout().addWidget(self.wdgEditor)

        self.repo = RepositoryPersistenceManager.instance()

    @overrides
    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if self._maxContentWidth > 0:
            self._resizeToCharacterWidth()

    def defaultFont(self) -> QFont:
        if app_env.is_linux():
            return QFont('Palatino', 16)
        elif app_env.is_mac():
            return QFont('Palatino', 18)
        elif app_env.is_windows():
            return QFont('Georgia', 18)
        else:
            font = QApplication.font()
            font.setPointSize(16)
            return font

    def setNovel(self, novel: Novel):
        self._novel = novel

        if app_env.platform() in self._novel.prefs.manuscript.font.keys():
            fontSettings = self._getFontSettings()
            if fontSettings.family:
                self._font.setFamily(fontSettings.family)
            if fontSettings.font_size:
                self._font.setPointSize(fontSettings.font_size)
            if fontSettings.text_width:
                self.setCharacterWidth(fontSettings.text_width)
        else:
            self.setCharacterWidth(60)

        title_font = self.textTitle.font()
        title_font.setBold(True)
        title_font.setPointSize(32)
        title_font.setFamily(self._font.family())
        self.textTitle.setFont(title_font)

    def manuscriptFont(self) -> QFont:
        return self._font

    def setManuscriptFontPointSize(self, value: int):
        self._font.setPointSize(value)
        self._setFontForTextEdits()

    def setManuscriptFontFamily(self, family: str):
        self._font.setFamily(family)
        self._setFontForTextEdits()

    def characterWidth(self) -> int:
        return self._characterWidth

    def setCharacterWidth(self, width: int):
        self._characterWidth = width
        metrics = QtGui.QFontMetricsF(self.font())
        self._maxContentWidth = metrics.boundingRect('M' * self._characterWidth).width()
        self._resizeToCharacterWidth()

    def clear(self):
        self._scenes.clear()
        self._sceneLabels.clear()
        self._scene = None
        clear_layout(self.wdgEditor)

    def setScene(self, scene: Scene):
        self.clear()
        self._scene = scene

        self.textTitle.setText(self._scene.title)
        self.textTitle.setPlaceholderText('Scene title')
        self.textTitle.setReadOnly(False)

        wdg = self._initTextEdit(scene)
        self.wdgEditor.layout().addWidget(wdg)
        self.wdgEditor.layout().addWidget(vspacer())
        wdg.setFocus()

    def setChapterScenes(self, scenes: List[Scene], title: str):
        self.clear()

        self.textTitle.setText(title)
        self.textTitle.setPlaceholderText('Chapter')
        self.textTitle.setReadOnly(True)

        for scene in scenes:
            wdg = self._initTextEdit(scene)

            sceneLbl = push_btn(text=f'~{scene.title if scene.title else "Scene"}~', transparent_=True)
            sceneLbl.clicked.connect(partial(self.sceneSeparatorClicked.emit, scene))
            self._sceneLabels.append(sceneLbl)
            italic(sceneLbl)
            translucent(sceneLbl)
            self.wdgEditor.layout().addWidget(sceneLbl, alignment=Qt.AlignmentFlag.AlignCenter)
            self.wdgEditor.layout().addWidget(wdg)

        self.wdgEditor.layout().addWidget(vspacer())
        self._scenes[0].setFocus()

    def setNightMode(self, mode: bool):
        for lbl in self._sceneLabels:
            if mode:
                lbl.setStyleSheet(f'color: {RELAXED_WHITE_COLOR}; border: 0px; background-color: rgba(0, 0, 0, 0);')
            else:
                transparent(lbl)

    def attachSettingsWidget(self, settings: ManuscriptEditorSettingsWidget):
        self._settings = settings
        self._settings.smartTypingSettings.dashChanged.connect(self._dashInsertionChanged)
        self._settings.smartTypingSettings.capitalizationChanged.connect(self._capitalizationChanged)

        self._settings.fontSettings.sizeSetting.attach(self)
        self._settings.fontSettings.widthSetting.attach(self)
        self._settings.fontSettings.fontSetting.attach(self)

        self._settings.fontSettings.sizeSetting.sizeChanged.connect(self._fontSizeChanged)
        self._settings.fontSettings.widthSetting.widthChanged.connect(self._textWidthChanged)
        self._settings.fontSettings.fontSetting.fontSelected.connect(self._fontChanged)

    def statistics(self) -> TextStatistics:
        overall_stats = TextStatistics(0)
        if self.hasScenes():
            for editor in self._scenes:
                overall_stats.word_count += editor.statistics().word_count

        return overall_stats

    def asyncCheckGrammar(self):
        for textedit in self._scenes:
            textedit.setGrammarCheckEnabled(True)
            textedit.asyncCheckGrammar()

    def resetGrammarChecking(self):
        for textedit in self._scenes:
            textedit.setGrammarCheckEnabled(False)
            textedit.checkGrammar()

    def initSentenceHighlighter(self):
        for textedit in self._scenes:
            textedit.initSentenceHighlighter()

    def setSentenceHighlighterEnabled(self, enabled: bool):
        for textedit in self._scenes:
            textedit.setSentenceHighlighterEnabled(enabled)

    def clearSentenceHighlighter(self):
        for textedit in self._scenes:
            textedit.clearSentenceHighlighter()

    def hasScenes(self) -> bool:
        return len(self._scenes) > 0

    def _textChanged(self, textedit: ManuscriptTextEdit, scene: Scene):
        if scene.manuscript.statistics is None:
            scene.manuscript.statistics = DocumentStatistics()

        wc = textedit.statistics().word_count
        updated_progress = self._updateProgress(scene, wc)

        scene.manuscript.content = textedit.toHtml()
        self.repo.update_doc(app_env.novel, scene.manuscript)
        if updated_progress:
            self.repo.update_scene(scene)
            self.repo.update_novel(self._novel)

        self.textChanged.emit()

    def _updateProgress(self, scene: Scene, wc: int) -> bool:
        if scene.manuscript.statistics.wc == wc:
            return False

        diff = wc - scene.manuscript.statistics.wc
        progress: DocumentProgress = daily_progress(scene)
        overall_progress = daily_overall_progress(self._novel)
        if diff > 0:
            progress.added += diff
            overall_progress.added += diff
        else:
            progress.removed += abs(diff)
            overall_progress.removed += abs(diff)
        self.progressChanged.emit(overall_progress)
        scene.manuscript.statistics.wc = wc

        return True

    def _initTextEdit(self, scene: Scene) -> ManuscriptTextEdit:
        _textedit = ManuscriptTextEdit()
        _textedit.setFont(self._font)
        _textedit.setDashInsertionMode(self._novel.prefs.manuscript.dash)
        _textedit.setAutoCapitalizationMode(self._novel.prefs.manuscript.capitalization)
        transparent(_textedit)

        # _textedit.zoomIn(int(_textedit.font().pointSize() * 0.25))
        _textedit.setBlockFormat(DEFAULT_MANUSCRIPT_LINE_SPACE, textIndent=DEFAULT_MANUSCRIPT_INDENT)
        _textedit.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoNone)
        # _textedit.selectionChanged.connect(self.selectionChanged.emit)
        _textedit.setProperty('borderless', True)

        _textedit.setPlaceholderText('Write this scene...')
        _textedit.setSidebarEnabled(False)
        _textedit.setReadOnly(self._novel.is_readonly())
        # _textedit.setViewportMargins(25, 0, 0, 0)
        _textedit.setDocumentMargin(0)

        _textedit.setScene(scene)
        _textedit.textChanged.connect(partial(self._textChanged, _textedit, scene))
        self._scenes.append(_textedit)

        return _textedit

    def _setFontForTextEdits(self):
        for textedit in self._scenes:
            textedit.setFont(self._font)
            textedit.resizeToContent()

    def _getFontSettings(self) -> FontSettings:
        if app_env.platform() not in self._novel.prefs.manuscript.font.keys():
            self._novel.prefs.manuscript.font[app_env.platform()] = FontSettings()
        return self._novel.prefs.manuscript.font[app_env.platform()]

    def _resizeToCharacterWidth(self):
        # print(f'max {self._maxContentWidth} width {self.width()}')
        if 0 < self._maxContentWidth < self.width():
            margin = self.width() - self._maxContentWidth
        else:
            margin = 0

        margin = int(margin // 2)
        # print(margin)
        margins(self, left=margin, right=margin)
        # current_margins: QMargins = self.viewportMargins()
        # self.setViewportMargins(margin, current_margins.top(), margin, current_margins.bottom())
        # self.resizeToContent()

    def _dashInsertionChanged(self, mode: DashInsertionMode):
        for textedit in self._scenes:
            textedit.setDashInsertionMode(mode)
        self._novel.prefs.manuscript.dash = mode
        self.repo.update_novel(self._novel)

    def _capitalizationChanged(self, mode: AutoCapitalizationMode):
        for textedit in self._scenes:
            textedit.setAutoCapitalizationMode(mode)
        self._novel.prefs.manuscript.capitalization = mode
        self.repo.update_novel(self._novel)

    def _fontSizeChanged(self, size: int):
        fontSettings = self._getFontSettings()
        fontSettings.font_size = size
        self.repo.update_novel(self._novel)

    def _textWidthChanged(self, width: int):
        fontSettings = self._getFontSettings()
        fontSettings.text_width = width
        self.repo.update_novel(self._novel)

    def _fontChanged(self, family: str):
        fontSettings = self._getFontSettings()
        fontSettings.family = family

        titleFont = self.textTitle.font()
        titleFont.setFamily(family)
        self.textTitle.setFont(titleFont)

        self.repo.update_novel(self._novel)

    def _titleEdited(self, title: str):
        if self._scene:
            self._scene.title = title
            self.sceneTitleChanged.emit(self._scene)
