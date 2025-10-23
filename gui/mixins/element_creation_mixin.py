# -*- coding: utf-8 -*-
"""在画布上创建元素的混入类"""

from PySide6.QtWidgets import QFileDialog, QMessageBox
from core.elements.text_element import TextElement, GraphicsTextItem
from core.elements.image_element import ImageElement, GraphicsImageItem, ImageConfig
from core.elements.base import ElementConfig
from core.undo_commands import AddElementCommand
from utils.logger import logger
import base64


class ElementCreationMixin:
    """在画布上创建元素的方法"""

    def _add_text(self):
        """添加文本元素"""
        config = ElementConfig(x=10, y=10)
        text_element = TextElement(config, "新文本", font_size=25)

        graphics_item = GraphicsTextItem(text_element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled

        command = AddElementCommand(self, text_element, graphics_item)
        self.undo_stack.push(command)

        logger.info(f"文本已添加在 ({text_element.config.x}, {text_element.config.y})")

    def _add_ean13(self):
        """添加 EAN-13 条形码"""
        from core.elements.barcode_element import EAN13BarcodeElement, GraphicsBarcodeItem

        config = ElementConfig(x=10, y=10)
        element = EAN13BarcodeElement(config, data='1234567890123', width=20, height=10)

        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(f"EAN-13 条形码已添加在 ({element.config.x}, {element.config.y})")

    def _add_code128(self):
        """添加 Code 128 条形码"""
        from core.elements.barcode_element import Code128BarcodeElement, GraphicsBarcodeItem

        config = ElementConfig(x=10, y=10)
        element = Code128BarcodeElement(config, data='SAMPLE128', width=30, height=10)

        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(f"Code 128 条形码已添加在 ({element.config.x}, {element.config.y})")

    def _add_qrcode(self):
        """添加 QR 码"""
        from core.elements.barcode_element import QRCodeElement, GraphicsBarcodeItem

        config = ElementConfig(x=10, y=10)
        element = QRCodeElement(config, data='https://example.com', size=15)

        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(f"QR 码已添加在 ({element.config.x}, {element.config.y})")

    def _add_rectangle(self):
        """添加矩形"""
        from core.elements.shape_element import RectangleElement, ShapeConfig, GraphicsRectangleItem

        config = ShapeConfig(x=10, y=10, width=20, height=10, fill=False, border_thickness=1)
        element = RectangleElement(config)

        graphics_item = GraphicsRectangleItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(
            f"矩形已添加在 ({element.config.x}, {element.config.y})mm, 尺寸=({element.config.width}x{element.config.height})mm")

    def _add_circle(self):
        """添加圆形"""
        from core.elements.shape_element import CircleElement, ShapeConfig, GraphicsCircleItem

        config = ShapeConfig(x=10, y=10, width=15, height=15, fill=False, border_thickness=1)
        element = CircleElement(config)

        graphics_item = GraphicsCircleItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(
            f"圆形已添加在 ({element.config.x}, {element.config.y})mm, 尺寸=({element.config.width}x{element.config.height})mm")

    def _add_line(self):
        """添加线条"""
        from core.elements.shape_element import LineElement, LineConfig, GraphicsLineItem

        config = LineConfig(x=10, y=10, x2=25, y2=20, thickness=1)
        element = LineElement(config)

        graphics_item = GraphicsLineItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(
            f"线条已添加从 ({element.config.x}, {element.config.y})mm 到 ({element.config.x2}, {element.config.y2})mm")

    def _add_image(self):
        """添加图片元素"""
        logger.debug(f"[添加图片] 打开文件对话框")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图片",
            "",
            "图片 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)"
        )

        if not file_path:
            logger.debug(f"[添加图片] 未选择文件")
            return

        logger.debug(f"[添加图片] 选择的文件: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
                image_data = base64.b64encode(image_bytes).decode('utf-8')

            logger.debug(f"[添加图片] 图片数据长度: {len(image_data)} 字符")

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

            logger.info(f"图片已添加: {file_path}")

        except Exception as e:
            logger.error(f"[添加图片] 加载图片失败: {e}", exc_info=True)
            QMessageBox.critical(self, "添加图片", f"加载图片失败:\n{e}")

    def _create_graphics_item(self, element):
        """为元素创建图形项（在加载模板时使用）"""
        if isinstance(element, TextElement):
            graphics_item = GraphicsTextItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        elif isinstance(element, ImageElement):
            graphics_item = GraphicsImageItem(element, dpi=self.canvas.dpi, canvas=self.canvas)
        else:
            from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem
            from core.elements.shape_element import ShapeElement, GraphicsRectangleItem, GraphicsCircleItem, \
                GraphicsLineItem, RectangleElement, CircleElement, LineElement

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