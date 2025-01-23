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
import datetime
import random
from dataclasses import dataclass
from typing import List, Dict, Optional

from PyQt6.QtCore import QThreadPool, QSize, Qt
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QWidget, QTabWidget, QPushButton, QProgressBar
from dataclasses_json import dataclass_json, Undefined
from overrides import overrides
from qthandy import vbox, hbox, clear_layout, line, vspacer, spacer, translucent, margins, transparent, incr_font, flow

from plotlyst.common import PLOTLYST_MAIN_COLOR, PLOTLYST_SECONDARY_COLOR, PLOTLYST_TERTIARY_COLOR
from plotlyst.core.domain import Board, Task, TaskStatus
from plotlyst.env import app_env
from plotlyst.service.resource import JsonDownloadResult, JsonDownloadWorker
from plotlyst.view.common import label, set_tab_enabled, push_btn, spin, scroll_area, wrap, frame
from plotlyst.view.icons import IconRegistry
from plotlyst.view.layout import group
from plotlyst.view.widget.chart import ChartItem, PolarChart, PieChart
from plotlyst.view.widget.display import IconText, ChartView
from plotlyst.view.widget.input import AutoAdjustableTextEdit


@dataclass
class PatreonTier:
    name: str
    description: str
    perks: List[str]
    price: str
    has_roadmap_form: bool = False
    has_plotlyst_plus: bool = False
    has_early_access: bool = False
    has_premium_recognition: bool = False


@dataclass
class SurveyResults:
    title: str
    description: str
    items: Dict[str, ChartItem]


@dataclass
class PatreonSurvey:
    stage: SurveyResults
    panels: SurveyResults
    genres: SurveyResults
    new: SurveyResults
    secondary: SurveyResults
    personalization: SurveyResults


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Patreon:
    tiers: List[PatreonTier]
    survey: PatreonSurvey


@dataclass
class Patron:
    name: str
    web: str = ''
    description: str = ''
    genre: str = ''
    vip: bool = False


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Community:
    patrons: List[Patron]


class PlusTaskWidget(QWidget):
    def __init__(self, task: Task, status: TaskStatus, parent=None):
        super().__init__(parent)
        self.task = task
        self.status = status
        vbox(self, 10, spacing=5)

        self.lblStatus = label(self.status.text)
        self.lblStatus.setStyleSheet(f'''
            color: {self.status.color_hexa};
        ''')

        self.lblName = IconText()
        incr_font(self.lblName, 4)
        self.lblName.setText(self.task.title)
        if self.task.icon:
            self.lblName.setIcon(IconRegistry.from_name(self.task.icon))
        self.lblDescription = label(self.task.summary, description=True, wordWrap=True)
        self.lblDescription.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        incr_font(self.lblDescription)

        self.layout().addWidget(self.lblStatus, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout().addWidget(self.lblName, alignment=Qt.AlignmentFlag.AlignLeft)
        self.layout().addWidget(self.lblDescription)


class PlusFeaturesWidget(QWidget):
    DOWNLOAD_THRESHOLD_SECONDS = 60 * 60 * 8  # 8 hours in seconds

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_fetched = None
        self._downloading = False
        self._board: Optional[Board] = None
        self._thread_pool = QThreadPool()

        vbox(self)

        self._scroll = scroll_area(frameless=True)
        self._scroll.setProperty('relaxed-white-bg', True)
        self.centerWdg = QWidget()
        self.centerWdg.setProperty('relaxed-white-bg', True)
        vbox(self.centerWdg, spacing=15)
        self._scroll.setWidget(self.centerWdg)
        self.layout().addWidget(self._scroll)

        self.lblLastUpdated = label('', description=True, decr_font_diff=1)

        self.wdgTasks = QWidget()
        vbox(self.wdgTasks)

        self.wdgLoading = QWidget()
        vbox(self.wdgLoading, 0, 0)
        self.centerWdg.layout().addWidget(self.lblLastUpdated, alignment=Qt.AlignmentFlag.AlignRight)
        self.centerWdg.layout().addWidget(self.wdgLoading)
        self.centerWdg.layout().addWidget(self.wdgTasks)
        self.centerWdg.layout().addWidget(vspacer())
        self.wdgLoading.setHidden(True)

    @overrides
    def showEvent(self, event: QShowEvent):
        super().showEvent(event)

        if self._downloading:
            return

        if self._last_fetched is None or (
                datetime.datetime.now() - self._last_fetched).total_seconds() > self.DOWNLOAD_THRESHOLD_SECONDS:
            self._handle_downloading_status(True)
            self._download_data()

    def _download_data(self):
        result = JsonDownloadResult()
        runnable = JsonDownloadWorker("https://raw.githubusercontent.com/plotlyst/feed/refs/heads/main/plus.json",
                                      result)
        result.finished.connect(self._handle_downloaded_data)
        result.failed.connect(self._handle_download_failure)
        self._thread_pool.start(runnable)

    def _handle_downloaded_data(self, data):
        self._board: Board = Board.from_dict(data)
        clear_layout(self.wdgTasks)

        statuses = {}
        for status in self._board.statuses:
            statuses[str(status.id)] = status

        for task in self._board.tasks:
            wdg = PlusTaskWidget(task, statuses[str(task.status_ref)])
            self.wdgTasks.layout().addWidget(wdg)
            self.wdgTasks.layout().addWidget(line())

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.lblLastUpdated.setText(f"Last updated: {now}")
        self._last_fetched = datetime.datetime.now()

        self._handle_downloading_status(False)

    def _handle_download_failure(self, status_code: int, message: str):
        if self._board is None:
            self.lblLastUpdated.setText("Failed to update data.")
        self._handle_downloading_status(False)

    def _handle_downloading_status(self, loading: bool):
        self._downloading = loading
        # self.scrollAreaWidgetContents.setDisabled(loading)
        # self.splitter.setHidden(loading)
        # self.wdgTopSelectors.setHidden(loading)
        self.wdgLoading.setVisible(loading)
        if loading:
            btn = push_btn(transparent_=True)
            btn.setIconSize(QSize(128, 128))
            self.wdgLoading.layout().addWidget(btn,
                                               alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            spin(btn, PLOTLYST_SECONDARY_COLOR)
        else:
            clear_layout(self.wdgLoading)


class SurveyResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        vbox(self)

        self._scroll = scroll_area(frameless=True)
        self._scroll.setProperty('relaxed-white-bg', True)
        self.centerWdg = QWidget()
        self.centerWdg.setProperty('relaxed-white-bg', True)
        vbox(self.centerWdg)
        self._scroll.setWidget(self.centerWdg)
        self.layout().addWidget(self._scroll)

    def setPatreon(self, patreon: Patreon):
        clear_layout(self.centerWdg)

        # patreon.survey.stage['Brainstorming'] = 16
        # patreon.survey.stage['Outlining and planning'] = 160
        # patreon.survey.stage['Drafting'] = 54
        # patreon.survey.stage['Developmental editing'] = 5
        # patreon.survey.stage['Line and copy-editing'] = 0

        stages = self._polarChart(patreon.survey.stage.items)
        panels = self._polarChart(patreon.survey.panels.items)
        newVsOld = self._pieChart(patreon.survey.new.items)
        personalization = self._pieChart(patreon.survey.personalization.items)

        self._addTitle(patreon.survey.stage)
        self.centerWdg.layout().addWidget(stages)
        self._addTitle(patreon.survey.panels)
        self.centerWdg.layout().addWidget(panels)
        self._addTitle(patreon.survey.genres)
        self._addTitle(patreon.survey.new)
        self.centerWdg.layout().addWidget(newVsOld)
        self._addTitle(patreon.survey.personalization)
        self.centerWdg.layout().addWidget(personalization)
        self._addTitle(patreon.survey.secondary)

        for k, item in patreon.survey.secondary.items.items():
            wdg = QWidget()
            vbox(wdg)
            margins(wdg, left=35, bottom=15)
            wdg.layout().addWidget(label(k, h5=True))
            wdg.layout().addWidget(label(item.description, description=True))

            bar = QProgressBar()
            bar.setMinimum(0)
            bar.setMaximum(100)
            bar.setValue(item.value)
            bar.setTextVisible(True)
            bar.setStyleSheet(f'''
                QProgressBar {{
                    border: 2px solid grey;
                    border-radius: 8px;
                    text-align: center;
                }}

                QProgressBar::chunk {{
                    background-color: {PLOTLYST_TERTIARY_COLOR};
                    width: 20px;
                }}
            }}''')
            wdg.layout().addWidget(bar)
            self.centerWdg.layout().addWidget(wdg)

        self.centerWdg.layout().addWidget(vspacer())

    def _polarChart(self, values: Dict[str, ChartItem]) -> ChartView:
        view = ChartView()
        chart = PolarChart()
        chart.setMinimumSize(400, 400)
        chart.setAngularRange(0, len(values.keys()))
        chart.setLogarithmicScaleEnabled(True)
        items = []
        labels = []
        i = 0
        for k, v in values.items():
            i += 1
            labels.append((k, float(i)))
            if not v.value:
                v.value = 0.1
            v.text = k
            items.append(v)
        chart.setAngularLabels(labels)
        chart.setItems(items)
        view.setChart(chart)

        return view

    def _pieChart(self, values: Dict[str, ChartItem]) -> ChartView:
        view = ChartView()
        chart = PieChart()

        items = []
        for k, v in values.items():
            if not v.value:
                v.value = 0.1
            v.text = k
            items.append(v)

        chart.setItems(items)
        view.setChart(chart)

        return view

    def _addTitle(self, result: SurveyResults):
        self.centerWdg.layout().addWidget(wrap(label(result.title, h4=True), margin_top=20))
        self.centerWdg.layout().addWidget(line())
        self.centerWdg.layout().addWidget(label(result.description, description=True, wordWrap=True))


class PriceLabel(QPushButton):
    def __init__(self, price: str, parent=None):
        super().__init__(parent)

        self.setText(f'{price}$')
        self.setStyleSheet(f'''
            background: {PLOTLYST_TERTIARY_COLOR};
            border: 1px solid {PLOTLYST_SECONDARY_COLOR};
            padding: 8px;
            border-radius: 4px;
            font-family: {app_env.serif_font()};
        ''')
        translucent(self, 0.7)


class PatreonTierSection(QWidget):
    def __init__(self, tier: PatreonTier, parent=None):
        super().__init__(parent)
        self.tier = tier
        self.lblHeader = label(self.tier.name, h3=True)
        self.lblDesc = label(self.tier.description, wordWrap=True, description=True)
        incr_font(self.lblDesc, 2)
        self.wdgPerks = frame()
        self.wdgPerks.setProperty('large-rounded', True)
        self.wdgPerks.setProperty('highlighted-bg', True)
        vbox(self.wdgPerks, margin=8)
        self.textPerks = AutoAdjustableTextEdit()
        incr_font(self.textPerks, 3)
        self.textPerks.setReadOnly(True)
        self.textPerks.setAcceptRichText(True)
        transparent(self.textPerks)
        html = '<html><ul>'
        for perk in self.tier.perks:
            html += f'<li>{perk}</li>'
        self.textPerks.setHtml(html)
        self.wdgPerks.layout().addWidget(self.textPerks)

        vbox(self)
        margins(self, top=13, bottom=13)
        self.layout().addWidget(group(self.lblHeader, spacer(), PriceLabel(self.tier.price)))
        self.layout().addWidget(line())
        self.layout().addWidget(wrap(self.lblDesc, margin_left=20))
        self.layout().addWidget(wrap(self.wdgPerks, margin_left=20))


class PatreonTiersWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        vbox(self)
        margins(self, bottom=45)

        self._scroll = scroll_area(frameless=True)
        self._scroll.setProperty('relaxed-white-bg', True)
        self.centerWdg = QWidget()
        self.centerWdg.setProperty('relaxed-white-bg', True)
        vbox(self.centerWdg)
        self._scroll.setWidget(self.centerWdg)
        self.layout().addWidget(self._scroll)

    def setPatreon(self, patreon: Patreon):
        clear_layout(self.centerWdg)

        for tier in patreon.tiers:
            section = PatreonTierSection(tier)
            self.centerWdg.layout().addWidget(section)
            # self.centerWdg.layout().addWidget(line())

        self.centerWdg.layout().addWidget(vspacer())


class PatronLabel(QWidget):
    def __init__(self, patron: Patron, parent=None):
        super().__init__(parent)
        vbox(self, 0, 0)
        margins(self, left=self.__randomMargin(), right=self.__randomMargin(), top=self.__randomMargin(),
                bottom=self.__randomMargin())

        if patron.vip:
            self.lbl = QPushButton(patron.name)
        else:
            self.lbl = label(patron.name)

        self.layout().addWidget(self.lbl)

    def __randomMargin(self) -> int:
        return random.randint(3, 10)


class PatronsWidget(QWidget):
    DOWNLOAD_THRESHOLD_SECONDS = 60 * 60 * 8  # 8 hours in seconds

    def __init__(self, parent=None):
        super().__init__(parent)
        self._last_fetched = None
        self._downloading = False
        self._community: Optional[Community] = None
        self._thread_pool = QThreadPool()

        vbox(self)

        self._scroll = scroll_area(frameless=True)
        self._scroll.setProperty('relaxed-white-bg', True)
        self.centerWdg = QWidget()
        self.centerWdg.setProperty('relaxed-white-bg', True)
        vbox(self.centerWdg, spacing=15)
        self._scroll.setWidget(self.centerWdg)
        self.layout().addWidget(self._scroll)

        self.lblLastUpdated = label('', description=True, decr_font_diff=1)

        self.wdgPatrons = QWidget()
        flow(self.wdgPatrons, 0, spacing=5)

        self.wdgLoading = QWidget()
        vbox(self.wdgLoading, 0, 0)
        self.centerWdg.layout().addWidget(self.lblLastUpdated, alignment=Qt.AlignmentFlag.AlignRight)
        self.centerWdg.layout().addWidget(self.wdgLoading)
        self.centerWdg.layout().addWidget(self.wdgPatrons)
        self.centerWdg.layout().addWidget(vspacer())
        self.wdgLoading.setHidden(True)

    @overrides
    def showEvent(self, event: QShowEvent):
        super().showEvent(event)

        if self._downloading:
            return

        if self._last_fetched is None or (
                datetime.datetime.now() - self._last_fetched).total_seconds() > self.DOWNLOAD_THRESHOLD_SECONDS:
            self._handle_downloading_status(True)
            self._download_data()

    def _download_data(self):
        result = JsonDownloadResult()
        runnable = JsonDownloadWorker(
            "https://raw.githubusercontent.com/plotlyst/feed/refs/heads/main/patrons_dev.json",
            result)
        result.finished.connect(self._handle_downloaded_data)
        result.failed.connect(self._handle_download_failure)
        self._thread_pool.start(runnable)

    def _handle_downloaded_data(self, data):
        self._community: Community = Community.from_dict(data)
        clear_layout(self.wdgPatrons)

        print(len(self._community.patrons))
        for patron in self._community.patrons:
            lbl = PatronLabel(patron)
            self.wdgPatrons.layout().addWidget(lbl)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.lblLastUpdated.setText(f"Last updated: {now}")
        self._last_fetched = datetime.datetime.now()

        self._handle_downloading_status(False)

    def _handle_download_failure(self, status_code: int, message: str):
        if self._community is None:
            self.lblLastUpdated.setText("Failed to update data.")
        self._handle_downloading_status(False)

    def _handle_downloading_status(self, loading: bool):
        self._downloading = loading
        self.wdgLoading.setVisible(loading)
        if loading:
            btn = push_btn(transparent_=True)
            btn.setIconSize(QSize(128, 128))
            self.wdgLoading.layout().addWidget(btn,
                                               alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            spin(btn, PLOTLYST_SECONDARY_COLOR)
        else:
            clear_layout(self.wdgLoading)


class PlotlystPlusWidget(QWidget):
    DOWNLOAD_THRESHOLD_SECONDS = 60 * 60 * 8  # 8 hours in seconds

    def __init__(self, parent=None):
        super().__init__(parent)
        hbox(self)
        self._patreon: Optional[Patreon] = None
        self._last_fetched = None
        self._downloading = False

        self.tabWidget = QTabWidget()
        self.tabWidget.setProperty('centered', True)
        self.tabWidget.setProperty('large-rounded', True)
        self.tabWidget.setProperty('relaxed-white-bg', True)
        self.tabWidget.setMaximumWidth(1000)
        self.tabReport = QWidget()
        vbox(self.tabReport, 10, 5)
        self.tabPatreon = QWidget()
        vbox(self.tabPatreon, 10, 5)
        self.tabPlus = QWidget()
        vbox(self.tabPlus, 10, 5)
        self.tabPatrons = QWidget()
        vbox(self.tabPatrons, 10, 5)

        self.tabWidget.addTab(self.tabReport, IconRegistry.from_name('mdi.crystal-ball', color_on=PLOTLYST_MAIN_COLOR),
                              'Vision')
        self.tabWidget.addTab(self.tabPatreon, IconRegistry.from_name('fa5b.patreon', color_on=PLOTLYST_MAIN_COLOR),
                              'Patreon')
        self.tabWidget.addTab(self.tabPlus, IconRegistry.from_name('mdi.certificate', color_on=PLOTLYST_MAIN_COLOR),
                              'Plus Features')
        self.tabWidget.addTab(self.tabPatrons, IconRegistry.from_name('msc.organization', color_on=PLOTLYST_MAIN_COLOR),
                              'Community')
        self.layout().addWidget(self.tabWidget)

        self.lblVisionLastUpdated = label('', description=True, decr_font_diff=1)
        self.wdgLoading = QWidget()
        vbox(self.wdgLoading, 0, 0)
        self._patreonWdg = PatreonTiersWidget()
        self._surveyWdg = SurveyResultsWidget()
        self._plusWdg = PlusFeaturesWidget()
        self._patronsWdg = PatronsWidget()

        self.tabReport.layout().addWidget(self.lblVisionLastUpdated, alignment=Qt.AlignmentFlag.AlignRight)
        self.tabReport.layout().addWidget(self._surveyWdg)
        self.tabReport.layout().addWidget(self.wdgLoading)
        self.wdgLoading.setHidden(True)

        self.tabPatreon.layout().addWidget(self._patreonWdg)
        self.tabPlus.layout().addWidget(self._plusWdg)
        self.tabPatrons.layout().addWidget(self._patronsWdg)

        self._thread_pool = QThreadPool()

    @overrides
    def showEvent(self, event: QShowEvent):
        super().showEvent(event)

        if self._downloading:
            return

        if self._last_fetched is None or (
                datetime.datetime.now() - self._last_fetched).total_seconds() > self.DOWNLOAD_THRESHOLD_SECONDS:
            self._handle_downloading_patreon_status(True)
            self._download_data()

    def _download_data(self):
        result = JsonDownloadResult()
        runnable = JsonDownloadWorker("https://raw.githubusercontent.com/plotlyst/feed/refs/heads/main/patreon.json",
                                      result)
        result.finished.connect(self._handle_downloaded_patreon_data)
        result.failed.connect(self._handle_download_patreon_failure)
        self._thread_pool.start(runnable)

    def _handle_downloaded_patreon_data(self, data):
        self._handle_downloading_patreon_status(False)

        self._patreon = Patreon.from_dict(data)
        self._surveyWdg.setPatreon(self._patreon)
        self._patreonWdg.setPatreon(self._patreon)

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.lblVisionLastUpdated.setText(f"Last updated: {now}")
        self._last_fetched = datetime.datetime.now()

    def _handle_download_patreon_failure(self, status_code: int, message: str):
        if self._patreon is None:
            self.lblVisionLastUpdated.setText("Failed to update data.")
        self._handle_downloading_patreon_status(False)

    def _handle_downloading_patreon_status(self, loading: bool):
        self._downloading = loading
        set_tab_enabled(self.tabWidget, self.tabPatreon, not loading)
        self.wdgLoading.setVisible(loading)
        if loading:
            btn = push_btn(transparent_=True)
            btn.setIconSize(QSize(128, 128))
            self.wdgLoading.layout().addWidget(btn,
                                               alignment=Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
            spin(btn, PLOTLYST_SECONDARY_COLOR)
        else:
            clear_layout(self.wdgLoading)
