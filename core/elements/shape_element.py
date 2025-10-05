# -*- coding: utf-8 -*-
"""Shape Elements для ZPL Label Designer"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsLineItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF, QRectF, QLineF
from PySide6.QtGui import QPen, QBrush, QColor

from core.elements.base import BaseElement, ElementConfig
from utils.logger import logger


class ShapeConfig(ElementConfig):
    """Базова конфігурація для Shape елементів"""
    
    def __init__(self, x=0, y=0, width=50, height=50, 
                 fill=False, border_thickness=2, color='black'):
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.fill = fill
        self.border_thickness = border_thickness
        self.color = color


class RectangleElement(BaseElement):
    """Rectangle елемент"""
    
    def __init__(self, config=None):
        if config is None:
            config = ShapeConfig()
        super().__init__(config)
        logger.debug(f"[SHAPE-RECT] Created: size=({config.width}x{config.height})mm, fill={config.fill}")
    
    def to_dict(self):
        """Серіалізація у dict"""
        return {
            'type': 'rectangle',
            'x': self.config.x,
            'y': self.config.y,
            'width': self.config.width,
            'height': self.config.height,
            'fill': self.config.fill,
            'border_thickness': self.config.border_thickness,
            'color': self.config.color
        }
    
    @classmethod
    def from_dict(cls, data):
        """Десеріалізація з dict"""
        config = ShapeConfig(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            fill=data.get('fill', False),
            border_thickness=data.get('border_thickness', 2),
            color=data.get('color', 'black')
        )
        return cls(config)
    
    def to_zpl(self, dpi=203):
        """Генерація ZPL команд для rectangle
        
        Format: ^GB{width},{height},{thickness},{color},{rounding}
        """
        # Конвертувати координати mm -> dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        width_dots = int(self.config.width * dpi / 25.4)
        height_dots = int(self.config.height * dpi / 25.4)
        
        logger.debug(f"[SHAPE-ZPL-RECT] Position: ({x_dots}, {y_dots}) dots")
        logger.debug(f"[SHAPE-ZPL-RECT] Size: ({width_dots}x{height_dots}) dots")
        
        # Визначити thickness для fill
        if self.config.fill:
            # Fill: thickness = height
            thickness = height_dots
        else:
            # Border: thickness у dots
            thickness = int(self.config.border_thickness * dpi / 25.4)
        
        logger.debug(f"[SHAPE-ZPL-RECT] Fill={self.config.fill}, thickness={thickness}")
        
        # Color (B=black, W=white)
        color = 'B' if self.config.color == 'black' else 'W'
        
        # Rounding (0 = no rounding)
        rounding = 0
        
        zpl_commands = [
            f"^FO{x_dots},{y_dots}",
            f"^GB{width_dots},{height_dots},{thickness},{color},{rounding}",
            "^FS"
        ]
        
        logger.debug(f"[SHAPE-ZPL-RECT] Generated ZPL")
        return "\n".join(zpl_commands)


class CircleElement(BaseElement):
    """Circle елемент"""
    
    def __init__(self, config=None):
        if config is None:
            config = ShapeConfig(width=50, height=50)
        super().__init__(config)
        logger.debug(f"[SHAPE-CIRCLE] Created: size=({config.width}x{config.height})mm, fill={config.fill}")
    
    def to_dict(self):
        """Серіалізація у dict"""
        return {
            'type': 'circle',
            'x': self.config.x,
            'y': self.config.y,
            'width': self.config.width,
            'height': self.config.height,
            'fill': self.config.fill,
            'border_thickness': self.config.border_thickness,
            'color': self.config.color
        }
    
    @classmethod
    def from_dict(cls, data):
        """Десеріалізація з dict"""
        config = ShapeConfig(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            fill=data.get('fill', False),
            border_thickness=data.get('border_thickness', 2),
            color=data.get('color', 'black')
        )
        return cls(config)
    
    def to_zpl(self, dpi=203):
        """Генерація ZPL команд для circle
        
        Format: ^GC{diameter},{thickness},{color}
        """
        # Конвертувати координати mm -> dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        
        # Circle diameter (використаємо width)
        diameter_dots = int(self.config.width * dpi / 25.4)
        
        logger.debug(f"[SHAPE-ZPL-CIRCLE] Position: ({x_dots}, {y_dots}) dots")
        logger.debug(f"[SHAPE-ZPL-CIRCLE] Diameter: {diameter_dots} dots")
        
        # Визначити thickness для fill
        if self.config.fill:
            # Fill: thickness = diameter (повністю заповнити)
            thickness = diameter_dots
        else:
            # Border: thickness у dots
            thickness = int(self.config.border_thickness * dpi / 25.4)
        
        logger.debug(f"[SHAPE-ZPL-CIRCLE] Fill={self.config.fill}, thickness={thickness}")
        
        # Color (B=black, W=white)
        color = 'B' if self.config.color == 'black' else 'W'
        
        zpl_commands = [
            f"^FO{x_dots},{y_dots}",
            f"^GC{diameter_dots},{thickness},{color}",
            "^FS"
        ]
        
        logger.debug(f"[SHAPE-ZPL-CIRCLE] Generated ZPL")
        return "\n".join(zpl_commands)


class LineConfig(ElementConfig):
    """Конфігурація для Line елемента"""
    
    def __init__(self, x=0, y=0, x2=50, y2=50, thickness=2, color='black'):
        super().__init__(x, y)
        self.x2 = x2
        self.y2 = y2
        self.thickness = thickness
        self.color = color


class LineElement(BaseElement):
    """Line елемент"""
    
    def __init__(self, config=None):
        if config is None:
            config = LineConfig()
        super().__init__(config)
        logger.debug(f"[SHAPE-LINE] Created: from ({config.x},{config.y}) to ({config.x2},{config.y2})mm")
    
    def to_dict(self):
        """Серіалізація у dict"""
        return {
            'type': 'line',
            'x': self.config.x,
            'y': self.config.y,
            'x2': self.config.x2,
            'y2': self.config.y2,
            'thickness': self.config.thickness,
            'color': self.config.color
        }
    
    @classmethod
    def from_dict(cls, data):
        """Десеріалізація з dict"""
        config = LineConfig(
            x=data['x'],
            y=data['y'],
            x2=data['x2'],
            y2=data['y2'],
            thickness=data.get('thickness', 2),
            color=data.get('color', 'black')
        )
        return cls(config)
    
    def to_zpl(self, dpi=203):
        """Генерація ZPL команд для line
        
        Format: ^GD{width},{height},{thickness},{color},{orientation}
        """
        # Конвертувати координати mm -> dots
        x1_dots = int(self.config.x * dpi / 25.4)
        y1_dots = int(self.config.y * dpi / 25.4)
        x2_dots = int(self.config.x2 * dpi / 25.4)
        y2_dots = int(self.config.y2 * dpi / 25.4)
        
        # Обчислити width і height
        width_dots = abs(x2_dots - x1_dots)
        height_dots = abs(y2_dots - y1_dots)
        
        logger.debug(f"[SHAPE-ZPL-LINE] From: ({x1_dots}, {y1_dots}) dots")
        logger.debug(f"[SHAPE-ZPL-LINE] To: ({x2_dots}, {y2_dots}) dots")
        logger.debug(f"[SHAPE-ZPL-LINE] Width: {width_dots}, Height: {height_dots} dots")
        
        # Thickness у dots
        thickness = int(self.config.thickness * dpi / 25.4)
        
        # Color (B=black, W=white)
        color = 'B' if self.config.color == 'black' else 'W'
        
        # Orientation: L (left lean \), R (right lean /)
        # Визначаємо за знаком (x2-x1) та (y2-y1)
        if (x2_dots >= x1_dots and y2_dots >= y1_dots) or (x2_dots < x1_dots and y2_dots < y1_dots):
            orientation = 'R'  # Right lean /
        else:
            orientation = 'L'  # Left lean \
        
        logger.debug(f"[SHAPE-ZPL-LINE] Thickness={thickness}, orientation={orientation}")
        
        zpl_commands = [
            f"^FO{x1_dots},{y1_dots}",
            f"^GD{width_dots},{height_dots},{thickness},{color},{orientation}",
            "^FS"
        ]
        
        logger.debug(f"[SHAPE-ZPL-LINE] Generated ZPL")
        return "\n".join(zpl_commands)


# === GRAPHICS ITEMS ===

class GraphicsRectangleItem(QGraphicsRectItem):
    """Graphics item для Rectangle на canvas"""
    
    def __init__(self, element, dpi=203, canvas=None, parent=None):
        super().__init__(parent)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # Посилання на canvas для GridConfig
        
        # КРИТИЧНО: створити ПЕРЕД setPos()!
        self.snap_enabled = True
        self.grid_step_mm = 2.0
        self.snap_threshold_mm = 1.0
        
        # Встановити розмір
        width_px = self._mm_to_px(element.config.width)
        height_px = self._mm_to_px(element.config.height)
        self.setRect(0, 0, width_px, height_px)
        
        # Встановити стиль
        self._update_style()
        
        # Встановити позицію
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)
        
        # Flags для drag and drop
        self.setFlags(
            QGraphicsItem.ItemIsMovable | 
            QGraphicsItem.ItemIsSelectable | 
            QGraphicsItem.ItemSendsGeometryChanges
        )
        
        logger.debug(f"[SHAPE-ITEM-RECT] Created at: ({element.config.x:.2f}, {element.config.y:.2f})mm")
    
    def _update_style(self):
        """Оновити стиль (fill/border)"""
        color = QColor('black') if self.element.config.color == 'black' else QColor('white')
        
        if self.element.config.fill:
            # Fill
            self.setBrush(QBrush(color))
            self.setPen(QPen(Qt.NoPen))
        else:
            # Border
            thickness_px = self._mm_to_px(self.element.config.border_thickness)
            self.setBrush(QBrush(Qt.NoBrush))
            self.setPen(QPen(color, thickness_px))
        
        logger.debug(f"[SHAPE-ITEM-RECT] Style updated: fill={self.element.config.fill}")
    
    def itemChange(self, change, value):
        """Перевизначити для snap to grid"""
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value
            
            # Конвертувати у мм
            x_mm = self._px_to_mm(new_pos.x())
            y_mm = self._px_to_mm(new_pos.y())
            
            # EMIT cursor position для rulers при drag
            if self.canvas:
                logger.debug(f"[ITEM-DRAG] Emitting cursor: ({x_mm:.2f}, {y_mm:.2f})mm")
                self.canvas.cursor_position_changed.emit(x_mm, y_mm)
            
            if self.snap_enabled:
                # Snap до сітки
                snapped_x = self._snap_to_grid(x_mm)
                snapped_y = self._snap_to_grid(y_mm)
                
                # Конвертувати назад у пікселі
                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x),
                    self._mm_to_px(snapped_y)
                )
                
                return snapped_pos
            
            return new_pos
        
        elif change == QGraphicsItem.ItemPositionHasChanged:
            # Оновити config після переміщення
            x_mm = self._px_to_mm(self.pos().x())
            y_mm = self._px_to_mm(self.pos().y())
            self.element.config.x = x_mm
            self.element.config.y = y_mm
        
        return super().itemChange(change, value)
    
    def _snap_to_grid(self, value_mm):
        """Прив'язка до сітки"""
        nearest = round(value_mm / self.grid_step_mm) * self.grid_step_mm
        
        if abs(value_mm - nearest) <= self.snap_threshold_mm:
            return nearest
        
        return value_mm
    
    def _mm_to_px(self, mm):
        """Конвертація мм -> пікселі"""
        return mm * self.dpi / 25.4
    
    def _px_to_mm(self, px):
        """Конвертація пікселі -> мм"""
        return px * 25.4 / self.dpi
    
    def update_from_element(self):
        """Оновити graphics item з element config"""
        width_px = self._mm_to_px(self.element.config.width)
        height_px = self._mm_to_px(self.element.config.height)
        self.setRect(0, 0, width_px, height_px)
        
        self._update_style()
        
        x_px = self._mm_to_px(self.element.config.x)
        y_px = self._mm_to_px(self.element.config.y)
        self.setPos(x_px, y_px)
        
        logger.debug(f"[SHAPE-ITEM-RECT] Updated from element")


class GraphicsCircleItem(QGraphicsEllipseItem):
    """Graphics item для Circle на canvas"""
    
    def __init__(self, element, dpi=203, canvas=None, parent=None):
        super().__init__(parent)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # Посилання на canvas для GridConfig
        
        # КРИТИЧНО: створити ПЕРЕД setPos()!
        self.snap_enabled = True
        self.grid_step_mm = 2.0
        self.snap_threshold_mm = 1.0
        
        # Встановити розмір (еліпс)
        width_px = self._mm_to_px(element.config.width)
        height_px = self._mm_to_px(element.config.height)
        self.setRect(0, 0, width_px, height_px)
        
        # Встановити стиль
        self._update_style()
        
        # Встановити позицію
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)
        
        # Flags для drag and drop
        self.setFlags(
            QGraphicsItem.ItemIsMovable | 
            QGraphicsItem.ItemIsSelectable | 
            QGraphicsItem.ItemSendsGeometryChanges
        )
        
        logger.debug(f"[SHAPE-ITEM-CIRCLE] Created at: ({element.config.x:.2f}, {element.config.y:.2f})mm")
    
    def _update_style(self):
        """Оновити стиль (fill/border)"""
        color = QColor('black') if self.element.config.color == 'black' else QColor('white')
        
        if self.element.config.fill:
            # Fill
            self.setBrush(QBrush(color))
            self.setPen(QPen(Qt.NoPen))
        else:
            # Border
            thickness_px = self._mm_to_px(self.element.config.border_thickness)
            self.setBrush(QBrush(Qt.NoBrush))
            self.setPen(QPen(color, thickness_px))
        
        logger.debug(f"[SHAPE-ITEM-CIRCLE] Style updated: fill={self.element.config.fill}")
    
    def itemChange(self, change, value):
        """Перевизначити для snap to grid - аналогічно Rectangle"""
        if change == QGraphicsItem.ItemPositionChange:
            new_pos = value
            
            x_mm = self._px_to_mm(new_pos.x())
            y_mm = self._px_to_mm(new_pos.y())
            
            # EMIT cursor position для rulers при drag
            if self.canvas:
                logger.debug(f"[ITEM-DRAG] Emitting cursor: ({x_mm:.2f}, {y_mm:.2f})mm")
                self.canvas.cursor_position_changed.emit(x_mm, y_mm)
            
            if self.snap_enabled:
                snapped_x = self._snap_to_grid(x_mm)
                snapped_y = self._snap_to_grid(y_mm)
                
                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x),
                    self._mm_to_px(snapped_y)
                )
                
                return snapped_pos
            
            return new_pos
        
        elif change == QGraphicsItem.ItemPositionHasChanged:
            x_mm = self._px_to_mm(self.pos().x())
            y_mm = self._px_to_mm(self.pos().y())
            self.element.config.x = x_mm
            self.element.config.y = y_mm
        
        return super().itemChange(change, value)
    
    def _snap_to_grid(self, value_mm):
        """Прив'язка до сітки"""
        nearest = round(value_mm / self.grid_step_mm) * self.grid_step_mm
        
        if abs(value_mm - nearest) <= self.snap_threshold_mm:
            return nearest
        
        return value_mm
    
    def _mm_to_px(self, mm):
        """Конвертація мм -> пікселі"""
        return mm * self.dpi / 25.4
    
    def _px_to_mm(self, px):
        """Конвертація пікселі -> мм"""
        return px * 25.4 / self.dpi
    
    def update_from_element(self):
        """Оновити graphics item з element config"""
        width_px = self._mm_to_px(self.element.config.width)
        height_px = self._mm_to_px(self.element.config.height)
        self.setRect(0, 0, width_px, height_px)
        
        self._update_style()
        
        x_px = self._mm_to_px(self.element.config.x)
        y_px = self._mm_to_px(self.element.config.y)
        self.setPos(x_px, y_px)
        
        logger.debug(f"[SHAPE-ITEM-CIRCLE] Updated from element")


class GraphicsLineItem(QGraphicsLineItem):
    """Graphics item для Line на canvas"""
    
    def __init__(self, element, dpi=203, canvas=None, parent=None):
        super().__init__(parent)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # Посилання на canvas для GridConfig
        
        # КРИТИЧНО: створити ПЕРЕД setPos()!
        self.snap_enabled = True
        self.grid_step_mm = 2.0
        self.snap_threshold_mm = 1.0
        
        # Встановити лінію
        x1_px = self._mm_to_px(element.config.x)
        y1_px = self._mm_to_px(element.config.y)
        x2_px = self._mm_to_px(element.config.x2)
        y2_px = self._mm_to_px(element.config.y2)
        
        self.setLine(x1_px, y1_px, x2_px, y2_px)
        
        # Встановити стиль
        self._update_style()
        
        # Flags для drag and drop
        self.setFlags(
            QGraphicsItem.ItemIsMovable | 
            QGraphicsItem.ItemIsSelectable | 
            QGraphicsItem.ItemSendsGeometryChanges
        )
        
        logger.debug(f"[SHAPE-ITEM-LINE] Created: from ({element.config.x:.2f},{element.config.y:.2f}) to ({element.config.x2:.2f},{element.config.y2:.2f})mm")
    
    def _update_style(self):
        """Оновити стиль (thickness, color)"""
        color = QColor('black') if self.element.config.color == 'black' else QColor('white')
        thickness_px = self._mm_to_px(self.element.config.thickness)
        
        self.setPen(QPen(color, thickness_px))
        
        logger.debug(f"[SHAPE-ITEM-LINE] Style updated: thickness={self.element.config.thickness}mm")
    
    def itemChange(self, change, value):
        """Перевизначити для snap to grid"""
        if change == QGraphicsItem.ItemPositionChange:
            # Line має складнішу логіку snap - snap обох кінців
            # Тут спрощена версія - snap тільки start point
            new_pos = value
            
            x_mm = self._px_to_mm(new_pos.x())
            y_mm = self._px_to_mm(new_pos.y())
            
            # EMIT cursor position для rulers при drag
            if self.canvas:
                logger.debug(f"[ITEM-DRAG] Emitting cursor: ({x_mm:.2f}, {y_mm:.2f})mm")
                self.canvas.cursor_position_changed.emit(x_mm, y_mm)
            
            if self.snap_enabled:
                snapped_x = self._snap_to_grid(x_mm)
                snapped_y = self._snap_to_grid(y_mm)
                
                snapped_pos = QPointF(
                    self._mm_to_px(snapped_x),
                    self._mm_to_px(snapped_y)
                )
                
                return snapped_pos
            
            return new_pos
        
        elif change == QGraphicsItem.ItemPositionHasChanged:
            # Оновити config після переміщення
            # Line config зберігає абсолютні координати
            line_in_scene = self.line()
            x1_mm = self._px_to_mm(line_in_scene.x1() + self.pos().x())
            y1_mm = self._px_to_mm(line_in_scene.y1() + self.pos().y())
            x2_mm = self._px_to_mm(line_in_scene.x2() + self.pos().x())
            y2_mm = self._px_to_mm(line_in_scene.y2() + self.pos().y())
            
            self.element.config.x = x1_mm
            self.element.config.y = y1_mm
            self.element.config.x2 = x2_mm
            self.element.config.y2 = y2_mm
        
        return super().itemChange(change, value)
    
    def _snap_to_grid(self, value_mm):
        """Прив'язка до сітки"""
        nearest = round(value_mm / self.grid_step_mm) * self.grid_step_mm
        
        if abs(value_mm - nearest) <= self.snap_threshold_mm:
            return nearest
        
        return value_mm
    
    def _mm_to_px(self, mm):
        """Конвертація мм -> пікселі"""
        return mm * self.dpi / 25.4
    
    def _px_to_mm(self, px):
        """Конвертація пікселі -> мм"""
        return px * 25.4 / self.dpi
    
    def update_from_element(self):
        """Оновити graphics item з element config"""
        x1_px = self._mm_to_px(self.element.config.x)
        y1_px = self._mm_to_px(self.element.config.y)
        x2_px = self._mm_to_px(self.element.config.x2)
        y2_px = self._mm_to_px(self.element.config.y2)
        
        self.setLine(x1_px, y1_px, x2_px, y2_px)
        self._update_style()
        
        logger.debug(f"[SHAPE-ITEM-LINE] Updated from element")
