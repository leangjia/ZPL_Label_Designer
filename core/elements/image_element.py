# -*- coding: utf-8 -*-
"""Image Element для ZPL Label Designer"""

from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsItem
from PySide6.QtCore import Qt, QPointF, Signal
from PySide6.QtGui import QPixmap
from pathlib import Path
import base64
from PIL import Image
import io

from core.elements.base import BaseElement, ElementConfig
from utils.logger import logger


class ImageConfig(ElementConfig):
    """Конфігурація Image елемента"""
    
    def __init__(self, x=0, y=0, width=30, height=30, 
                 image_path=None, image_data=None):
        """
        Args:
            x, y: Position в мм
            width, height: Size в мм
            image_path: Шлях до оригінального файлу (для reference)
            image_data: Base64 encoded image (для збереження в JSON)
        """
        super().__init__(x, y)
        self.width = width
        self.height = height
        self.image_path = image_path
        self.image_data = image_data


class ImageElement(BaseElement):
    """Image/Logo елемент"""
    
    def __init__(self, config=None):
        if config is None:
            config = ImageConfig()
        super().__init__(config)
        logger.debug(f"[IMAGE-ELEM] Created: pos=({config.x:.2f}, {config.y:.2f})mm, size=({config.width}x{config.height})mm")
    
    def to_dict(self):
        """Серіалізація у dict для JSON"""
        return {
            'type': 'image',
            'x': self.config.x,
            'y': self.config.y,
            'width': self.config.width,
            'height': self.config.height,
            'image_path': self.config.image_path,
            'image_data': self.config.image_data
        }
    
    @classmethod
    def from_dict(cls, data):
        """Десеріалізація з dict"""
        config = ImageConfig(
            x=data['x'],
            y=data['y'],
            width=data['width'],
            height=data['height'],
            image_path=data.get('image_path'),
            image_data=data.get('image_data')
        )
        return cls(config)
    
    def to_zpl(self, dpi=203):
        """
        Генерація ZPL ^GFA команди для зображення
        
        Returns:
            str: ZPL код для друку зображення
        """
        if not self.config.image_data and not self.config.image_path:
            logger.warning(f"[IMAGE-ZPL] No image data or path")
            return ""
        
        # Конвертувати координати mm → dots
        x_dots = int(self.config.x * dpi / 25.4)
        y_dots = int(self.config.y * dpi / 25.4)
        width_dots = int(self.config.width * dpi / 25.4)
        height_dots = int(self.config.height * dpi / 25.4)
        
        logger.debug(f"[IMAGE-ZPL] Position: ({x_dots}, {y_dots}) dots")
        logger.debug(f"[IMAGE-ZPL] Size: ({width_dots}x{height_dots}) dots")
        
        # Конвертувати зображення у ZPL hex format
        hex_data = self._convert_image_to_zpl_hex(width_dots, height_dots)
        
        if not hex_data:
            logger.error(f"[IMAGE-ZPL] Failed to convert image")
            return ""
        
        # Генерувати ZPL ^GFA команду
        # Format: ^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_data}
        bytes_per_row = (width_dots + 7) // 8
        total_bytes = bytes_per_row * height_dots
        
        zpl_commands = [
            f"^FO{x_dots},{y_dots}",
            f"^GFA,{total_bytes},{total_bytes},{bytes_per_row},{hex_data}",
            "^FS"
        ]
        
        logger.debug(f"[IMAGE-ZPL] Generated: total_bytes={total_bytes}, bytes_per_row={bytes_per_row}")
        return "\n".join(zpl_commands)
    
    def _convert_image_to_zpl_hex(self, width_dots, height_dots):
        """
        Конвертувати зображення у ZPL hex format
        
        Процес:
        1. Load image (from base64 or path)
        2. Resize to target size
        3. Convert to grayscale
        4. Apply Floyd-Steinberg dithering → 1-bit monochrome
        5. Convert pixels to hex format
        
        Args:
            width_dots: Ширина у dots
            height_dots: Висота у dots
            
        Returns:
            str: Hex data для ^GFA команди
        """
        try:
            # === 1. LOAD IMAGE ===
            if self.config.image_data:
                # З base64
                image_bytes = base64.b64decode(self.config.image_data)
                img = Image.open(io.BytesIO(image_bytes))
                logger.debug(f"[IMAGE-CONVERT] Loaded from base64")
            elif self.config.image_path:
                # З файлу
                img = Image.open(self.config.image_path)
                logger.debug(f"[IMAGE-CONVERT] Loaded from file: {self.config.image_path}")
            else:
                logger.error(f"[IMAGE-CONVERT] No image source")
                return None
            
            logger.debug(f"[IMAGE-CONVERT] Original size: {img.size}, mode: {img.mode}")
            
            # === 2. RESIZE ===
            img = img.resize((width_dots, height_dots), Image.Resampling.LANCZOS)
            logger.debug(f"[IMAGE-CONVERT] Resized to: {width_dots}x{height_dots} dots")
            
            # === 3. GRAYSCALE ===
            img = img.convert('L')
            logger.debug(f"[IMAGE-CONVERT] Converted to grayscale")
            
            # === 4. DITHERING → MONOCHROME ===
            # Floyd-Steinberg dithering для кращої якості
            img = img.convert('1')
            logger.debug(f"[IMAGE-CONVERT] Applied dithering + converted to 1-bit monochrome")
            
            # === 5. PIXELS → HEX FORMAT ===
            hex_lines = []
            bytes_per_row = (width_dots + 7) // 8
            
            for y in range(height_dots):
                row_bytes = []
                
                for x in range(0, width_dots, 8):
                    byte_value = 0
                    
                    # 8 pixels → 1 byte
                    for bit in range(8):
                        if x + bit < width_dots:
                            pixel = img.getpixel((x + bit, y))
                            # PIL '1' mode: 0 = black, 255 = white
                            # ZPL format: 1 = black, 0 = white
                            if pixel == 0:  # Black pixel
                                byte_value |= (1 << (7 - bit))
                    
                    row_bytes.append(f"{byte_value:02X}")
                
                # Padding якщо потрібно
                while len(row_bytes) < bytes_per_row:
                    row_bytes.append("00")
                
                hex_lines.append("".join(row_bytes))
            
            hex_data = "".join(hex_lines)
            logger.debug(f"[IMAGE-CONVERT] Hex data length: {len(hex_data)} chars ({len(hex_data)//2} bytes)")
            
            return hex_data
            
        except Exception as e:
            logger.error(f"[IMAGE-CONVERT] Error: {e}", exc_info=True)
            return None


class GraphicsImageItem(QGraphicsPixmapItem):
    """Graphics item для Image на canvas"""
    
    # Signal для оновлення PropertyPanel
    position_changed = Signal(float, float)
    
    def __init__(self, element, dpi=203, canvas=None, parent=None):
        super().__init__(parent)
        self.element = element
        self.dpi = dpi
        self.canvas = canvas  # Посилання на canvas для GridConfig
        
        # Snap to grid - КРИТИЧНО: створити ПЕРЕД setPos()!
        self.snap_enabled = True
        self.grid_step_mm = 2.0
        self.snap_threshold_mm = 1.0
        
        # Завантажити зображення
        self._load_image()
        
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
        
        logger.debug(f"[IMAGE-ITEM] Created at: ({element.config.x:.2f}, {element.config.y:.2f})mm")
    
    def _load_image(self):
        """Завантажити і відобразити зображення"""
        try:
            if self.element.config.image_data:
                # З base64
                image_bytes = base64.b64decode(self.element.config.image_data)
                pixmap = QPixmap()
                pixmap.loadFromData(image_bytes)
                logger.debug(f"[IMAGE-ITEM] Loaded from base64")
            elif self.element.config.image_path:
                # З файлу
                pixmap = QPixmap(self.element.config.image_path)
                logger.debug(f"[IMAGE-ITEM] Loaded from file")
            else:
                # Placeholder
                pixmap = QPixmap(100, 100)
                pixmap.fill(Qt.lightGray)
                logger.debug(f"[IMAGE-ITEM] Created placeholder")
            
            # Resize до потрібного розміру
            width_px = int(self._mm_to_px(self.element.config.width))
            height_px = int(self._mm_to_px(self.element.config.height))
            
            pixmap = pixmap.scaled(
                width_px, 
                height_px, 
                Qt.KeepAspectRatio, 
                Qt.SmoothTransformation
            )
            
            self.setPixmap(pixmap)
            logger.debug(f"[IMAGE-ITEM] Displayed: size=({pixmap.width()}x{pixmap.height()})px")
            
        except Exception as e:
            logger.error(f"[IMAGE-ITEM] Load error: {e}", exc_info=True)
            # Placeholder при помилці
            pixmap = QPixmap(100, 100)
            pixmap.fill(Qt.red)
            self.setPixmap(pixmap)
    
    def itemChange(self, change, value):
        """Обробка змін item (snap to grid, position updates)"""
        if change == QGraphicsItem.ItemPositionChange and self.snap_enabled:
            new_pos = value
            
            # Конвертувати у мм
            x_mm = self._px_to_mm(new_pos.x())
            y_mm = self._px_to_mm(new_pos.y())
            
            # Snap до сітки
            snapped_x = self._snap_to_grid(x_mm)
            snapped_y = self._snap_to_grid(y_mm)
            
            logger.debug(f"[IMAGE-SNAP] ({x_mm:.2f}, {y_mm:.2f})mm -> ({snapped_x:.2f}, {snapped_y:.2f})mm")
            
            # Конвертувати назад у пікселі
            snapped_pos = QPointF(
                self._mm_to_px(snapped_x),
                self._mm_to_px(snapped_y)
            )
            
            return snapped_pos
        
        elif change == QGraphicsItem.ItemPositionHasChanged:
            # Оновити config після переміщення
            x_mm = self._px_to_mm(self.pos().x())
            y_mm = self._px_to_mm(self.pos().y())
            self.element.config.x = x_mm
            self.element.config.y = y_mm
            
            # Signal для PropertyPanel
            self.position_changed.emit(x_mm, y_mm)
        
        return super().itemChange(change, value)
    
    def _snap_to_grid(self, value_mm):
        """Прив'язка значення до сітки"""
        nearest = round(value_mm / self.grid_step_mm) * self.grid_step_mm
        
        if abs(value_mm - nearest) <= self.snap_threshold_mm:
            return nearest
        
        return value_mm
    
    def _mm_to_px(self, mm):
        """Конвертація мм → пікселі"""
        return mm * self.dpi / 25.4
    
    def _px_to_mm(self, px):
        """Конвертація пікселі → мм"""
        return px * 25.4 / self.dpi
    
    def update_from_element(self):
        """Оновити graphics item з element config"""
        self._load_image()
        
        x_px = self._mm_to_px(self.element.config.x)
        y_px = self._mm_to_px(self.element.config.y)
        self.setPos(x_px, y_px)
        
        logger.debug(f"[IMAGE-ITEM] Updated from element")
