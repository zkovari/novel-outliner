import sys
from pathlib import Path
from uuid import UUID

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QFileDialog

from src.main.python.plotlyst.core.client import client
from src.main.python.plotlyst.test.common import go_to_home, create_novel
from src.main.python.plotlyst.view.home_view import HomeView
from src.main.python.plotlyst.view.main_window import MainWindow


def assert_views(window: MainWindow, visible: bool = True, scene_dependent_enabled: bool = True,
                 character_dependent_enabled: bool = True):
    assert window.btnNovel.isVisible() == visible
    assert window.btnCharacters.isVisible() == visible
    assert window.btnScenes.isVisible() == visible
    assert window.btnReport.isVisible() == visible
    assert window.btnNotes.isVisible() == visible

    if not visible:
        return

    assert window.btnNovel.isEnabled()
    assert window.btnCharacters.isEnabled()
    assert window.btnScenes.isEnabled() == character_dependent_enabled
    assert window.btnReport.isEnabled() == scene_dependent_enabled
    assert window.btnNotes.isEnabled() == scene_dependent_enabled


def test_empty_window(qtbot, window: MainWindow):
    assert not client.novels()

    assert window.btnHome.isVisible()
    assert window.btnHome.isChecked()
    assert_views(window, visible=False)


def test_change_font_size(qtbot, window: MainWindow):
    font_size = QApplication.font().pointSize()
    window.actionIncreaseFontSize.trigger()
    window.actionIncreaseFontSize.trigger()
    assert QApplication.font().pointSize() == font_size + 2

    window.actionDecreaseFontSize.trigger()
    assert QApplication.font().pointSize() == font_size + 1


def test_load_new_empty_novel(qtbot, filled_window: MainWindow):
    view: HomeView = go_to_home(filled_window)
    assert len(view.novel_cards) == 1

    new_title = 'New title'
    create_novel(filled_window, new_title)
    assert len(view.novel_cards) == 2

    card = view.novel_cards[1]
    assert card.novel.id
    assert card.novel.title == new_title
    qtbot.mouseClick(card, Qt.LeftButton)

    card.btnLoad.click()

    assert_views(filled_window, scene_dependent_enabled=False, character_dependent_enabled=False)
    first_card = view.novel_cards[0]
    assert first_card.novel.id
    qtbot.mouseClick(first_card, Qt.LeftButton)

    first_card.btnLoad.click()
    assert_views(filled_window)


def test_import_from_scrivener(qtbot, window: MainWindow, monkeypatch):
    folder = Path(sys.path[0]).joinpath('resources/scrivener/v3/NovelWithParts')
    monkeypatch.setattr(QFileDialog, "getExistingDirectory", lambda *args: folder)

    view: HomeView = go_to_home(window)
    assert len(view.novel_cards) == 0
    window.actionImportScrivener.trigger()

    assert len(view.novel_cards) == 1

    card = view.novel_cards[0]
    assert card.novel.id == UUID('C4B3D990-B9C2-4FE6-861E-B06B498283A4')
    assert card.novel.title == 'Importer project'
    qtbot.mouseClick(card, Qt.LeftButton)

    card.btnLoad.click()
    assert_views(window)
