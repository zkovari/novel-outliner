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
from functools import partial
from typing import Optional, Any

import qtanim
from PyQt6.QtCore import Qt, QPoint, QSize, QPointF, QRectF, pyqtSignal, QTimer, QObject
from PyQt6.QtGui import QColor, QPixmap, QShowEvent, QResizeEvent, QImage, QPainter, QKeyEvent, QIcon
from PyQt6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QGraphicsItem, QAbstractGraphicsShapeItem, QWidget, \
    QGraphicsSceneMouseEvent, QGraphicsOpacityEffect, QGraphicsDropShadowEffect, QFrame, QTextEdit, QLineEdit
from overrides import overrides
from qthandy import busy, vbox, vspacer, sp, line, decr_icon, incr_font, flow
from qthandy.filter import OpacityEventFilter
from qtmenu import MenuWidget, ActionTooltipDisplayMode

from src.main.python.plotlyst.common import PLOTLYST_SECONDARY_COLOR, RELAXED_WHITE_COLOR
from src.main.python.plotlyst.core.domain import Novel, WorldBuildingMap, WorldBuildingMarker
from src.main.python.plotlyst.service.image import load_image, upload_image, LoadedImage
from src.main.python.plotlyst.service.persistence import RepositoryPersistenceManager
from src.main.python.plotlyst.view.common import tool_btn, action, shadow, scrolled, wrap
from src.main.python.plotlyst.view.icons import IconRegistry
from src.main.python.plotlyst.view.widget.button import CollapseButton
from src.main.python.plotlyst.view.widget.graphics import BaseGraphicsView
from src.main.python.plotlyst.view.widget.graphics.editor import ZoomBar
from src.main.python.plotlyst.view.widget.input import AutoAdjustableTextEdit


class PopupText(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet('''QFrame {
                    background: #ede0d4;
                    border-radius: 12px;
                }''')
        shadow(self)
        vbox(self, 10, spacing=6)

        self.textEdit = AutoAdjustableTextEdit()
        self.textEdit.setProperty('transparent', True)
        self.textEdit.setProperty('rounded', True)
        self.textEdit.setReadOnly(True)

        self.layout().addWidget(self.textEdit)

        self.setFixedWidth(200)

        sp(self).v_max()

    def setText(self, text: str):
        self.textEdit.setText(text)


marker_colors = ['#ef233c', '#0077b6', '#fb8500', '#B28DC8', '#CE9861']
marker_selected_colors = {
    '#ef233c': '#A50C1E',
    '#0077b6': '#00669D',
    '#fb8500': '#C46900',
    '#B28DC8': '#9967B6',
    '#CE9861': '#C3803D',
}


class MarkerColorSelectorWidget(QWidget):
    colorSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        flow(self)
        for color in marker_colors:
            btn = tool_btn(IconRegistry.from_name('fa5s.map-marker', color), transparent_=True)
            btn.setIconSize(QSize(32, 32))
            btn.clicked.connect(partial(self.colorSelected.emit, color))
            self.layout().addWidget(btn)


class MarkerIconSelectorWidget(QWidget):
    iconReset = pyqtSignal()
    iconSelected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.icons = ['mdi.castle', 'mdi.tower-fire', 'mdi.lighthouse-on', 'mdi.warehouse', 'mdi6.hoop-house',
                      'ph.house-line-bold', 'mdi.city-variant', 'mdi6.town-hall', 'fa5s.place-of-worship',
                      'mdi.water-well',
                      'mdi.treasure-chest', 'fa5s.flag',
                      'mdi6.axe-battle', 'mdi.sword-cross',
                      'mdi.horse-human',
                      'fa5s.dragon',
                      'fa5s.skull', 'fa5s.skull-crossbones', 'ri.ghost-2-fill', 'mdi.grave-stone',
                      'fa5s.train', 'mdi.ship-wheel', 'mdi.sail-boat',
                      'fa5s.mountain', 'fa5s.tree', 'mdi.tree', 'mdi.island', 'mdi.circle'
                      ]
        flow(self, 0, 1)
        for icon in self.icons:
            btn = tool_btn(IconRegistry.from_name(icon), transparent_=True)
            btn.setIconSize(QSize(24, 24))
            btn.clicked.connect(partial(self.iconSelected.emit, icon))
            self.layout().addWidget(btn)


class EntityEditorWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._marker: Optional[WorldBuildingMarker] = None
        self._item: Optional[MarkerItem] = None
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setStyleSheet('''QFrame {
            background: #ede0d4;
            border-radius: 12px;
        }''')

        vbox(self, 5, 0)
        self._scrollarea, self.wdgCenter = scrolled(self)
        self._scrollarea.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._scrollarea.setProperty('transparent', True)
        self.wdgCenter.setProperty('transparent', True)

        shadow(self)
        vbox(self.wdgCenter, 2, spacing=6)

        self.lineTitle = QLineEdit()
        self.lineTitle.setProperty('transparent', True)
        self.lineTitle.setPlaceholderText('Name')
        incr_font(self.lineTitle)
        self.lineTitle.textEdited.connect(self._nameChanged)

        self.textEdit = QTextEdit()
        self.textEdit.setProperty('transparent', True)
        self.textEdit.setProperty('rounded', True)
        self.textEdit.setPlaceholderText('Edit synopsis')
        self.textEdit.setMaximumHeight(150)
        self.textEdit.textChanged.connect(self._synopsisChanged)

        self.wdgColorSelector = MarkerColorSelectorWidget()
        self.wdgColorSelector.colorSelected.connect(self._colorChanged)
        self.wdgIconSelector = MarkerIconSelectorWidget()
        self.wdgIconSelector.iconReset.connect(self._iconReset)
        self.wdgIconSelector.iconSelected.connect(self._iconChanged)

        self.wdgCenter.layout().addWidget(self.lineTitle)
        self.wdgCenter.layout().addWidget(line(color='lightgrey'))
        self._addHeader('Synopsis', self.textEdit)
        self._addHeader('Color', self.wdgColorSelector)
        self._addHeader('Icon', self.wdgIconSelector)
        self.wdgCenter.layout().addWidget(vspacer())

        self.setFixedWidth(200)

        sp(self).v_max()

    def setMarker(self, item: 'MarkerItem'):
        self._marker = None
        self._item = None
        self.textEdit.setText(item.marker().description)
        self._marker = item.marker()
        self._item = item

    def _nameChanged(self, text: str):
        if self._marker:
            self._marker.name = text

    def _synopsisChanged(self):
        if self._marker:
            self._marker.description = self.textEdit.toPlainText()

    def _colorChanged(self, color: str):
        if self._marker:
            self._marker.color = color
            self._marker.color_selected = marker_selected_colors[color]
            self._item.refresh()

    def _iconChanged(self, icon: str):
        if self._marker:
            self._marker.icon = icon
            self._item.refresh()

    def _iconReset(self):
        if self._marker:
            self._marker.icon = ''
            self._item.refresh()

    def _addHeader(self, text: str, wdg: QWidget) -> CollapseButton:
        btn = CollapseButton(Qt.Edge.RightEdge, Qt.Edge.BottomEdge)
        decr_icon(btn, 2)
        btn.setChecked(True)
        btn.setText(text)
        wrapped = wrap(wdg, margin_left=5)
        btn.toggled.connect(wrapped.setVisible)

        self.wdgCenter.layout().addWidget(btn, alignment=Qt.AlignmentFlag.AlignLeft)
        self.wdgCenter.layout().addWidget(wrapped)


class MarkerItem(QAbstractGraphicsShapeItem):
    DEFAULT_MARKER_WIDTH: int = 50
    DEFAULT_MARKER_HEIGHT: int = 70

    def __init__(self, marker: WorldBuildingMarker, parent=None):
        super().__init__(parent)
        self._marker = marker
        self.__default_type_size = 25
        self._width = self.DEFAULT_MARKER_WIDTH
        self._height = self.DEFAULT_MARKER_HEIGHT
        self._typeSize = self.__default_type_size

        self.setFlag(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

        self._iconMarker = IconRegistry.from_name('fa5s.map-marker', self._marker.color)
        self._iconMarkerSelected = IconRegistry.from_name('fa5s.map-marker', self._marker.color_selected)
        if self._marker.icon:
            self._iconType = IconRegistry.from_name(self._marker.icon, RELAXED_WHITE_COLOR)
        else:
            self._iconType = QIcon()

        self.setPos(self._marker.x, self._marker.y)

    def marker(self) -> WorldBuildingMarker:
        return self._marker

    def refresh(self):
        self._iconMarker = IconRegistry.from_name('fa5s.map-marker', self._marker.color)
        self._iconMarkerSelected = IconRegistry.from_name('fa5s.map-marker', self._marker.color_selected)
        if self._marker.icon:
            self._iconType = IconRegistry.from_name(self._marker.icon, RELAXED_WHITE_COLOR)

        self.update()

    @overrides
    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self._width, self._height)

    @overrides
    def paint(self, painter: QPainter, option: 'QStyleOptionGraphicsItem', widget: Optional[QWidget] = ...) -> None:
        painter.setPen(Qt.PenStyle.NoPen)
        if self.isSelected():
            painter.setBrush(QColor(RELAXED_WHITE_COLOR))
            marker = self._iconMarkerSelected
        else:
            marker = self._iconMarker
        marker.paint(painter, 0, 0, self._width, self._height)
        if self._marker.icon:
            self._iconType.paint(painter, (self._width - self._typeSize) // 2, 15, self._typeSize, self._typeSize)

    @overrides
    def itemChange(self, change: QGraphicsItem.GraphicsItemChange, value: Any) -> Any:
        # if change == QGraphicsItem.GraphicsItemChange.ItemPositionHasChanged:
        #     self._posChangedTimer.start()
        #     self._onPosChanged()
        if change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            self._onSelection(value)
        return super().itemChange(change, value)

    @overrides
    def hoverEnterEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if not self.isSelected():
            effect = QGraphicsOpacityEffect()
            effect.setOpacity(0.9)
            self.setGraphicsEffect(effect)
            self._typeSize = self.__default_type_size + 1
            self.update()

            if self._marker.description:
                QTimer.singleShot(250, self._triggerPopup)

    @overrides
    def hoverLeaveEvent(self, event: 'QGraphicsSceneHoverEvent') -> None:
        if not self.isSelected():
            self.setGraphicsEffect(None)
            self._typeSize = self.__default_type_size
            self.update()

            if self._marker.description:
                self.scene().hidePopupEvent()

    def _triggerPopup(self):
        if not self.isSelected() and self.isUnderMouse():
            self.scene().showPopupEvent(self)

    def _onSelection(self, selected: bool):
        if selected:
            effect = QGraphicsDropShadowEffect()
            effect.setBlurRadius(12)
            effect.setOffset(0)
            effect.setColor(QColor('white'))
            self.setGraphicsEffect(effect)

            self._typeSize = self.__default_type_size + 2
        else:
            self._typeSize = self.__default_type_size
            self.setGraphicsEffect(None)

        if self._marker.description:
            self.scene().hidePopupEvent()


class WorldBuildingMapScene(QGraphicsScene):
    showPopup = pyqtSignal(MarkerItem)
    hidePopup = pyqtSignal()

    def __init__(self, novel: Novel, parent=None):
        super().__init__(parent)
        self._novel = novel
        self._map: Optional[WorldBuildingMap] = None
        self._animParent = QObject()

    def map(self) -> Optional[WorldBuildingMap]:
        return self._map

    def showPopupEvent(self, item: MarkerItem):
        self.showPopup.emit(item)

    def hidePopupEvent(self):
        self.hidePopup.emit()

    @overrides
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.key() == Qt.Key.Key_Delete or event.key() == Qt.Key.Key_Backspace:
            for item in self.selectedItems():
                self._removeItem(item)
            # self.clearSelection()

    @busy
    def loadMap(self, map: WorldBuildingMap) -> Optional[QGraphicsPixmapItem]:
        self.clear()
        image: Optional[QImage] = load_image(self._novel, map.ref)
        if image:
            self._map = map
            item = QGraphicsPixmapItem()
            item.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
            item.setPixmap(QPixmap.fromImage(image))
            self.addItem(item)

            return item
        else:
            self._map = None

    @overrides
    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if self._map:
            self._addMarker(event.scenePos())

    def _addMarker(self, pos: QPointF):
        pos = pos - QPointF(MarkerItem.DEFAULT_MARKER_WIDTH / 2, MarkerItem.DEFAULT_MARKER_HEIGHT)
        marker = WorldBuildingMarker(pos.x(), pos.y())
        markerItem = MarkerItem(marker)
        self.addItem(markerItem)

        anim = qtanim.fade_in(markerItem)
        anim.setParent(self._animParent)

    def _removeItem(self, item: QGraphicsItem):
        def remove():
            self.removeItem(item)

        anim = qtanim.fade_out(item, teardown=remove, hide_if_finished=False)
        anim.setParent(self._animParent)


class WorldBuildingMapView(BaseGraphicsView):
    def __init__(self, novel: Novel, parent=None):
        super().__init__(parent)
        self._novel = novel
        self._shown = False
        self._bgItem: Optional[QGraphicsPixmapItem] = None

        self._wdgZoomBar = ZoomBar(self)
        self._wdgZoomBar.zoomed.connect(self._scale)

        self._wdgEditor = EntityEditorWidget(self)
        self._wdgEditor.setHidden(True)

        self._popup = PopupText(self)
        self._popup.setHidden(True)

        self._btnEdit = tool_btn(IconRegistry.plus_edit_icon(PLOTLYST_SECONDARY_COLOR), parent=self)
        self._btnEdit.installEventFilter(OpacityEventFilter(self._btnEdit, 0.8, 0.5))
        self._btnEdit.setIconSize(QSize(48, 48))
        self._btnEdit.setStyleSheet(f'''
        QToolButton {{
            border: 2px solid {PLOTLYST_SECONDARY_COLOR};
            border-radius: 36px;
            background: {RELAXED_WHITE_COLOR};
            padding: 10px;
        }}
        ''')

        self._menuEdit = MenuWidget(self._btnEdit)
        self._menuEdit.setTooltipDisplayMode(ActionTooltipDisplayMode.DISPLAY_UNDER)
        self._menuEdit.aboutToShow.connect(self._fillUpEditMenu)

        self.setBackgroundBrush(QColor('#F2F2F2'))
        self._scene = WorldBuildingMapScene(self._novel)
        self.setScene(self._scene)
        self._scene.selectionChanged.connect(self._selectionChanged)
        self._scene.showPopup.connect(self._showPopup)
        self._scene.hidePopup.connect(self._hidePopup)

        self.repo = RepositoryPersistenceManager.instance()

    @overrides
    def showEvent(self, event: QShowEvent) -> None:
        if not self._shown:
            self._shown = True
            if self._novel.world.maps:
                map = self._novel.world.maps[0]
                self._loadMap(self._novel.world.maps[0])
                self._bgItem = self._scene.loadMap(map)
                if self._bgItem:
                    # call to calculate rect size
                    _ = self._scene.sceneRect()
                    self.centerOn(self._bgItem)

    @overrides
    def itemAt(self, pos: QPoint) -> QGraphicsItem:
        item = super().itemAt(pos)
        if self._bgItem and item is self._bgItem:
            return None

        return item

    @overrides
    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)
        self._arrangeSideBars()

    @overrides
    def _scale(self, scale: float):
        super()._scale(scale)
        self._wdgZoomBar.updateScaledFactor(self.scaledFactor())

    def _arrangeSideBars(self):
        self._wdgZoomBar.setGeometry(10, self.height() - self._wdgZoomBar.sizeHint().height() - 25,
                                     self._wdgZoomBar.sizeHint().width(),
                                     self._wdgZoomBar.sizeHint().height())
        self._btnEdit.setGeometry(self.width() - self._btnEdit.sizeHint().width() - 20,
                                  self.height() - self._btnEdit.sizeHint().height() - 20,
                                  self._btnEdit.sizeHint().width(),
                                  self._btnEdit.sizeHint().height())

        self._wdgEditor.setGeometry(self.width() - self._wdgEditor.width() - 20,
                                    20,
                                    self._wdgEditor.width(),
                                    self._wdgEditor.sizeHint().height())

    def _loadMap(self, map: WorldBuildingMap):
        self._bgItem = self._scene.loadMap(map)
        if self._bgItem:
            # call to calculate rect size
            _ = self._scene.sceneRect()
            self.centerOn(self._bgItem)

    def _addNewMap(self):
        loadedImage: Optional[LoadedImage] = upload_image(self._novel)
        if loadedImage:
            self._novel.world.maps.clear()
            map = WorldBuildingMap(loadedImage.ref)
            self._novel.world.maps.append(map)
            self._scene.loadMap(map)
            self._loadMap(map)
            self.repo.update_world(self._novel)

    def _selectionChanged(self):
        if len(self._scene.selectedItems()) == 1:
            self._wdgEditor.setMarker(self._scene.selectedItems()[0])
            qtanim.fade_in(self._wdgEditor)
        else:
            qtanim.fade_out(self._wdgEditor)

    def _showPopup(self, item: MarkerItem):
        self._popup.setText(item.marker().description)
        self._popupAbove(self._popup, item)

    def _hidePopup(self):
        self._popup.setHidden(True)

    def _fillUpEditMenu(self):
        self._menuEdit.clear()
        addAction = action('Add map', IconRegistry.plus_icon(), tooltip="Upload a picture for your map",
                           slot=self._addNewMap)
        if self._scene.map():
            addAction.setText('Add another map')
        self._menuEdit.addAction(addAction)
