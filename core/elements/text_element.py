# -*- coding: utf-8 -*-
"""Текстовый элемент этикетки"""

from PySide6.QtWidgets import QGraphicsTextItem, QGraphicsItem
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QFont

from utils.logger import logger
from .base import BaseElement, ElementConfig
from enum import Enum

class ZplFont(Enum):
    """ZEBRA принтер fonts"""
    SCALABLE_0 = ("0", "Scalable (Helvetica-like)", True, (10, 32000))
    FONT_A = ("A", "9x5 Fixed", False, (9, 5))
    FONT_B = ("B", "11x7 Fixed", False, (11, 7))
    FONT_C = ("C", "18x10 Monospace Italic", False, (18, 10))
    FONT_D = ("D", "18x10 Fixed", False, (18, 10))
    FONT_E = ("E", "28x15 OCR-B", False, (28, 15))
    FONT_F = ("F", "26x13 Fixed", False, (26, 13))
    FONT_G = ("G", "60x40 Large", False, (60, 40))
    FONT_H = ("H", "34x22 OCR-A", False, (34, 22))
    
    def __init__(self, zpl_code, display_name, scalable, base_size):
        self.zpl_code = zpl_code
        self.display_name = display_name
        self.scalable = scalable
        self.base_width, self.base_height = base_size
    
    @classmethod
    def from_zpl_code(cls, code):
        """Знайти font за ZPL кодом"""
        for font in cls:
            if font.zpl_code == code:
                return font
        return cls.SCALABLE_0  # default

class TextElement(BaseElement):
    """Текстовый элемент"""
    
    def __init__(self, config: ElementConfig, text="Text", font_size=20, font_family=None):
        super().__init__(config)
        self.text = text
        self.font_size = font_size
        self.font_family = font_family or ZplFont.SCALABLE_0  # default Font 0
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
            'font_family': self.font_family.zpl_code,  # save ZPL code
            'data_field': self.data_field,
            'bold': self.bold,
            'italic': self.italic,
            'underline': self.underline
        }
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        
        # Backward compatibility: if font_family missing -> Font 0
        font_code = data.get('font_family', '0')
        font_family = ZplFont.from_zpl_code(font_code)
        
        element = cls(config, data['text'], data['font_size'], font_family)
        element.data_field = data.get('data_field')
        element.bold = data.get('bold', False)
        element.italic = data.get('italic', False)
        element.underline = data.get('underline', False)
        return element
    
    def to_zpl(self, dpi):
        """Генерация ZPL кода"""
        
        # Конвертация мм → dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        
        # Использовать placeholder или текст
        content = self.data_field if self.data_field else self.text
        
        # Font height and width
        font_height = self.font_size
        
        # Bold: увеличить ширину шрифта на 50% (только для Font 0)
        if self.bold and self.font_family == ZplFont.SCALABLE_0:
            font_width = int(font_height * 1.5)
        else:
            font_width = font_height  # proportional
        
        # ZPL font command: ^A{font_code}N,{height},{width}
        font_cmd = f"^A{self.font_family.zpl_code}N,{font_height},{font_width}"
        
        logger.debug(
            f"[ZPL-FONT] Font={self.font_family.zpl_code} "
            f"({self.font_family.display_name}), "
            f"height={font_height}, width={font_width}"
        )
        
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
    
    def __init__(self, element: TextElement, dpi=203, canvas=None):
        super().__init__(element.text)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # Посилання на canvas для GridConfig
        
        # Настройки
        self.setFlag(QGraphicsTextItem.ItemIsMovable)
        self.setFlag(QGraphicsTextItem.ItemIsSelectable)
        self.setFlag(QGraphicsTextItem.ItemSendsGeometryChanges)
        
        # Установить правильний шрифт для ZEBRA font_family
        font = self._get_qt_font_for_zebra_font(element.font_size)
        self.setFont(font)
        
        # Snap to grid - КРИТИЧНО: створити ПЕРЕД setPos()!
        self.snap_enabled = True
        self.grid_step_mm = 1.0
        self.snap_threshold_mm = 1.0  # grid_step / 2 для полного snap
        
        # Установить позицию (викликає itemChange)
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)
        
        # Оновити відображення (показати placeholder якщо є)
        self.update_display_text()
    
    def _mm_to_px(self, mm):
        return mm * self.dpi / 25.4
    
    def _px_to_mm(self, px):
        return px * 25.4 / self.dpi
    
    def itemChange(self, change, value):
        """Отслеживание изменений позиции с snap to grid"""
        # SNAP TO GRID - при движении
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value

            # Конвертувати у мм
            x_mm = self._px_to_mm(new_pos.x())
            y_mm = self._px_to_mm(new_pos.y())

            logger.debug(
                f"[ITEM-DRAG] Position changing: ({new_pos.x():.2f}, {new_pos.y():.2f})px -> "
                f"({x_mm:.2f}, {y_mm:.2f})mm"
            )

            # EMIT cursor position для rulers при drag
            if self.canvas:
                logger.debug(f"[ITEM-DRAG] Emitting cursor: ({x_mm:.2f}, {y_mm:.2f})mm")
                self.canvas.cursor_position_changed.emit(x_mm, y_mm)

            if self.snap_enabled:
                # Snap до сітки (окремо для X та Y)
                snapped_x = self._snap_to_grid(x_mm, 'x')
                snapped_y = self._snap_to_grid(y_mm, 'y')

                if snapped_x != x_mm or snapped_y != y_mm:
                    logger.debug(
                        f"[SNAP] {x_mm:.2f}mm, {y_mm:.2f}mm -> {snapped_x:.1f}mm, {snapped_y:.1f}mm"
                    )

                # Конвертувати назад у пікселі
                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x),
                    self._mm_to_px(snapped_y)
                )

                return snapped_pos

            return new_pos

        # ОБНОВЛЕНИЕ ЭЛЕМЕНТА - после движения
        if change == QGraphicsTextItem.ItemPositionHasChanged:
            # Обновить элемент с учетом snap
            x_mm = self._px_to_mm(self.pos().x())
            y_mm = self._px_to_mm(self.pos().y())

            logger.debug(
                f"[ITEM-DRAG] Position changed (raw): ({self.pos().x():.2f}, {self.pos().y():.2f})px -> "
                f"({x_mm:.2f}, {y_mm:.2f})mm"
            )

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

            if (
                self.canvas
                and getattr(self.canvas, 'bounds_update_callback', None)
                and self.isSelected()
            ):
                logger.debug(
                    f"[ITEM-DRAG] Position changed: bounds update needed "
                    f"({self.element.config.x:.2f}, {self.element.config.y:.2f})mm"
                )
                self.canvas.bounds_update_callback(self)

        return super().itemChange(change, value)

    def _snap_to_grid(self, value_mm, axis='x'):
        """Прив'язка до сітки з GridConfig (size, offset)"""
        from config import SnapMode
        
        # Fallback для старих елементів без canvas
        if not self.canvas:
            logger.debug(f"[SNAP-FALLBACK] Using default: size=1.0mm, offset=0.0mm")
            size = 1.0
            offset = 0.0
            threshold = 1.0
        else:
            config = self.canvas.grid_config
            
            # Check snap mode
            if config.snap_mode != SnapMode.GRID:
                logger.debug(f"[SNAP] Mode={config.snap_mode.value}, skipping grid snap")
                return value_mm
            
            size = config.size_x_mm if axis == 'x' else config.size_y_mm
            offset = config.offset_x_mm if axis == 'x' else config.offset_y_mm
            threshold = size / 2
            
            logger.debug(f"[SNAP-{axis.upper()}] Value: {value_mm:.2f}mm, Offset: {offset:.2f}mm, Size: {size:.2f}mm")
        
        # Snap формула: nearest = offset + round((value - offset) / size) * size
        relative = value_mm - offset
        rounded = round(relative / size) * size + offset
        
        logger.debug(f"[SNAP-{axis.upper()}] Relative: {relative:.2f}mm, Rounded: {rounded:.2f}mm")
        
        if abs(value_mm - rounded) <= threshold:
            logger.debug(f"[SNAP-{axis.upper()}] Result: {value_mm:.2f}mm -> {rounded:.2f}mm")
            return rounded
        
        logger.debug(f"[SNAP-{axis.upper()}] No snap (distance > threshold)")
        return value_mm
    
    def update_text(self, text):
        """Обновить текст"""
        self.element.text = text
        self.update_display_text()
    
    def _get_qt_font_for_zebra_font(self, size):      
        """Отримати Qt font для візуалізації ZEBRA font"""
        zpl_font = self.element.font_family
        
        if zpl_font == ZplFont.SCALABLE_0:
            # Font 0: Arial Bold (Helvetica-like)
            font = QFont("Arial", size)
            font.setBold(True)
            logger.debug(f"[CANVAS-FONT] Font 0 -> Arial Bold, size={size}")
            
        elif zpl_font == ZplFont.FONT_C:
            # Font C: Courier Italic
            font = QFont("Courier New", size)
            font.setItalic(True)
            logger.debug(f"[CANVAS-FONT] Font C -> Courier Italic, size={size}")
            
        elif zpl_font in [ZplFont.FONT_E, ZplFont.FONT_H]:
            # Font E, H: OCR fonts (fallback to Courier)
            # Спробувати OCR-A або OCR-B якщо встановлені
            font_name = "OCR A Extended" if zpl_font == ZplFont.FONT_H else "OCR B"
            font = QFont(font_name, size)
            if not font.exactMatch():
                # Fallback to Courier
                font = QFont("Courier New", size)
                logger.debug(f"[CANVAS-FONT] Font {zpl_font.zpl_code} -> Courier (OCR not available), size={size}")
            else:
                logger.debug(f"[CANVAS-FONT] Font {zpl_font.zpl_code} -> {font_name}, size={size}")
        
        else:
            # Fonts A, B, D, F, G: Courier New (monospace)
            font = QFont("Courier New", size)
            logger.debug(f"[CANVAS-FONT] Font {zpl_font.zpl_code} -> Courier New, size={size}")
        
        # Застосувати user styles (bold, underline)
        if self.element.bold and zpl_font != ZplFont.SCALABLE_0:
            # Font 0 завжди bold, для інших застосувати якщо user enable
            font.setBold(True)
        
        if self.element.underline:
            font.setUnderline(True)
        
        return font
    
    def update_font_size(self, font_size):
        """Обновить размер шрифта"""
        self.element.font_size = font_size
        # Використати правильний font для ZEBRA font_family
        font = self._get_qt_font_for_zebra_font(font_size)
        self.setFont(font)
    
    def update_font_family(self):
        """Оновити font family (викликається з PropertyPanel)"""
        logger.debug(f"[CANVAS-FONT] Updating font family to {self.element.font_family.zpl_code} ({self.element.font_family.display_name})")
        font = self._get_qt_font_for_zebra_font(self.element.font_size)
        self.setFont(font)
        logger.debug(f"[CANVAS-FONT] Font family updated successfully")
    
    def update_display_text(self):
        """Обновить отображаемый текст (placeholder или text)"""
        # Показывать placeholder если есть, иначе text
        display = self.element.data_field if self.element.data_field else self.element.text
        self.setPlainText(display)
    
    def update_display(self):
        """Обновить визуальное отображение с учетом стилей"""
        
        font = self.font()
        
        # Bold
        font.setBold(self.element.bold)
        
        # Underline
        font.setUnderline(self.element.underline)
        
        # Italic - НЕ устанавливаем, т.к. ZPL не поддерживает
        # font.setItalic(self.element.italic)  # ← НЕ делать!
        
        self.setFont(font)
        logger.debug(f"[TEXT-ITEM] Display updated: Bold={self.element.bold}, Underline={self.element.underline}")
