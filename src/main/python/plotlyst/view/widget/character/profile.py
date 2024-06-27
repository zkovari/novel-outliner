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
from abc import abstractmethod
from functools import partial
from typing import Optional, List, Dict, Any, Tuple

import emoji
import qtanim
from PyQt6.QtCore import pyqtSignal, Qt, QSize, QObject, QEvent, QPoint
from PyQt6.QtGui import QResizeEvent, QWheelEvent, QColor
from PyQt6.QtWidgets import QWidget, QLabel, QSizePolicy, QSlider, QToolButton, QVBoxLayout, QGridLayout
from overrides import overrides
from qthandy import vbox, clear_layout, hbox, bold, underline, spacer, vspacer, margins, pointy, retain_when_hidden, \
    transparent, sp, gc, decr_font, grid, incr_font, line
from qthandy.filter import OpacityEventFilter, VisibilityToggleEventFilter
from qtmenu import MenuWidget, ActionTooltipDisplayMode

from plotlyst.common import PLOTLYST_MAIN_COLOR
from plotlyst.core.domain import Character, CharacterProfileSectionReference, CharacterProfileFieldReference, \
    CharacterProfileFieldType, CharacterMultiAttribute, CharacterProfileSectionType, MultiAttributePrimaryType, \
    MultiAttributeSecondaryType, CharacterSecondaryAttribute, StrengthWeaknessAttribute, CharacterPersonalityAttribute, \
    NovelSetting, Novel
from plotlyst.core.help import enneagram_help, mbti_keywords, mbti_help, work_style_help, love_style_help
from plotlyst.core.template import TemplateField, iq_field, eq_field, rationalism_field, willpower_field, \
    creativity_field, traits_field, values_field, flaw_placeholder_field, goal_field, internal_goal_field, stakes_field, \
    conflict_field, motivation_field, methods_field, internal_motivation_field, internal_conflict_field, \
    internal_stakes_field, baggage_source_field, baggage_manifestation_field, baggage_relation_field, \
    baggage_coping_field, baggage_healing_field, baggage_deterioration_field, ghost_field, \
    baggage_defense_mechanism_field, wound_field, demon_field, baggage_trigger_field, fear_field, misbelief_field, \
    flaw_triggers_field, flaw_coping_field, flaw_manifestation_field, flaw_relation_field, flaw_goals_field, \
    flaw_growth_field, flaw_deterioration_field, enneagram_choices, SelectionItem, mbti_choices, love_style_choices, \
    work_style_choices
from plotlyst.env import app_env
from plotlyst.view.common import tool_btn, wrap, emoji_font, action, insert_before_the_end, push_btn, label, \
    fade_out_and_gc
from plotlyst.view.icons import IconRegistry, avatars
from plotlyst.view.layout import group
from plotlyst.view.style.base import apply_white_menu
from plotlyst.view.style.slider import apply_slider_color
from plotlyst.view.widget.button import CollapseButton, SecondaryActionPushButton, DotsMenuButton
from plotlyst.view.widget.character.editor import StrengthWeaknessEditor, DiscSelector, EnneagramSelector, MbtiSelector, \
    LoveStyleSelector
from plotlyst.view.widget.display import Icon, Emoji, dash_icon
from plotlyst.view.widget.input import AutoAdjustableTextEdit, Toggle, TextInputDialog
from plotlyst.view.widget.settings import SettingBaseWidget, setting_titles
from plotlyst.view.widget.template.impl import TraitSelectionWidget, LabelsSelectionWidget


class ProfileFieldWidget(QWidget):
    valueFilled = pyqtSignal(float)
    valueReset = pyqtSignal()


class TemplateFieldWidgetBase(ProfileFieldWidget):
    def __init__(self, parent=None):
        super(TemplateFieldWidgetBase, self).__init__(parent)
        self.lblEmoji = QLabel(self)
        self.lblEmoji.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        # self.lblEmoji.setToolTip(field.description if field.description else field.placeholder)
        self.lblName = QLabel(self)
        self.lblName.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        # self.lblName.setText(self.field.name)
        # self.lblName.setToolTip(field.description if field.description else field.placeholder)

        # if self.field.emoji:
        #     self.updateEmoji(emoji.emojize(self.field.emoji))
        # else:
        self.lblName.setHidden(True)
        self.lblEmoji.setHidden(True)

        # if not field.show_label:
        #     self.lblName.setHidden(True)

        if app_env.is_mac():
            self._boxSpacing = 1
            self._boxMargin = 0
        else:
            self._boxSpacing = 3
            self._boxMargin = 1

    @abstractmethod
    def value(self) -> Any:
        pass

    @abstractmethod
    def setValue(self, value: Any):
        pass

    def updateEmoji(self, emoji: str):
        self.lblEmoji.setFont(emoji_font())
        self.lblEmoji.setText(emoji)
        self.lblEmoji.setVisible(True)

    def updateLabel(self, text: str):
        self.lblName.setText(text)
        self.lblName.setVisible(True)


class SectionContext:

    def has_addition(self) -> bool:
        return False

    def has_menu(self) -> bool:
        return False

    def primaryFields(self) -> List[TemplateField]:
        return []

    def primaryButtonText(self) -> str:
        return 'Add new item'

    def primaryAttributes(self, character: Character) -> List[CharacterMultiAttribute]:
        pass

    def primaryFieldType(self) -> CharacterProfileFieldType:
        pass

    def editorTitle(self) -> str:
        return 'Define a new attribute'

    def editorPlaceholder(self) -> str:
        return 'Name of the attribute'


def character_primary_attribute_type(field: TemplateField) -> MultiAttributePrimaryType:
    if field is goal_field:
        return MultiAttributePrimaryType.External_goal
    elif field is internal_goal_field:
        return MultiAttributePrimaryType.Internal_goal
    elif field is ghost_field:
        return MultiAttributePrimaryType.Ghost
    elif field is wound_field:
        return MultiAttributePrimaryType.Wound
    elif field is demon_field:
        return MultiAttributePrimaryType.Demon
    elif field is fear_field:
        return MultiAttributePrimaryType.Fear
    elif field is misbelief_field:
        return MultiAttributePrimaryType.Misbelief
    elif field is flaw_placeholder_field:
        return MultiAttributePrimaryType.Flaw


def character_primary_field(type_: MultiAttributePrimaryType) -> TemplateField:
    if type_ == MultiAttributePrimaryType.External_goal:
        return goal_field
    elif type_ == MultiAttributePrimaryType.Internal_goal:
        return internal_goal_field

    elif type_ == MultiAttributePrimaryType.Ghost:
        return ghost_field
    elif type_ == MultiAttributePrimaryType.Wound:
        return wound_field
    elif type_ == MultiAttributePrimaryType.Fear:
        return fear_field
    elif type_ == MultiAttributePrimaryType.Demon:
        return demon_field
    elif type_ == MultiAttributePrimaryType.Misbelief:
        return misbelief_field

    elif type_ == MultiAttributePrimaryType.Flaw:
        return flaw_placeholder_field


def character_secondary_attribute_type(field: TemplateField) -> MultiAttributeSecondaryType:
    if field is motivation_field:
        return MultiAttributeSecondaryType.External_motivation
    elif field is internal_motivation_field:
        return MultiAttributeSecondaryType.Internal_motivation
    elif field is conflict_field:
        return MultiAttributeSecondaryType.External_conflict
    elif field is internal_conflict_field:
        return MultiAttributeSecondaryType.Internal_conflict
    elif field is stakes_field:
        return MultiAttributeSecondaryType.External_stakes
    elif field is internal_stakes_field:
        return MultiAttributeSecondaryType.Internal_stakes
    elif field is methods_field:
        return MultiAttributeSecondaryType.Methods

    elif field is baggage_source_field:
        return MultiAttributeSecondaryType.Baggage_source
    elif field is baggage_manifestation_field:
        return MultiAttributeSecondaryType.Baggage_manifestation
    elif field is baggage_relation_field:
        return MultiAttributeSecondaryType.Baggage_relation
    elif field is baggage_coping_field:
        return MultiAttributeSecondaryType.Baggage_coping
    elif field is baggage_healing_field:
        return MultiAttributeSecondaryType.Baggage_healing
    elif field is baggage_deterioration_field:
        return MultiAttributeSecondaryType.Baggage_deterioration
    elif field is baggage_defense_mechanism_field:
        return MultiAttributeSecondaryType.Baggage_defense_mechanism
    elif field is baggage_trigger_field:
        return MultiAttributeSecondaryType.Baggage_trigger

    elif field is flaw_triggers_field:
        return MultiAttributeSecondaryType.Flaw_triggers
    elif field is flaw_coping_field:
        return MultiAttributeSecondaryType.Flaw_coping
    elif field is flaw_manifestation_field:
        return MultiAttributeSecondaryType.Flaw_manifestation
    elif field is flaw_relation_field:
        return MultiAttributeSecondaryType.Flaw_relation
    elif field is flaw_goals_field:
        return MultiAttributeSecondaryType.Flaw_goals
    elif field is flaw_growth_field:
        return MultiAttributeSecondaryType.Flaw_growth
    elif field is flaw_deterioration_field:
        return MultiAttributeSecondaryType.Flaw_deterioration


def character_secondary_field(value: str) -> TemplateField:
    secondary = MultiAttributeSecondaryType(value)
    if secondary == MultiAttributeSecondaryType.External_motivation:
        return motivation_field
    elif secondary == MultiAttributeSecondaryType.Internal_motivation:
        return internal_motivation_field
    elif secondary == MultiAttributeSecondaryType.External_conflict:
        return conflict_field
    elif secondary == MultiAttributeSecondaryType.Internal_conflict:
        return internal_conflict_field
    elif secondary == MultiAttributeSecondaryType.External_stakes:
        return stakes_field
    elif secondary == MultiAttributeSecondaryType.Internal_stakes:
        return internal_stakes_field
    elif secondary == MultiAttributeSecondaryType.Methods:
        return methods_field

    elif secondary == MultiAttributeSecondaryType.Baggage_source:
        return baggage_source_field
    elif secondary == MultiAttributeSecondaryType.Baggage_manifestation:
        return baggage_manifestation_field
    elif secondary == MultiAttributeSecondaryType.Baggage_relation:
        return baggage_relation_field
    elif secondary == MultiAttributeSecondaryType.Baggage_coping:
        return baggage_coping_field
    elif secondary == MultiAttributeSecondaryType.Baggage_healing:
        return baggage_healing_field
    elif secondary == MultiAttributeSecondaryType.Baggage_deterioration:
        return baggage_deterioration_field
    elif secondary == MultiAttributeSecondaryType.Baggage_defense_mechanism:
        return baggage_defense_mechanism_field
    elif secondary == MultiAttributeSecondaryType.Baggage_trigger:
        return baggage_trigger_field

    elif secondary == MultiAttributeSecondaryType.Flaw_triggers:
        return flaw_triggers_field
    elif secondary == MultiAttributeSecondaryType.Flaw_coping:
        return flaw_coping_field
    elif secondary == MultiAttributeSecondaryType.Flaw_manifestation:
        return flaw_manifestation_field
    elif secondary == MultiAttributeSecondaryType.Flaw_relation:
        return flaw_relation_field
    elif secondary == MultiAttributeSecondaryType.Flaw_goals:
        return flaw_goals_field
    elif secondary == MultiAttributeSecondaryType.Flaw_growth:
        return flaw_growth_field
    elif secondary == MultiAttributeSecondaryType.Flaw_deterioration:
        return flaw_deterioration_field


class ProfileSectionWidget(ProfileFieldWidget):
    headerEnabledChanged = pyqtSignal(bool)
    fieldAdded = pyqtSignal(CharacterProfileFieldReference)

    def __init__(self, section: CharacterProfileSectionReference, context: SectionContext, character: Character,
                 parent=None):
        super().__init__(parent)
        self.character = character
        self.section = section
        self.context = context
        vbox(self)
        self.btnHeader = CollapseButton(Qt.Edge.BottomEdge, Qt.Edge.RightEdge)
        self.btnHeader.setIconSize(QSize(16, 16))
        bold(self.btnHeader)
        underline(self.btnHeader)
        self.btnHeader.setText(section.type.name)
        self.btnHeader.setToolTip(section.type.name)

        self.wdgHeader = QWidget()
        hbox(self.wdgHeader, 1, 0)
        self.wdgHeader.layout().addWidget(self.btnHeader, alignment=Qt.AlignmentFlag.AlignLeft)
        # self.progress = CircularProgressBar()
        # self.wdgHeader.layout().addWidget(self.progress, alignment=Qt.AlignmentFlag.AlignVCenter)
        # self.wdgHeader.layout().addWidget(spacer())

        self.wdgContainer = QWidget()
        vbox(self.wdgContainer, 0)
        margins(self.wdgContainer, left=20)

        self.wdgBottom = QWidget()
        vbox(self.wdgBottom, 0, 0)
        margins(self.wdgBottom, left=20)

        self.layout().addWidget(self.wdgHeader)
        self.layout().addWidget(self.wdgContainer)
        self.layout().addWidget(self.wdgBottom)

        if self.context.has_addition():
            self._btnPrimary = SecondaryActionPushButton()
            self._btnPrimary.setText(self.context.primaryButtonText())
            self._btnPrimary.setIcon(IconRegistry.plus_icon('grey'))
            decr_font(self._btnPrimary)
            fields = self.context.primaryFields()

            if self.context.has_menu():
                self._menu = MenuWidget(self._btnPrimary)
                self._menu.setTooltipDisplayMode(ActionTooltipDisplayMode.DISPLAY_UNDER)
                for field in fields:
                    self._menu.addAction(
                        action(field.name, icon=IconRegistry.from_name(field.icon), tooltip=field.description,
                               slot=partial(self._addPrimaryField, field),
                               parent=self._menu))
            else:
                self._btnPrimary.clicked.connect(self._initNewPrimaryField)

            self.wdgBottom.layout().addWidget(self._btnPrimary)

        self.children: List[ProfileFieldWidget] = []
        # self.progressStatuses: Dict[ProfileFieldWidget, float] = {}

        self.btnHeader.toggled.connect(self._toggleCollapse)

    def attachWidget(self, widget: ProfileFieldWidget):
        self.children.append(widget)
        if self.section.type == CharacterProfileSectionType.Summary:
            self.wdgContainer.layout().addWidget(widget, alignment=Qt.AlignmentFlag.AlignTop)
        else:
            self.wdgContainer.layout().addWidget(widget)
        # self.progressStatuses[widget] = False
        # widget.valueFilled.connect(partial(self._valueFilled, widget))
        # widget.valueReset.connect(partial(self._valueReset, widget))

    # def updateProgress(self):
    #     self.progress.setMaxValue(len(self.progressStatuses.keys()))
    #     self.progress.update()

    def findWidget(self, clazz) -> Optional[ProfileFieldWidget]:
        for wdg in self.children:
            if isinstance(wdg, clazz):
                return wdg

    def collapse(self, collapsed: bool):
        self.btnHeader.setChecked(collapsed)

    def _toggleCollapse(self, checked: bool):
        self.wdgContainer.setHidden(checked)
        self.wdgBottom.setHidden(checked)

    # def _valueFilled(self, widget: ProfileFieldWidget, value: float):
    #     if self.progressStatuses[widget] == value:
    #         return
    #
    #     self.progressStatuses[widget] = value
    #     self.progress.setValue(sum(self.progressStatuses.values()))
    #
    # def _valueReset(self, widget: ProfileFieldWidget):
    #     if not self.progressStatuses[widget]:
    #         return
    #
    #     self.progressStatuses[widget] = 0
    #     self.progress.setValue(sum(self.progressStatuses.values()))

    def _initNewPrimaryField(self):
        label = TextInputDialog.edit(self.context.editorTitle(), self.context.editorPlaceholder())
        if label:
            self._addPrimaryField(flaw_placeholder_field, label)

    def _addPrimaryField(self, field: TemplateField, label: Optional[str] = None):
        attr = CharacterMultiAttribute(character_primary_attribute_type(field))
        if label:
            attr.label = label
        self.context.primaryAttributes(self.character).append(attr)
        field = CharacterProfileFieldReference(self.context.primaryFieldType(), ref=attr.id)
        self.section.fields.append(field)

        fieldWdg = field_widget(field, self.character)
        fieldWdg.removed.connect(partial(self._removePrimaryField, fieldWdg, field))
        fieldWdg.renamed.connect(partial(self._renamePrimaryField, fieldWdg))
        self.attachWidget(fieldWdg)

    def _removePrimaryField(self, wdg: 'MultiAttributesTemplateWidgetBase', fieldRef: CharacterProfileFieldReference):
        self.section.fields.remove(fieldRef)
        self.context.primaryAttributes(self.character).append(wdg.attribute)
        self.children.remove(wdg)
        fade_out_and_gc(self.wdgContainer, wdg)

    def _renamePrimaryField(self, wdg: 'MultiAttributesTemplateWidgetBase'):
        label = TextInputDialog.edit('Rename attribute', self.context.editorPlaceholder(), wdg.attribute.label)
        if label:
            wdg.attribute.label = label
            wdg.setLabel(label)


class SmallTextTemplateFieldWidget(TemplateFieldWidgetBase):
    def __init__(self, parent=None, minHeight: int = 60):
        super(SmallTextTemplateFieldWidget, self).__init__(parent)
        _layout = vbox(self, margin=self._boxMargin, spacing=self._boxSpacing)
        self.wdgEditor = AutoAdjustableTextEdit(height=minHeight)
        self.wdgEditor.setProperty('white-bg', True)
        self.wdgEditor.setProperty('rounded', True)
        self.wdgEditor.setAcceptRichText(False)
        self.wdgEditor.setTabChangesFocus(True)
        self.setMaximumWidth(600)

        self._filledBefore: bool = False

        self.wdgTop = group(self.lblEmoji, self.lblName, spacer())
        sp(self.wdgTop).v_max()
        _layout.addWidget(self.wdgTop)
        _layout.addWidget(self.wdgEditor)

        self.wdgEditor.textChanged.connect(self._textChanged)

    @overrides
    def value(self) -> Any:
        return self.wdgEditor.toPlainText()

    @overrides
    def setValue(self, value: Any):
        self.wdgEditor.setText(value)

    def _textChanged(self):
        text = self.wdgEditor.toPlainText()
        if text and not self._filledBefore:
            self.valueFilled.emit(1)
            self._filledBefore = True
        elif not text:
            self.valueReset.emit()
            self._filledBefore = False

        self._saveText(text)

    def _saveText(self, text: str):
        pass


class NoteField(SmallTextTemplateFieldWidget):
    def __init__(self, field: CharacterProfileFieldReference, parent=None):
        super().__init__(parent)
        self.field = field
        self.setValue(self.field.value)
        self.wdgEditor.setPlaceholderText('Write your notes...')

    @overrides
    def _saveText(self, text: str):
        self.field.value = text


class CustomTextField(SmallTextTemplateFieldWidget):
    def __init__(self, field: TemplateField, attribute, parent=None, minHeight: int = 60):
        super().__init__(parent, minHeight=minHeight)
        self.field = field
        self.attribute = attribute
        self.updateEmoji(emoji.emojize(self.field.emoji))
        self.updateLabel(self.field.name)
        self.wdgEditor.setPlaceholderText(self.field.placeholder)

        self.setValue(self.attribute.value)

    @overrides
    def _saveText(self, text: str):
        self.attribute.value = text


class SummaryField(SmallTextTemplateFieldWidget):
    def __init__(self, character: Character, parent=None):
        super().__init__(parent=parent)
        self.character = character
        self.wdgEditor.setPlaceholderText("Summarize your character's role in the story")
        self.setValue(self.character.summary)

        self.wdgTop.setHidden(True)

    @overrides
    def _saveText(self, text: str):
        self.character.summary = text


class LabelsTemplateFieldWidget(TemplateFieldWidgetBase):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.wdgEditor = self._editor()
        _layout = vbox(self)
        _layout.addWidget(group(self.lblEmoji, self.lblName, spacer()))
        _layout.addWidget(self.wdgEditor)

        self.wdgEditor.selectionChanged.connect(self._selectionChanged)

    @abstractmethod
    def _editor(self) -> LabelsSelectionWidget:
        pass

    @overrides
    def value(self) -> Any:
        return self.wdgEditor.value()

    @overrides
    def setValue(self, value: Any):
        self.wdgEditor.setValue(value)

    def _selectionChanged(self):
        value = self.value()
        if value:
            self.valueFilled.emit(1)
        else:
            self.valueReset.emit()

        self._saveValue(value)

    def _saveValue(self, value: Any):
        pass


class TraitsFieldWidget(LabelsTemplateFieldWidget):
    def __init__(self, character: Character, parent=None):
        super(TraitsFieldWidget, self).__init__(parent)
        self.character = character

        self.updateEmoji(emoji.emojize(':dna:'))
        self.updateLabel('Traits')

        self.setValue(self.character.traits)

    def save(self):
        self._saveValue(self.value())

    @overrides
    def _editor(self) -> LabelsSelectionWidget:
        return TraitSelectionWidget(traits_field)

    @overrides
    def _saveValue(self, value: Any):
        self.character.traits[:] = value


class ValuesFieldWidget(LabelsTemplateFieldWidget):
    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character

        self.updateEmoji(emoji.emojize(':smiling_face_with_open_hands:'))
        self.updateLabel('Values')

        self.setValue(self.character.values)

    @overrides
    def _editor(self) -> LabelsSelectionWidget:
        return LabelsSelectionWidget(values_field)

    @overrides
    def _saveValue(self, value: Any):
        self.character.values[:] = value


class TemplateFieldBarSlider(QSlider):
    def __init__(self, field: TemplateField, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(orientation, parent)
        self.setMinimum(field.min_value)
        self.setMaximum(field.max_value)
        if field.color:
            apply_slider_color(self, field.color)

    @overrides
    def wheelEvent(self, event: QWheelEvent) -> None:
        event.ignore()


class BarTemplateFieldWidget(TemplateFieldWidgetBase):
    def __init__(self, field: TemplateField, parent=None):
        super().__init__(parent)
        _layout = vbox(self)
        self.wdgEditor = TemplateFieldBarSlider(field)
        pointy(self.wdgEditor)
        self.wdgEditor.setPageStep(5)
        self.setMaximumWidth(600)

        _layout.addWidget(group(self.lblEmoji, self.lblName, spacer()))
        # if self.field.compact:
        #     editor = group(self.wdgEditor, spacer())
        #     margins(editor, left=5)
        #     _layout.addWidget(editor)
        # else:
        _layout.addWidget(wrap(self.wdgEditor, margin_left=5))

        self.wdgEditor.valueChanged.connect(self._valueChanged)

    @overrides
    def value(self) -> Any:
        return self.wdgEditor.value()

    @overrides
    def setValue(self, value: Any):
        self.wdgEditor.setValue(value)

    def _valueChanged(self, value: int):
        if value:
            self.valueFilled.emit(1)
        else:
            self.valueReset.emit()
        self._saveValue(value)

    def _saveValue(self, value: int):
        pass


class FacultyComparisonPopup(QWidget):
    def __init__(self, facultyType: CharacterProfileFieldType, field: TemplateField, character: Character, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setProperty('relaxed-white-bg', True)

        self.facultyType = facultyType
        self.field = field
        self.character = character
        self.novel: Optional[Novel] = None

        vbox(self, 10)

    def setNovel(self, novel: Novel):
        self.novel = novel

    def refresh(self):
        clear_layout(self)
        self.layout().addWidget(label(self.field.name, bold=True), alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(line(color=self.field.color))

        faculty_values = [x.faculties.get(self.facultyType.value, 0) for x in self.novel.characters]
        character_faculty_pairs = list(zip(self.novel.characters, faculty_values))
        sorted_characters = sorted(character_faculty_pairs, key=lambda pair: pair[1], reverse=True)
        top3_characters = [pair[0] for pair in sorted_characters[:min(3, len(sorted_characters))]]
        for character in top3_characters:
            self.__initSliderDisplay(character)

        if self.character not in top3_characters:
            self.layout().addWidget(line(color='lightgrey'))
            self.__initSliderDisplay(self.character)


    def __initSliderDisplay(self, character: Character):
        avatar = tool_btn(avatars.avatar(character), transparent_=True)
        slider = TemplateFieldBarSlider(self.field)
        slider.setValue(character.faculties.get(self.facultyType.value, 0))

        self.layout().addWidget(group(avatar, slider))


class FacultyField(BarTemplateFieldWidget):
    def __init__(self, facultyType: CharacterProfileFieldType, field: TemplateField, character: Character, parent=None):
        super().__init__(field, parent)
        self.facultyType = facultyType
        self.field = field
        self.character = character

        self.lblEmoji.setToolTip(field.description if field.description else field.placeholder)
        self.lblName.setText(self.field.name)
        self.lblName.setVisible(True)
        self.lblName.setToolTip(field.description if field.description else field.placeholder)

        self.popupDisplay = FacultyComparisonPopup(self.facultyType, self.field, self.character)
        self.popupDisplay.setHidden(True)

        if self.field.emoji:
            self.updateEmoji(emoji.emojize(self.field.emoji))
        else:
            self.lblEmoji.setHidden(True)

        # self.wdgEditor.setMinimum(field.min_value)
        # self.wdgEditor.setMaximum(field.max_value)
        # if field.color:
        #     apply_slider_color(self.wdgEditor, field.color)

        self.setValue(self.character.faculties.get(self.facultyType.value, 0))

        self.wdgEditor.installEventFilter(self)

    def setNovel(self, novel: Novel):
        self.popupDisplay.setNovel(novel)

    @overrides
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if event.type() == QEvent.Type.MouseButtonPress:
            self.popupDisplay.refresh()
            self.popupDisplay.move(
                self.mapToGlobal(self.lblEmoji.pos()) - QPoint(0, self.popupDisplay.sizeHint().height()))
            self.popupDisplay.show()
        elif event.type() == QEvent.Type.MouseButtonRelease:
            self.popupDisplay.hide()
        return super().eventFilter(watched, event)

    @overrides
    def _saveValue(self, value: int):
        self.character.faculties[self.facultyType.value] = value


class FieldToggle(QWidget):
    def __init__(self, field: TemplateField, parent=None):
        super().__init__(parent)
        self._field = field
        hbox(self)

        self._lblEmoji = QLabel(self)
        self._lblEmoji.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self._lblEmoji.setToolTip(field.description if field.description else field.placeholder)
        self._lblName = QLabel(self)
        self._lblName.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self._lblName.setText(self._field.name)
        self._lblName.setToolTip(field.description if field.description else field.placeholder)

        if self._field.emoji:
            self._lblEmoji.setFont(emoji_font())
            self._lblEmoji.setText(emoji.emojize(self._field.emoji))
        else:
            self._lblEmoji.setHidden(True)

        self.toggle = Toggle()

        self.layout().addWidget(self._lblEmoji)
        self.layout().addWidget(self._lblName)
        self.layout().addWidget(spacer())
        self.layout().addWidget(self.toggle)


class FieldSelector(QWidget):
    toggled = pyqtSignal(TemplateField, bool)
    clicked = pyqtSignal(TemplateField, bool)

    def __init__(self, fields: List[TemplateField], parent=None):
        super().__init__(parent)
        vbox(self)
        self._fields: Dict[TemplateField, FieldToggle] = {}

        for field in fields:
            wdg = FieldToggle(field)
            self._fields[field] = wdg
            self.layout().addWidget(wdg)
            wdg.toggle.toggled.connect(partial(self.toggled.emit, field))
            wdg.toggle.clicked.connect(partial(self.clicked.emit, field))

    def toggle(self, field: TemplateField):
        self._fields[field].toggle.toggle()


class _SecondaryFieldSelectorButton(QToolButton):
    removalRequested = pyqtSignal()
    renameRequested = pyqtSignal()

    def __init__(self, field: TemplateField, selector: FieldSelector, enableRename: bool = False, parent=None):
        super(_SecondaryFieldSelectorButton, self).__init__(parent)
        self._field = field
        self._selector = selector

        retain_when_hidden(self)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        transparent(self)
        pointy(self)
        self.setIconSize(QSize(22, 22))
        self.setIcon(IconRegistry.plus_edit_icon())

        menu = MenuWidget(self)
        menu.addWidget(self._selector)
        menu.addSeparator()

        if enableRename:
            menu.addAction(action('Rename', IconRegistry.edit_icon(), slot=self.renameRequested))
            menu.addSeparator()

        menu.addAction(action(f'Remove {self._field.name}', IconRegistry.trash_can_icon(), slot=self.removalRequested))
        self.installEventFilter(OpacityEventFilter(self, leaveOpacity=0.7))


class _PrimaryFieldWidget(QWidget):
    removed = pyqtSignal()
    renamed = pyqtSignal()
    valueChanged = pyqtSignal()

    def __init__(self, attribute: CharacterMultiAttribute, field: TemplateField, secondaryFields: List[TemplateField],
                 parent=None):
        super().__init__(parent)
        self.attribute = attribute
        self._field = field
        self._secondaryFields = secondaryFields
        self._secondaryFieldWidgets: Dict[TemplateField, Optional[SmallTextTemplateFieldWidget]] = {}
        for sf in secondaryFields:
            self._secondaryFieldWidgets[sf] = None
        vbox(self, 0, 2)
        self._primaryWdg = CustomTextField(field, self.attribute)
        self._primaryWdg.valueFilled.connect(self.valueChanged.emit)
        self._primaryWdg.valueReset.connect(self.valueChanged.emit)

        self._selector = FieldSelector(secondaryFields)
        btnSecondary = _SecondaryFieldSelectorButton(self._field, self._selector,
                                                     enableRename=field.id == flaw_placeholder_field.id)
        btnSecondary.removalRequested.connect(self.removed)
        btnSecondary.renameRequested.connect(self.renamed)
        self._selector.toggled.connect(self._toggleSecondaryField)
        self._selector.clicked.connect(self._clickSecondaryField)
        insert_before_the_end(self._primaryWdg.wdgTop, btnSecondary)

        self._secondaryWdgContainer = QWidget()
        vbox(self._secondaryWdgContainer, 0, 2)
        margins(self._secondaryWdgContainer, left=40)
        for _ in self._secondaryFields:
            self._secondaryWdgContainer.layout().addWidget(spacer())

        top = QWidget()
        hbox(top)
        top.layout().addWidget(self._primaryWdg)
        spacer_ = spacer()
        sp(spacer_).h_preferred()
        top.layout().addWidget(spacer_)
        self.layout().addWidget(top)
        self.layout().addWidget(self._secondaryWdgContainer)

        for value, toggled in self.attribute.settings.items():
            if toggled:
                self._selector.toggle(character_secondary_field(value))

        self.installEventFilter(VisibilityToggleEventFilter(btnSecondary, self._primaryWdg))

    def field(self) -> TemplateField:
        return self._field

    def value(self) -> str:
        return self._primaryWdg.value()

    def setValue(self, value: str):
        self._primaryWdg.setValue(value)

    def refresh(self):
        self._primaryWdg.refresh()

    def setLabel(self, label: str):
        self._primaryWdg.updateLabel(label)

    def secondaryFields(self) -> List[Tuple[str, str]]:
        fields = []
        for field, wdg in self._secondaryFieldWidgets.items():
            if wdg is None:
                continue
            fields.append((str(field.id), wdg.value()))

        return fields

    def setSecondaryField(self, secondary: TemplateField, value: str):
        self._selector.toggle(secondary)
        self._secondaryFieldWidgets[secondary].setValue(value)

    def _toggleSecondaryField(self, secondary: TemplateField, toggled: bool):
        i = self._secondaryFields.index(secondary)

        if toggled:
            type_ = character_secondary_attribute_type(secondary)
            secondary_attribute = self.attribute.attributes.get(type_.value)
            if secondary_attribute is None:
                secondary_attribute = CharacterSecondaryAttribute(type_)
                self.attribute.attributes[type_.value] = secondary_attribute
            wdg = CustomTextField(secondary, secondary_attribute, minHeight=50)
            wdg.valueFilled.connect(self.valueChanged.emit)
            wdg.valueReset.connect(self.valueChanged.emit)
            self._secondaryFieldWidgets[secondary] = wdg
            item = self._secondaryWdgContainer.layout().itemAt(i)
            icon = Icon()
            icon.setIcon(IconRegistry.from_name('msc.dash', 'grey'))
            spac = spacer()
            sp(spac).h_preferred()
            self._secondaryWdgContainer.layout().replaceWidget(item.widget(), group(icon, wdg, spac))
        else:
            self._secondaryWdgContainer.layout().replaceWidget(self._secondaryFieldWidgets[secondary], spacer())
            gc(self._secondaryFieldWidgets[secondary])
            self._secondaryFieldWidgets[secondary] = None

    def _clickSecondaryField(self, secondary: TemplateField, toggled: bool):
        self.attribute.settings[character_secondary_attribute_type(secondary).value] = toggled
        self.valueChanged.emit()


class MultiAttributesTemplateWidgetBase(ProfileFieldWidget):
    removed = pyqtSignal()
    renamed = pyqtSignal()

    def __init__(self, attribute: CharacterMultiAttribute, character: Character, parent=None):
        super().__init__(parent)
        self.attribute = attribute
        # self.field = field
        self.character = character
        self._hasAlias = False

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        self._layout: QVBoxLayout = vbox(self, 0, 5)

        field = character_primary_field(attribute.type)
        self._wdgPrimary = _PrimaryFieldWidget(self.attribute, field, self._secondaryFields(field))
        self._wdgPrimary.removed.connect(self.removed)
        self._wdgPrimary.renamed.connect(self.renamed)
        self.layout().addWidget(self._wdgPrimary)

        self._layout.addWidget(vspacer())

    def setLabel(self, label: str):
        self._wdgPrimary.setLabel(label)

    def _secondaryFields(self, primary: TemplateField) -> List[TemplateField]:
        return []

    def _removePrimaryField(self, wdg: _PrimaryFieldWidget):
        self._primaryWidgets.remove(wdg)
        self._layout.removeWidget(wdg)
        gc(wdg)

    def _renamePrimaryField(self, wdg: _PrimaryFieldWidget):
        pass

    def _valueChanged(self):
        count = 0
        value = 0
        for wdg in self._primaryWidgets:
            count += 1
            if wdg.value():
                value += 1
            for _, v in wdg.secondaryFields():
                count += 1
                if v:
                    value += 1
        self.valueFilled.emit(value / count if count else 0)


class MultiAttributeSectionContext(SectionContext):

    @overrides
    def has_addition(self) -> bool:
        return True

    @overrides
    def has_menu(self) -> bool:
        return True


class GmcSectionContext(MultiAttributeSectionContext):
    @overrides
    def primaryButtonText(self) -> str:
        return 'Add new goal'

    @overrides
    def primaryFields(self) -> List[TemplateField]:
        return [goal_field, internal_goal_field]

    @overrides
    def primaryAttributes(self, character: Character) -> List[CharacterMultiAttribute]:
        return character.gmc

    @overrides
    def primaryFieldType(self) -> CharacterProfileFieldType:
        return CharacterProfileFieldType.Field_Goals


class BaggageSectionContext(MultiAttributeSectionContext):

    @overrides
    def primaryButtonText(self) -> str:
        return 'Add new baggage'

    @overrides
    def primaryFields(self) -> List[TemplateField]:
        return [ghost_field, wound_field, demon_field, fear_field, misbelief_field]

    @overrides
    def primaryAttributes(self, character: Character) -> List[CharacterMultiAttribute]:
        return character.baggage

    @overrides
    def primaryFieldType(self) -> CharacterProfileFieldType:
        return CharacterProfileFieldType.Field_Baggage


class FlawsSectionContext(MultiAttributeSectionContext):

    @overrides
    def has_menu(self) -> bool:
        return False

    @overrides
    def primaryButtonText(self) -> str:
        return 'Add new flaw'

    @overrides
    def primaryFields(self) -> List[TemplateField]:
        return [flaw_placeholder_field]

    @overrides
    def primaryAttributes(self, character: Character) -> List[CharacterMultiAttribute]:
        return character.flaws

    @overrides
    def primaryFieldType(self) -> CharacterProfileFieldType:
        return CharacterProfileFieldType.Field_Flaws

    @overrides
    def editorTitle(self) -> str:
        return 'Define a character flaw'

    @overrides
    def editorPlaceholder(self) -> str:
        return 'Name of the flaw'


class GmcFieldWidget(MultiAttributesTemplateWidgetBase):

    def __init__(self, attribute: CharacterMultiAttribute, character: Character,
                 ref: CharacterProfileFieldReference, parent=None):
        super().__init__(attribute, character, parent=parent)
        self.ref = ref

    @overrides
    def _secondaryFields(self, primary: TemplateField) -> List[TemplateField]:
        if primary.id == goal_field.id:
            return [stakes_field, conflict_field, motivation_field, methods_field, internal_motivation_field,
                    internal_conflict_field,
                    internal_stakes_field]
        else:
            return [methods_field, internal_motivation_field, internal_conflict_field, internal_stakes_field]


class BaggageFieldWidget(MultiAttributesTemplateWidgetBase):

    def __init__(self, attribute: CharacterMultiAttribute, character: Character,
                 ref: CharacterProfileFieldReference, parent=None):
        super().__init__(attribute, character, parent=parent)
        self.ref = ref

    @overrides
    def _secondaryFields(self, primary: TemplateField) -> List[TemplateField]:
        elements = [baggage_source_field, baggage_manifestation_field,
                    baggage_relation_field, baggage_coping_field, baggage_healing_field, baggage_deterioration_field]

        if primary.id != ghost_field.id:
            elements.insert(3, baggage_defense_mechanism_field)

        if primary.id in [wound_field.id, ghost_field.id, demon_field.id]:
            elements.insert(1, baggage_trigger_field)

        return elements


class FlawsFieldWidget(MultiAttributesTemplateWidgetBase):

    def __init__(self, attribute: CharacterMultiAttribute, character: Character,
                 ref: CharacterProfileFieldReference, parent=None):
        super().__init__(attribute, character, parent=parent)
        self.ref = ref
        self.setLabel(attribute.label)

    @overrides
    def _secondaryFields(self, primary: TemplateField) -> List[TemplateField]:
        return [flaw_triggers_field, flaw_coping_field, flaw_manifestation_field, flaw_relation_field, flaw_goals_field,
                flaw_growth_field, flaw_deterioration_field]


class StrengthsWeaknessesHeader(QWidget):
    edit = pyqtSignal()
    remove = pyqtSignal()

    def __init__(self, attribute: StrengthWeaknessAttribute, parent=None):
        super().__init__(parent)
        self.attribute = attribute
        hbox(self, 0)

        self.btnKey = push_btn(text=self.attribute.name, transparent_=True)
        bold(self.btnKey)
        self.btnKey.clicked.connect(self.edit)

        self.btnMenu = DotsMenuButton()
        self.btnMenu.installEventFilter(OpacityEventFilter(self.btnMenu))
        retain_when_hidden(self.btnMenu)

        menu = MenuWidget(self.btnMenu)
        menu.addAction(action('Edit', IconRegistry.edit_icon(), slot=self.edit))
        menu.addSeparator()
        menu.addAction(action('Remove', IconRegistry.trash_can_icon(), slot=self.remove))

        self.layout().addWidget(self.btnKey, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout().addWidget(self.btnMenu, alignment=Qt.AlignmentFlag.AlignRight)

        self.installEventFilter(VisibilityToggleEventFilter(self.btnMenu, self))

    def refreshAttribute(self, attribute: StrengthWeaknessAttribute):
        self.attribute.name = attribute.name
        self.attribute.has_strength = attribute.has_strength
        self.attribute.has_weakness = attribute.has_weakness
        self.btnKey.setText(self.attribute.name)


class StrengthsWeaknessesTableRow(QWidget):
    changed = pyqtSignal()

    def __init__(self, attribute: StrengthWeaknessAttribute, parent=None):
        super().__init__(parent)
        self.attribute = attribute
        hbox(self, 0, spacing=10)
        self.textStrength = self._textEditor()
        self.textStrength.setPlaceholderText('Define the strength of this attribute')
        self.textStrength.setText(self.attribute.strength)
        self.textStrength.textChanged.connect(self._strengthChanged)

        self.textWeakness = self._textEditor()
        self.textWeakness.setPlaceholderText('Define the weakness of this attribute')
        self.textWeakness.setText(self.attribute.weakness)
        self.textWeakness.textChanged.connect(self._weaknessChanged)

        self.layout().addWidget(self.textStrength)
        self.layout().addWidget(self.textWeakness)

        self.textStrength.setVisible(self.attribute.has_strength)
        self.textWeakness.setVisible(self.attribute.has_weakness)

    def refreshAttribute(self, attribute: StrengthWeaknessAttribute):
        self.attribute = attribute
        self.attribute.strength = self.textStrength.toPlainText()
        self.attribute.weakness = self.textWeakness.toPlainText()
        self.textStrength.setVisible(self.attribute.has_strength)
        self.textWeakness.setVisible(self.attribute.has_weakness)

    def _strengthChanged(self):
        self.attribute.strength = self.textStrength.toPlainText()
        self.changed.emit()

    def _weaknessChanged(self):
        self.attribute.weakness = self.textWeakness.toPlainText()
        self.changed.emit()

    def _textEditor(self) -> AutoAdjustableTextEdit:
        editor = AutoAdjustableTextEdit(height=75)
        editor.setMaximumWidth(500)
        editor.setProperty('white-bg', True)
        editor.setProperty('rounded', True)
        retain_when_hidden(editor)
        return editor


class StrengthsWeaknessesFieldWidget(TemplateFieldWidgetBase):
    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character
        self._rows: List[StrengthsWeaknessesTableRow] = []

        vbox(self, 0)
        self._center = QWidget()
        self._centerlayout: QGridLayout = grid(self._center, 0, 0, 5)
        margins(self._centerlayout, left=5)
        self._centerlayout.setColumnMinimumWidth(0, 70)
        self._centerlayout.setColumnStretch(1, 1)
        self._centerlayout.setColumnStretch(2, 1)

        self.emojiStrength = label('')
        self.emojiStrength.setFont(emoji_font())
        self.emojiStrength.setText(emoji.emojize(':flexed_biceps:'))
        self.emojiWeakness = label('')
        self.emojiWeakness.setFont(emoji_font())
        self.emojiWeakness.setText(emoji.emojize(':nauseated_face:'))
        self.lblStrength = label('Strength', underline=True)
        self.lblWeakness = label('Weakness', underline=True)
        incr_font(self.lblStrength)
        incr_font(self.lblWeakness)
        self._centerlayout.addWidget(group(self.emojiStrength, self.lblStrength), 0, 1,
                                     alignment=Qt.AlignmentFlag.AlignCenter)
        self._centerlayout.addWidget(group(self.emojiWeakness, self.lblWeakness), 0, 2,
                                     alignment=Qt.AlignmentFlag.AlignCenter)

        self._btnPrimary = SecondaryActionPushButton()
        self._btnPrimary.setText('Add new attribute')
        self._btnPrimary.setIcon(IconRegistry.plus_icon('grey'))
        self._btnPrimary.clicked.connect(self._addNewAttribute)
        decr_font(self._btnPrimary)

        self.layout().addWidget(self._center)
        self.layout().addWidget(wrap(self._btnPrimary, margin_left=5), alignment=Qt.AlignmentFlag.AlignLeft)

        for strength in self.character.strengths:
            self._addAttribute(strength)

    @property
    def wdgEditor(self):
        return self

    # @overrides
    # def value(self) -> Any:
    #     values = []
    #     for row in self._rows:
    #         values.append({
    #             'key': row.attribute.name,
    #             'has_strength': row.attribute.has_strength,
    #             'has_weakness': row.attribute.has_weakness,
    #             'strength': row.attribute.strength,
    #             'weakness': row.attribute.weakness
    #         })
    #
    #     return values

    # @overrides
    # def setValue(self, value: Any):
    #     self._rows.clear()
    #     if value is None:
    #         return
    #     if isinstance(value, str):
    #         return
    #
    #     for item in value:
    #         attribute = StrengthWeaknessAttribute(item.get('key', ''),
    #                                               has_strength=item.get('has_strength', True),
    #                                               has_weakness=item.get('has_weakness', True),
    #                                               strength=item.get('strength', ''),
    #                                               weakness=item.get('weakness', '')
    #                                               )
    #         self._addAttribute(attribute)
    #
    #     self._valueChanged()

    def _addNewAttribute(self):
        attribute = StrengthWeaknessEditor.popup()
        if attribute:
            header, rowWdg = self._addAttribute(attribute)
            qtanim.fade_in(header, teardown=lambda: header.setGraphicsEffect(None))
            qtanim.fade_in(rowWdg, teardown=lambda: rowWdg.setGraphicsEffect(None))
            self._valueChanged()
            self.character.strengths.append(attribute)

    def _addAttribute(self, attribute: StrengthWeaknessAttribute):
        rowWdg = StrengthsWeaknessesTableRow(attribute)
        rowWdg.changed.connect(self._valueChanged)
        self._rows.append(rowWdg)
        header = StrengthsWeaknessesHeader(attribute)
        header.edit.connect(partial(self._edit, header, rowWdg))
        header.remove.connect(partial(self._remove, header, rowWdg))

        row = self._centerlayout.rowCount()
        self._centerlayout.addWidget(header, row, 0, alignment=Qt.AlignmentFlag.AlignTop)
        self._centerlayout.addWidget(rowWdg, row, 1, 1, 2)

        return header, rowWdg

    def _edit(self, header: StrengthsWeaknessesHeader, row: StrengthsWeaknessesTableRow):
        attribute = StrengthWeaknessEditor.popup(header.attribute)
        if attribute:
            header.refreshAttribute(attribute)
            row.refreshAttribute(attribute)
            self._valueChanged()

    def _remove(self, header: StrengthsWeaknessesHeader, row: StrengthsWeaknessesTableRow):
        self.character.strengths.remove(header.attribute)
        self._rows.remove(row)
        fade_out_and_gc(self._center, header)
        fade_out_and_gc(self._center, row)

    def _valueChanged(self):
        count = 0
        value = 0
        for wdg in self._rows:
            if wdg.attribute.has_strength:
                count += 1
                if wdg.attribute.strength:
                    value += 1
            if wdg.attribute.has_weakness:
                count += 1
                if wdg.attribute.weakness:
                    value += 1
        self.valueFilled.emit(value / count if count else 0)


class EnneagramFieldWidget(TemplateFieldWidgetBase):
    def __init__(self, character: Character, parent=None):
        super(EnneagramFieldWidget, self).__init__(parent)
        self.character = character
        self.wdgEditor = EnneagramSelector()
        self._defaultTooltip: str = 'Select Enneagram personality'
        _layout = vbox(self)
        _layout.addWidget(self.wdgEditor, alignment=Qt.AlignmentFlag.AlignTop)

        emojiDesire = Emoji()
        emojiDesire.setText(emoji.emojize(':smiling_face:'))
        emojiDesire.setToolTip('Core desire')
        emojiFear = Emoji()
        emojiFear.setText(emoji.emojize(':face_screaming_in_fear:'))
        emojiFear.setToolTip('Core fear')
        self.lblDesire = label(wordWrap=True)
        sp(self.lblDesire).h_exp()
        self.lblDesire.setToolTip('Core desire')
        self.lblFear = label(wordWrap=True)
        sp(self.lblFear).h_exp()
        self.lblFear.setToolTip('Core fear')

        decr_font(emojiDesire, 2)
        decr_font(self.lblDesire)
        decr_font(emojiFear, 2)
        decr_font(self.lblFear)

        self.wdgAttr = group(
            group(dash_icon(), emojiDesire, self.lblDesire, spacer()),
            group(dash_icon(), emojiFear, self.lblFear, spacer()),
            vertical=False)
        margins(self.wdgAttr, left=10)
        _layout.addWidget(self.wdgAttr)
        self.wdgAttr.setHidden(True)

        _layout.addWidget(spacer())

        self.wdgEditor.selected.connect(self._selectionChanged)

        if self.character.personality.enneagram:
            self.setValue(self.character.personality.enneagram.value)

    @overrides
    def value(self) -> Any:
        return self.wdgEditor.value()

    @overrides
    def setValue(self, value: Any):
        self.wdgEditor.setValue(value)
        enneagram = enneagram_choices.get(value)
        if enneagram:
            self._selectionChanged(enneagram)
        elif value is None:
            self._ignored()
        else:
            self.wdgEditor.setToolTip(self._defaultTooltip)

    def _selectionChanged(self, item: SelectionItem):
        self.valueFilled.emit(1)

        if self.character.personality.enneagram is None:
            self.character.personality.enneagram = CharacterPersonalityAttribute()
        self.character.personality.enneagram.value = item.text

        self.lblDesire.setText(item.meta['desire'])
        self.lblFear.setText(item.meta['fear'])
        self.wdgEditor.setToolTip(enneagram_help[item.text])
        if self.isVisible():
            qtanim.fade_in(self.wdgAttr)
        else:
            self.wdgAttr.setVisible(True)


class MbtiFieldWidget(TemplateFieldWidgetBase):
    def __init__(self, character: Character, parent=None):
        super(MbtiFieldWidget, self).__init__(parent)
        self.character = character
        self.wdgEditor = MbtiSelector()
        self._defaultTooltip: str = 'Select MBTI personality type'
        self.wdgEditor.setToolTip(self._defaultTooltip)

        _layout = vbox(self)
        _layout.addWidget(self.wdgEditor)

        self.lblKeywords = label(wordWrap=True)
        decr_font(self.lblKeywords)

        self.wdgAttr = group(dash_icon(), self.lblKeywords, spacer())
        margins(self.wdgAttr, left=10)
        _layout.addWidget(self.wdgAttr)
        self.wdgAttr.setHidden(True)

        _layout.addWidget(spacer())

        self.wdgEditor.selected.connect(self._selectionChanged)

        if self.character.personality.mbti:
            self.setValue(self.character.personality.mbti.value)

    @overrides
    def value(self) -> Any:
        return self.wdgEditor.value()

    @overrides
    def setValue(self, value: Any):
        self.wdgEditor.setValue(value)
        if value:
            mbti = mbti_choices[value]
            self._selectionChanged(mbti)
        elif value is None:
            self._ignored()
        else:
            self.wdgEditor.setToolTip(self._defaultTooltip)

    def _selectionChanged(self, item: SelectionItem):
        if self.character.personality.mbti is None:
            self.character.personality.mbti = CharacterPersonalityAttribute()
        self.character.personality.mbti.value = item.text

        self.lblKeywords.setText(mbti_keywords.get(item.text, ''))
        if self.isVisible():
            qtanim.fade_in(self.wdgAttr)
        else:
            self.wdgAttr.setVisible(True)

        self.wdgEditor.setToolTip(mbti_help[item.text])
        self.valueFilled.emit(1)


class LoveStyleFieldWidget(TemplateFieldWidgetBase):
    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character
        self.wdgEditor = LoveStyleSelector()
        self._defaultTooltip: str = 'Select love style'
        _layout = vbox(self)
        _layout.addWidget(self.wdgEditor, alignment=Qt.AlignmentFlag.AlignLeft)

        self.emoji = Emoji()
        self.lblKeywords = label(wordWrap=True)
        decr_font(self.emoji, 2)
        decr_font(self.lblKeywords)

        self.wdgAttr = group(dash_icon(), self.emoji, self.lblKeywords, spacer())
        margins(self.wdgAttr, left=10)
        _layout.addWidget(self.wdgAttr)
        self.wdgAttr.setHidden(True)

        self.wdgEditor.selected.connect(self._selectionChanged)

        if self.character.personality.love:
            self.setValue(self.character.personality.love.value)

    @overrides
    def value(self) -> Any:
        return self.wdgEditor.value()

    @overrides
    def setValue(self, value: Any):
        self.wdgEditor.setValue(value)
        if value:
            mbti = love_style_choices[value]
            self._selectionChanged(mbti)
        else:
            self.wdgEditor.setToolTip(self._defaultTooltip)

    def _selectionChanged(self, item: SelectionItem):
        if self.character.personality.love is None:
            self.character.personality.love = CharacterPersonalityAttribute()
        self.character.personality.love.value = item.text

        self.emoji.setText(emoji.emojize(item.meta['emoji']))
        self.lblKeywords.setText(item.meta['desc'])
        self.wdgEditor.setToolTip(love_style_help[item.text])
        if self.isVisible():
            qtanim.fade_in(self.wdgAttr)
        else:
            self.wdgAttr.setVisible(True)


class WorkStyleFieldWidget(TemplateFieldWidgetBase):
    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character
        self.wdgEditor = DiscSelector()
        self._defaultTooltip: str = 'Select work style'
        _layout = vbox(self)
        _layout.addWidget(self.wdgEditor, alignment=Qt.AlignmentFlag.AlignLeft)

        self.emoji = Emoji()
        self.lblKeywords = label(wordWrap=True)
        decr_font(self.emoji, 2)
        decr_font(self.lblKeywords)

        self.wdgAttr = group(dash_icon(), self.emoji, self.lblKeywords, spacer())
        margins(self.wdgAttr, left=10)
        _layout.addWidget(self.wdgAttr)
        self.wdgAttr.setHidden(True)

        self.wdgEditor.selected.connect(self._selectionChanged)

        if self.character.personality.work:
            self.setValue(self.character.personality.work.value)

    @overrides
    def value(self) -> Any:
        return self.wdgEditor.value()

    @overrides
    def setValue(self, value: Any):
        self.wdgEditor.setValue(value)
        if value:
            style = work_style_choices[value]
            self._selectionChanged(style)
        else:
            self.wdgEditor.setToolTip(self._defaultTooltip)

    def _selectionChanged(self, item: SelectionItem):
        if self.character.personality.work is None:
            self.character.personality.work = CharacterPersonalityAttribute()
        self.character.personality.work.value = item.text

        self.emoji.setText(emoji.emojize(item.meta['emoji']))
        self.lblKeywords.setText(item.meta['desc'])
        self.wdgEditor.setToolTip(work_style_help[item.text])
        if self.isVisible():
            qtanim.fade_in(self.wdgAttr)
        else:
            self.wdgAttr.setVisible(True)


class PersonalityFieldWidget(TemplateFieldWidgetBase):
    ignored = pyqtSignal(NovelSetting)
    enneagramChanged = pyqtSignal(str)

    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self.character = character

        self._layout: QGridLayout = grid(self)
        self._widgets: Dict[NovelSetting, TemplateFieldWidgetBase] = {}

        enneagram = EnneagramFieldWidget(self.character)
        enneagram.valueFilled.connect(lambda: self.enneagramChanged.emit(enneagram.value()))

        self._addWidget(NovelSetting.Character_enneagram, enneagram, 0, 0)
        self._addWidget(NovelSetting.Character_mbti, MbtiFieldWidget(self.character), 0, 1)
        self._addWidget(NovelSetting.Character_love_style, LoveStyleFieldWidget(self.character), 1, 0)
        self._addWidget(NovelSetting.Character_work_style, WorkStyleFieldWidget(self.character), 1, 1)

    def toggle(self, setting: NovelSetting, toggled: bool):
        self._widgets[setting].setVisible(toggled)

    def _addWidget(self, setting: NovelSetting, wdg: TemplateFieldWidgetBase, row: int, col: int):
        self._widgets[setting] = wdg
        self._layout.addWidget(wdg, row, col)
        wdg.setVisible(self.character.prefs.toggled(setting))
        wdg.wdgEditor.ignored.connect(partial(self.ignored.emit, setting))


def field_widget(ref: CharacterProfileFieldReference, character: Character) -> ProfileFieldWidget:
    if ref.type == CharacterProfileFieldType.Field_Summary:
        return SummaryField(character)
    elif ref.type.name.startswith('Field_Faculties'):
        if ref.type == CharacterProfileFieldType.Field_Faculties_IQ:
            field = iq_field
        elif ref.type == CharacterProfileFieldType.Field_Faculties_EQ:
            field = eq_field
        elif ref.type == CharacterProfileFieldType.Field_Faculties_Rationalism:
            field = rationalism_field
        elif ref.type == CharacterProfileFieldType.Field_Faculties_Willpower:
            field = willpower_field
        elif ref.type == CharacterProfileFieldType.Field_Faculties_Creativity:
            field = creativity_field
        else:
            raise ValueError(f'Unrecognized field type {ref.type}')
        return FacultyField(ref.type, field, character)
    elif ref.type == CharacterProfileFieldType.Field_Personality:
        return PersonalityFieldWidget(character)
    elif ref.type == CharacterProfileFieldType.Field_Traits:
        return TraitsFieldWidget(character)
    elif ref.type == CharacterProfileFieldType.Field_Values:
        return ValuesFieldWidget(character)
    elif ref.type == CharacterProfileFieldType.Field_Goals:
        attribute = None
        for gmc in character.gmc:
            if gmc.id == ref.ref:
                attribute = gmc
                break
        return GmcFieldWidget(attribute, character, ref)
    elif ref.type == CharacterProfileFieldType.Field_Baggage:
        attribute = None
        for baggage in character.baggage:
            if baggage.id == ref.ref:
                attribute = baggage
                break
        return BaggageFieldWidget(attribute, character, ref)
    elif ref.type == CharacterProfileFieldType.Field_Flaws:
        attribute = None
        for flaw in character.flaws:
            if flaw.id == ref.ref:
                attribute = flaw
                break
        return FlawsFieldWidget(attribute, character, ref)
    elif ref.type == CharacterProfileFieldType.Field_Strengths:
        return StrengthsWeaknessesFieldWidget(character)
    else:
        return NoteField(ref)


class SectionSettingToggle(SettingBaseWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, section: CharacterProfileSectionReference, parent=None):
        super().__init__(parent)
        self.section = section

        if self.section.type:
            self._title.setText(self.section.type.name)
        self._description.setHidden(True)

        self._toggle.setChecked(self.section.enabled)

    @overrides
    def _clicked(self, toggled: bool):
        self.section.enabled = toggled
        self.toggled.emit(toggled)


class PersonalitySettingToggle(SettingBaseWidget):
    toggled = pyqtSignal(bool)

    def __init__(self, character: Character, personality: NovelSetting, parent=None):
        super().__init__(parent)
        self.character = character
        self._personality = personality

        self._title.setText(setting_titles[personality])
        self._description.setHidden(True)

        self._toggle.setChecked(self.character.prefs.toggled(personality))

    @overrides
    def _clicked(self, toggled: bool):
        self.character.prefs.settings[self._personality.value] = toggled
        self.toggled.emit(toggled)


class SectionSettings(QWidget):
    toggled = pyqtSignal(CharacterProfileSectionReference, bool)
    personalityToggled = pyqtSignal(NovelSetting, bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        vbox(self)
        self._sections: Dict[CharacterProfileSectionType, SectionSettingToggle] = {}
        self._personalities: Dict[NovelSetting, PersonalitySettingToggle] = {}
        self._character: Optional[Character] = None

    def refresh(self, character: Character):
        self._character = character

        clear_layout(self)
        for section in character.profile:
            wdg = SectionSettingToggle(section)
            self._sections[section.type] = wdg
            wdg.toggled.connect(partial(self.toggled.emit, section))
            self.layout().addWidget(wdg)

            if section.type == CharacterProfileSectionType.Personality:
                for personality in [NovelSetting.Character_enneagram, NovelSetting.Character_mbti,
                                    NovelSetting.Character_love_style, NovelSetting.Character_work_style]:
                    child = PersonalitySettingToggle(character, personality)
                    self._personalities[personality] = child
                    child.toggled.connect(partial(self.personalityToggled.emit, personality))
                    wdg.addChild(child)

    def toggleSection(self, sectionType: CharacterProfileSectionType, toggled: bool):
        self._sections[sectionType].setChecked(toggled)
        self._sections[sectionType].section.enabled = toggled

    def togglePersonality(self, personality: NovelSetting, toggled: bool):
        self._personalities[personality].setChecked(toggled)
        self._character.prefs.settings[personality.value] = toggled


class CharacterProfileEditor(QWidget):
    def __init__(self, novel: Novel, parent=None):
        super().__init__(parent)
        self._novel = novel
        self._character: Optional[Character] = None
        self.btnCustomize = tool_btn(IconRegistry.preferences_icon(), tooltip='Customize character profile', base=True,
                                     parent=self)
        menu = MenuWidget(self.btnCustomize)
        apply_white_menu(menu)
        self._settings = SectionSettings()
        menu.addWidget(self._settings)
        self._settings.toggled.connect(self._sectionToggled)
        self._settings.personalityToggled.connect(self._personalityToggled)

        self._sections: Dict[CharacterProfileSectionType, ProfileSectionWidget] = {}

        vbox(self)

    def setCharacter(self, character: Character):
        self._character = character
        self._settings.refresh(character)
        self.refresh()

    @overrides
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._setBtnSettingsGeometry(event.size().width())

    def refresh(self):
        clear_layout(self)

        for section in self._character.profile:
            sc = SectionContext()
            if section.type == CharacterProfileSectionType.Goals:
                sc = GmcSectionContext()
            elif section.type == CharacterProfileSectionType.Baggage:
                sc = BaggageSectionContext()
            elif section.type == CharacterProfileSectionType.Flaws:
                sc = FlawsSectionContext()
            wdg = ProfileSectionWidget(section, sc, self._character)
            self._sections[section.type] = wdg

            self.layout().addWidget(wdg)
            wdg.setVisible(section.enabled)
            for field in section.fields:
                fieldWdg = field_widget(field, self._character)
                wdg.attachWidget(fieldWdg)

                if section.type == CharacterProfileSectionType.Personality and isinstance(fieldWdg,
                                                                                          PersonalityFieldWidget):
                    fieldWdg.enneagramChanged.connect(self._enneagramChanged)
                    fieldWdg.ignored.connect(self._personalityIgnored)
                elif section.type == CharacterProfileSectionType.Faculties and isinstance(fieldWdg, FacultyField):
                    fieldWdg.setNovel(self._novel)

        self.layout().addWidget(vspacer())

        self.btnCustomize.raise_()

    def applyMinorRoleSettings(self):
        for personality in [NovelSetting.Character_enneagram, NovelSetting.Character_mbti,
                            NovelSetting.Character_love_style, NovelSetting.Character_work_style]:
            self._personalityToggled(personality, False)
            self._settings.togglePersonality(personality, False)

        for sectionType in [CharacterProfileSectionType.Summary, CharacterProfileSectionType.Personality]:
            self._sections[sectionType].setVisible(True)
            self._settings.toggleSection(sectionType, True)

        for sectionType in [CharacterProfileSectionType.Philosophy, CharacterProfileSectionType.Strengths,
                            CharacterProfileSectionType.Faculties, CharacterProfileSectionType.Flaws,
                            CharacterProfileSectionType.Baggage,
                            CharacterProfileSectionType.Goals
                            ]:
            self._sections[sectionType].setVisible(False)
            self._settings.toggleSection(sectionType, False)

        self._highlightSettingsButton(resize=True)

    def _sectionToggled(self, section: CharacterProfileSectionReference):
        self._sections[section.type].setVisible(section.enabled)

    def _personalityToggled(self, personality: NovelSetting, toggled: bool):
        wdg: Optional[PersonalityFieldWidget] = self._sections[CharacterProfileSectionType.Personality].findWidget(
            PersonalityFieldWidget)
        if wdg:
            wdg.toggle(personality, toggled)

    def _personalityIgnored(self, personality: NovelSetting):
        self._personalityToggled(personality, False)
        self._settings.togglePersonality(personality, False)

        self._highlightSettingsButton()

    def _setBtnSettingsGeometry(self, width: int, baseSize: int = 25):
        self.btnCustomize.setGeometry(width - baseSize - 5, 2, baseSize, baseSize)

    def _highlightSettingsButton(self, resize: bool = False):
        def finished():
            if resize:
                self._setBtnSettingsGeometry(self.width())

        if resize:
            self._setBtnSettingsGeometry(self.width(), baseSize=32)
        qtanim.glow(self.btnCustomize, color=QColor(PLOTLYST_MAIN_COLOR), loop=3, duration=100, radius=14,
                    teardown=finished)

    def _enneagramChanged(self, enneagram: str):
        wdgTraits: Optional[TraitsFieldWidget] = self._sections[CharacterProfileSectionType.Personality].findWidget(
            TraitsFieldWidget)
        if wdgTraits:
            if self._character.personality.enneagram:
                previous = enneagram_choices[self._character.personality.enneagram.value]
            else:
                previous = None
            current_enneagram = enneagram_choices[enneagram]

            if wdgTraits:
                traits: List[str] = wdgTraits.value()
                if previous:
                    for pos_trait in previous.meta['positive']:
                        if pos_trait in traits:
                            traits.remove(pos_trait)
                    for neg_trait in previous.meta['negative']:
                        if neg_trait in traits:
                            traits.remove(neg_trait)
                for pos_trait in current_enneagram.meta['positive']:
                    if pos_trait not in traits:
                        traits.append(pos_trait)
                for neg_trait in current_enneagram.meta['negative']:
                    if neg_trait not in traits:
                        traits.append(neg_trait)

                wdgTraits.setValue(traits)
                wdgTraits.save()
