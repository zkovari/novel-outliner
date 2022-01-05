from typing import Optional

from src.main.python.plotlyst.core.domain import Novel, Scene
from src.main.python.plotlyst.view.scene_editor import SceneEditor
from src.main.python.plotlyst.view.stylesheet import APP_STYLESHEET


def editor(qtbot, novel: Novel, scene: Optional[Scene] = None):
    editor = SceneEditor(novel, scene)
    editor.widget.setStyleSheet(APP_STYLESHEET)
    editor.widget.show()
    qtbot.addWidget(editor.widget)
    qtbot.waitExposed(editor.widget, timeout=5000)

    return editor


def test_editor_with_new_scene(qtbot):
    novel = Novel('Test-novel')
    view: SceneEditor = editor(qtbot, novel)

    assert view.ui.wdgSceneStructure.rbScene.isChecked()
    assert view.ui.cbPov.currentIndex() == 0
    assert view.ui.cbPov.currentText() == 'Select POV ...'


def test_editor_with_none_values(qtbot):
    novel = Novel('Test-novel')
    scene = Scene(title='')
    novel.scenes.append(scene)

    view: SceneEditor = editor(qtbot, novel, scene)

    assert view.ui.wdgSceneStructure.rbScene.isChecked()


def _test_display_scene_builder(qtbot):
    novel = Novel('Test-novel')
    view: SceneEditor = editor(qtbot, novel)

    view.ui.btnBuilder.click()
