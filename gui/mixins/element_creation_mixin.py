# -*- coding: utf-8 -*-
"""Mixin для створення елементів на canvas"""

from PySide6.QtWidgets import QFileDialog, QMessageBox
from core.elements.text_element import TextElement, GraphicsTextItem
from core.elements.image_element import ImageElement, GraphicsImageItem, ImageConfig
from core.elements.base import ElementConfig
from core.undo_commands import AddElementCommand
from utils.logger import logger
import base64


class ElementCreationMixin:
    """Methods for creating elements on canvas"""
    
    def _add_text(self):
        """Добавить текстовый элемент"""
        config = ElementConfig(x=10, y=10)
        text_element = TextElement(config, "New Text", font_size=25)
        
        graphics_item = GraphicsTextItem(text_element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        
        command = AddElementCommand(self, text_element, graphics_item)
        self.undo_stack.push(command)
        
        logger.info(f"Text added at ({text_element.config.x}, {text_element.config.y})")
    
    def _add_ean13(self):
        """Добавить EAN-13 штрихкод"""
        from core.elements.barcode_element import EAN13BarcodeElement, GraphicsBarcodeItem
        
        config = ElementConfig(x=10, y=10)
        element = EAN13BarcodeElement(config, data='1234567890123', width=20, height=10)
        
        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)
        
        self.elements.append(element)
        self.graphics_items.append(graphics_item)
        
        logger.info(f"EAN-13 barcode added at ({element.config.x}, {element.config.y})")
    
    def _add_code128(self):
        """Добавить Code 128 штрихкод"""
        from core.elements.barcode_element import Code128BarcodeElement, GraphicsBarcodeItem
        
        config = ElementConfig(x=10, y=10)
        element = Code128BarcodeElement(config, data='SAMPLE128', width=30, height=10)
        
        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)
        
        self.elements.append(element)
        self.graphics_items.append(graphics_item)
        
        logger.info(f"Code 128 barcode added at ({element.config.x}, {element.config.y})")
    
    def _add_qrcode(self):
        """Добавить QR Code"""
        from core.elements.barcode_element import QRCodeElement, GraphicsBarcodeItem
        
        config = ElementConfig(x=10, y=10)
        element = QRCodeElement(config, data='https://example.com', size=15)
        
        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)
        
        self.elements.append(element)
        self.graphics_items.append(graphics_item)
        
        logger.info(f"QR Code added at ({element.config.x}, {element.config.y})")
    
    def _add_rectangle(self):
        """Додати Rectangle"""
        from core.elements.shape_element import RectangleElement, ShapeConfig, GraphicsRectangleItem
        
        config = ShapeConfig(x=10, y=10, width=20, height=10, fill=False, border_thickness=1)
        element = RectangleElement(config)
        
        graphics_item = GraphicsRectangleItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)
        
        self.elements.append(element)
        self.graphics_items.append(graphics_item)
        
        logger.info(f"Rectangle added at ({element.config.x}, {element.config.y})mm, size=({element.config.width}x{element.config.height})mm")
    
    def _add_circle(self):
        """Додати Circle"""
        from core.elements.shape_element import CircleElement, ShapeConfig, GraphicsCircleItem
        
        config = ShapeConfig(x=10, y=10, width=15, height=15, fill=False, border_thickness=1)
        element = CircleElement(config)
        
        graphics_item = GraphicsCircleItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)
        
        self.elements.append(element)
        self.graphics_items.append(graphics_item)
        
        logger.info(f"Circle added at ({element.config.x}, {element.config.y})mm, size=({element.config.width}x{element.config.height})mm")
    
    def _add_line(self):
        """Додати Line"""
        from core.elements.shape_element import LineElement, LineConfig, GraphicsLineItem
        
        config = LineConfig(x=10, y=10, x2=25, y2=20, thickness=1)
        element = LineElement(config)
        
        graphics_item = GraphicsLineItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)
        
        self.elements.append(element)
        self.graphics_items.append(graphics_item)
        
        logger.info(f"Line added from ({element.config.x}, {element.config.y})mm to ({element.config.x2}, {element.config.y2})mm")
    
    def _add_image(self):
        """Додати Image елемент"""
        logger.debug(f"[ADD-IMAGE] Opening file dialog")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if not file_path:
            logger.debug(f"[ADD-IMAGE] No file selected")
            return
        
        logger.debug(f"[ADD-IMAGE] Selected file: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
                image_data = base64.b64encode(image_bytes).decode('utf-8')
            
            logger.debug(f"[ADD-IMAGE] Image data length: {len(image_data)} chars")
            
            config = ImageConfig(
                x=10.0,
                y=10.0,
                width=30.0,
                height=30.0,
                image_path=file_path,
                image_data=image_data
            )
            image_element = ImageElement(config)
            
            graphics_item = GraphicsImageItem(image_element, dpi=self.canvas.dpi, canvas=self.canvas)
            graphics_item.snap_enabled = self.snap_enabled
            
            command = AddElementCommand(self, image_element, graphics_item)
            self.undo_stack.push(command)
            
            logger.info(f"Image added: {file_path}")
            
        except Exception as e:
            logger.error(f"[ADD-IMAGE] Failed to load image: {e}", exc_info=True)
            QMessageBox.critical(self, "Add Image", f"Failed to load image:\n{e}")
    
    def _create_graphics_item(self, element):
        """Створити graphics item для елемента (використовується при завантаженні template)"""
        if isinstance(element, TextElement):
            graphics_item = GraphicsTextItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        elif isinstance(element, ImageElement):
            graphics_item = GraphicsImageItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        else:
            from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem
            from core.elements.shape_element import ShapeElement, GraphicsRectangleItem, GraphicsCircleItem, GraphicsLineItem, RectangleElement, CircleElement, LineElement
            
            if isinstance(element, BarcodeElement):
                graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
            elif isinstance(element, RectangleElement):
                graphics_item = GraphicsRectangleItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
            elif isinstance(element, CircleElement):
                graphics_item = GraphicsCircleItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
            elif isinstance(element, LineElement):
                graphics_item = GraphicsLineItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
            else:
                return None
        
        graphics_item.snap_enabled = self.snap_enabled
        return graphics_item
