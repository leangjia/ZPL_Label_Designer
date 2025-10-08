# -*- coding: utf-8 -*-
"""Классы штрихкодов для ZPL Label Designer"""

from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor

from utils.logger import logger
from .base import BaseElement, ElementConfig


class BarcodeElement(BaseElement):
    """Базовый класс для штрихкодов"""
    
    BARCODE_TYPES = {
        'EAN13': 'EAN-13',
        'CODE128': 'Code 128',
        'QRCODE': 'QR Code'
    }
    
    def __init__(self, config: ElementConfig, barcode_type: str, data: str, 
                 width: int = 50, height: int = 30):
        super().__init__(config)
        self.barcode_type = barcode_type
        self.data = data
        self.width = width
        self.height = height
        self.data_field = None
        self.show_text = True
    
    def to_dict(self):
        return {
            'type': 'barcode',
            'barcode_type': self.barcode_type,
            'x': self.config.x,
            'y': self.config.y,
            'data': self.data,
            'width': self.width,
            'height': self.height,
            'data_field': self.data_field,
            'show_text': self.show_text
        }
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            barcode_type=data['barcode_type'],
            data=data['data'],
            width=data.get('width', 50),
            height=data.get('height', 30)
        )
        element.data_field = data.get('data_field')
        element.show_text = data.get('show_text', True)
        return element
    
    def to_zpl(self, dpi):
        raise NotImplementedError
    
    def _get_barcode_data(self):
        return self.data_field if self.data_field else self.data


class GraphicsBarcodeItem(QGraphicsRectItem):
    """Графический элемент штрихкода"""
    
    def __init__(self, element: BarcodeElement, dpi=203, canvas=None):
        # КРИТИЧНО: Використовувати РЕАЛЬНУ ширину замість element.width!
        if hasattr(element, 'calculate_real_width'):
            real_width_mm = element.calculate_real_width(dpi)
            width_px = int(real_width_mm * dpi / 25.4)
            logger.debug(f"[BARCODE-ITEM] Using REAL width: {real_width_mm:.1f}mm -> {width_px}px")
        else:
            # Fallback для QRCode та інших
            width_px = int(element.width * dpi / 25.4)
            logger.debug(f"[BARCODE-ITEM] Using element.width: {element.width}mm -> {width_px}px")
        
        height_px = int(element.height * dpi / 25.4)
        
        super().__init__(0, 0, width_px, height_px)
        
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # Посилання на canvas для GridConfig
        
        self.setFlag(QGraphicsRectItem.ItemIsMovable)
        self.setFlag(QGraphicsRectItem.ItemIsSelectable)
        self.setFlag(QGraphicsRectItem.ItemSendsGeometryChanges)
        
        pen = QPen(QColor(0, 0, 255), 2, Qt.DashLine)
        brush = QBrush(QColor(200, 220, 255, 100))
        self.setPen(pen)
        self.setBrush(brush)
        
        # Snap to grid - КРИТИЧНО: створити ПЕРЕД setPos()!
        self.snap_enabled = True
        self.grid_step_mm = 1.0
        self.snap_threshold_mm = 1.0  # grid_step / 2 для правильного snap
        
        # Установить позицию (викликає itemChange)
        x_px = self._mm_to_px(element.config.x)
        y_px = self._mm_to_px(element.config.y)
        self.setPos(x_px, y_px)
    
    def _mm_to_px(self, mm):
        return int(mm * self.dpi / 25.4)
    
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
        if change == QGraphicsRectItem.ItemPositionHasChanged:
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
    
    def update_size(self, width, height):
        self.element.width = width
        self.element.height = height
        
        # КРИТИЧНО: Використовувати РЕАЛЬНУ ширину!
        if hasattr(self.element, 'calculate_real_width'):
            real_width_mm = self.element.calculate_real_width(self.dpi)
            width_px = self._mm_to_px(real_width_mm)
            logger.debug(f"[BARCODE-ITEM] Update: REAL width {real_width_mm:.1f}mm -> {width_px}px")
        else:
            width_px = self._mm_to_px(width)
        
        height_px = self._mm_to_px(height)
        self.setRect(0, 0, width_px, height_px)


class EAN13BarcodeElement(BarcodeElement):
    """EAN-13 штрихкод"""
    
    def __init__(self, config: ElementConfig, data: str, 
                 width: int = 20, height: int = 10):
        super().__init__(config, 'EAN13', data, width, height)
        self.module_width = 2  # dots (^BY parameter)
    
    def calculate_real_width(self, dpi=203):
        """Розрахувати РЕАЛЬНУ ширину EAN-13 на основі module width
        
        EAN-13 structure:
        - 3 quiet zone (left)
        - 3 start guard (101)
        - 42 left half (6 digits * 7 modules)
        - 5 middle guard (01010)
        - 42 right half (6 digits * 7 modules)
        - 3 end guard (101)
        - 7 quiet zone (right)
        Total: 105 modules
        """
        total_modules = 105
        width_dots = total_modules * self.module_width
        width_mm = width_dots * 25.4 / dpi
        logger.debug(f"[BARCODE-EAN13] Real width: {width_mm:.1f}mm ({total_modules} modules * {self.module_width} dots)")
        return width_mm
    
    def to_zpl(self, dpi):
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        height_dots = int(self.height * dpi / 25.4)
        
        logger.debug(f"[BARCODE-ZPL-EAN13] Position: ({self.config.x:.1f}, {self.config.y:.1f})mm -> ({x_dots}, {y_dots})dots")
        logger.debug(f"[BARCODE-ZPL-EAN13] Height: {self.height:.1f}mm -> {height_dots}dots")
        
        barcode_data = self._get_barcode_data()
        logger.debug(f"[BARCODE-ZPL-EAN13] Data: '{barcode_data}'")
        
        # Розрахувати РЕАЛЬНУ ширину для логу
        real_width_mm = self.calculate_real_width(dpi)
        logger.debug(f"[BARCODE-ZPL-EAN13] Real width: {real_width_mm:.1f}mm (will be used on print)")
        
        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BY{self.module_width}")
        zpl_lines.append(f"^BEN,{height_dots},Y,N")
        zpl_lines.append(f"^FD{barcode_data}^FS")
        
        zpl = "\n".join(zpl_lines)
        logger.debug(f"[BARCODE-ZPL-EAN13] Generated: {zpl.replace(chr(10), ' | ')}")
        
        return zpl
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            data=data['data'],
            width=data.get('width', 20),
            height=data.get('height', 10)
        )
        element.data_field = data.get('data_field')
        element.show_text = data.get('show_text', True)
        return element


class Code128BarcodeElement(BarcodeElement):
    """Code 128 штрихкод"""
    
    def __init__(self, config: ElementConfig, data: str, 
                 width: int = 30, height: int = 10):
        super().__init__(config, 'CODE128', data, width, height)
        self.module_width = 2  # dots (^BY parameter)
    
    def calculate_real_width(self, dpi=203):
        """Розрахувати РЕАЛЬНУ ширину CODE128 на основі module width
        
        CODE128 structure:
        - 10 quiet zone (left)
        - 11 start character
        - data_length * 11 (average per character)
        - 13 stop character (includes 2-bar stop pattern)
        - 10 quiet zone (right)
        """
        data_length = len(self.data)
        total_modules = 10 + 11 + (data_length * 11) + 13 + 10
        width_dots = total_modules * self.module_width
        width_mm = width_dots * 25.4 / dpi
        logger.debug(f"[BARCODE-CODE128] Real width: {width_mm:.1f}mm ({total_modules} modules * {self.module_width} dots, data_len={data_length})")
        return width_mm
    
    def to_zpl(self, dpi):
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        height_dots = int(self.height * dpi / 25.4)
        
        logger.debug(f"[BARCODE-ZPL-CODE128] Position: ({self.config.x:.1f}, {self.config.y:.1f})mm -> ({x_dots}, {y_dots})dots")
        logger.debug(f"[BARCODE-ZPL-CODE128] Height: {self.height:.1f}mm -> {height_dots}dots")
        
        barcode_data = self._get_barcode_data()
        logger.debug(f"[BARCODE-ZPL-CODE128] Data: '{barcode_data}' (len={len(barcode_data)})")
        
        # Розрахувати РЕАЛЬНУ ширину для логу
        real_width_mm = self.calculate_real_width(dpi)
        logger.debug(f"[BARCODE-ZPL-CODE128] Real width: {real_width_mm:.1f}mm (will be used on print)")
        
        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BY{self.module_width}")
        zpl_lines.append(f"^BCN,{height_dots},Y,N,N")
        zpl_lines.append(f"^FD{barcode_data}^FS")
        
        zpl = "\n".join(zpl_lines)
        logger.debug(f"[BARCODE-ZPL-CODE128] Generated: {zpl.replace(chr(10), ' | ')}")
        
        return zpl
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            data=data['data'],
            width=data.get('width', 30),
            height=data.get('height', 10)
        )
        element.data_field = data.get('data_field')
        element.show_text = data.get('show_text', True)
        return element


class QRCodeElement(BarcodeElement):
    """QR Code"""
    
    def __init__(self, config: ElementConfig, data: str, 
                 size: int = 15):
        super().__init__(config, 'QRCODE', data, width=size, height=size)
        self.size = size
        self.magnification = 3
    
    def to_zpl(self, dpi):
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        
        barcode_data = self._get_barcode_data()
        
        zpl_lines = []
        zpl_lines.append(f"^FO{x_dots},{y_dots}")
        zpl_lines.append(f"^BQN,2,{self.magnification}")
        zpl_lines.append(f"^FD{barcode_data}^FS")
        
        return "\n".join(zpl_lines)
    
    def to_dict(self):
        data = super().to_dict()
        data['size'] = self.size
        data['magnification'] = self.magnification
        return data
    
    @classmethod
    def from_dict(cls, data):
        config = ElementConfig(x=data['x'], y=data['y'])
        element = cls(
            config=config,
            data=data['data'],
            size=data.get('size', 15)
        )
        element.data_field = data.get('data_field')
        element.magnification = data.get('magnification', 3)
        return element
