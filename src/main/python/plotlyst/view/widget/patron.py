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
from dataclasses import dataclass
from typing import List, Dict, Optional

from PyQt6.QtCore import QThreadPool, QSize, Qt
from PyQt6.QtGui import QShowEvent
from PyQt6.QtWidgets import QWidget, QTabWidget
from dataclasses_json import dataclass_json, Undefined
from overrides import overrides
from qthandy import vbox, hbox, clear_layout

from plotlyst.common import PLOTLYST_MAIN_COLOR, PLOTLYST_SECONDARY_COLOR
from plotlyst.service.resource import JsonDownloadResult, JsonDownloadWorker
from plotlyst.view.common import label, set_tab_enabled, push_btn, spin
from plotlyst.view.icons import IconRegistry


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
class PatreonSurvey:
    stage: Dict[str, int]
    panels: Dict[str, int]
    genres: Dict[str, int]
    new: Dict[str, int]
    secondary: Dict[str, int]


@dataclass_json(undefined=Undefined.EXCLUDE)
@dataclass
class Patreon:
    tiers: List[PatreonTier]
    survey: PatreonSurvey


class SurveyResultsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        vbox(self).addWidget(label('Survey'))


class PatronsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        vbox(self).addWidget(label('Patrons'))


class PlotlystPlusWidget(QWidget):
    DOWNLOAD_THRESHOLD_SECONDS = 60 * 60 * 8  # 8 hours in seconds

    def __init__(self, parent=None):
        super().__init__(parent)
        hbox(self)

        self._patreon: Optional[Patreon] = None

        self.tabWidget = QTabWidget()
        self.tabWidget.setProperty('centered', True)
        self.tabWidget.setProperty('large-rounded', True)
        self.tabWidget.setProperty('relaxed-white-bg', True)
        self.tabWidget.setMaximumWidth(1000)
        self.tabReport = QWidget()
        vbox(self.tabReport, 10, 5)
        self.tabPatreon = QWidget()
        self.tabPlus = QWidget()
        self.tabPatrons = QWidget()

        self.tabWidget.addTab(self.tabReport, IconRegistry.from_name('mdi.crystal-ball', color_on=PLOTLYST_MAIN_COLOR),
                              'Vision')
        self.tabWidget.addTab(self.tabPatreon, IconRegistry.from_name('fa5b.patreon', color_on=PLOTLYST_MAIN_COLOR),
                              'Patreon')
        self.tabWidget.addTab(self.tabPlus, IconRegistry.from_name('mdi.certificate', color_on=PLOTLYST_MAIN_COLOR),
                              'Plotlyst Plus')
        self.tabWidget.addTab(self.tabPatrons, IconRegistry.from_name('msc.organization', color_on=PLOTLYST_MAIN_COLOR),
                              'Community')
        self.layout().addWidget(self.tabWidget)

        self._last_fetched = None
        self._downloading = False

        self.lblVisionLastUpdated = label('', description=True, decr_font_diff=1)
        self.lblPatreonLastUpdated = label('', description=True, decr_font_diff=1)

        self.wdgLoading = QWidget()
        vbox(self.wdgLoading, 0, 0)

        self.tabReport.layout().addWidget(self.lblVisionLastUpdated, alignment=Qt.AlignmentFlag.AlignRight)
        self.tabReport.layout().addWidget(self.wdgLoading)
        self.wdgLoading.setHidden(True)

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

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.lblVisionLastUpdated.setText(f"Last updated: {now}")
        self._last_fetched = datetime.datetime.now()

    def _handle_download_patreon_failure(self, status_code: int, message: str):
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
