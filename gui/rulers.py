# -*- coding: utf-8 -*-
"""Линейки для точного позиционирования элементов"""

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from utils.logger import logger
from utils.unit_converter import MeasurementUnit, UnitConverter


class RulerWidget(QWidget):
    """Линейка с делениями в миллиметрах"""
    
    def __init__(self, orientation, length_mm, dpi, scale=2.5, unit=MeasurementUnit.MM):
        """
        Args:
            orientation: Qt.Horizontal или Qt.Vertical
            length_mm: длина линейки в мм
            dpi: DPI canvas для конвертации
            scale: масштаб canvas (для синхронизации)
            unit: одиници вимірювання для відображення
        """
        super().__init__()
        
        self.orientation = orientation
        self.length_mm = length_mm
        self.dpi = dpi
        self.scale_factor = scale
        self.unit = unit
        
        # Размеры линейки
        self.ruler_thickness = 25
        self.length_px = round(self._mm_to_px(length_mm) * scale)
        
        # Настроить размер widget
        if orientation == Qt.Horizontal:
            self.setFixedHeight(self.ruler_thickness)
            self.setMinimumWidth(self.length_px)
        else:
            self.setFixedWidth(self.ruler_thickness)
            self.setMinimumHeight(self.length_px)
        
        # Цвета
        self.bg_color = QColor(240, 240, 240)
        self.major_tick_color = QColor(0, 0, 0)
        self.minor_tick_color = QColor(100, 100, 100)
        self.text_color = QColor(0, 0, 0)
        
        # Размеры делений
        self.major_tick_length = 10
        self.minor_tick_length = 5
        
        # Шрифт
        self.font = QFont("Arial", 8)
        
        # Cursor tracking
        self.cursor_pos_mm = None
        self.show_cursor = False
        
        # Element bounds highlighting
        self.highlighted_bounds = None  # (start_mm, width_mm)
    
    def _mm_to_px(self, mm):
        """Конвертация мм -> пиксели (без учета scale)"""
        return mm * self.dpi / 25.4  # Зберігаємо float для точності
    
    def set_unit(self, unit: MeasurementUnit):
        """Змінити одиницю відображення"""
        logger.debug(f"[RULER-{'H' if self.orientation==Qt.Horizontal else 'V'}] Set unit: {self.unit.value} -> {unit.value}")
        
        self.unit = unit
        self.update()
    
    def paintEvent(self, event):
        """Отрисовка линейки"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Фон
        painter.fillRect(self.rect(), self.bg_color)
        
        # Деления
        self._draw_ticks(painter)
        
        # Малюємо highlighted bounds
        if self.highlighted_bounds:
            self._draw_bounds_highlight(painter)
        
        # Малюємо cursor marker
        if self.show_cursor and self.cursor_pos_mm is not None:
            self._draw_cursor_marker(painter)
        
        painter.end()
    
    def _draw_ticks(self, painter):
        """Нарисовать деления и подписи"""
        # === GRID PARAMETERS залежно від units ===
        if self.unit == MeasurementUnit.MM:
            major_step_mm = 5.0   # Major tick (з labels) кожні 5mm → 0, 5, 10, 15, 20, 25
            minor_step_mm = 2.0   # Minor tick кожен 2mm (СПІВПАДАЄ з canvas grid)
            decimals = 0          # Labels без десяткових
        
        elif self.unit == MeasurementUnit.CM:
            major_step_mm = 10.0  # Major tick кожен 1cm
            minor_step_mm = 5.0   # Minor tick кожні 0.5cm
            decimals = 1          # Labels з 1 десятковою
        
        elif self.unit == MeasurementUnit.INCH:
            major_step_mm = 25.4      # Major tick кожен 1 inch
            minor_step_mm = 25.4 / 8  # Minor tick кожна 1/8 inch
            decimals = 2              # Labels з 2 десятковими
        
        # === DRAW TICKS ===
        # Збираємо всі позиції для ticks (major + minor)
        tick_positions = set()
        
        # Додаємо major tick позиції (кожні 5mm)
        mm = 0.0
        while mm <= self.length_mm:
            tick_positions.add(mm)
            mm += major_step_mm
        
        # Додаємо minor tick позиції (кожні 2mm)
        mm = 0.0
        while mm <= self.length_mm:
            tick_positions.add(mm)
            mm += minor_step_mm
        
        # Малюємо всі ticks
        for pos_mm in sorted(tick_positions):
            # Визначити чи це major tick (з label)
            is_major = (abs(pos_mm % major_step_mm) < 0.01)
            
            # Позиція tick в пікселях
            pos_px = round(self._mm_to_px(pos_mm) * self.scale_factor)
            
            if is_major:
                # Major tick з label
                tick_length = self.major_tick_length
                
                # Label в обраних units
                label_mm = pos_mm
                label_value = UnitConverter.mm_to_unit(label_mm, self.unit)
                
                if decimals == 0:
                    label_text = f"{int(label_value)}"
                else:
                    label_text = f"{label_value:.{decimals}f}"
                
                # Малювати tick
                self._draw_tick_at_px(painter, pos_px, tick_length, self.major_tick_color, width=2)
                self._draw_label_at_px(painter, pos_px, label_text)
            
            else:
                # Minor tick без label
                tick_length = self.minor_tick_length
                self._draw_tick_at_px(painter, pos_px, tick_length, self.minor_tick_color, width=1)
    
    def _draw_tick_at_px(self, painter, pos_px, tick_length, color, width=1):
        """Нарисувати одне ділення на позиції пікселях"""
        pen = QPen(color, width)
        painter.setPen(pen)
        
        if self.orientation == Qt.Horizontal:
            # Горизонтальна линейка
            x = pos_px
            y1 = self.ruler_thickness - tick_length
            y2 = self.ruler_thickness
            painter.drawLine(x, y1, x, y2)
        else:
            # Вертикальна линейка
            x1 = self.ruler_thickness - tick_length
            x2 = self.ruler_thickness
            y = pos_px
            painter.drawLine(x1, y, x2, y)
    
    def _draw_label_at_px(self, painter, pos_px, text):
        """Нарисувати підпис на позиції пікселях"""
        painter.setFont(self.font)
        painter.setPen(self.text_color)
        
        # Розміри тексту
        fm = painter.fontMetrics()
        text_width = fm.horizontalAdvance(text)
        text_height = fm.height()
        
        if self.orientation == Qt.Horizontal:
            # Горизонтальна линейка - текст зверху по центру
            x = pos_px - text_width // 2
            y = self.ruler_thickness - self.major_tick_length - 2
            
            rect = QRect(x, 0, text_width, y)
            painter.drawText(rect, Qt.AlignCenter, text)
        else:
            # Вертикальна линейка - текст зліва
            x = 2
            y = pos_px - text_height // 2
            
            rect = QRect(x, y, self.ruler_thickness - self.major_tick_length - 4, text_height)
            painter.drawText(rect, Qt.AlignRight | Qt.AlignVCenter, text)
    
    def update_cursor_position(self, mm):
        """Оновити позицію курсора на лінейці"""
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[RULER-{orientation_name}] Update position: {mm:.2f}mm")
        self.cursor_pos_mm = mm
        self.show_cursor = True
        self.update()  # Перемалювати
    
    def hide_cursor(self):
        """Сховати курсор"""
        self.show_cursor = False
        self.update()
    
    def _draw_cursor_marker(self, painter):
        """Малювати червону лінію на позиції курсора"""
        pen = QPen(QColor(255, 0, 0), 2, Qt.SolidLine)
        painter.setPen(pen)
        
        pos_px = round(self._mm_to_px(self.cursor_pos_mm) * self.scale_factor)
        
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[RULER-{orientation_name}] Drawn at: {pos_px}px")
        
        if self.orientation == Qt.Horizontal:
            # Вертикальна лінія на горизонтальній лінійці
            painter.drawLine(pos_px, 0, pos_px, self.ruler_thickness)
        else:
            # Горизонтальна лінія на вертикальній лінійці
            painter.drawLine(0, pos_px, self.ruler_thickness, pos_px)
    
    def highlight_bounds(self, start_mm, width_mm):
        """Підсвітити межі елемента"""
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        end_mm = start_mm + width_mm
        logger.debug(
            f"[RULER-{orientation_name}] Bounds updated: start={start_mm:.2f}mm, "
            f"end={end_mm:.2f}mm, width={width_mm:.2f}mm"
        )
        self.highlighted_bounds = (start_mm, width_mm)
        self.update()
    
    def clear_highlight(self):
        """Очистити підсвічування"""
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[BOUNDS-{orientation_name}] Clear highlight")
        self.highlighted_bounds = None
        self.update()
    
    def _draw_bounds_highlight(self, painter):
        """Малювати підсвічування меж"""
        start_mm, width_mm = self.highlighted_bounds
        
        start_px = round(self._mm_to_px(start_mm) * self.scale_factor)
        width_px = round(self._mm_to_px(width_mm) * self.scale_factor)
        
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[BOUNDS-{orientation_name}] Draw: start_px={start_px}, width_px={width_px}")
        
        # Напівпрозорий синій прямокутник
        color = QColor(100, 150, 255, 80)
        
        if self.orientation == Qt.Horizontal:
            rect = QRect(start_px, 0, width_px, self.ruler_thickness)
        else:
            rect = QRect(0, start_px, self.ruler_thickness, width_px)
        
        painter.fillRect(rect, color)
        
        # Рамка
        pen = QPen(QColor(50, 100, 255), 1)
        painter.setPen(pen)
        painter.drawRect(rect)
    
    def update_scale(self, scale_factor):
        """Обновить масштаб линейки"""
        self.scale_factor = scale_factor
        
        # Пересчитать длину
        self.length_px = round(self._mm_to_px(self.length_mm) * scale_factor)
        
        # Обновить размер widget
        if self.orientation == Qt.Horizontal:
            self.setMinimumWidth(self.length_px)
        else:
            self.setMinimumHeight(self.length_px)
        
        # Перерисовать
        self.update()
    
    def set_length(self, length_mm):
        """Змінити довжину лінейки"""
        orientation_name = "H" if self.orientation == Qt.Horizontal else "V"
        logger.debug(f"[RULER-{orientation_name}] set_length: {self.length_mm}mm -> {length_mm}mm")
        
        self.length_mm = length_mm
        self.length_px = round(self._mm_to_px(length_mm) * self.scale_factor)
        
        logger.debug(f"[RULER-{orientation_name}] New length: {length_mm}mm = {self.length_px}px (scale={self.scale_factor})")
        
        # Оновити розмір widget
        if self.orientation == Qt.Horizontal:
            self.setMinimumWidth(self.length_px)
        else:
            self.setMinimumHeight(self.length_px)
        
        # Перемалювати
        self.update()
        logger.debug(f"[RULER-{orientation_name}] Ruler updated")


class HorizontalRuler(RulerWidget):
    """Горизонтальная линейка (удобный alias)"""
    
    def __init__(self, length_mm, dpi, scale=2.5):
        super().__init__(Qt.Horizontal, length_mm, dpi, scale)


class VerticalRuler(RulerWidget):
    """Вертикальная линейка (удобный alias)"""
    
    def __init__(self, length_mm, dpi, scale=2.5):
        super().__init__(Qt.Vertical, length_mm, dpi, scale)
