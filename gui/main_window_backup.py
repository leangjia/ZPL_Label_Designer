# -*- coding: utf-8 -*-
"""应用程序主窗口"""

from PySide6.QtWidgets import (QMainWindow, QDockWidget, QMessageBox,
                               QTextEdit, QDialog, QVBoxLayout, QLabel,
                               QInputDialog, QFileDialog, QWidget, QGridLayout, QToolTip, QCheckBox,
                               QDoubleSpinBox, QPushButton, QHBoxLayout, QComboBox)
from PySide6.QtCore import Qt, QEvent
from PySide6.QtGui import QPixmap, QCursor, QShortcut, QKeySequence, QUndoStack
from io import BytesIO
from .canvas_view import CanvasView
from .toolbar import EditorToolbar
from .property_panel import PropertyPanel
from .smart_guides import SmartGuides
from .rulers import HorizontalRuler, VerticalRuler
from core.elements.text_element import TextElement, GraphicsTextItem
from core.elements.image_element import ImageElement, GraphicsImageItem, ImageConfig
from core.undo_commands import (
    AddElementCommand,
    DeleteElementCommand,
    MoveElementCommand,
    ChangePropertyCommand
)
from core.elements.base import ElementConfig
from core.template_manager import TemplateManager
from zpl.generator import ZPLGenerator
from integration.labelary_client import LabelaryClient
from utils.logger import logger
from utils.unit_converter import MeasurementUnit, UnitConverter
from config import DEFAULT_UNIT, UNIT_DECIMALS, UNIT_STEPS


class MainWindow(QMainWindow):
    """编辑器主窗口"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZPL 标签设计器")
        self.resize(1200, 700)
        logger.info("主窗口已初始化")

        # 元素和图形项列表
        self.elements = []
        self.graphics_items = []
        self.selected_item = None

        # 剪贴板用于复制/粘贴
        self.clipboard_element = None

        # ZPL 生成器
        self.zpl_generator = ZPLGenerator(dpi=203)
        self.labelary_client = LabelaryClient(dpi=203)
        self.template_manager = TemplateManager()
        logger.info("ZPL 生成器、Labelary 客户端和模板管理器已创建")

        # 创建画布
        self.canvas = CanvasView(width_mm=28, height_mm=28, dpi=203)
        logger.info("画布已创建 (28x28mm, DPI 203)")

        # 智能参考线（在创建画布之后！）
        self.smart_guides = SmartGuides(self.canvas.scene)
        self.guides_enabled = True
        logger.info("智能参考线已初始化")

        # 撤销/重做堆栈
        self.undo_stack = QUndoStack(self)
        logger.debug(f"[撤销堆栈] 已初始化")

        # 保存拖拽前的位置用于移动命令
        self.drag_start_pos = None

        # 创建标尺
        self.h_ruler = HorizontalRuler(length_mm=28, dpi=203, scale=2.5)
        self.v_ruler = VerticalRuler(length_mm=28, dpi=203, scale=2.5)
        logger.info("标尺已创建")

        # 在画布中设置标尺引用
        self.canvas.h_ruler = self.h_ruler
        self.canvas.v_ruler = self.v_ruler
        logger.info("标尺已链接到画布")

        # 创建中央控件和布局
        central_widget = QWidget()
        grid_layout = QGridLayout(central_widget)
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        # 添加到布局: [空白] [水平标尺]
        #                     [垂直标尺] [画布]
        corner_spacer = QWidget()
        corner_spacer.setFixedSize(25, 25)
        grid_layout.addWidget(corner_spacer, 0, 0)
        grid_layout.addWidget(self.h_ruler, 0, 1)
        grid_layout.addWidget(self.v_ruler, 1, 0)
        grid_layout.addWidget(self.canvas, 1, 1)

        self.setCentralWidget(central_widget)
        logger.info("带标尺的中央控件已配置")

        # 创建工具栏
        self.toolbar = EditorToolbar(self)
        self.addToolBar(self.toolbar)
        logger.info("工具栏已创建")

        # 创建属性面板
        self.property_panel = PropertyPanel()
        dock = QDockWidget("属性", self)
        dock.setWidget(self.property_panel)
        dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        logger.info("属性面板已创建")

        # 连接画布信号
        self.canvas.scene.selectionChanged.connect(self._on_selection_changed)

        # 连接工具栏信号
        self.toolbar.add_text_action.triggered.connect(self._add_text)
        self.toolbar.add_ean13_action.triggered.connect(self._add_ean13)
        self.toolbar.add_code128_action.triggered.connect(self._add_code128)
        self.toolbar.add_qrcode_action.triggered.connect(self._add_qrcode)
        self.toolbar.add_rectangle_action.triggered.connect(self._add_rectangle)
        self.toolbar.add_circle_action.triggered.connect(self._add_circle)
        self.toolbar.add_line_action.triggered.connect(self._add_line)
        self.toolbar.add_image_action.triggered.connect(self._add_image)
        self.toolbar.save_action.triggered.connect(self._save_template)
        self.toolbar.load_action.triggered.connect(self._load_template)
        self.toolbar.export_action.triggered.connect(self._export_zpl)
        self.toolbar.preview_action.triggered.connect(self._show_preview)
        logger.info("信号已连接")

        # 连接光标追踪
        self.canvas.cursor_position_changed.connect(self._update_ruler_cursor)
        self.canvas.context_menu_requested.connect(self._show_context_menu)

        # 追踪光标何时离开画布
        self.canvas.viewport().installEventFilter(self)
        self.canvas.scene.installEventFilter(self)
        logger.info("光标追踪和场景事件已连接")

        # 缩放键盘快捷键
        self._setup_shortcuts()
        logger.info("键盘快捷键已配置")

        # 网格吸附
        self.snap_enabled = True
        self._create_snap_toggle()

        # 当前显示单位
        self.current_unit = DEFAULT_UNIT

        # 标签尺寸控件
        self._create_label_size_controls()

        # 单位控件
        self._create_units_controls()

    def _undo(self):
        """撤销最后一次操作"""
        if self.undo_stack.canUndo():
            logger.debug(f"[撤销操作] 撤销: {self.undo_stack.undoText()}")
            self.undo_stack.undo()
        else:
            logger.debug(f"[撤销操作] 没有可撤销的操作")

    def _redo(self):
        """重做已撤销的操作"""
        if self.undo_stack.canRedo():
            logger.debug(f"[撤销操作] 重做: {self.undo_stack.redoText()}")
            self.undo_stack.redo()
        else:
            logger.debug(f"[撤销操作] 没有可重做的操作")

    def _add_text(self):
        """添加文本元素"""
        # 创建元素
        config = ElementConfig(x=10, y=10)
        text_element = TextElement(config, "新文本", font_size=25)

        # 创建图形元素
        graphics_item = GraphicsTextItem(text_element, dpi=self.canvas.dpi)
        # 根据当前状态设置吸附
        graphics_item.snap_enabled = self.snap_enabled

        # 通过撤销命令添加
        command = AddElementCommand(self, text_element, graphics_item)
        self.undo_stack.push(command)

        logger.info(f"文本已添加在 ({text_element.config.x}, {text_element.config.y})")

    def _add_ean13(self):
        """添加 EAN-13 条码"""
        from core.elements.barcode_element import EAN13BarcodeElement, GraphicsBarcodeItem

        config = ElementConfig(x=10, y=10)
        element = EAN13BarcodeElement(config, data='1234567890123', width=20, height=10)

        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(f"EAN-13 条码已添加在 ({element.config.x}, {element.config.y})")

    def _add_code128(self):
        """添加 Code 128 条码"""
        from core.elements.barcode_element import Code128BarcodeElement, GraphicsBarcodeItem

        config = ElementConfig(x=10, y=10)
        element = Code128BarcodeElement(config, data='SAMPLE128', width=30, height=10)

        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(f"Code 128 条码已添加在 ({element.config.x}, {element.config.y})")

    def _add_qrcode(self):
        """添加 QR 码"""
        from core.elements.barcode_element import QRCodeElement, GraphicsBarcodeItem

        config = ElementConfig(x=10, y=10)
        element = QRCodeElement(config, data='https://example.com', size=15)

        graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(f"QR 码已添加在 ({element.config.x}, {element.config.y})")

    def _add_rectangle(self):
        """添加矩形"""
        from core.elements.shape_element import RectangleElement, ShapeConfig, GraphicsRectangleItem

        config = ShapeConfig(x=10, y=10, width=20, height=10, fill=False, border_thickness=2)
        element = RectangleElement(config)

        graphics_item = GraphicsRectangleItem(element, dpi=self.canvas.dpi)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(
            f"矩形已添加在 ({element.config.x}, {element.config.y})mm, 尺寸=({element.config.width}x{element.config.height})mm")

    def _add_circle(self):
        """添加圆形"""
        from core.elements.shape_element import CircleElement, ShapeConfig, GraphicsCircleItem

        config = ShapeConfig(x=10, y=10, width=15, height=15, fill=False, border_thickness=2)
        element = CircleElement(config)

        graphics_item = GraphicsCircleItem(element, dpi=self.canvas.dpi)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(
            f"圆形已添加在 ({element.config.x}, {element.config.y})mm, 尺寸=({element.config.width}x{element.config.height})mm")

    def _add_line(self):
        """添加线条"""
        from core.elements.shape_element import LineElement, LineConfig, GraphicsLineItem

        config = LineConfig(x=10, y=10, x2=25, y2=20, thickness=2)
        element = LineElement(config)

        graphics_item = GraphicsLineItem(element, dpi=self.canvas.dpi)
        graphics_item.snap_enabled = self.snap_enabled
        self.canvas.scene.addItem(graphics_item)

        self.elements.append(element)
        self.graphics_items.append(graphics_item)

        logger.info(
            f"线条已添加从 ({element.config.x}, {element.config.y})mm 到 ({element.config.x2}, {element.config.y2})mm")

    def _add_image(self):
        """添加图片元素"""
        import base64

        logger.debug(f"[添加图片] 打开文件对话框")

        # 文件选择对话框
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

        # 将图片转换为 base64
        try:
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
                image_data = base64.b64encode(image_bytes).decode('utf-8')

            logger.debug(f"[添加图片] 图片数据长度: {len(image_data)} 字符")

            # 创建图片元素
            config = ImageConfig(
                x=10.0,
                y=10.0,
                width=30.0,  # 30mm 默认
                height=30.0,
                image_path=file_path,
                image_data=image_data
            )
            image_element = ImageElement(config)

            # 创建图形项
            graphics_item = GraphicsImageItem(image_element, dpi=self.canvas.dpi)
            graphics_item.snap_enabled = self.snap_enabled

            # 通过撤销命令添加
            command = AddElementCommand(self, image_element, graphics_item)
            self.undo_stack.push(command)

            logger.info(f"图片已添加: {file_path}")

        except Exception as e:
            logger.error(f"[添加图片] 加载图片失败: {e}", exc_info=True)
            QMessageBox.critical(self, "添加图片", f"加载图片失败:\n{e}")

    def _on_selection_changed(self):
        """处理选择变化"""
        selected = self.canvas.scene.selectedItems()

        if len(selected) == 1:
            # 单选
            graphics_item = selected[0]

            if hasattr(graphics_item, 'element'):
                element = graphics_item.element
                self.selected_item = graphics_item
                self.property_panel.set_element(element, graphics_item)

                # 在标尺上高亮边界
                self._highlight_element_bounds(graphics_item)

                logger.info(f"已选择元素在 ({element.config.x:.1f}, {element.config.y:.1f})")

        elif len(selected) > 1:
            # 多选
            logger.debug(f"[多选] {len(selected)} 个项目被选择")
            self.selected_item = None
            self.property_panel.set_element(None, None)
            self.h_ruler.clear_highlight()
            self.v_ruler.clear_highlight()
            logger.info(f"多选: {len(selected)} 个元素")

        else:
            # 清除高亮
            self.h_ruler.clear_highlight()
            self.v_ruler.clear_highlight()
            self.selected_item = None
            self.property_panel.set_element(None, None)
            logger.debug("选择已清除")

    def _export_zpl(self):
        """导出为 ZPL"""
        if not self.elements:
            logger.warning("导出 ZPL: 没有要导出的元素")
            QMessageBox.warning(self, "导出", "没有要导出的元素")
            return

        # 生成 ZPL
        label_config = {
            'width': self.canvas.width_mm,
            'height': self.canvas.height_mm,
            'dpi': self.canvas.dpi
        }

        zpl_code = self.zpl_generator.generate(self.elements, label_config)
        logger.info("已生成 ZPL 代码用于导出")

        # 在对话框中显示
        dialog = QDialog(self)
        dialog.setWindowTitle("ZPL 代码")
        dialog.resize(600, 400)

        layout = QVBoxLayout()
        text_edit = QTextEdit()
        text_edit.setPlainText(zpl_code)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        dialog.setLayout(layout)

        dialog.exec()

        logger.info("ZPL 导出对话框已显示")

    def _save_template(self):
        """将模板保存为 JSON"""
        if not self.elements:
            logger.warning("保存模板: 没有要保存的元素")
            QMessageBox.warning(self, "保存", "没有要保存的元素")
            return

        # 选择保存路径的对话框
        default_path = str(self.template_manager.templates_dir / "my_template.json")
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "保存模板",
            default_path,
            "JSON 文件 (*.json)"
        )

        if not filepath:
            return

        # 确保扩展名为 .json
        if not filepath.endswith('.json'):
            filepath += '.json'

        # 从路径中提取模板名称
        from pathlib import Path
        template_name = Path(filepath).stem

        # 准备配置
        label_config = {
            'width': self.canvas.width_mm,
            'height': self.canvas.height_mm,
            'dpi': self.canvas.dpi
        }

        # 元数据
        metadata = {
            'elements_count': len(self.elements),
            'application': 'ZPL 标签设计器 1.0'
        }

        try:
            # 直接创建 JSON 结构
            from datetime import datetime
            import json

            template_data = {
                "name": template_name,
                "version": "1.0",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "label_config": {
                    "width_mm": label_config.get('width', 28),
                    "height_mm": label_config.get('height', 28),
                    "dpi": label_config.get('dpi', 203),
                    "display_unit": self.current_unit.value  # ← 保存显示单位
                },
                "elements": [element.to_dict() for element in self.elements],
                "metadata": metadata
            }

            logger.info(f"[模板] 使用显示单位保存: {self.current_unit.value}")

            # 保存到选择的文件
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)

            logger.info(f"模板已保存: {filepath}")
            QMessageBox.information(
                self,
                "保存",
                f"模板保存成功!\n{filepath}"
            )

        except Exception as e:
            logger.error(f"保存模板失败: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "保存错误",
                f"保存模板失败:\n{e}"
            )

    def _load_template(self):
        """从 JSON 加载模板"""
        # 打开文件选择对话框
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "加载模板",
            str(self.template_manager.templates_dir),
            "JSON 文件 (*.json)"
        )

        if not filepath:
            return

        try:
            # 加载模板
            template_data = self.template_manager.load_template(filepath)

            # 清除当前画布（重新绘制网格）
            self.canvas.clear_and_redraw_grid()
            self.elements.clear()
            self.graphics_items.clear()

            # 应用模板中的显示单位
            display_unit = template_data.get('display_unit', MeasurementUnit.MM)

            # 设置单位组合框
            index = self.units_combobox.findData(display_unit)
            if index >= 0:
                self.units_combobox.setCurrentIndex(index)
                # 会自动调用 _on_unit_changed

            logger.info(f"[模板] 应用显示单位: {display_unit.value}")

            # 更新画布配置（如果需要）
            label_config = template_data['label_config']
            width_mm = label_config.get('width_mm', 28)
            height_mm = label_config.get('height_mm', 28)

            logger.debug(f"[加载模板] 模板中的标签尺寸: {width_mm}x{height_mm}mm")

            # 如果尺寸不同则应用新尺寸
            if width_mm != self.canvas.width_mm or height_mm != self.canvas.height_mm:
                logger.info(f"[加载模板] 应用新标签尺寸: {width_mm}x{height_mm}mm")
                self.canvas.set_label_size(width_mm, height_mm)
                self.h_ruler.set_length(width_mm)
                self.v_ruler.set_length(height_mm)

                # 更新微调框
                self.width_spinbox.blockSignals(True)
                self.height_spinbox.blockSignals(True)
                self.width_spinbox.setValue(width_mm)
                self.height_spinbox.setValue(height_mm)
                self.width_spinbox.blockSignals(False)
                self.height_spinbox.blockSignals(False)

                logger.debug(f"[加载模板] 微调框已更新: 宽={width_mm}, 高={height_mm}")

            # 添加元素到画布
            from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem

            for element in template_data['elements']:
                # 创建图形元素
                if isinstance(element, TextElement):
                    graphics_item = GraphicsTextItem(element, dpi=self.canvas.dpi)
                elif isinstance(element, BarcodeElement):
                    graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
                elif isinstance(element, ImageElement):
                    graphics_item = GraphicsImageItem(element, dpi=self.canvas.dpi)
                else:
                    continue

                self.canvas.scene.addItem(graphics_item)

                # 保存
                self.elements.append(element)
                self.graphics_items.append(graphics_item)

            logger.info(f"模板已加载: {filepath} ({len(self.elements)} 个元素)")
            QMessageBox.information(
                self,
                "加载",
                f"模板加载成功!\n{len(self.elements)} 个元素"
            )

        except Exception as e:
            logger.error(f"加载模板失败: {e}", exc_info=True)
            QMessageBox.critical(
                self,
                "加载错误",
                f"加载模板失败:\n{e}"
            )

    def _highlight_element_bounds(self, item):
        """在标尺上高亮元素边界"""
        if hasattr(item, 'element'):
            element = item.element
            x = element.config.x
            y = element.config.y

            # 从 boundingRect 获取尺寸
            bounds = item.boundingRect()
            width_px = bounds.width()
            height_px = bounds.height()

            # 转换为毫米
            dpi = 203
            width_mm = width_px * 25.4 / dpi
            height_mm = height_px * 25.4 / dpi

            logger.debug(f"[边界] 元素位置: x={x:.2f}mm, y={y:.2f}mm")
            logger.debug(f"[边界] 尺寸: 宽={width_mm:.2f}mm, 高={height_mm:.2f}mm")

            # 在标尺上高亮
            self.h_ruler.highlight_bounds(x, width_mm)
            self.v_ruler.highlight_bounds(y, height_mm)
            logger.info(f"已高亮边界: X={x}mm 宽={width_mm:.1f}mm, Y={y}mm 高={height_mm:.1f}mm")

    def _update_ruler_cursor(self, x_mm, y_mm):
        """更新标尺上的光标标记"""
        self.h_ruler.update_cursor_position(x_mm)
        self.v_ruler.update_cursor_position(y_mm)

        # 显示工具提示
        self._show_cursor_tooltip(x_mm, y_mm)

    def _show_cursor_tooltip(self, x_mm, y_mm):
        """显示带坐标的工具提示"""
        tooltip_text = f"X: {x_mm:.1f} mm\nY: {y_mm:.1f} mm"
        QToolTip.showText(QCursor.pos(), tooltip_text)

    def eventFilter(self, obj, event):
        """处理画布和场景事件"""
        if obj == self.canvas.viewport():
            if event.type() == QEvent.Leave:
                self.h_ruler.hide_cursor()
                self.v_ruler.hide_cursor()
            # 将滚轮事件传递给 CanvasView
            elif event.type() == QEvent.Wheel:
                return False  # 不阻塞，传递

        elif obj == self.canvas.scene:
            # 为移动命令保存位置
            if event.type() == QEvent.GraphicsSceneMousePress:
                items = self.canvas.scene.items(event.scenePos())
                item = items[0] if items else None

                if item and hasattr(item, 'element'):
                    self.drag_start_pos = (item.element.config.x, item.element.config.y)
                    logger.debug(f"[拖拽开始] 位置: ({self.drag_start_pos[0]:.2f}, {self.drag_start_pos[1]:.2f})")
                else:
                    self.drag_start_pos = None

            # 拖拽期间的智能参考线
            elif event.type() == QEvent.GraphicsSceneMouseMove:
                # 获取光标下的项目
                items = self.canvas.scene.items(event.scenePos())
                dragged_item = items[0] if items else None

                if self.guides_enabled and dragged_item and hasattr(dragged_item, 'element'):
                    snap_pos = self.smart_guides.check_alignment(
                        dragged_item,
                        self.graphics_items,
                        dpi=203
                    )
                    if snap_pos:
                        snap_x, snap_y = snap_pos
                        if snap_x is not None:
                            dragged_item.element.config.x = snap_x
                        if snap_y is not None:
                            dragged_item.element.config.y = snap_y

                        # 更新图形位置
                        dpi = 203
                        x_px = dragged_item.element.config.x * dpi / 25.4
                        y_px = dragged_item.element.config.y * dpi / 25.4
                        dragged_item.setPos(x_px, y_px)

            # 拖拽后清除参考线
            elif event.type() == QEvent.GraphicsSceneMouseRelease:
                # 如果位置改变则创建移动命令
                items = self.canvas.scene.items(event.scenePos())
                item = items[0] if items else None

                if item and hasattr(item, 'element') and self.drag_start_pos:
                    old_x, old_y = self.drag_start_pos
                    new_x = item.element.config.x
                    new_y = item.element.config.y

                    if abs(new_x - old_x) > 0.01 or abs(new_y - old_y) > 0.01:
                        logger.debug(f"[拖拽结束] 创建移动命令")
                        command = MoveElementCommand(item.element, item, old_x, old_y, new_x, new_y)
                        self.undo_stack.push(command)

                    self.drag_start_pos = None

                self.smart_guides.clear_guides()

        return super().eventFilter(obj, event)

    def _setup_shortcuts(self):
        """键盘快捷键"""
        # 放大
        zoom_in = QShortcut(QKeySequence("Ctrl++"), self)
        zoom_in.activated.connect(self.canvas.zoom_in)

        # 放大（替代键）
        zoom_in2 = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in2.activated.connect(self.canvas.zoom_in)

        # 缩小
        zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out.activated.connect(self.canvas.zoom_out)

        # 重置缩放
        zoom_reset = QShortcut(QKeySequence("Ctrl+0"), self)
        zoom_reset.activated.connect(self.canvas.reset_zoom)

        # 吸附切换
        snap_toggle = QShortcut(QKeySequence("Ctrl+G"), self)
        snap_toggle.activated.connect(lambda: self._toggle_snap(0 if self.snap_enabled else 2))

        # 字体样式 - 粗体
        bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_shortcut.activated.connect(self._toggle_bold)

        # 字体样式 - 下划线
        underline_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        underline_shortcut.activated.connect(self._toggle_underline)

        # 粗体切换
        bold_toggle = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_toggle.activated.connect(self._toggle_bold)

        # 下划线切换
        underline_toggle = QShortcut(QKeySequence("Ctrl+U"), self)
        underline_toggle.activated.connect(self._toggle_underline)

        logger.debug("缩放快捷键: Ctrl+加号, Ctrl+减号, Ctrl+0")
        logger.debug("吸附快捷键: Ctrl+G")

    def _toggle_guides(self, state):
        """智能参考线切换器"""
        self.guides_enabled = (state == 2)
        self.smart_guides.set_enabled(self.guides_enabled)
        logger.debug(f"[参考线切换] 启用: {self.guides_enabled}")

    def _create_snap_toggle(self):
        """创建网格吸附切换器"""
        snap_checkbox = QCheckBox("网格吸附")
        snap_checkbox.setChecked(True)
        snap_checkbox.stateChanged.connect(self._toggle_snap)

        # 添加到工具栏
        self.toolbar.addSeparator()
        self.toolbar.addWidget(snap_checkbox)

        # 智能参考线复选框
        guides_checkbox = QCheckBox("智能参考线")
        guides_checkbox.setChecked(True)
        guides_checkbox.stateChanged.connect(self._toggle_guides)
        self.toolbar.addWidget(guides_checkbox)

        logger.info("网格吸附和智能参考线切换器已创建")

        # 关键：调用 _toggle_snap 为现有元素设置吸附
        self._toggle_snap(2)  # 2 = Qt.Checked

    def _toggle_snap(self, state):
        """启用/禁用吸附"""
        # state 是 int: 0=未选中, 2=选中
        self.snap_enabled = (state == 2)  # Qt.Checked = 2

        # 更新所有元素
        for item in self.graphics_items:
            if hasattr(item, 'snap_enabled'):
                item.snap_enabled = self.snap_enabled

        logger.info(f"网格吸附: {'开启' if self.snap_enabled else '关闭'} (项目: {len(self.graphics_items)})")

    def _toggle_bold(self):
        """为选中元素切换粗体"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            element = self.selected_item.element

            if hasattr(element, 'bold'):
                element.bold = not element.bold

                # 更新图形项
                if hasattr(self.selected_item, 'update_display'):
                    self.selected_item.update_display()

                # 更新属性面板复选框
                if self.property_panel.current_element == element:
                    self.property_panel.bold_checkbox.blockSignals(True)
                    self.property_panel.bold_checkbox.setChecked(element.bold)
                    self.property_panel.bold_checkbox.blockSignals(False)

                logger.debug(f"[快捷键] 粗体已切换: {element.bold}")

    def _toggle_underline(self):
        """为选中元素切换下划线"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            element = self.selected_item.element

            if hasattr(element, 'underline'):
                element.underline = not element.underline

                # 更新图形项
                if hasattr(self.selected_item, 'update_display'):
                    self.selected_item.update_display()

                # 更新属性面板复选框
                if self.property_panel.current_element == element:
                    self.property_panel.underline_checkbox.blockSignals(True)
                    self.property_panel.underline_checkbox.setChecked(element.underline)
                    self.property_panel.underline_checkbox.blockSignals(False)

                logger.debug(f"[快捷键] 下划线已切换: {element.underline}")

    def _move_selected(self, dx_mm, dy_mm):
        """移动选中的元素（支持多选）"""
        selected = self.canvas.scene.selectedItems()

        if len(selected) > 1:
            # 组移动
            logger.debug(f"[组移动] 移动 {len(selected)} 个项目 ({dx_mm:.2f}, {dy_mm:.2f})mm")

            for item in selected:
                if hasattr(item, 'element'):
                    element = item.element
                    old_x, old_y = element.config.x, element.config.y

                    element.config.x += dx_mm
                    element.config.y += dy_mm

                    # 更新图形项位置
                    dpi = 203
                    new_x = element.config.x * dpi / 25.4
                    new_y = element.config.y * dpi / 25.4
                    item.setPos(new_x, new_y)

                    # 为撤销创建移动命令
                    command = MoveElementCommand(element, item, old_x, old_y, element.config.x, element.config.y)
                    self.undo_stack.push(command)

            logger.info(f"移动了 {len(selected)} 个元素 ({dx_mm}, {dy_mm})mm")

        elif self.selected_item and hasattr(self.selected_item, 'element'):
            # 单元素移动
            element = self.selected_item.element
            old_x, old_y = element.config.x, element.config.y

            element.config.x += dx_mm
            element.config.y += dy_mm

            logger.debug(f"[移动] 之前: ({old_x:.2f}, {old_y:.2f})mm")
            logger.debug(f"[移动] 增量: ({dx_mm:.2f}, {dy_mm:.2f})mm")
            logger.debug(f"[移动] 之后: ({element.config.x:.2f}, {element.config.y:.2f})mm")

            # 更新图形项位置
            dpi = 203
            new_x = element.config.x * dpi / 25.4
            new_y = element.config.y * dpi / 25.4
            self.selected_item.setPos(new_x, new_y)

            # 更新属性面板和边界
            if self.property_panel.current_element:
                self.property_panel.update_position(element.config.x, element.config.y)
            self._highlight_element_bounds(self.selected_item)

            logger.info(f"元素已移动: dx={dx_mm}mm, dy={dy_mm}mm -> ({element.config.x}, {element.config.y})")

    def _copy_selected(self):
        """将选中元素复制到剪贴板"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            import copy
            self.clipboard_element = copy.deepcopy(self.selected_item.element)
            logger.debug(f"[剪贴板] 已复制: {self.clipboard_element.__class__.__name__}")
            logger.info(f"元素已复制到剪贴板")

    def _paste_from_clipboard(self):
        """从剪贴板粘贴元素"""
        if not self.clipboard_element:
            logger.debug(f"[剪贴板] 为空 - 没有可粘贴的内容")
            return

        import copy
        new_element = copy.deepcopy(self.clipboard_element)

        # 偏移以视觉区分
        new_element.config.x += 5.0
        new_element.config.y += 5.0

        logger.debug(f"[剪贴板] 粘贴位置: ({new_element.config.x:.2f}, {new_element.config.y:.2f})mm")

        # 添加到画布
        graphics_item = self._create_graphics_item(new_element)
        self.canvas.scene.addItem(graphics_item)
        self.elements.append(new_element)
        self.graphics_items.append(graphics_item)

        # 选择新项目
        self.canvas.scene.clearSelection()
        graphics_item.setSelected(True)

        logger.info(f"元素已从剪贴板粘贴")

    def _create_graphics_item(self, element):
        """为元素创建图形项"""
        if isinstance(element, TextElement):
            graphics_item = GraphicsTextItem(element, dpi=self.canvas.dpi)
        else:
            from core.elements.barcode_element import BarcodeElement, GraphicsBarcodeItem
            if isinstance(element, BarcodeElement):
                graphics_item = GraphicsBarcodeItem(element, dpi=self.canvas.dpi)
            else:
                return None

        graphics_item.snap_enabled = self.snap_enabled
        return graphics_item

    def _duplicate_selected(self):
        """复制选中元素（复制 + 粘贴）"""
        if self.selected_item:
            logger.debug(f"[复制] 开始")
            self._copy_selected()
            self._paste_from_clipboard()
            logger.info(f"元素已复制")

    def _bring_to_front(self):
        """移到最前面（z 顺序）"""
        if self.selected_item:
            max_z = max([item.zValue() for item in self.graphics_items], default=0)
            self.selected_item.setZValue(max_z + 1)
            logger.debug(f"[Z顺序] 移到最前面: z={max_z + 1}")
            logger.info(f"元素已移到最前面")

    def _send_to_back(self):
        """移到最后面（z 顺序）"""
        if self.selected_item:
            min_z = min([item.zValue() for item in self.graphics_items], default=0)
            self.selected_item.setZValue(min_z - 1)
            logger.debug(f"[Z顺序] 移到最后面: z={min_z - 1}")
            logger.info(f"元素已移到最后面")

    def _show_context_menu(self, item, global_pos):
        """显示上下文菜单"""
        from PySide6.QtWidgets import QMenu

        menu = QMenu(self)

        if item:  # 项目上下文菜单
            logger.debug(f"[上下文菜单] 创建项目菜单")

            copy_action = menu.addAction("复制 (Ctrl+C)")
            copy_action.triggered.connect(self._copy_selected)

            duplicate_action = menu.addAction("复制 (Ctrl+D)")
            duplicate_action.triggered.connect(self._duplicate_selected)

            menu.addSeparator()

            front_action = menu.addAction("移到最前面")
            front_action.triggered.connect(self._bring_to_front)

            back_action = menu.addAction("移到最后面")
            back_action.triggered.connect(self._send_to_back)

            menu.addSeparator()

            delete_action = menu.addAction("删除 (Del)")
            delete_action.triggered.connect(self._delete_selected)
        else:  # 画布上下文菜单
            logger.debug(f"[上下文菜单] 创建画布菜单")

            paste_action = menu.addAction("粘贴 (Ctrl+V)")
            paste_action.triggered.connect(self._paste_from_clipboard)
            paste_action.setEnabled(self.clipboard_element is not None)

        logger.debug(f"[上下文菜单] 显示位置: {global_pos}")
        menu.exec(global_pos)

    def _delete_selected(self):
        """删除选中的元素（支持多选）"""
        selected = self.canvas.scene.selectedItems()

        if len(selected) > 1:
            # 组删除
            logger.debug(f"[组删除] 删除 {len(selected)} 个项目")

            for item in selected:
                if hasattr(item, 'element'):
                    element = item.element
                    command = DeleteElementCommand(self, element, item)
                    self.undo_stack.push(command)

            # 清除 UI
            self.selected_item = None
            self.h_ruler.clear_highlight()
            self.v_ruler.clear_highlight()
            self.property_panel.set_element(None, None)
            logger.info(f"删除了 {len(selected)} 个元素")

        elif self.selected_item:
            # 单元素删除
            # 在 removeItem 之前保存（竞态条件！）
            item_to_delete = self.selected_item
            element_to_delete = item_to_delete.element if hasattr(item_to_delete, 'element') else None

            if element_to_delete:
                logger.debug(f"[删除] 创建删除命令")
                command = DeleteElementCommand(self, element_to_delete, item_to_delete)
                self.undo_stack.push(command)

                # 清除 UI
                self.selected_item = None
                self.h_ruler.clear_highlight()
                self.v_ruler.clear_highlight()
                self.property_panel.set_element(None, None)
                logger.debug(f"[删除] UI 已清除")

    def keyPressEvent(self, event):
        """键盘快捷键"""
        modifiers = event.modifiers()
        key = event.key()

        # === 缩放 ===
        if modifiers == Qt.ControlModifier:
            if key in (Qt.Key_Plus, Qt.Key_Equal):
                logger.debug("[快捷键] Ctrl+加号 - 放大")
                self.canvas.zoom_in()
            elif key == Qt.Key_Minus:
                logger.debug("[快捷键] Ctrl+减号 - 缩小")
                self.canvas.zoom_out()
            elif key == Qt.Key_0:
                logger.debug("[快捷键] Ctrl+0 - 重置缩放")
                self.canvas.reset_zoom()
            # === 吸附 ===
            elif key == Qt.Key_G:
                logger.debug("[快捷键] Ctrl+G - 切换吸附")
                self.snap_enabled = not self.snap_enabled
                self._toggle_snap(Qt.Checked if self.snap_enabled else Qt.Unchecked)
            # === 剪贴板 ===
            elif key == Qt.Key_C:
                logger.debug("[快捷键] Ctrl+C - 复制")
                self._copy_selected()
            elif key == Qt.Key_V:
                logger.debug("[快捷键] Ctrl+V - 粘贴")
                self._paste_from_clipboard()
            elif key == Qt.Key_D:
                logger.debug("[快捷键] Ctrl+D - 复制")
                self._duplicate_selected()
            # === 撤销/重做 ===
            elif key == Qt.Key_Z:
                logger.debug("[快捷键] Ctrl+Z - 撤销")
                self._undo()
            elif key == Qt.Key_Y:
                logger.debug("[快捷键] Ctrl+Y - 重做")
                self._redo()

        # === 删除 ===
        elif key in (Qt.Key_Delete, Qt.Key_Backspace):
            logger.debug(f"[快捷键] {event.key()} - 删除元素")
            self._delete_selected()

        # === 精确移动 (Shift + 方向键) ===
        elif modifiers == Qt.ShiftModifier:
            if key == Qt.Key_Left:
                logger.debug("[快捷键] Shift+左 - 移动 -0.1mm")
                self._move_selected(-0.1, 0)
            elif key == Qt.Key_Right:
                logger.debug("[快捷键] Shift+右 - 移动 +0.1mm")
                self._move_selected(0.1, 0)
            elif key == Qt.Key_Up:
                logger.debug("[快捷键] Shift+上 - 移动 -0.1mm")
                self._move_selected(0, -0.1)
            elif key == Qt.Key_Down:
                logger.debug("[快捷键] Shift+下 - 移动 +0.1mm")
                self._move_selected(0, 0.1)

        # === 正常移动 (方向键) ===
        elif modifiers == Qt.NoModifier:
            if key == Qt.Key_Left:
                logger.debug("[快捷键] 左 - 移动 -1mm")
                self._move_selected(-1, 0)
            elif key == Qt.Key_Right:
                logger.debug("[快捷键] 右 - 移动 +1mm")
                self._move_selected(1, 0)
            elif key == Qt.Key_Up:
                logger.debug("[快捷键] 上 - 移动 -1mm")
                self._move_selected(0, -1)
            elif key == Qt.Key_Down:
                logger.debug("[快捷键] 下 - 移动 +1mm")
                self._move_selected(0, 1)

        super().keyPressEvent(event)

    def _show_preview(self):
        """通过 Labelary 显示预览"""
        logger.info("=" * 60)
        logger.info("预览请求已启动")
        logger.info("=" * 60)

        if not self.elements:
            logger.warning("预览中止: 画布上没有元素")
            QMessageBox.warning(self, "预览", "没有要预览的元素")
            return

        # 元素信息
        logger.info(f"元素数量: {len(self.elements)}")
        for i, element in enumerate(self.elements):
            element_info = f"元素 {i + 1}: 类型={element.__class__.__name__}"
            if hasattr(element, 'text'):
                element_info += f", 文本='{element.text}'"
            if hasattr(element, 'font_size'):
                element_info += f", 字体大小={element.font_size}"
            element_info += f", 位置=({element.config.x:.1f}, {element.config.y:.1f})"
            if hasattr(element, 'data_field') and element.data_field:
                element_info += f", 占位符='{element.data_field}'"
            logger.info(element_info)

        # 生成 ZPL
        label_config = {
            'width': self.canvas.width_mm,
            'height': self.canvas.height_mm,
            'dpi': self.canvas.dpi
        }
        logger.info(f"标签配置: {label_config}")

        # 为预览将占位符替换为测试数据
        test_data = {}
        for element in self.elements:
            if hasattr(element, 'data_field') and element.data_field:
                # 从 {{字段名}} 中提取字段名称
                field_name = element.data_field.replace('{{', '').replace('}}', '')
                test_data[field_name] = '[测试数据]'

        if test_data:
            logger.info(f"占位符的测试数据: {test_data}")
        else:
            logger.info("没有占位符，使用实际文本值")

        logger.info("正在生成 ZPL 代码...")
        zpl_code = self.zpl_generator.generate(self.elements, label_config, test_data)

        # 在 DEBUG 模式下显示 ZPL
        logger.debug("=" * 60)
        logger.debug("生成的 ZPL 代码:")
        logger.debug("=" * 60)
        for line in zpl_code.split('\n'):
            logger.debug(line)
        logger.debug("=" * 60)

        # 获取预览
        logger.info("正在从 Labelary API 请求预览...")
        try:
            image = self.labelary_client.preview(
                zpl_code,
                self.canvas.width_mm,
                self.canvas.height_mm
            )

            if image:
                logger.info("收到预览图片，显示对话框")

                # 显示预览
                dialog = QDialog(self)
                dialog.setWindowTitle("预览")

                layout = QVBoxLayout()
                label = QLabel()

                # 转换 PIL Image -> QPixmap
                image_bytes = BytesIO()
                image.save(image_bytes, format='PNG')
                pixmap = QPixmap()
                pixmap.loadFromData(image_bytes.getvalue())

                logger.info(f"图片尺寸: {pixmap.width()}x{pixmap.height()}px")

                # 缩放以显示
                pixmap = pixmap.scaled(400, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                label.setPixmap(pixmap)

                layout.addWidget(label)
                dialog.setLayout(layout)
                dialog.resize(450, 450)
                dialog.exec()

                logger.info("预览对话框已关闭")
                logger.info("=" * 60)
            else:
                logger.error("预览失败: Labelary 客户端返回 None")
                logger.info("=" * 60)
                QMessageBox.critical(self, "预览", "生成预览失败。请检查日志了解详情。")

        except Exception as e:
            logger.error("=" * 60)
            logger.error("预览异常")
            logger.error("=" * 60)
            logger.error(f"异常类型: {type(e).__name__}")
            logger.error(f"异常消息: {e}", exc_info=True)
            logger.error("=" * 60)
            QMessageBox.critical(self, "预览", f"生成预览失败: {e}")

    def _create_label_size_controls(self):
        """创建用于更改标签尺寸的控件"""
        from config import CONFIG

        # 容器控件
        label_size_widget = QWidget()
        layout = QHBoxLayout(label_size_widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        # 标签
        layout.addWidget(QLabel("标签尺寸 (mm):"))

        # 宽度微调框
        layout.addWidget(QLabel("宽:"))
        self.width_spinbox = QDoubleSpinBox()
        self.width_spinbox.setRange(CONFIG['MIN_LABEL_WIDTH_MM'], CONFIG['MAX_LABEL_WIDTH_MM'])
        self.width_spinbox.setValue(self.canvas.width_mm)
        self.width_spinbox.setDecimals(1)
        self.width_spinbox.setSingleStep(1.0)
        self.width_spinbox.setFixedWidth(70)
        layout.addWidget(self.width_spinbox)

        # 高度微调框
        layout.addWidget(QLabel("高:"))
        self.height_spinbox = QDoubleSpinBox()
        self.height_spinbox.setRange(CONFIG['MIN_LABEL_HEIGHT_MM'], CONFIG['MAX_LABEL_HEIGHT_MM'])
        self.height_spinbox.setValue(self.canvas.height_mm)
        self.height_spinbox.setDecimals(1)
        self.height_spinbox.setSingleStep(1.0)
        self.height_spinbox.setFixedWidth(70)
        layout.addWidget(self.height_spinbox)

        # 应用按钮
        apply_button = QPushButton("应用")
        apply_button.clicked.connect(self._apply_label_size)
        apply_button.setFixedWidth(60)
        layout.addWidget(apply_button)

        # 添加到工具栏
        self.toolbar.addSeparator()
        self.toolbar.addWidget(label_size_widget)

        logger.info(f"标签尺寸控件已创建 (范围: {CONFIG['MIN_LABEL_WIDTH_MM']}-{CONFIG['MAX_LABEL_WIDTH_MM']}mm)")

    def _apply_label_size(self):
        """应用新标签尺寸"""
        width_mm = self.width_spinbox.value()
        height_mm = self.height_spinbox.value()

        logger.debug(f"[尺寸应用] 用户请求: {width_mm}x{height_mm}mm")

        # 检查是否改变
        if width_mm == self.canvas.width_mm and height_mm == self.canvas.height_mm:
            logger.debug(f"[尺寸应用] 无变化，跳过")
            return

        # 应用到画布
        self.canvas.set_label_size(width_mm, height_mm)

        # 更新标尺
        self.h_ruler.set_length(width_mm)
        self.v_ruler.set_length(height_mm)

        logger.info(f"[尺寸应用] 标签尺寸已更新: {width_mm}x{height_mm}mm")

    def _create_units_controls(self):
        """创建用于选择测量单位的控件"""
        # 单位组合框
        units_label = QLabel("单位:")
        self.units_combobox = QComboBox()

        # 添加所有选项
        for unit in MeasurementUnit:
            self.units_combobox.addItem(unit.value.upper(), unit)

        # 设置默认值
        index = self.units_combobox.findData(self.current_unit)
        self.units_combobox.setCurrentIndex(index)

        # 连接信号
        self.units_combobox.currentIndexChanged.connect(self._on_unit_changed)

        # 添加到工具栏
        self.toolbar.addSeparator()
        self.toolbar.addWidget(units_label)
        self.toolbar.addWidget(self.units_combobox)

        logger.debug(f"[单位] 已初始化: {self.current_unit.value}")

    def _on_unit_changed(self, index):
        """单位组合框已更改"""
        old_unit = self.current_unit
        new_unit = self.units_combobox.itemData(index)

        logger.info(f"[单位] 已更改: {old_unit.value} -> {new_unit.value}")

        self.current_unit = new_unit

        # 1. 更新标签尺寸微调框
        self._update_label_size_spinboxes(old_unit, new_unit)

        # 2. 更新属性面板（如果有选中的元素）
        if self.selected_item and hasattr(self.selected_item, 'element'):
            self.property_panel.update_for_unit(new_unit)

        # 3. 更新标尺
        if hasattr(self.canvas, 'h_ruler') and self.canvas.h_ruler:
            self.canvas.h_ruler.set_unit(new_unit)

        if hasattr(self.canvas, 'v_ruler') and self.canvas.v_ruler:
            self.canvas.v_ruler.set_unit(new_unit)

        logger.info(f"[单位] 更新完成")

    def _update_label_size_spinboxes(self, old_unit, new_unit):
        """更改单位时更新标签尺寸微调框"""
        # 获取当前值（毫米）（始终以毫米保存！）
        width_mm = UnitConverter.unit_to_mm(
            self.width_spinbox.value(),
            old_unit
        )
        height_mm = UnitConverter.unit_to_mm(
            self.height_spinbox.value(),
            old_unit
        )

        # 转换为新单位
        width_new = UnitConverter.mm_to_unit(width_mm, new_unit)
        height_new = UnitConverter.mm_to_unit(height_mm, new_unit)

        # 更新微调框
        from config import CONFIG
        decimals = UNIT_DECIMALS[new_unit]
        step = UNIT_STEPS[new_unit]

        # 宽度
        self.width_spinbox.blockSignals(True)
        self.width_spinbox.setDecimals(decimals)
        self.width_spinbox.setSingleStep(step)
        self.width_spinbox.setSuffix(f" {new_unit.value}")

        # 新单位范围
        min_width, max_width = UnitConverter.get_range_in_unit(
            CONFIG['MIN_LABEL_WIDTH_MM'],
            CONFIG['MAX_LABEL_WIDTH_MM'],
            new_unit
        )
        self.width_spinbox.setRange(min_width, max_width)
        self.width_spinbox.setValue(width_new)
        self.width_spinbox.blockSignals(False)

        # 高度（类似）
        self.height_spinbox.blockSignals(True)
        self.height_spinbox.setDecimals(decimals)
        self.height_spinbox.setSingleStep(step)
        self.height_spinbox.setSuffix(f" {new_unit.value}")

        min_height, max_height = UnitConverter.get_range_in_unit(
            CONFIG['MIN_LABEL_HEIGHT_MM'],
            CONFIG['MAX_LABEL_HEIGHT_MM'],
            new_unit
        )
        self.height_spinbox.setRange(min_height, max_height)
        self.height_spinbox.setValue(height_new)
        self.height_spinbox.blockSignals(False)

        logger.debug(f"[单位] 标签尺寸已更新: {width_new:.2f}x{height_new:.2f} {new_unit.value}")

    def _toggle_bold(self):
        """切换选中元素的粗体"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            element = self.selected_item.element

            if hasattr(element, 'bold'):
                element.bold = not element.bold

                # 更新图形项
                if hasattr(self.selected_item, 'update_display'):
                    self.selected_item.update_display()

                # 更新属性面板复选框
                if self.property_panel.current_element == element:
                    self.property_panel.bold_checkbox.blockSignals(True)
                    self.property_panel.bold_checkbox.setChecked(element.bold)
                    self.property_panel.bold_checkbox.blockSignals(False)

                logger.debug(f"[快捷键] 粗体已切换: {element.bold}")

    def _toggle_underline(self):
        """切换选中元素的下划线"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            element = self.selected_item.element

            if hasattr(element, 'underline'):
                element.underline = not element.underline

                # 更新图形项
                if hasattr(self.selected_item, 'update_display'):
                    self.selected_item.update_display()

                # 更新属性面板复选框
                if self.property_panel.current_element == element:
                    self.property_panel.underline_checkbox.blockSignals(True)
                    self.property_panel.underline_checkbox.setChecked(element.underline)
                    self.property_panel.underline_checkbox.blockSignals(False)

                logger.debug(f"[快捷键] 下划线已切换: {element.underline}")