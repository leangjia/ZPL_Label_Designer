# -*- coding: utf-8 -*-
"""Canvas для визуального редактирования этикетки"""

from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMenu
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QPen, QColor, QPainter
from utils.logger import logger

class CanvasView(QGraphicsView):
    """Canvas с сеткой для дизайна этикетки"""
    
    # Сигнал для cursor tracking
    cursor_position_changed = Signal(float, float)  # x_mm, y_mm
    context_menu_requested = Signal(object, QPoint)  # (item, global_pos)
    
    def __init__(self, width_mm=28, height_mm=28, dpi=203):
        super().__init__()
        
        self.dpi = dpi
        self.width_mm = width_mm
        self.height_mm = height_mm
        
        # Конвертация мм -> пиксели
        self.width_px = round(self._mm_to_px(width_mm))
        self.height_px = round(self._mm_to_px(height_mm))
        
        # Создать scene
        self.scene = QGraphicsScene(0, 0, self.width_px, self.height_px)
        self.setScene(self.scene)
        
        # Вирівняти scene по лівому верхньому куту (як у ZebraDesigner)
        self.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        
        # Вимкнути scroll bars щоб canvas завжди був на позиції (0,0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Настройки отображения
        self.setRenderHint(QPainter.Antialiasing)
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setBackgroundBrush(QColor(255, 255, 255))

        # Підключити signal для multi-select
        self.scene.selectionChanged.connect(self._on_selection_changed)

        # Налаштування сітки
        self.grid_visible = True
        self.grid_items = []

        # Нарисовать сетку
        self._draw_grid()
        
        # Параметри масштабування
        self.current_scale = 2.5
        self.min_scale = 0.5
        self.max_scale = 10.0
        
        # Застосувати початковий масштаб
        self.scale(self.current_scale, self.current_scale)
        
        # Посилання на лінейки (буде встановлено з MainWindow)
        self.h_ruler = None
        self.v_ruler = None
        
        # Увімкнути mouse tracking
        self.setMouseTracking(True)
        self.viewport().setMouseTracking(True)
        
        # Event filter для viewport для перехоплення wheel events
        self.viewport().installEventFilter(self)
    
    def _mm_to_px(self, mm):
        """Конвертация мм -> пиксели"""
        return mm * self.dpi / 25.4  # Float для точності
    
    def _draw_grid(self):
        """Нарисовать сетку каждые 2мм"""
        grid_step_mm = 2.0
        logger.debug(f"[GRID-DRAW] Drawing grid with step: {grid_step_mm}mm, visible: {self.grid_visible}")

        pen = QPen(QColor(200, 200, 200), 1, Qt.SolidLine)

        # Прибрати попередню сітку
        for item in self.grid_items:
            try:
                self.scene.removeItem(item)
            except RuntimeError:
                pass
        self.grid_items = []

        # Вертикальні лінії
        mm = 0.0
        while mm <= self.width_mm:
            x_px = round(self._mm_to_px(mm))
            line = self.scene.addLine(x_px, 0, x_px, self.height_px, pen)
            self.grid_items.append(line)
            mm += grid_step_mm

        # Горизонтальні лінії
        mm = 0.0
        while mm <= self.height_mm:
            y_px = round(self._mm_to_px(mm))
            line = self.scene.addLine(0, y_px, self.width_px, y_px, pen)
            self.grid_items.append(line)
            mm += grid_step_mm

        # Рамка
        border_pen = QPen(QColor(0, 0, 0), 2, Qt.SolidLine)
        border = self.scene.addRect(0, 0, self.width_px, self.height_px, border_pen)
        self.grid_items.append(border)
        
        # Встановити видимість ПІСЛЯ створення всіх items
        for item in self.grid_items:
            item.setVisible(self.grid_visible)
        
        logger.debug(f"[GRID-DRAW] Created {len(self.grid_items)} items, visibility: {self.grid_visible}")

    def set_grid_visible(self, visible: bool):
        """Керування видимістю сітки"""
        self.grid_visible = visible
        logger.debug(f"[GRID-VISIBILITY] Set to: {visible}")
        
        # Перевірити чи grid_items валідний
        if not self.grid_items:
            logger.debug(f"[GRID-VISIBILITY] grid_items empty, redrawing")
            self._draw_grid()
            return
        
        # Перевірити чи items ще у сцені
        items_valid = True
        for item in self.grid_items:
            if item is None or item.scene() is None:
                items_valid = False
                logger.debug(f"[GRID-VISIBILITY] grid_items invalid, redrawing")
                break
        
        if not items_valid:
            self.grid_items = []
            self._draw_grid()
            return
        
        # Items валідні → просто змінити видимість
        logger.debug(f"[GRID-VISIBILITY] Setting visibility on {len(self.grid_items)} items")
        for item in self.grid_items:
            try:
                item.setVisible(self.grid_visible)
            except RuntimeError:
                logger.debug(f"[GRID-VISIBILITY] RuntimeError, redrawing")
                self.grid_items = []
                self._draw_grid()
                return
        
        logger.debug(f"[GRID-VISIBILITY] Successfully set visibility to {visible}")
    
    def _on_selection_changed(self):
        """Обробка зміни виділення (для multi-select)"""
        try:
            selected = self.scene.selectedItems()
        except RuntimeError:
            # Scene уже удален при закрытии приложения
            return
        
        logger.debug(f"[SELECTION] Items selected: {len(selected)}")
        
        if len(selected) > 1:
            logger.debug(f"[SELECTION] Multi-select: {len(selected)} items")
    
    def contextMenuEvent(self, event):
        """Context menu на canvas"""
        # Отримати item під курсором
        pos = self.mapToScene(event.pos())
        item = self.scene.itemAt(pos, self.transform())
        
        logger.debug(f"[CONTEXT] Menu at: ({pos.x():.1f}, {pos.y():.1f})px")
        
        if item and hasattr(item, 'element'):
            logger.debug(f"[CONTEXT] Item found: {item.element.__class__.__name__}")
            self.context_menu_requested.emit(item, event.globalPos())
        else:
            logger.debug(f"[CONTEXT] No item - canvas menu")
            # Canvas context menu (може бути Paste якщо є clipboard)
            self.context_menu_requested.emit(None, event.globalPos())
    
    def mouseMoveEvent(self, event):
        """Відстежувати позицію курсора"""
        # Конвертувати позицію у мм
        scene_pos = self.mapToScene(event.pos())
        x_mm = self._px_to_mm(scene_pos.x())
        y_mm = self._px_to_mm(scene_pos.y())
        
        # DEBUG: cursor tracking
        logger.debug(f"[CURSOR] Signal emit: {x_mm:.2f}mm, {y_mm:.2f}mm")
        
        # Емітувати сигнал
        self.cursor_position_changed.emit(x_mm, y_mm)
        
        # Викликати батьківський метод
        super().mouseMoveEvent(event)
    
    def _px_to_mm(self, px):
        """Конвертація пікселі -> мм"""
        return px * 25.4 / self.dpi
    
    def eventFilter(self, obj, event):
        """Event filter для перехоплення wheel подій"""
        from PySide6.QtCore import QEvent
        
        if obj == self.viewport() and event.type() == QEvent.Wheel:
            self.wheelEvent(event)
            return True  # Зупинити подальшу обробку
        
        return super().eventFilter(obj, event)
    
    def wheelEvent(self, event):
        """Zoom до точки під курсором"""
        logger.debug(f"[ZOOM] wheelEvent triggered, angleDelta={event.angleDelta().y()}")
        
        # Отримати позицію курсора у scene координатах
        old_pos = self.mapToScene(event.position().toPoint())
        logger.debug(f"[ZOOM] Before: scale={self.current_scale:.2f}, cursor_pos=({old_pos.x():.1f}, {old_pos.y():.1f})")
        
        # Обчислити новий масштаб
        zoom_factor = 1.15
        if event.angleDelta().y() > 0:
            # Zoom in
            new_scale = self.current_scale * zoom_factor
            logger.debug(f"[ZOOM] Zoom IN: {self.current_scale:.2f} -> {new_scale:.2f}")
        else:
            # Zoom out
            new_scale = self.current_scale / zoom_factor
            logger.debug(f"[ZOOM] Zoom OUT: {self.current_scale:.2f} -> {new_scale:.2f}")
        
        # Обмежити масштаб
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        # Застосувати масштаб
        scale_ratio = new_scale / self.current_scale
        self.scale(scale_ratio, scale_ratio)
        self.current_scale = new_scale
        logger.debug(f"[ZOOM] Applied scale: {self.current_scale:.2f}x")
        
        # Відкоригувати позицію щоб zoom був до курсора
        new_pos = self.mapToScene(event.position().toPoint())
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        logger.debug(f"[ZOOM] After: scale={self.current_scale:.2f}, cursor_pos=({new_pos.x():.1f}, {new_pos.y():.1f})")
        logger.debug(f"[ZOOM] Position correction: delta=({delta.x():.1f}, {delta.y():.1f})")
        
        # Оновити лінейки
        self._update_rulers_scale()
        
        event.accept()
    
    def _update_rulers_scale(self):
        """Оновити масштаб лінейок"""
        updated = False

        if self.h_ruler:
            self.h_ruler.update_scale(self.current_scale)
            updated = True

        if self.v_ruler:
            self.v_ruler.update_scale(self.current_scale)
            updated = True

        if updated:
            logger.debug(f"[RULER-SCALE] Updated to: {self.current_scale:.2f}")
    
    def zoom_in(self):
        """Zoom in відносно центру viewport"""
        center = self.viewport().rect().center()
        self._zoom_at_point(center, 1.15)
    
    def zoom_out(self):
        """Zoom out відносно центру viewport"""
        center = self.viewport().rect().center()
        self._zoom_at_point(center, 1/1.15)
    
    def reset_zoom(self):
        """Скинути zoom до 100%"""
        self.resetTransform()
        self.current_scale = 1.0
        self._update_rulers_scale()
    
    def _zoom_at_point(self, point, factor):
        """Zoom до конкретної точки"""
        old_pos = self.mapToScene(point)
        
        new_scale = self.current_scale * factor
        new_scale = max(self.min_scale, min(self.max_scale, new_scale))
        
        scale_ratio = new_scale / self.current_scale
        self.scale(scale_ratio, scale_ratio)
        self.current_scale = new_scale
        
        new_pos = self.mapToScene(point)
        delta = new_pos - old_pos
        self.translate(delta.x(), delta.y())
        
        self._update_rulers_scale()
    
    def clear_and_redraw_grid(self):
        """Очистить scene и перемалевать сетку"""
        grid_visible_state = self.grid_visible
        
        self.scene.clear()
        self.grid_items = []
        
        self.grid_visible = grid_visible_state
        self._draw_grid()
        
        logger.debug(f"[CLEAR-REDRAW] Grid redrawn with visibility: {self.grid_visible}")
    
    def set_label_size(self, width_mm, height_mm):
        """Змінити розмір етикетки"""
        logger.debug(f"[LABEL-SIZE] Before: {self.width_mm}x{self.height_mm}mm")
        logger.debug(f"[LABEL-SIZE] Request: {width_mm}x{height_mm}mm")
        
        # Зберегти старий розмір
        old_width = self.width_mm
        old_height = self.height_mm
        
        # Оновити розмір
        self.width_mm = width_mm
        self.height_mm = height_mm
        self.width_px = round(self._mm_to_px(width_mm))
        self.height_px = round(self._mm_to_px(height_mm))

        # Оновити лінейки, якщо вони прикріплені до canvas
        if self.h_ruler:
            self.h_ruler.set_length(width_mm)
        if self.v_ruler:
            self.v_ruler.set_length(height_mm)

        # Переконатися, що масштаб лінейок синхронізований з canvas
        self._update_rulers_scale()
        
        logger.debug(f"[LABEL-SIZE] Width: {width_mm}mm = {self.width_px}px")
        logger.debug(f"[LABEL-SIZE] Height: {height_mm}mm = {self.height_px}px")
        
        # Оновити scene rect
        self.scene.setSceneRect(0, 0, self.width_px, self.height_px)
        logger.debug(f"[LABEL-SIZE] Scene rect updated: {self.width_px}x{self.height_px}px")
        
        # Перемалювати сітку та рамку
        # Зберегти елементи та grid_visible ПЕРЕД очисткою
        items_to_preserve = [item for item in self.scene.items() 
                            if hasattr(item, 'element')]
        grid_visible_state = self.grid_visible
        logger.debug(f"[LABEL-SIZE] Preserving {len(items_to_preserve)} elements, grid_visible={grid_visible_state}")
        
        # Очистити scene
        self.scene.clear()
        self.grid_items = []
        
        # Перемалювати сітку з ЗБЕРЕЖЕНИМ state
        self.grid_visible = grid_visible_state
        self._draw_grid()

        # Відновити елементи
        for item in items_to_preserve:
            self.scene.addItem(item)
        
        logger.debug(f"[LABEL-SIZE] Grid redrawn with visibility: {self.grid_visible}, {len(items_to_preserve)} elements restored")
        logger.debug(f"[LABEL-SIZE] After: {self.width_mm}x{self.height_mm}mm")
