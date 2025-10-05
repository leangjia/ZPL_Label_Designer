# -*- coding: utf-8 -*-
"""Текстовый элемент этикетки"""

from PySide6.QtWidgets import QGraphicsTextItem, QGraphicsItem
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QFont
from .base import BaseElement, ElementConfig

class TextElement(BaseElement):
    """Текстовый элемент"""
    
    def __init__(self, config: ElementConfig, text="Text", font_size=20):
        super().__init__(config)
        self.text = text
        self.font_size = font_size
        self.data_field = None  # Placeholder {{FIELD}}
        # Font styles
        self.bold = False
        self.italic = False  # NOT implemented in ZPL without font upload
        self.underline = False
    
    def to_dict(self):
        return {
            'type': 'text',
            'x': self.config.x,
            'y': self.config.y,
            'text': self.text,
            'font_size': self.font_size,
            'data_field': self.data_field,
            'bold': self.bold,
            'italic': self.italic,
            'underline': self.underline
        }
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(config, data['text'], data['font_size'])
        element.data_field = data.get('data_field')
        element.bold = data.get('bold', False)
        element.italic = data.get('italic', False)
        element.underline = data.get('underline', False)
        return element
    
    def to_zpl(self, dpi):
        """Генерация ZPL кода"""
        from utils.logger import logger
        
        # Конвертация мм → dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        
        # Использовать placeholder или текст
        content = self.data_field if self.data_field else self.text
        
        # Font height
        font_height = self.font_size
        
        # Bold: увеличить ширину шрифта на 50%
        if self.bold:
            font_width = int(font_height * 1.5)
            font_cmd = f"^A0N,{font_height},{font_width}"
            logger.debug(f"[ZPL-FONT] Bold: height={font_height}, width={font_width} (height*1.5)")
        else:
            # Normal: ширина = высоте (пропорциональный)
            font_cmd = f"^A0N,{font_height},{font_height}"
            logger.debug(f"[ZPL-FONT] Normal: height={font_height}")
        
        # Генерация ZPL
        lines = []
        lines.append(f"^FO{x_dots},{y_dots}")
        lines.append(font_cmd)
        lines.append(f"^FD{content}^FS")
        
        # Underline: нарисовать линию под текстом
        if self.underline:
            # Позиция линии: y + font_height + 2px offset
            underline_y = y_dots + font_height + 2
            
            # Длина текста в точках (приблизительно)
            char_count = len(content)
            avg_char_width = font_height * 0.6  # примерно 60% от высоты
            text_width = int(char_count * avg_char_width)
            
            underline_cmd = f"^FO{x_dots},{underline_y}^GB{text_width},1,1^FS"
            lines.append(underline_cmd)
            logger.debug(f"[ZPL-UNDERLINE] y={underline_y}, width={text_width}px")
        
        logger.debug(f"[ZPL-FONT-STYLES] Bold={self.bold}, Italic={self.italic}, Underline={self.underline}")
        
        return '\n'.join(lines)


class GraphicsTextItem(QGraphicsTextItem):
    """Графический текстовый элемент с drag-and-drop"""
    
    position_changed = Signal(float, float)  # x, y в мм
    
    def __init__(self, element: TextElement, dpi=203):
        super().__init__(element.text)
        self.element = element
        self.dpi = dpi
        
        # Настройки
        self.setFlag(QGraphicsTextItem.ItemIsMovable)
        self.setFlag(QGraphicsTextItem.ItemIsSelectable)
        self.setFlag(QGraphicsTextItem.ItemSendsGeometryChanges)
        
        # Установить шрифт
        font = QFont("Arial", element.font_size)
        self.setFont(font)
        
        # Snap to grid - КРИТИЧНО: створити ПЕРЕД setPos()!
        self.snap_enabled = True
        self.grid_step_mm = 2.0
        self.snap_threshold_mm = 1.0  # grid_step / 2 для полного snap
        
        # Установить позицию (викликає itemChange)
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)
    
    def _mm_to_px(self, mm):
        return mm * self.dpi / 25.4
    
    def _px_to_mm(self, px):
        return px * 25.4 / self.dpi
    
    def itemChange(self, change, value):
        """Отслеживание изменений позиции с snap to grid"""
        # SNAP TO GRID - при движении
        if change == QGraphicsItem.ItemPositionChange:
            if self.snap_enabled:
                new_pos = value
                
                # Конвертувати у мм
                x_mm = self._px_to_mm(new_pos.x())
                y_mm = self._px_to_mm(new_pos.y())
                
                # Snap до сітки
                snapped_x = self._snap_to_grid(x_mm)
                snapped_y = self._snap_to_grid(y_mm)
                
                # DEBUG
                from utils.logger import logger
                if snapped_x != x_mm or snapped_y != y_mm:
                    logger.debug(f"[SNAP] {x_mm:.2f}mm, {y_mm:.2f}mm -> {snapped_x:.1f}mm, {snapped_y:.1f}mm")
                
                # Конвертувати назад у пікселі
                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x),
                    self._mm_to_px(snapped_y)
                )
                
                return snapped_pos
        
        # ОБНОВЛЕНИЕ ЭЛЕМЕНТА - после движения
        if change == QGraphicsTextItem.ItemPositionHasChanged:
            # Обновить элемент с учетом snap
            x_mm = self._px_to_mm(self.pos().x())
            y_mm = self._px_to_mm(self.pos().y())
            
            # Применить snap если включен
            if self.snap_enabled:
                x_mm = self._snap_to_grid(x_mm)
                y_mm = self._snap_to_grid(y_mm)
            
            self.element.config.x = x_mm
            self.element.config.y = y_mm
            
            # Сигнал об изменении
            self.position_changed.emit(
                self.element.config.x, 
                self.element.config.y
            )
        
        return super().itemChange(change, value)
    
    def _snap_to_grid(self, value_mm):
        """Прив'язка до сітки"""
        # Знайти найближчу grid line
        nearest = round(value_mm / self.grid_step_mm) * self.grid_step_mm
        
        # Перевірити threshold
        if abs(value_mm - nearest) <= self.snap_threshold_mm:
            return nearest
        
        return value_mm
    
    def update_text(self, text):
        """Обновить текст"""
        self.element.text = text
        self.update_display_text()
    
    def update_font_size(self, font_size):
        """Обновить размер шрифта"""
        self.element.font_size = font_size
        font = QFont("Arial", font_size)
        self.setFont(font)
    
    def update_display_text(self):
        """Обновить отображаемый текст (placeholder или text)"""
        # Показывать placeholder если есть, иначе text
        display = self.element.data_field if self.element.data_field else self.element.text
        self.setPlainText(display)
    
    def update_display(self):
        """Обновить визуальное отображение с учетом стилей"""
        from utils.logger import logger
        
        font = self.font()
        
        # Bold
        font.setBold(self.element.bold)
        
        # Underline
        font.setUnderline(self.element.underline)
        
        # Italic - НЕ устанавливаем, т.к. ZPL не поддерживает
        # font.setItalic(self.element.italic)  # ← НЕ делать!
        
        self.setFont(font)
        logger.debug(f"[TEXT-ITEM] Display updated: Bold={self.element.bold}, Underline={self.element.underline}")
