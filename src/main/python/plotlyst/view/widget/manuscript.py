# """
# Plotlyst
# Copyright (C) 2021-2024  Zsolt Kovari
#
# This file is part of Plotlyst.
#
# Plotlyst is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Plotlyst is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# """
# import datetime
# import math
# from functools import partial
# from typing import Optional, List, Dict
#
# import qtanim
# from PyQt6 import QtGui
# from PyQt6.QtCharts import QChart
# from PyQt6.QtCore import QUrl, pyqtSignal, QTimer, Qt, QTextBoundaryFinder, QObject, QEvent, QSizeF, QRectF, \
#     QRect, QDate, QPoint, QVariantAnimation, QEasingCurve
# from PyQt6.QtGui import QTextDocument, QTextCharFormat, QColor, QTextBlock, QSyntaxHighlighter, QKeyEvent, \
#     QMouseEvent, QTextCursor, QFont, QScreen, QTextFormat, QTextObjectInterface, QPainter, QFontMetrics, QTextOption, \
#     QShowEvent, QIcon, QResizeEvent
# from PyQt6.QtMultimedia import QSoundEffect
# from PyQt6.QtWidgets import QWidget, QTextEdit, QApplication, QLineEdit, QButtonGroup, QCalendarWidget, QTableView, \
#     QPushButton, QToolButton, QWidgetItem, QGraphicsColorizeEffect, QGraphicsTextItem
# from overrides import overrides
# from qthandy import retain_when_hidden, translucent, clear_layout, gc, margins, vbox, bold, vline, decr_font, \
#     underline, transparent, italic, decr_icon, pointy, vspacer, hbox
# from qthandy.filter import OpacityEventFilter
# from qtmenu import MenuWidget, group
# from qttextedit import TextBlockState, remove_font, OBJECT_REPLACEMENT_CHARACTER
# from qttextedit.ops import Heading2Operation, Heading3Operation, InsertListOperation, InsertNumberedListOperation, \
#     Heading1Operation, BoldOperation, ItalicOperation, UnderlineOperation, StrikethroughOperation, \
#     AlignLeftOperation, AlignCenterOperation, AlignRightOperation
# from textstat import textstat
#
# from plotlyst.common import RELAXED_WHITE_COLOR, DEFAULT_MANUSCRIPT_LINE_SPACE, \
#     DEFAULT_MANUSCRIPT_INDENT, PLOTLYST_TERTIARY_COLOR, PLOTLYST_SECONDARY_COLOR, PLOTLYST_MAIN_COLOR
# from plotlyst.core.client import json_client
# from plotlyst.core.domain import Novel, Scene, TextStatistics, DocumentStatistics, DocumentProgress, FontSettings
# from plotlyst.core.sprint import TimerModel
# from plotlyst.core.text import wc, sentence_count, clean_text
# from plotlyst.env import app_env
# from plotlyst.resources import resource_registry
# from plotlyst.service.manuscript import export_manuscript_to_docx, daily_progress, \
#     daily_overall_progress, find_daily_overall_progress
# from plotlyst.service.persistence import RepositoryPersistenceManager
# from plotlyst.view.common import spin, ButtonPressResizeEventFilter, label, push_btn, \
#     tool_btn
# from plotlyst.view.generated.distraction_free_manuscript_editor_ui import \
#     Ui_DistractionFreeManuscriptEditor
# from plotlyst.view.generated.manuscript_lang_setting_ui import Ui_ManuscriptLangSettingWidget
# from plotlyst.view.generated.readability_widget_ui import Ui_ReadabilityWidget
# from plotlyst.view.generated.sprint_widget_ui import Ui_SprintWidget
# from plotlyst.view.generated.timer_setup_widget_ui import Ui_TimerSetupWidget
# from plotlyst.view.icons import IconRegistry
# from plotlyst.view.style.button import apply_button_palette_color
# from plotlyst.view.widget.display import WordsDisplay, IconText, Emoji, ChartView
# from plotlyst.view.widget.input import TextEditBase, GrammarHighlighter, GrammarHighlightStyle, TextEditorBase, \
#     BasePopupTextEditorToolbar
# from plotlyst.view.widget.progress import ProgressChart
#
#
# class TimerSetupWidget(QWidget, Ui_TimerSetupWidget):
#     def __init__(self, parent=None):
#         super(TimerSetupWidget, self).__init__(parent)
#         self.setupUi(self)
#
#     def value(self) -> int:
#         return self.sbTimer.value() * 60
#
#
# class SprintWidget(QWidget, Ui_SprintWidget):
#     def __init__(self, parent=None):
#         super(SprintWidget, self).__init__(parent)
#         self.setupUi(self)
#         self._model = None
#         self._compact: bool = False
#         self.setModel(TimerModel())
#
#         self._toggleState(False)
#         transparent(self.time)
#         transparent(self.btnPause)
#         transparent(self.btnReset)
#
#         self.btnTimer.setIcon(IconRegistry.timer_icon())
#         self.btnPause.installEventFilter(OpacityEventFilter(self.btnPause, leaveOpacity=0.7))
#         self.btnPause.installEventFilter(ButtonPressResizeEventFilter(self.btnPause))
#         self.btnReset.setIcon(IconRegistry.restore_alert_icon('#ED6868'))
#         self.btnReset.installEventFilter(OpacityEventFilter(self.btnReset, leaveOpacity=0.7))
#         self.btnReset.installEventFilter(ButtonPressResizeEventFilter(self.btnReset))
#
#         self._timer_setup = TimerSetupWidget()
#         self._menu = MenuWidget(self.btnTimer)
#         self._menu.addWidget(self._timer_setup)
#
#         self._timer_setup.btnStart.clicked.connect(self.start)
#         self.btnPause.clicked.connect(self._pauseStartTimer)
#         self.btnReset.clicked.connect(self._reset)
#
#         self._effect: Optional[QSoundEffect] = None
#
#     def model(self) -> TimerModel:
#         return self._model
#
#     def setModel(self, model: TimerModel):
#         self._model = model
#         self._model.valueChanged.connect(self._updateTimer)
#         self._model.finished.connect(self._finished)
#         self._toggleState(self._model.isActive())
#
#     def setCompactMode(self, compact: bool):
#         self._compact = compact
#         self._toggleState(self.model().isActive())
#         self.time.setStyleSheet(f'border: 0px; color: {RELAXED_WHITE_COLOR}; background-color: rgba(0,0,0,0);')
#
#     def start(self):
#         self._toggleState(True)
#         self._model.start(self._timer_setup.value())
#         self._updateTimer()
#         self._menu.close()
#
#     def _toggleState(self, running: bool):
#         self.time.setVisible(running)
#         if running:
#             self.btnPause.setChecked(True)
#             self.btnPause.setIcon(IconRegistry.pause_icon(color='grey'))
#         if self._compact:
#             self.btnTimer.setHidden(running)
#             retain_when_hidden(self.btnPause)
#             retain_when_hidden(self.btnReset)
#             self.btnPause.setHidden(True)
#             self.btnReset.setHidden(True)
#         else:
#             self.btnPause.setVisible(running)
#             self.btnReset.setVisible(running)
#
#     def _updateTimer(self):
#         mins, secs = self._model.remainingTime()
#         time = datetime.time(minute=mins, second=secs)
#         self.time.setTime(time)
#
#     def _pauseStartTimer(self, played: bool):
#         self.model().toggle()
#         if played:
#             self.btnPause.setIcon(IconRegistry.pause_icon(color='grey'))
#         else:
#             self.btnPause.setIcon(IconRegistry.play_icon())
#
#     def _reset(self):
#         self.model().stop()
#         self._toggleState(False)
#
#     def _finished(self):
#         if self._effect is None:
#             self._effect = QSoundEffect()
#             self._effect.setSource(QUrl.fromLocalFile(resource_registry.cork))
#             self._effect.setVolume(0.3)
#         self._effect.play()
#
#
# class ManuscriptLanguageSettingWidget(QWidget, Ui_ManuscriptLangSettingWidget):
#     def __init__(self, novel: Novel, parent=None):
#         super().__init__(parent)
#         self.setupUi(self)
#         self.novel = novel
#
#         self.btnArabicIcon.setIcon(IconRegistry.from_name('mdi.abjad-arabic'))
#
#         self.cbEnglish.clicked.connect(partial(self._changed, 'en-US'))
#         self.cbEnglish.setChecked(True)
#         self.cbEnglishBritish.clicked.connect(partial(self._changed, 'en-GB'))
#         self.cbEnglishCanadian.clicked.connect(partial(self._changed, 'en-CA'))
#         self.cbEnglishAustralian.clicked.connect(partial(self._changed, 'en-AU'))
#         self.cbEnglishNewZealand.clicked.connect(partial(self._changed, 'en-NZ'))
#         self.cbEnglishSouthAfrican.clicked.connect(partial(self._changed, 'en-ZA'))
#         self.cbSpanish.clicked.connect(partial(self._changed, 'es'))
#         self.cbPortugese.clicked.connect(partial(self._changed, 'pt-PT'))
#         self.cbPortugeseBrazil.clicked.connect(partial(self._changed, 'pt-BR'))
#         self.cbPortugeseAngola.clicked.connect(partial(self._changed, 'pt-AO'))
#         self.cbPortugeseMozambique.clicked.connect(partial(self._changed, 'pt-MZ'))
#         self.cbFrench.clicked.connect(partial(self._changed, 'fr'))
#         self.cbGerman.clicked.connect(partial(self._changed, 'de-DE'))
#         self.cbGermanAustrian.clicked.connect(partial(self._changed, 'de-AT'))
#         self.cbGermanSwiss.clicked.connect(partial(self._changed, 'de-CH'))
#         self.cbChinese.clicked.connect(partial(self._changed, 'zh-CN'))
#         self.cbArabic.clicked.connect(partial(self._changed, 'ar'))
#         self.cbDanish.clicked.connect(partial(self._changed, 'da-DK'))
#         self.cbDutch.clicked.connect(partial(self._changed, 'nl'))
#         self.cbDutchBelgian.clicked.connect(partial(self._changed, 'nl-BE'))
#         self.cbGreek.clicked.connect(partial(self._changed, 'el-GR'))
#         self.cbIrish.clicked.connect(partial(self._changed, 'ga-IE'))
#         self.cbItalian.clicked.connect(partial(self._changed, 'it'))
#         self.cbJapanese.clicked.connect(partial(self._changed, 'ja-JP'))
#         self.cbNorwegian.clicked.connect(partial(self._changed, 'no'))
#         self.cbPersian.clicked.connect(partial(self._changed, 'fa'))
#         self.cbPolish.clicked.connect(partial(self._changed, 'pl-PL'))
#         self.cbRomanian.clicked.connect(partial(self._changed, 'ro-RO'))
#         self.cbRussian.clicked.connect(partial(self._changed, 'ru-RU'))
#         self.cbSlovak.clicked.connect(partial(self._changed, 'sk-SK'))
#         self.cbSlovenian.clicked.connect(partial(self._changed, 'sl-SI'))
#         self.cbSwedish.clicked.connect(partial(self._changed, 'sv'))
#         self.cbTagalog.clicked.connect(partial(self._changed, 'tl-PH'))
#         self.cbUkrainian.clicked.connect(partial(self._changed, 'uk-UA'))
#
#     def _changed(self, lang: str, checked: bool):
#         if not checked:
#             return
#         self.novel.lang_settings.lang = lang
#
#
# class SentenceHighlighter(QSyntaxHighlighter):
#     DEFAULT_FOREGROUND_COLOR = '#dee2e6'
#
#     def __init__(self, textedit: QTextEdit):
#         super(SentenceHighlighter, self).__init__(textedit.document())
#         self._editor = textedit
#         self._sentenceEnabled: bool = False
#
#         self._hidden_format = QTextCharFormat()
#         self._hidden_format.setForeground(QColor(self.DEFAULT_FOREGROUND_COLOR))
#
#         self._visible_format = QTextCharFormat()
#         self._visible_format.setForeground(QColor(RELAXED_WHITE_COLOR))
#
#         self._prevBlock: Optional[QTextBlock] = None
#         self._editor.cursorPositionChanged.connect(self.rehighlight)
#
#     def setSentenceHighlightEnabled(self, enabled: bool):
#         self._sentenceEnabled = enabled
#         self._hidden_format.setForeground(QColor('#38414A' if enabled else self.DEFAULT_FOREGROUND_COLOR))
#         self.rehighlight()
#
#     @overrides
#     def highlightBlock(self, text: str) -> None:
#         self.setFormat(0, len(text), self._hidden_format)
#         if self._sentenceEnabled and self._editor.textCursor().block() == self.currentBlock():
#             text = self._editor.textCursor().block().text()
#             finder = QTextBoundaryFinder(QTextBoundaryFinder.BoundaryType.Sentence, text)
#             pos = self._editor.textCursor().positionInBlock()
#             boundary = finder.toNextBoundary()
#             prev_boundary = 0
#             while -1 < boundary < pos:
#                 prev_boundary = boundary
#                 boundary = finder.toNextBoundary()
#
#             self.setFormat(prev_boundary, boundary - prev_boundary, self._visible_format)
#
#
# # class NightModeHighlighter(QSyntaxHighlighter):
# #     def __init__(self, textedit: QTextEdit):
# #         super().__init__(textedit.document())
# #
# #         self._nightFormat = QTextCharFormat()
# #         self._nightFormat.setForeground(QColor(RELAXED_WHITE_COLOR))
# #
# #     @overrides
# #     def highlightBlock(self, text: str) -> None:
# #         self.setFormat(0, len(text), self._nightFormat)
#
#
# # class WordTagHighlighter(QSyntaxHighlighter):
# #     def __init__(self, textedit: QTextEdit):
# #         super().__init__(textedit.document())
# #
# #         self._adverbFormat = QTextCharFormat()
# #         self._adverbFormat.setBackground(QColor('#0a9396'))
# #         self.tokenizer = WhitespaceTokenizer()
# #
# #     @overrides
# #     def highlightBlock(self, text: str) -> None:
# #         span_generator = self.tokenizer.span_tokenize(text)
# #         spans = [x for x in span_generator]
# #         tokens = self.tokenizer.tokenize(text)
# #         tags = nltk.pos_tag(tokens)
# #
# #         for i, pos_tag in enumerate(tags):
# #             if pos_tag[1] == 'RB':
# #                 if len(spans) > i:
# #                     self.setFormat(spans[i][0], spans[i][1] - spans[i][0], self._adverbFormat)
#
#
# class ManuscriptPopupTextEditorToolbar(BasePopupTextEditorToolbar):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self.setProperty('rounded', True)
#         self.setProperty('relaxed-white-bg', True)
#         margins(self, 5, 5, 5, 5)
#
#         self.addTextEditorOperation(BoldOperation)
#         self.addTextEditorOperation(ItalicOperation)
#         self.addTextEditorOperation(UnderlineOperation)
#         self.addTextEditorOperation(StrikethroughOperation)
#         self.addSeparator()
#         self.addTextEditorOperation(AlignLeftOperation)
#         self.addTextEditorOperation(AlignCenterOperation)
#         self.addTextEditorOperation(AlignRightOperation)
#         self.addSeparator()
#         self.addTextEditorOperation(InsertListOperation)
#         self.addTextEditorOperation(InsertNumberedListOperation)
#
#
# class ManuscriptTextEdit(TextEditBase):
#     sceneSeparatorClicked = pyqtSignal(Scene)
#
#     def __init__(self, parent=None):
#         super(ManuscriptTextEdit, self).__init__(parent)
#         self._pasteAsOriginalEnabled = False
#         self._resizedOnShow: bool = False
#         self._minHeight = 40
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#         self.setTabChangesFocus(True)
#
#         self.highlighter = GrammarHighlighter(self.document(), checkEnabled=False,
#                                               highlightStyle=GrammarHighlightStyle.BACKGOUND)
#
#         self._sentenceHighlighter: Optional[SentenceHighlighter] = None
#
#         toolbar = ManuscriptPopupTextEditorToolbar()
#         toolbar.activate(self)
#         self.setPopupWidget(toolbar)
#
#         # self._sceneSepBlockFormat = QTextBlockFormat()
#         # self._sceneSepBlockFormat.setTextIndent(40)
#         # self._sceneSepBlockFormat.setTopMargin(20)
#         # self._sceneSepBlockFormat.setBottomMargin(20)
#
#         # self._sceneTextObject = SceneSeparatorTextObject(self)
#         # self.document().documentLayout().registerHandler(SceneSeparatorTextFormat, self._sceneTextObject)
#
#         self._setDefaultStyleSheet()
#         self.setCommandOperations([Heading1Operation, Heading2Operation, Heading3Operation, InsertListOperation,
#                                    InsertNumberedListOperation])
#
#         self.textChanged.connect(self.resizeToContent)
#
#     @overrides
#     def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
#         cursor: QTextCursor = self.textCursor()
#         if cursor.atBlockEnd() and event.key() == Qt.Key.Key_Space:
#             cursor.movePosition(QTextCursor.MoveOperation.PreviousCharacter, QTextCursor.MoveMode.KeepAnchor)
#             if cursor.selectedText() == ' ':
#                 self.textCursor().deletePreviousChar()
#                 self.textCursor().insertText('.')
#         super(ManuscriptTextEdit, self).keyPressEvent(event)
#
#     # @overrides
#     # def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
#     #     anchor = self.anchorAt(event.pos())
#     #     if anchor and anchor.startswith(SceneSeparatorTextFormatPrefix):
#     #         if QApplication.overrideCursor() is None:
#     #             QApplication.setOverrideCursor(Qt.CursorShape.PointingHandCursor)
#     #         synopsis = self._sceneTextObject.sceneSynopsis(anchor.replace(SceneSeparatorTextFormatPrefix, ''))
#     #         self.setToolTip(synopsis)
#     #         return
#     #     else:
#     #         QApplication.restoreOverrideCursor()
#     #         self.setToolTip('')
#     #     super(ManuscriptTextEdit, self).mouseMoveEvent(event)
#
#     # @overrides
#     # def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
#     #     anchor = self.anchorAt(event.pos())
#     #     if anchor and anchor.startswith(SceneSeparatorTextFormatPrefix):
#     #         scene = self._sceneTextObject.scene(anchor.replace(SceneSeparatorTextFormatPrefix, ''))
#     #         if scene:
#     #             self.sceneSeparatorClicked.emit(scene)
#     #         return
#     #
#     #     super(ManuscriptTextEdit, self).mouseReleaseEvent(event)
#
#     def setGrammarCheckEnabled(self, enabled: bool):
#         self.highlighter.setCheckEnabled(enabled)
#
#     def checkGrammar(self):
#         self.highlighter.rehighlight()
#
#     def asyncCheckGrammar(self):
#         self.highlighter.asyncRehighlight()
#
#     def initSentenceHighlighter(self):
#         transparent(self)
#         self._sentenceHighlighter = SentenceHighlighter(self)
#
#     def clearSentenceHighlighter(self):
#         if self._sentenceHighlighter is not None:
#             gc(self._sentenceHighlighter)
#             self._sentenceHighlighter = None
#
#         self._setDefaultStyleSheet()
#
#     def setSentenceHighlighterEnabled(self, enabled: bool):
#         self._sentenceHighlighter.setSentenceHighlightEnabled(enabled)
#
#     def setScene(self, scene: Scene):
#         # self._sceneTextObject.setScenes([scene])
#
#         self._addScene(scene)
#         self.setUneditableBlocksEnabled(False)
#         self.document().clearUndoRedoStacks()
#         self.resizeToContent()
#
#     # def setScenes(self, scenes: List[Scene]):
#     #     def sceneCharFormat(scene: Scene) -> QTextCharFormat:
#     #         sceneSepCharFormat = QTextCharFormat()
#     #         sceneSepCharFormat.setObjectType(SceneSeparatorTextFormat)
#     #         sceneSepCharFormat.setToolTip(scene.synopsis)
#     #         sceneSepCharFormat.setAnchor(True)
#     #         sceneSepCharFormat.setAnchorHref(f'{SceneSeparatorTextFormatPrefix}{scene.id}')
#     #
#     #         return sceneSepCharFormat
#     #
#     #     self.setUneditableBlocksEnabled(True)
#     #     self._sceneTextObject.setScenes(scenes)
#     #
#     #     for i, scene in enumerate(scenes):
#     #         self.textCursor().insertBlock(self._sceneSepBlockFormat)
#     #         self.textCursor().insertText(f'{OBJECT_REPLACEMENT_CHARACTER}', sceneCharFormat(scene))
#     #         self.textCursor().block().setUserState(TextBlockState.UNEDITABLE.value)
#     #         self.insertNewBlock()
#     #         self._addScene(scene)
#     #
#     #     self._deleteBlock(0, force=True)
#     #
#     #     self.document().clearUndoRedoStacks()
#     #     self.resizeToContent()
#
#     # def insertNewBlock(self):
#     #     self.textCursor().insertBlock(self._defaultBlockFormat, QTextCharFormat())
#
#     @overrides
#     def showEvent(self, event: QShowEvent) -> None:
#         super().showEvent(event)
#         if not self._resizedOnShow:
#             self.resizeToContent()
#             self._resizedOnShow = True
#
#     @overrides
#     def resizeEvent(self, event: QResizeEvent):
#         super().resizeEvent(event)
#         if self._resizedOnShow:
#             self.resizeToContent()
#
#     def resizeToContent(self):
#         padding = self.contentsMargins().top() + self.contentsMargins().bottom() + 2 * self.document().documentMargin()
#         size = self.document().size()
#         self.setFixedHeight(max(self._minHeight, math.ceil(size.height() + padding)))
#
#     def _addScene(self, scene: Scene):
#         if not scene.manuscript.loaded:
#             json_client.load_document(app_env.novel, scene.manuscript)
#
#         first_scene_block = self.textCursor().block()
#         self.textCursor().insertHtml(remove_font(scene.manuscript.content))
#         if first_scene_block.userState() == TextBlockState.UNEDITABLE.value:
#             first_scene_block.setUserState(-1)
#
#     def _transparent(self):
#         border = 0
#         self.setStyleSheet(f'border-top: {border}px dashed {RELAXED_WHITE_COLOR}; background-color: rgba(0, 0, 0, 0);')
#
#     def _setDefaultStyleSheet(self):
#         self.setStyleSheet(
#             f'ManuscriptTextEdit {{background-color: {RELAXED_WHITE_COLOR};}}')
#
#
# SceneSeparatorTextFormat = QTextFormat.FormatType.UserFormat + 9999
# SceneSeparatorTextFormatPrefix = 'scene:/'
#
#
# class SceneSeparatorTextObject(QObject, QTextObjectInterface):
#     def __init__(self, textedit: ManuscriptTextEdit):
#         super(SceneSeparatorTextObject, self).__init__(textedit)
#         self._textedit = textedit
#         self._scenes: Dict[str, Scene] = {}
#
#     def setScenes(self, scenes: List[Scene]):
#         self._scenes.clear()
#         for scene in scenes:
#             self._scenes[str(scene.id)] = scene
#
#     def sceneTitle(self, id_str: str) -> str:
#         if id_str in self._scenes.keys():
#             return self._scenes[id_str].title or 'Scene'
#         else:
#             return 'Scene'
#
#     def sceneSynopsis(self, id_str: str) -> str:
#         if id_str in self._scenes.keys():
#             return self._scenes[id_str].synopsis
#         else:
#             return ''
#
#     def scene(self, id_str: str) -> Optional[Scene]:
#         return self._scenes.get(id_str)
#
#     @overrides
#     def intrinsicSize(self, doc: QTextDocument, posInDocument: int, format_: QTextFormat) -> QSizeF:
#         metrics = QFontMetrics(self._textedit.font())
#         return QSizeF(350, metrics.boundingRect('W').height())
#
#     @overrides
#     def drawObject(self, painter: QPainter, rect: QRectF, doc: QTextDocument, posInDocument: int,
#                    format_: QTextFormat) -> None:
#         match = doc.find(OBJECT_REPLACEMENT_CHARACTER, posInDocument)
#         if match:
#             anchor = match.charFormat().anchorHref()
#             if anchor:
#                 painter.setPen(Qt.GlobalColor.lightGray)
#                 scene_id = anchor.replace(SceneSeparatorTextFormatPrefix, "")
#                 painter.drawText(rect, f'~{self.sceneTitle(scene_id)}~')
#
#
# class ManuscriptTextEditor(TextEditorBase):
#     textChanged = pyqtSignal()
#     selectionChanged = pyqtSignal()
#     sceneTitleChanged = pyqtSignal(Scene)
#     progressChanged = pyqtSignal(DocumentProgress)
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._novel: Optional[Novel] = None
#         self.toolbar().setHidden(True)
#         self._titleVisible: bool = True
#         self.setCharacterWidth(40)
#         self._scenes: List[Scene] = []
#
#         self._textTitle = QLineEdit()
#         self._textTitle.setProperty('transparent', True)
#         self._textTitle.setFrame(False)
#         self._textTitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         title_font = self._textedit.font()
#         title_font.setBold(True)
#         title_font.setPointSize(32)
#         self._textTitle.setFont(title_font)
#         self._textTitle.returnPressed.connect(self.textEdit.setFocus)
#         self._textTitle.textEdited.connect(self._titleChanged)
#         self._wdgTitle = group(self._textTitle, margin=0, spacing=0)
#         self._wdgTitle.setProperty('relaxed-white-bg', True)
#         margins(self._wdgTitle, left=20)
#
#         self.layout().insertWidget(1, self._wdgTitle, alignment=Qt.AlignmentFlag.AlignTop)
#
#         self.repo = RepositoryPersistenceManager.instance()
#
#     @overrides
#     def _initTextEdit(self) -> ManuscriptTextEdit:
#         _textedit = ManuscriptTextEdit()
#         _textedit.zoomIn(int(_textedit.font().pointSize() * 0.25))
#         _textedit.setBlockFormat(DEFAULT_MANUSCRIPT_LINE_SPACE, textIndent=DEFAULT_MANUSCRIPT_INDENT)
#         _textedit.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoNone)
#         _textedit.selectionChanged.connect(self.selectionChanged.emit)
#         _textedit.textChanged.connect(self._textChanged)
#         _textedit.setProperty('borderless', True)
#         return _textedit
#
#     def manuscriptTextEdit(self) -> ManuscriptTextEdit:
#         return self._textedit
#
#     def refresh(self):
#         if len(self._scenes) == 1:
#             self.setScene(self._scenes[0])
#         elif len(self._scenes) > 1:
#             self.setChapterScenes(self._scenes, self._textTitle.text())
#
#     def setTitleVisible(self, visible: bool):
#         self._titleVisible = visible
#         self._wdgTitle.setVisible(visible)
#
#     def setGrammarCheckEnabled(self, enabled: bool):
#         self.textEdit.setGrammarCheckEnabled(enabled)
#
#     def checkGrammar(self):
#         self.textEdit.checkGrammar()
#
#     def asyncCheckGrammar(self):
#         self.textEdit.asyncCheckGrammar()
#
#     def scenes(self) -> List[Scene]:
#         return self._scenes
#
#     def setScene(self, scene: Scene):
#         self.clear()
#         self._textedit.setScene(scene)
#
#         self._scenes.append(scene)
#         self._textTitle.setPlaceholderText('Scene title')
#         self._textTitle.setText(scene.title)
#         self._textTitle.setReadOnly(False)
#
#     def setChapterScenes(self, scenes: List[Scene], title: str = ''):
#         self.clear()
#         self._textedit.setScenes(scenes)
#
#         self._scenes.extend(scenes)
#         self._textTitle.setPlaceholderText('Chapter')
#         self._textTitle.setText(title)
#         self._textTitle.setReadOnly(True)
#
#     def clear(self):
#         self._scenes.clear()
#         self.textEdit.document().clear()
#         self.textEdit.clear()
#
#     def document(self) -> QTextDocument:
#         return self.textEdit.document()
#
#     def statistics(self) -> TextStatistics:
#         return self.textEdit.statistics()
#
#     def setViewportMargins(self, left: int, top: int, right: int, bottom: int):
#         self.textEdit.setViewportMargins(left, top, right, bottom)
#
#     def setMargins(self, left: int, top: int, right: int, bottom: int):
#         self.textEdit.setViewportMargins(left, top, right, bottom)
#
#     def initSentenceHighlighter(self):
#         self.textEdit.initSentenceHighlighter()
#
#     def clearSentenceHighlighter(self):
#         self.textEdit.clearSentenceHighlighter()
#
#     def setSentenceHighlighterEnabled(self, enabled: bool):
#         self.textEdit.setSentenceHighlighterEnabled(enabled)
#
#     @overrides
#     def setFocus(self):
#         self.textEdit.setFocus()
#
#     def setVerticalScrollBarPolicy(self, policy):
#         self.textEdit.setVerticalScrollBarPolicy(policy)
#
#     def installEventFilterOnEditors(self, filter):
#         self.textEdit.installEventFilter(filter)
#
#     def removeEventFilterFromEditors(self, filter):
#         self.textEdit.removeEventFilter(filter)
#
#     def _textChanged(self):
#         if not self._scenes:
#             return
#
#         for scene in self._scenes:
#             if scene.manuscript.statistics is None:
#                 scene.manuscript.statistics = DocumentStatistics()
#
#         if len(self._scenes) == 1:
#             scene = self._scenes[0]
#             wc = self.textEdit.statistics().word_count
#             updated_progress = self._updateProgress(scene, wc)
#             scene.manuscript.content = self.textEdit.toHtml()
#             self.repo.update_doc(app_env.novel, scene.manuscript)
#             if updated_progress:
#                 self.repo.update_scene(scene)
#                 self.repo.update_novel(self._novel)
#         else:
#             scene_i = 0
#             block: QTextBlock = self.textEdit.document().begin()
#             first_scene_block = None
#             while block.isValid():
#                 if block.userState() == TextBlockState.UNEDITABLE.value:
#                     if first_scene_block is not None:
#                         scene = self._scenes[scene_i]
#                         self._updateSceneManuscript(scene, first_scene_block, block.blockNumber() - 1)
#                         scene_i += 1
#                     first_scene_block = block.next()
#                 block = block.next()
#
#             # update last scene
#             self._updateSceneManuscript(self._scenes[scene_i], first_scene_block, self.textEdit.document().blockCount())
#
#         self.textChanged.emit()
#
#     def _updateSceneManuscript(self, scene: Scene, first_scene_block: QTextBlock, blockNumber: int):
#         cursor = QTextCursor(first_scene_block)
#         cursor.movePosition(QTextCursor.MoveOperation.NextBlock, QTextCursor.MoveMode.KeepAnchor,
#                             blockNumber - first_scene_block.blockNumber())
#         cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
#         scene.manuscript.content = cursor.selection().toHtml()
#         wc_ = wc(cursor.selection().toPlainText())
#         if scene.manuscript.statistics.wc != wc_:
#             self._updateProgress(scene, wc_)
#             scene.manuscript.statistics.wc = wc_
#             self.repo.update_scene(scene)
#             self.repo.update_novel(self._novel)
#
#         self.repo.update_doc(app_env.novel, scene.manuscript)
#
#     def _updateProgress(self, scene, wc) -> bool:
#         if scene.manuscript.statistics.wc == wc:
#             return False
#
#         diff = wc - scene.manuscript.statistics.wc
#         progress: DocumentProgress = daily_progress(scene)
#         overall_progress = daily_overall_progress(self._novel)
#         if diff > 0:
#             progress.added += diff
#             overall_progress.added += diff
#         else:
#             progress.removed += abs(diff)
#             overall_progress.removed += abs(diff)
#         self.progressChanged.emit(overall_progress)
#         scene.manuscript.statistics.wc = wc
#
#         return True
#
#     def _titleChanged(self, text: str):
#         if len(self._scenes) == 1:
#             self._scenes[0].title = text
#             self.sceneTitleChanged.emit(self._scenes[0])
#
#
# class ManuscriptEditor(QWidget):
#     textChanged = pyqtSignal()
#     progressChanged = pyqtSignal(DocumentProgress)
#
#     def __init__(self, parent=None):
#         super().__init__(parent)
#         self._novel: Optional[Novel] = None
#         self._margins: int = 30
#         self._scenes: List[ManuscriptTextEdit] = []
#         self._font = self.defaultFont()
#         self._characterWidth: int = 40
#
#         vbox(self, 0, 0)
#
#         self.repo = RepositoryPersistenceManager.instance()
#
#     @overrides
#     def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
#         if self._maxContentWidth > 0:
#             self._resizeToCharacterWidth()
#
#     def defaultFont(self) -> QFont:
#         if app_env.is_linux():
#             return QFont('Palatino', 14)
#         elif app_env.is_mac():
#             return QFont('Palatino', 16)
#         elif app_env.is_windows():
#             return QFont('Georgia', 16)
#         else:
#             font = QApplication.font()
#             font.setPointSize(16)
#             return font
#
#     def setNovel(self, novel: Novel):
#         self._novel = novel
#
#         if app_env.platform() in self._novel.prefs.manuscript.font.keys():
#             fontSettings = self._getFontSettings()
#             if fontSettings.family:
#                 self._font.setFamily(fontSettings.family)
#             if fontSettings.font_size:
#                 self._font.setPointSize(fontSettings.font_size)
#             if fontSettings.text_width:
#                 self.setCharacterWidth(fontSettings.text_width)
#         else:
#             self.setCharacterWidth(60)
#
#     def setCharacterWidth(self, width: int):
#         self._characterWidth = width
#         metrics = QtGui.QFontMetricsF(self.font())
#         self._maxContentWidth = metrics.boundingRect('M' * self._characterWidth).width()
#         self._resizeToCharacterWidth()
#
#     def setScenes(self, scenes: List[Scene], title: Optional[str] = None):
#         self._scenes.clear()
#         clear_layout(self)
#
#         for scene in scenes:
#             wdg = self._initTextEdit()
#             wdg.setScene(scene)
#             wdg.textChanged.connect(partial(self._textChanged, wdg, scene))
#             self._scenes.append(wdg)
#             self.layout().addWidget(wdg)
#
#         self.layout().addWidget(vspacer())
#
#     def statistics(self) -> TextStatistics:
#         overall_stats = TextStatistics(0)
#         if self.hasScenes():
#             for editor in self._scenes:
#                 overall_stats.word_count += editor.statistics().word_count
#
#         return overall_stats
#
#     def hasScenes(self) -> bool:
#         return len(self._scenes) > 0
#
#     def _textChanged(self, textedit: ManuscriptTextEdit, scene: Scene):
#         if scene.manuscript.statistics is None:
#             scene.manuscript.statistics = DocumentStatistics()
#
#         wc = textedit.statistics().word_count
#         updated_progress = self._updateProgress(scene, wc)
#
#         scene.manuscript.content = textedit.toHtml()
#         self.repo.update_doc(app_env.novel, scene.manuscript)
#         if updated_progress:
#             self.repo.update_scene(scene)
#             self.repo.update_novel(self._novel)
#
#         self.textChanged.emit()
#
#     def _updateProgress(self, scene: Scene, wc: int) -> bool:
#         if scene.manuscript.statistics.wc == wc:
#             return False
#
#         diff = wc - scene.manuscript.statistics.wc
#         progress: DocumentProgress = daily_progress(scene)
#         overall_progress = daily_overall_progress(self._novel)
#         if diff > 0:
#             progress.added += diff
#             overall_progress.added += diff
#         else:
#             progress.removed += abs(diff)
#             overall_progress.removed += abs(diff)
#         self.progressChanged.emit(overall_progress)
#         scene.manuscript.statistics.wc = wc
#
#         return True
#
#     def _initTextEdit(self) -> ManuscriptTextEdit:
#         _textedit = ManuscriptTextEdit()
#         _textedit.setFont(self._font)
#         _textedit.setDashInsertionMode(self._novel.prefs.manuscript.dash)
#         _textedit.setAutoCapitalizationMode(self._novel.prefs.manuscript.capitalization)
#
#         _textedit.zoomIn(int(_textedit.font().pointSize() * 0.25))
#         _textedit.setBlockFormat(DEFAULT_MANUSCRIPT_LINE_SPACE, textIndent=DEFAULT_MANUSCRIPT_INDENT)
#         _textedit.setAutoFormatting(QTextEdit.AutoFormattingFlag.AutoNone)
#         # _textedit.selectionChanged.connect(self.selectionChanged.emit)
#         _textedit.setProperty('borderless', True)
#
#         _textedit.setPlaceholderText('Write your story...')
#         _textedit.setSidebarEnabled(False)
#         _textedit.setReadOnly(self._novel.is_readonly())
#         # _textedit.setViewportMargins(0, 0, 0, 0)
#         _textedit.setDocumentMargin(0)
#
#         return _textedit
#
#     def _getFontSettings(self) -> FontSettings:
#         if app_env.platform() not in self._novel.prefs.manuscript.font.keys():
#             self._novel.prefs.manuscript.font[app_env.platform()] = FontSettings()
#         return self._novel.prefs.manuscript.font[app_env.platform()]
#
#     def _resizeToCharacterWidth(self):
#         # print(f'max {self._maxContentWidth} width {self.width()}')
#         if 0 < self._maxContentWidth < self.width():
#             margin = self.width() - self._maxContentWidth
#         else:
#             margin = 0
#
#         margin = int(margin // 2)
#         # print(margin)
#         margins(self, left=margin, right=margin)
#         # current_margins: QMargins = self.viewportMargins()
#         # self.setViewportMargins(margin, current_margins.top(), margin, current_margins.bottom())
#         # self.resizeToContent()
#
#
# class ReadabilityWidget(QWidget, Ui_ReadabilityWidget):
#     def __init__(self, parent=None):
#         super(ReadabilityWidget, self).__init__(parent)
#         self.setupUi(self)
#
#         self.btnRefresh.setIcon(IconRegistry.refresh_icon())
#         self.btnRefresh.installEventFilter(OpacityEventFilter(parent=self.btnRefresh))
#         self.btnRefresh.installEventFilter(ButtonPressResizeEventFilter(self.btnRefresh))
#         retain_when_hidden(self.btnRefresh)
#         self.btnRefresh.setHidden(True)
#         self._updatedDoc: Optional[QTextDocument] = None
#         self.btnRefresh.clicked.connect(lambda: self.checkTextDocument(self._updatedDoc))
#
#     def checkTextDocument(self, doc: QTextDocument):
#         text = doc.toPlainText()
#         cleaned_text = clean_text(text)
#         word_count = wc(text)
#         spin(self.btnResult)
#         if word_count < 30:
#             msg = 'Text is too short for calculating readability score'
#             self.btnResult.setToolTip(msg)
#             self.btnResult.setIcon(IconRegistry.from_name('ei.question'))
#             self.lblResult.setText(f'<i style="color:grey">{msg}</i>')
#         else:
#             score = textstat.flesch_reading_ease(cleaned_text)
#             self.btnResult.setToolTip(f'Flesch–Kincaid readability score: {score}')
#
#             if score >= 80:
#                 self.btnResult.setIcon(IconRegistry.from_name('mdi.alpha-a-circle-outline', color='#2d6a4f'))
#                 result_text = 'Very easy to read' if score >= 90 else 'Easy to read'
#                 self.lblResult.setText(f'<i style="color:#2d6a4f">{result_text}</i>')
#             elif score >= 60:
#                 self.btnResult.setIcon(IconRegistry.from_name('mdi.alpha-b-circle-outline', color='#52b788'))
#                 result_text = 'Fairly easy to read. 7th grade' if score >= 70 else 'Fairly easy to read. 8-9th grade'
#                 self.lblResult.setText(f'<i style="color:#52b788">{result_text}</i>')
#             elif score >= 50:
#                 self.btnResult.setIcon(IconRegistry.from_name('mdi.alpha-c-circle-outline', color='#f77f00'))
#                 self.lblResult.setText('<i style="color:#f77f00">Fairly difficult to read. 10-12th grade</i>')
#             elif score >= 30:
#                 self.btnResult.setIcon(IconRegistry.from_name('mdi.alpha-d-circle-outline', color='#bd1f36'))
#                 self.lblResult.setText('<i style="color:#bd1f36">Difficult to read</i>')
#             else:
#                 self.btnResult.setIcon(IconRegistry.from_name('mdi.alpha-e-circle-outline', color='#85182a'))
#                 self.lblResult.setText('<i style="color:#85182a">Very difficult to read</i>')
#
#         sentences_count = 0
#         for i in range(doc.blockCount()):
#             block = doc.findBlockByNumber(i)
#             if block.userState() == TextBlockState.UNEDITABLE.value:
#                 continue
#             block_text = block.text()
#             if block_text:
#                 sentences_count += sentence_count(block_text)
#
#         if not sentences_count:
#             sentence_length = 0
#         else:
#             sentence_length = word_count / sentences_count
#         self.lblAvgSentenceLength.setText("%.2f" % round(sentence_length, 1))
#
#         self.btnRefresh.setHidden(True)
#
#     def setTextDocumentUpdated(self, doc: QTextDocument, updated: bool = True):
#         self._updatedDoc = doc
#         if updated:
#             if not self.btnRefresh.isVisible():
#                 anim = qtanim.fade_in(self.btnRefresh)
#                 if not app_env.test_env():
#                     anim.finished.connect(lambda: translucent(self.btnRefresh, 0.4))
#         else:
#             if self.btnRefresh.isVisible():
#                 qtanim.fade_out(self.btnRefresh)
#
#
# class DistractionFreeManuscriptEditor(QWidget, Ui_DistractionFreeManuscriptEditor):
#     exitRequested = pyqtSignal()
#
#     def __init__(self, parent=None):
#         super(DistractionFreeManuscriptEditor, self).__init__(parent)
#         self.setupUi(self)
#         self.editor: Optional[ManuscriptEditor] = None
#         self.lblWords: Optional[WordsDisplay] = None
#         self._firstInit: bool = True
#
#         self.wdgSprint = SprintWidget(self)
#         self.wdgSprint.setCompactMode(True)
#         self.wdgHeader.layout().insertWidget(0, self.wdgSprint, alignment=Qt.AlignmentFlag.AlignLeft)
#
#         self.wdgDistractionFreeEditor.installEventFilter(self)
#         self.wdgBottom.installEventFilter(self)
#         self.btnReturn.setIcon(IconRegistry.from_name('mdi.arrow-collapse', 'white'))
#         self.btnReturn.clicked.connect(self.exitRequested.emit)
#         self.btnFocus.setIcon(IconRegistry.from_name('mdi.credit-card', 'lightgrey', color_on=PLOTLYST_TERTIARY_COLOR))
#         self.btnFocus.toggled.connect(self._toggle_manuscript_focus)
#         self.btnTypewriterMode.setIcon(
#             IconRegistry.from_name('mdi.typewriter', 'lightgrey', color_on=PLOTLYST_TERTIARY_COLOR))
#         self.btnTypewriterMode.toggled.connect(self._toggle_typewriter_mode)
#         self.btnWordCount.setIcon(IconRegistry.from_name('mdi6.counter', 'lightgrey', color_on=PLOTLYST_TERTIARY_COLOR))
#         self.btnWordCount.clicked.connect(self._wordCountClicked)
#
#         decr_font(self.btnFocus, 2)
#         decr_font(self.btnTypewriterMode, 2)
#         decr_font(self.btnWordCount, 2)
#
#     def activate(self, editor: ManuscriptEditor, timer: Optional[TimerModel] = None):
#         self.editor = editor
#         self.editor.installEventFilterOnEditors(self)
#         editor.setTitleVisible(False)
#         clear_layout(self.wdgDistractionFreeEditor.layout())
#         if timer and timer.isActive():
#             self.wdgSprint.setModel(timer)
#             self.wdgSprint.setVisible(True)
#         else:
#             self.wdgSprint.setHidden(True)
#         self.wdgDistractionFreeEditor.layout().addWidget(self.editor)
#         self.editor.setFocus()
#         self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
#
#         self.wdgBottom.setVisible(True)
#         self.editor.initSentenceHighlighter()
#         if self._firstInit:
#             self.btnTypewriterMode.setChecked(True)
#             self._firstInit = False
#         else:
#             self._toggle_manuscript_focus(self.btnFocus.isChecked())
#             self._toggle_typewriter_mode(self.btnTypewriterMode.isChecked())
#
#         self._wordCountClicked(self.btnWordCount.isChecked())
#         self.setMouseTracking(True)
#         self.wdgDistractionFreeEditor.setMouseTracking(True)
#         QTimer.singleShot(5000, self._autoHideBottomBar)
#
#     def deactivate(self):
#         self.editor.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
#         self.editor.setTitleVisible(True)
#         self.editor.removeEventFilterFromEditors(self)
#         self.editor.setMargins(30, 30, 30, 30)
#         self.editor.clearSentenceHighlighter()
#         self.editor = None
#         self.setMouseTracking(False)
#         self.wdgDistractionFreeEditor.setMouseTracking(False)
#         if self.lblWords:
#             self.lblWords.setNightModeEnabled(False)
#
#     def setWordDisplay(self, words: WordsDisplay):
#         words.setNightModeEnabled(True)
#         self.lblWords = words
#         self.wdgHeader.layout().addWidget(self.lblWords, alignment=Qt.AlignmentFlag.AlignRight)
#         self._wordCountClicked(self.btnWordCount.isChecked())
#
#     @overrides
#     def eventFilter(self, watched: QObject, event: QEvent) -> bool:
#         if watched is self.wdgBottom and event.type() == QEvent.Type.Leave:
#             self.wdgBottom.setHidden(True)
#         if event.type() == QEvent.Type.MouseMove and isinstance(event, QMouseEvent):
#             if self.wdgBottom.isHidden() and event.pos().y() > self.height() - 25:
#                 self.wdgBottom.setVisible(True)
#         return super().eventFilter(watched, event)
#
#     @overrides
#     def keyPressEvent(self, event: QKeyEvent) -> None:
#         if event.key() == Qt.Key.Key_Escape:
#             if self.editor is not None:
#                 self.exitRequested.emit()
#         event.accept()
#
#     @overrides
#     def mouseMoveEvent(self, event: QtGui.QMouseEvent) -> None:
#         if self.wdgBottom.isHidden() and event.pos().y() > self.height() - 15:
#             self.wdgBottom.setVisible(True)
#
#     def _wordCountClicked(self, checked: bool):
#         if self.lblWords:
#             if checked:
#                 qtanim.fade_in(self.lblWords, 150)
#             else:
#                 qtanim.fade_out(self.lblWords, 150, teardown=lambda: self.lblWords.setGraphicsEffect(None))
#
#     def _toggle_manuscript_focus(self, toggled: bool):
#         self.editor.setSentenceHighlighterEnabled(toggled)
#
#     def _toggle_typewriter_mode(self, toggled: bool):
#         viewportMargins = self.editor.textEdit.viewportMargins()
#         if toggled:
#             screen: QScreen = QApplication.screenAt(self.editor.pos())
#             viewportMargins.setBottom(screen.size().height() // 2)
#         else:
#             viewportMargins.setBottom(30)
#
#         self.editor.textEdit.setViewportMargins(viewportMargins.left(), viewportMargins.top(),
#                                                 viewportMargins.right(), viewportMargins.bottom())
#         self.editor.textEdit.ensureCursorVisible()
#
#     def _autoHideBottomBar(self):
#         if not self.wdgBottom.underMouse():
#             self.wdgBottom.setHidden(True)
#
#
# class ManuscriptProgressChart(ProgressChart):
#     def __init__(self, novel: Novel, parent=None):
#         self.novel = novel
#         super().__init__(maxValue=self.novel.manuscript_goals.target_wc,
#                          color=PLOTLYST_SECONDARY_COLOR,
#                          titleColor=PLOTLYST_SECONDARY_COLOR,
#                          emptySliceColor=RELAXED_WHITE_COLOR, parent=parent)
#
#         self.setAnimationOptions(QChart.AnimationOption.SeriesAnimations)
#         self.setAnimationDuration(700)
#         self.setAnimationEasingCurve(QEasingCurve.Type.InQuad)
#
#         self._holeSize = 0.6
#         self._titleVisible = False
#
#
# class ManuscriptProgressWidget(QWidget):
#     def __init__(self, novel: Novel, parent=None):
#         super().__init__(parent)
#         self.novel = novel
#         vbox(self)
#
#         self._wordCount: int = 0
#
#         self.wdgGoalTitle = QWidget()
#         hbox(self.wdgGoalTitle, 0)
#
#         self.emojiGoal = Emoji(emoji='bullseye')
#         effect = QGraphicsColorizeEffect()
#         effect.setColor(QColor(PLOTLYST_MAIN_COLOR))
#         self.emojiGoal.setGraphicsEffect(effect)
#         self.lblGoal = WordsDisplay()
#         tooltip = 'Manuscript word count target'
#         self.emojiGoal.setToolTip(tooltip)
#         self.lblGoal.setToolTip(tooltip)
#         self.btnEditGoal = tool_btn(IconRegistry.edit_icon('grey'), transparent_=True,
#                                     tooltip="Edit manuscript word count goal")
#         decr_icon(self.btnEditGoal, 2)
#
#         self.chartProgress = ManuscriptProgressChart(self.novel)
#         self.chartProgressView = ChartView()
#         self.chartProgressView.setMaximumSize(200, 200)
#         self.chartProgressView.setChart(self.chartProgress)
#         self.chartProgressView.scale(1.05, 1.05)
#         self.percentageItem = QGraphicsTextItem()
#         font = self.percentageItem.font()
#         font.setBold(True)
#         font.setPointSize(16)
#         self.percentageItem.setFont(font)
#         self.percentageItem.setDefaultTextColor(QColor(PLOTLYST_SECONDARY_COLOR))
#         self.percentageItem.setTextWidth(200)
#         text_option = QTextOption()
#         text_option.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.percentageItem.document().setDefaultTextOption(text_option)
#         self.counterAnimation = QVariantAnimation()
#         self.counterAnimation.setEasingCurve(QEasingCurve.Type.OutCubic)
#         self.counterAnimation.setDuration(500)
#         self.counterAnimation.valueChanged.connect(self._updatePercentageText)
#         self.counterAnimation.finished.connect(self._counterAnimationFinished)
#         self._animation_started = False
#
#         scene = self.chartProgressView.scene()
#         scene.addItem(self.percentageItem)
#
#         self.percentageItem.setPos(0,
#                                    self.chartProgressView.chart().plotArea().center().y() - self.percentageItem.boundingRect().height() / 2)
#
#         self.wdgGoalTitle.layout().addWidget(self.emojiGoal)
#         self.wdgGoalTitle.layout().addWidget(self.lblGoal)
#         self.wdgGoalTitle.layout().addWidget(self.btnEditGoal)
#
#         self.layout().addWidget(self.wdgGoalTitle, alignment=Qt.AlignmentFlag.AlignCenter)
#         self.layout().addWidget(self.chartProgressView)
#
#     def setMaxValue(self, value: int):
#         self.lblGoal.setWordCount(value)
#         self.chartProgress.setMaxValue(value)
#         self.chartProgress.setValue(self._wordCount)
#         self._refresh()
#
#     def setValue(self, value: int):
#         self._wordCount = value
#         self.chartProgress.setValue(value)
#         self._refresh()
#
#     @overrides
#     def showEvent(self, event: QShowEvent):
#         super().showEvent(event)
#         if not self._animation_started:
#             self.counterAnimation.setStartValue(0)
#             self.counterAnimation.setEndValue(self.chartProgress.percentage())
#             QTimer.singleShot(200, self.counterAnimation.start)
#             self.percentageItem.setPlainText('')
#             self._animation_started = True
#
#     def _refresh(self):
#         self.chartProgress.refresh()
#
#         if self.isVisible():
#             self.percentageItem.setPlainText(f'{self.chartProgress.percentage()}%')
#
#     def _updatePercentageText(self, value: int):
#         self.percentageItem.setPlainText(f"{value}%")
#
#     def _counterAnimationFinished(self):
#         self._animation_started = False
#
#
# class ManuscriptExportWidget(QWidget):
#     def __init__(self, novel: Novel, parent=None):
#         super().__init__(parent)
#         self._novel = novel
#
#         vbox(self, spacing=15)
#         # self.layout().addWidget(label('Export manuscript', h5=True), alignment=Qt.AlignmentFlag.AlignCenter)
#         # self.layout().addWidget(line())
#
#         self._btnDocx = push_btn(IconRegistry.docx_icon(), 'Word (.docx)', checkable=True,
#                                  properties=['transparent-rounded-bg-on-hover', 'secondary-selector'])
#         self._btnDocx.setChecked(True)
#         self._btnPdf = push_btn(IconRegistry.from_name('fa5.file-pdf'), 'PDF', checkable=True,
#                                 tooltip='PDF export not available yet',
#                                 properties=['transparent-rounded-bg-on-hover', 'secondary-selector'])
#
#         self._btnGroup = QButtonGroup()
#         self._btnGroup.setExclusive(True)
#         self._btnGroup.addButton(self._btnDocx)
#         self._btnGroup.addButton(self._btnPdf)
#         self._btnPdf.setDisabled(True)
#         self.layout().addWidget(self._btnDocx, alignment=Qt.AlignmentFlag.AlignCenter)
#         self.layout().addWidget(self._btnPdf, alignment=Qt.AlignmentFlag.AlignCenter)
#
#         self._btnExport = push_btn(IconRegistry.from_name('mdi.file-export-outline', RELAXED_WHITE_COLOR), 'Export',
#                                    tooltip='Export manuscript',
#                                    properties=['base', 'positive'])
#         self.layout().addWidget(self._btnExport)
#
#         self._btnExport.clicked.connect(self._export)
#
#     def _export(self):
#         if self._btnDocx.isChecked():
#             export_manuscript_to_docx(self._novel)
#
#
# def date_to_str(date: QDate) -> str:
#     return date.toString(Qt.DateFormat.ISODate)
#
#
# class ManuscriptDailyProgress(QWidget):
#     jumpToToday = pyqtSignal()
#
#     def __init__(self, novel: Novel, parent=None):
#         super().__init__(parent)
#         self._novel = novel
#         vbox(self)
#
#         self.btnDay = IconText()
#         self.btnDay.setText('Today')
#         self.btnDay.setIcon(IconRegistry.from_name('mdi.calendar-month-outline'))
#
#         self.btnJumpToToday = push_btn(IconRegistry.from_name('fa5s.arrow-right'), 'Jump to today', transparent_=True)
#         retain_when_hidden(self.btnJumpToToday)
#         italic(self.btnJumpToToday)
#         self.btnJumpToToday.installEventFilter(OpacityEventFilter(self.btnJumpToToday, enterOpacity=0.7))
#         decr_icon(self.btnJumpToToday, 3)
#         decr_font(self.btnJumpToToday, 3)
#         self.btnJumpToToday.clicked.connect(self.jumpToToday)
#
#         self.lblAdded = label('', color=PLOTLYST_SECONDARY_COLOR, h3=True)
#         self.lblRemoved = label('', color='grey', h3=True)
#
#         self.layout().addWidget(group(self.btnDay, self.btnJumpToToday))
#         self.layout().addWidget(group(self.lblAdded, vline(), self.lblRemoved), alignment=Qt.AlignmentFlag.AlignRight)
#         lbl = label('Added/Removed', description=True)
#         decr_font(lbl)
#         self.layout().addWidget(lbl, alignment=Qt.AlignmentFlag.AlignRight)
#
#     def refresh(self):
#         self.setDate(QDate.currentDate())
#
#     def setDate(self, date: QDate):
#         date_str = date_to_str(date)
#         if date == QDate.currentDate():
#             self.btnDay.setText('Today')
#             self.btnJumpToToday.setHidden(True)
#         else:
#             self.btnDay.setText(date_str[5:].replace('-', '/'))
#             self.btnJumpToToday.setVisible(True)
#
#         progress = find_daily_overall_progress(self._novel, date_str)
#         if progress:
#             self.setProgress(progress)
#         else:
#             self.lblAdded.setText('+')
#             self.lblRemoved.setText('-')
#
#     def setProgress(self, progress: DocumentProgress):
#         self.lblAdded.setText(f'+{progress.added}')
#         self.lblRemoved.setText(f'-{progress.removed}')
#
#
# class ManuscriptProgressCalendar(QCalendarWidget):
#     dayChanged = pyqtSignal(QDate)
#
#     def __init__(self, novel: Novel, parent=None):
#         super().__init__(parent)
#         self._novel = novel
#
#         self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
#         self.setHorizontalHeaderFormat(QCalendarWidget.HorizontalHeaderFormat.NoHorizontalHeader)
#         self.setNavigationBarVisible(True)
#         self.setSelectionMode(QCalendarWidget.SelectionMode.SingleSelection)
#         self.setFirstDayOfWeek(Qt.DayOfWeek.Monday)
#         item = self.layout().itemAt(0)
#         item.widget().setStyleSheet(f'.QWidget {{background-color: {PLOTLYST_SECONDARY_COLOR};}}')
#
#         self._initButton(item.widget().layout().itemAt(0), 'ei.circle-arrow-left')
#         self._initButton(item.widget().layout().itemAt(6), 'ei.circle-arrow-right')
#
#         widget = self.layout().itemAt(1).widget()
#         if isinstance(widget, QTableView):
#             widget.setStyleSheet(f'''
#             QTableView {{
#                 selection-background-color: {RELAXED_WHITE_COLOR};
#             }}
#             ''')
#             widget.horizontalHeader().setMinimumSectionSize(20)
#             widget.verticalHeader().setMinimumSectionSize(20)
#
#         today = QDate.currentDate()
#         self.setMaximumDate(today)
#
#     @overrides
#     def showEvent(self, event: QShowEvent) -> None:
#         if QDate.currentDate() != self.maximumDate():
#             self.setMaximumDate(QDate.currentDate())
#             self.showToday()
#         super().showEvent(event)
#
#     @overrides
#     def showToday(self) -> None:
#         super().showToday()
#         self.setSelectedDate(QDate.currentDate())
#         self.dayChanged.emit(self.maximumDate())
#
#     @overrides
#     def paintCell(self, painter: QtGui.QPainter, rect: QRect, date: QDate) -> None:
#         painter.setRenderHint(QPainter.RenderHint.Antialiasing)
#
#         if date.month() == self.monthShown():
#             option = QTextOption()
#             option.setAlignment(Qt.AlignmentFlag.AlignCenter)
#             bold(painter, date == self.selectedDate())
#             underline(painter, date == self.selectedDate())
#
#             progress = find_daily_overall_progress(self._novel, date_to_str(date))
#             if progress:
#                 painter.setPen(QColor('#BB90CE'))
#                 if progress.added + progress.removed >= 1500:
#                     painter.setBrush(QColor('#C8A4D7'))
#                 elif progress.added + progress.removed >= 450:
#                     painter.setBrush(QColor('#EDE1F2'))
#                 else:
#                     painter.setBrush(QColor(RELAXED_WHITE_COLOR))
#                 rad = rect.width() // 2 - 1
#                 painter.drawEllipse(rect.center() + QPoint(1, 1), rad, rad)
#
#             if date > self.maximumDate():
#                 painter.setPen(QColor('grey'))
#             else:
#                 painter.setPen(QColor('black'))
#             painter.drawText(rect.toRectF(), str(date.day()), option)
#
#     def _initButton(self, btnItem: QWidgetItem, icon: str):
#         if btnItem and btnItem.widget() and isinstance(btnItem.widget(), QToolButton):
#             btn = btnItem.widget()
#             transparent(btn)
#             pointy(btn)
#             btn.setIcon(IconRegistry.from_name(icon, RELAXED_WHITE_COLOR))
#
#
# class ManuscriptProgressCalendarLegend(QWidget):
#     def __init__(self, parent=None):
#         super().__init__(parent)
#
#         vbox(self)
#         margins(self, left=15)
#
#         self.layout().addWidget(self._legend(IconRegistry.from_name('fa5.square', color='#BB90CE'), '1+ words'),
#                                 alignment=Qt.AlignmentFlag.AlignLeft)
#         self.layout().addWidget(self._legend(IconRegistry.from_name('fa5s.square', color='#EDE1F2'), '450+ words'),
#                                 alignment=Qt.AlignmentFlag.AlignLeft)
#         self.layout().addWidget(self._legend(IconRegistry.from_name('fa5s.square', color='#C8A4D7'), '1500+ words'),
#                                 alignment=Qt.AlignmentFlag.AlignLeft)
#
#     def _legend(self, icon: QIcon, text: str) -> QPushButton:
#         legend = IconText()
#         apply_button_palette_color(legend, 'grey')
#         legend.setIcon(icon)
#         legend.setText(text)
#
#         return legend
