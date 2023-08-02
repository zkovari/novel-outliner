"""
Plotlyst
Copyright (C) 2021-2023  Zsolt Kovari

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
from enum import Enum
from typing import Dict, Optional

from PyQt6 import sip
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QWidget, QLabel, QTextEdit
from overrides import overrides
from qthandy import vbox, hbox, line, flow, gc, vspacer, clear_layout, bold

from src.main.python.plotlyst.core.domain import Character, Novel
from src.main.python.plotlyst.event.core import emit_event, EventListener, Event
from src.main.python.plotlyst.event.handler import event_dispatcher
from src.main.python.plotlyst.events import CharacterSummaryChangedEvent, CharacterChangedEvent
from src.main.python.plotlyst.service.persistence import RepositoryPersistenceManager
from src.main.python.plotlyst.view.icons import set_avatar, avatars
from src.main.python.plotlyst.view.widget.big_five import BigFiveChart, dimension_from
from src.main.python.plotlyst.view.widget.button import EyeToggle
from src.main.python.plotlyst.view.widget.display import RoleIcon, ChartView
from src.main.python.plotlyst.view.widget.tree import TreeView, ContainerNode


class CharacterComparisonAttribute(Enum):
    SUMMARY = 0
    BIG_FIVE = 1


class BaseDisplay:

    @abstractmethod
    def refresh(self):
        pass


class BigFiveDisplay(ChartView, BaseDisplay):
    def __init__(self, character: Character, parent=None):
        super(BigFiveDisplay, self).__init__(parent)
        self._character = character
        self._bigFive = BigFiveChart()
        self._bigFive.setTitle('')

        self.setChart(self._bigFive)
        self.refresh()

        self.setMinimumSize(250, 250)

    @overrides
    def refresh(self):
        for bf, values in self._character.big_five.items():
            self._bigFive.refreshDimension(dimension_from(bf), values)
            self.update()


class SummaryDisplay(QTextEdit, BaseDisplay):
    def __init__(self, character: Character, parent=None):
        super(SummaryDisplay, self).__init__(parent)
        self._character = character
        self._blockSave = False
        self.setToolTip('Character summary')
        self.setPlaceholderText('Character summary...')
        self.setMaximumSize(250, 100)
        self.setMinimumWidth(200)
        self.setTabChangesFocus(True)

        self.repo = RepositoryPersistenceManager.instance()
        self.refresh()

        self.textChanged.connect(self._save)

    @overrides
    def refresh(self):
        self._blockSave = True
        self.setText(self._character.summary())
        self._blockSave = False

    def _save(self):
        if self._blockSave:
            return

        self._character.set_summary(self.toPlainText())
        self.repo.update_character(self._character)
        emit_event(CharacterSummaryChangedEvent(self, self._character))


class CharacterOverviewWidget(QWidget, EventListener):
    def __init__(self, character: Character, parent=None):
        super().__init__(parent)
        self._character = character

        self._avatar = QLabel(self)
        set_avatar(self._avatar, self._character, size=118)
        self._roleIcon = RoleIcon(self)
        self._roleIcon.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        if self._character.role:
            self._roleIcon.setRole(self._character.role, showText=True)

        vbox(self, 0)
        self.layout().addWidget(self._avatar, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(self._roleIcon, alignment=Qt.AlignmentFlag.AlignCenter)
        self.layout().addWidget(line())

        self._display: Optional[BaseDisplay] = None
        self._displayContainer = QWidget()
        hbox(self._displayContainer, 0, 0)

        self.layout().addWidget(self._displayContainer)
        self.layout().addWidget(vspacer())
        event_dispatcher.register(self, CharacterChangedEvent)

    @overrides
    def event_received(self, event: Event):
        if isinstance(event, CharacterChangedEvent):
            if event.character is self._character and self._display is not None:
                self._display.refresh()

    def display(self, attribute: CharacterComparisonAttribute):
        if self._display:
            self._displayContainer.layout().removeWidget(self._display)
            gc(self._display)
            self._display = None

        if attribute == CharacterComparisonAttribute.BIG_FIVE:
            self._display = BigFiveDisplay(self._character)
            self._displayContainer.layout().addWidget(self._display)
        elif attribute == CharacterComparisonAttribute.SUMMARY:
            self._display = SummaryDisplay(self._character)
            self._displayContainer.layout().addWidget(self._display, alignment=Qt.AlignmentFlag.AlignCenter)


class LayoutType(Enum):
    HORIZONTAL = 0
    VERTICAL = 1
    FLOW = 2


class CharacterComparisonWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._characters: Dict[Character, CharacterOverviewWidget] = {}
        hbox(self)
        self._currentDisplay: CharacterComparisonAttribute = CharacterComparisonAttribute.SUMMARY

    def updateCharacter(self, character: Character, enabled: bool):
        if enabled:
            wdg = CharacterOverviewWidget(character)
            wdg.display(self._currentDisplay)
            self._characters[character] = wdg
            self.layout().addWidget(wdg)
        else:
            wdg = self._characters.pop(character)
            self.layout().removeWidget(wdg)
            gc(wdg)

    def updateLayout(self, layoutType: LayoutType):
        widgets = []
        for i in range(self.layout().count()):
            widgets.append(self.layout().itemAt(i).widget())

        sip.delete(self.layout())

        if layoutType == LayoutType.HORIZONTAL:
            hbox(self)
        elif layoutType == LayoutType.VERTICAL:
            vbox(self)
        elif layoutType == LayoutType.FLOW:
            flow(self)

        for wdg in widgets:
            self.layout().addWidget(wdg)

        for wdg in self._characters.values():
            wdg.display(self._currentDisplay)

    def displayAttribute(self, attribute: CharacterComparisonAttribute):
        for wdg in self._characters.values():
            wdg.display(attribute)

        self._currentDisplay = attribute


class CharacterNode(ContainerNode):
    characterToggled = pyqtSignal(Character, bool)

    def __init__(self, character: Character, parent=None):
        super(CharacterNode, self).__init__(character.name, parent)
        self._character = character

        self.setPlusButtonEnabled(False)
        self.setMenuEnabled(False)
        self.setSelectionEnabled(False)

        self._btnVisible = EyeToggle()
        self._btnVisible.setToolTip('Toggle arc')
        self._btnVisible.toggled.connect(self._toggled)
        self._wdgTitle.layout().addWidget(self._btnVisible)

        self.refresh()

    def refresh(self):
        self._lblTitle.setText(self._character.name)
        icon = avatars.avatar(self._character, fallback=False)
        if icon:
            self._icon.setIcon(icon)
            self._icon.setVisible(True)
        else:
            self._icon.setHidden(True)

    def _toggled(self, toggled: bool):
        bold(self._lblTitle, toggled)
        self.characterToggled.emit(self._character, toggled)


class CharactersTreeView(TreeView):
    characterToggled = pyqtSignal(Character, bool)

    def __init__(self, novel: Novel, parent=None):
        super(CharactersTreeView, self).__init__(parent)
        self._novel = novel
        self._centralWidget.setProperty('bg', True)

    def refresh(self):
        clear_layout(self._centralWidget)

        for character in self._novel.characters:
            node = CharacterNode(character)
            node.characterToggled.connect(self.characterToggled.emit)
            self._centralWidget.layout().addWidget(node)

        self._centralWidget.layout().addWidget(vspacer())
