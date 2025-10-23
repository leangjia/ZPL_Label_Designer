# -*- coding: utf-8 -*-
"""元素属性面板"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit,
                               QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout, QComboBox)
from PySide6.QtCore import Signal
from utils.logger import logger
from utils.unit_converter import UnitConverter
from config import UNIT_DECIMALS, UNIT_STEPS
from core.elements.text_element import ZplFont


class PropertyPanel(QWidget):
    """选中元素的属性面板"""

    property_changed = Signal(str, object)  # (属性名称, 新值)

    def __init__(self):
        super().__init__()
        self.current_element = None
        self.current_graphics_item = None
        self._setup_ui()
        logger.info("属性面板已初始化")

    def _setup_ui(self):
        """创建用户界面"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)

        # === 位置分组 ===
        pos_group = QGroupBox("位置")
        pos_form = QFormLayout()

        self.x_input = QDoubleSpinBox()
        self.x_input.setRange(0, 100)
        self.x_input.setDecimals(1)
        self.x_input.setSingleStep(0.1)
        self.x_input.setSuffix(" mm")
        self.x_input.valueChanged.connect(
            lambda v: self._on_property_change('x', v)
        )
        pos_form.addRow("X:", self.x_input)

        self.y_input = QDoubleSpinBox()
        self.y_input.setRange(0, 100)
        self.y_input.setDecimals(1)
        self.y_input.setSingleStep(0.1)
        self.y_input.setSuffix(" mm")
        self.y_input.valueChanged.connect(
            lambda v: self._on_property_change('y', v)
        )
        pos_form.addRow("Y:", self.y_input)

        pos_group.setLayout(pos_form)

        # === 文本属性分组 ===
        text_group = QGroupBox("文本属性")
        text_form = QFormLayout()

        self.text_input = QLineEdit()
        self.text_input.textChanged.connect(
            lambda v: self._on_property_change('text', v)
        )
        text_form.addRow("文本:", self.text_input)

        # 字体族下拉菜单
        self.font_family_combo = QComboBox()
        for font in ZplFont:
            self.font_family_combo.addItem(font.display_name, font)
        self.font_family_combo.currentIndexChanged.connect(self._on_font_family_changed)
        text_form.addRow("字体:", self.font_family_combo)

        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(10, 100)
        self.font_size_input.valueChanged.connect(
            lambda v: self._on_property_change('font_size', v)
        )
        text_form.addRow("字体大小:", self.font_size_input)

        self.placeholder_input = QLineEdit()
        self.placeholder_input.setPlaceholderText("{{字段名}}")
        self.placeholder_input.textChanged.connect(
            lambda v: self._on_property_change('data_field', v if v else None)
        )
        text_form.addRow("占位符:", self.placeholder_input)

        # 字体样式
        from PySide6.QtWidgets import QCheckBox

        styles_label = QLabel("样式:")
        text_form.addRow(styles_label)

        self.bold_checkbox = QCheckBox("粗体 (Ctrl+B)")
        self.bold_checkbox.stateChanged.connect(self._on_bold_changed)
        text_form.addRow("", self.bold_checkbox)

        self.italic_checkbox = QCheckBox("斜体 [需要上传字体到打印机]")
        self.italic_checkbox.setEnabled(False)
        self.italic_checkbox.setToolTip("ZPL 不支持斜体，除非将斜体字体上传到打印机")
        text_form.addRow("", self.italic_checkbox)

        self.underline_checkbox = QCheckBox("下划线 (Ctrl+U)")
        self.underline_checkbox.stateChanged.connect(self._on_underline_changed)
        text_form.addRow("", self.underline_checkbox)

        text_group.setLayout(text_form)
        self.text_group = text_group

        # === 条码属性分组 ===
        barcode_group = QGroupBox("条码属性")
        barcode_form = QFormLayout()

        self.barcode_type_label = QLabel()
        barcode_form.addRow("类型:", self.barcode_type_label)

        self.barcode_data_input = QLineEdit()
        self.barcode_data_input.textChanged.connect(
            lambda v: self._on_property_change('barcode_data', v)
        )
        barcode_form.addRow("数据:", self.barcode_data_input)

        self.barcode_width_input = QSpinBox()
        self.barcode_width_input.setRange(10, 100)
        self.barcode_width_input.setSuffix(" mm")
        self.barcode_width_input.setReadOnly(True)  # 只读！宽度自动计算
        self.barcode_width_input.setStyleSheet("QSpinBox { background-color: #f0f0f0; }")
        self.barcode_width_input.setToolTip("宽度根据模块宽度自动计算")
        barcode_form.addRow("宽度:", self.barcode_width_input)

        # 关键：模块宽度用于控制实际宽度！
        self.barcode_module_width_input = QSpinBox()
        self.barcode_module_width_input.setRange(1, 5)
        self.barcode_module_width_input.setSuffix(" 点")
        self.barcode_module_width_input.setToolTip("模块宽度 (^BY 参数)。越小 = 条码越窄。")
        self.barcode_module_width_input.valueChanged.connect(
            lambda v: self._on_property_change('barcode_module_width', v)
        )
        barcode_form.addRow("模块宽度:", self.barcode_module_width_input)

        self.barcode_height_input = QSpinBox()
        self.barcode_height_input.setRange(10, 100)
        self.barcode_height_input.setSuffix(" mm")
        self.barcode_height_input.valueChanged.connect(
            lambda v: self._on_property_change('barcode_height', v)
        )
        barcode_form.addRow("高度:", self.barcode_height_input)

        self.barcode_placeholder_input = QLineEdit()
        self.barcode_placeholder_input.setPlaceholderText("{{字段名}}")
        self.barcode_placeholder_input.textChanged.connect(
            lambda v: self._on_property_change('barcode_data_field', v if v else None)
        )
        barcode_form.addRow("占位符:", self.barcode_placeholder_input)

        barcode_group.setLayout(barcode_form)
        barcode_group.setVisible(False)
        self.barcode_group = barcode_group

        # === 形状属性分组 ===
        shape_group = QGroupBox("形状属性")
        shape_form = QFormLayout()

        self.shape_type_label = QLabel()
        shape_form.addRow("类型:", self.shape_type_label)

        # 直径字段（仅用于圆形当 is_circle=True）
        self.shape_diameter_input = QDoubleSpinBox()
        self.shape_diameter_input.setRange(1, 100)
        self.shape_diameter_input.setDecimals(1)
        self.shape_diameter_input.setSingleStep(0.5)
        self.shape_diameter_input.setSuffix(" mm")
        self.shape_diameter_input.valueChanged.connect(
            lambda v: self._on_property_change('circle_diameter', v)
        )
        shape_form.addRow("直径:", self.shape_diameter_input)

        self.shape_width_input = QDoubleSpinBox()
        self.shape_width_input.setRange(1, 100)
        self.shape_width_input.setDecimals(1)
        self.shape_width_input.setSingleStep(0.5)
        self.shape_width_input.setSuffix(" mm")
        self.shape_width_input.valueChanged.connect(
            lambda v: self._on_property_change('shape_width', v)
        )
        shape_form.addRow("宽度:", self.shape_width_input)

        self.shape_height_input = QDoubleSpinBox()
        self.shape_height_input.setRange(1, 100)
        self.shape_height_input.setDecimals(1)
        self.shape_height_input.setSingleStep(0.5)
        self.shape_height_input.setSuffix(" mm")
        self.shape_height_input.valueChanged.connect(
            lambda v: self._on_property_change('shape_height', v)
        )
        shape_form.addRow("高度:", self.shape_height_input)

        from PySide6.QtWidgets import QCheckBox
        self.shape_fill_input = QCheckBox()
        self.shape_fill_input.stateChanged.connect(
            lambda v: self._on_property_change('shape_fill', v == 2)
        )
        shape_form.addRow("填充:", self.shape_fill_input)

        self.shape_thickness_input = QDoubleSpinBox()
        self.shape_thickness_input.setRange(0.5, 10)
        self.shape_thickness_input.setDecimals(1)
        self.shape_thickness_input.setSingleStep(0.5)
        self.shape_thickness_input.setSuffix(" mm")
        self.shape_thickness_input.valueChanged.connect(
            lambda v: self._on_property_change('shape_thickness', v)
        )
        shape_form.addRow("厚度:", self.shape_thickness_input)

        # 结束位置字段（仅用于线条）
        self.line_end_x_input = QDoubleSpinBox()
        self.line_end_x_input.setRange(0, 100)
        self.line_end_x_input.setDecimals(1)
        self.line_end_x_input.setSingleStep(0.5)
        self.line_end_x_input.setSuffix(" mm")
        self.line_end_x_input.valueChanged.connect(
            lambda v: self._on_property_change('line_end_x', v)
        )
        shape_form.addRow("结束 X:", self.line_end_x_input)

        self.line_end_y_input = QDoubleSpinBox()
        self.line_end_y_input.setRange(0, 100)
        self.line_end_y_input.setDecimals(1)
        self.line_end_y_input.setSingleStep(0.5)
        self.line_end_y_input.setSuffix(" mm")
        self.line_end_y_input.valueChanged.connect(
            lambda v: self._on_property_change('line_end_y', v)
        )
        shape_form.addRow("结束 Y:", self.line_end_y_input)

        shape_group.setLayout(shape_form)
        shape_group.setVisible(False)
        self.shape_group = shape_group

        # 默认隐藏结束 X、结束 Y（仅用于线条）
        self.line_end_x_input.setVisible(False)
        self.line_end_y_input.setVisible(False)

        # 默认隐藏直径（仅用于圆形当 is_circle=True）
        self.shape_diameter_input.setVisible(False)

        # === 图片属性 ===
        image_group = QGroupBox("图片属性")
        image_layout = QFormLayout()

        # 宽度
        self.image_width_input = QDoubleSpinBox()
        self.image_width_input.setRange(1, 200)
        self.image_width_input.setDecimals(1)
        self.image_width_input.setSingleStep(1.0)
        self.image_width_input.setSuffix(" mm")
        self.image_width_input.valueChanged.connect(self._on_image_width_changed)
        image_layout.addRow("宽度:", self.image_width_input)

        # 高度
        self.image_height_input = QDoubleSpinBox()
        self.image_height_input.setRange(1, 200)
        self.image_height_input.setDecimals(1)
        self.image_height_input.setSingleStep(1.0)
        self.image_height_input.setSuffix(" mm")
        self.image_height_input.valueChanged.connect(self._on_image_height_changed)
        image_layout.addRow("高度:", self.image_height_input)

        # 更改图片按钮
        from PySide6.QtWidgets import QPushButton
        self.change_image_btn = QPushButton("更改图片...")
        self.change_image_btn.clicked.connect(self._on_change_image)
        image_layout.addRow("", self.change_image_btn)

        image_group.setLayout(image_layout)
        image_group.setVisible(False)
        self.image_group = image_group

        # 组装布局
        layout.addWidget(pos_group)
        layout.addWidget(text_group)
        layout.addWidget(barcode_group)
        layout.addWidget(shape_group)
        layout.addWidget(image_group)
        layout.addStretch()

        self.setLayout(layout)
        self.setMinimumWidth(250)

        # 初始时禁用
        self.setEnabled(False)

    def set_element(self, element, graphics_item):
        """显示元素属性"""
        self.current_element = element
        self.current_graphics_item = graphics_item

        # 连接 position_changed 信号
        if graphics_item and hasattr(graphics_item, 'position_changed'):
            try:
                graphics_item.position_changed.disconnect()
            except:
                pass
            graphics_item.position_changed.connect(self.update_position)

        if element:
            self.setEnabled(True)
            logger.debug(f"属性面板激活，元素位置 ({element.config.x}, {element.config.y})")

            # 从主窗口获取当前单位
            main_window = self._get_main_window()
            if not main_window:
                return

            current_unit = main_window.current_unit
            decimals = UNIT_DECIMALS[current_unit]
            step = UNIT_STEPS[current_unit]

            # 阻塞信号以避免触发更改
            self.blockSignals(True)

            # 将值从毫米转换为当前单位
            x_display = UnitConverter.mm_to_unit(element.config.x, current_unit)
            y_display = UnitConverter.mm_to_unit(element.config.y, current_unit)

            # 更新位置分组
            self.x_input.blockSignals(True)
            self.x_input.setDecimals(decimals)
            self.x_input.setSingleStep(step)
            self.x_input.setSuffix(f" {current_unit.value}")
            self.x_input.setValue(x_display)
            self.x_input.blockSignals(False)

            self.y_input.blockSignals(True)
            self.y_input.setDecimals(decimals)
            self.y_input.setSingleStep(step)
            self.y_input.setSuffix(f" {current_unit.value}")
            self.y_input.setValue(y_display)
            self.y_input.blockSignals(False)

            # 确定元素类型
            from core.elements.text_element import TextElement
            from core.elements.barcode_element import BarcodeElement
            from core.elements.shape_element import RectangleElement, CircleElement, LineElement

            if isinstance(element, TextElement):
                # 仅显示文本属性
                self.text_group.setVisible(True)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(False)

                self.text_input.setText(element.text)

                # 字体族下拉菜单
                font = element.font_family
                for i in range(self.font_family_combo.count()):
                    if self.font_family_combo.itemData(i) == font:
                        self.font_family_combo.blockSignals(True)
                        self.font_family_combo.setCurrentIndex(i)
                        self.font_family_combo.blockSignals(False)
                        break

                self.font_size_input.setValue(element.font_size)
                self.placeholder_input.setText(
                    element.data_field if element.data_field else ""
                )

                # 加载字体样式
                self.bold_checkbox.setChecked(element.bold)
                self.underline_checkbox.setChecked(element.underline)
                logger.debug(f"[属性面板] 加载样式: 粗体={element.bold}, 下划线={element.underline}")

            elif isinstance(element, BarcodeElement):
                # 仅显示条码属性
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(True)
                self.shape_group.setVisible(False)

                self.barcode_type_label.setText(element.barcode_type)
                self.barcode_data_input.setText(element.data)

                # 关键：使用实际宽度！
                if hasattr(element, 'calculate_real_width'):
                    real_width = element.calculate_real_width(dpi=203)
                    self.barcode_width_input.setValue(int(real_width))
                    logger.debug(f"[属性-条码] 宽度（实际）: {real_width:.1f}mm")
                else:
                    self.barcode_width_input.setValue(int(element.width))
                    logger.debug(f"[属性-条码] 宽度（元素）: {element.width}mm")

                self.barcode_height_input.setValue(int(element.height))

                # 关键：设置模块宽度！
                if hasattr(element, 'module_width'):
                    self.barcode_module_width_input.setValue(element.module_width)
                    logger.debug(f"[属性-条码] 模块宽度: {element.module_width} 点")
                else:
                    self.barcode_module_width_input.setValue(2)  # 默认值
                    logger.debug(f"[属性-条码] 模块宽度: 2 点（默认）")

                self.barcode_placeholder_input.setText(
                    element.data_field if element.data_field else ""
                )

            elif hasattr(element.config, 'image_path'):
                # 图片元素
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(False)
                self.image_group.setVisible(True)

                # 填充字段
                self.image_width_input.blockSignals(True)
                self.image_height_input.blockSignals(True)

                self.image_width_input.setValue(element.config.width)
                self.image_height_input.setValue(element.config.height)

                self.image_width_input.blockSignals(False)
                self.image_height_input.blockSignals(False)

                logger.debug(f"[属性-图片] 设置属性: {element.config.width}x{element.config.height}mm")

            elif isinstance(element, RectangleElement):
                # 矩形：显示宽度/高度/填充/厚度
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(True)
                self.image_group.setVisible(False)

                self.shape_type_label.setText("矩形")

                # 隐藏直径，显示宽度/高度
                self.shape_diameter_input.setVisible(False)
                self.shape_width_input.setVisible(True)
                self.shape_height_input.setVisible(True)
                self.shape_fill_input.setVisible(True)
                self.line_end_x_input.setVisible(False)
                self.line_end_y_input.setVisible(False)

                self.shape_width_input.setValue(element.config.width)
                self.shape_height_input.setValue(element.config.height)
                self.shape_fill_input.setChecked(element.config.fill)
                self.shape_thickness_input.setValue(element.config.border_thickness)

            elif isinstance(element, CircleElement):
                # 圆形：动态切换直径 ↔ 宽度/高度
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(True)
                self.image_group.setVisible(False)

                # 隐藏结束 X/结束 Y（用于线条）
                self.line_end_x_input.setVisible(False)
                self.line_end_y_input.setVisible(False)

                logger.debug(f"[属性面板] 更新圆形: is_circle={element.is_circle}")

                if element.is_circle:
                    # 圆形：仅显示直径
                    self.shape_type_label.setText("圆形")
                    logger.debug(f"[属性面板] 显示直径字段")

                    self.shape_diameter_input.setVisible(True)
                    self.shape_width_input.setVisible(False)
                    self.shape_height_input.setVisible(False)

                    self.shape_diameter_input.blockSignals(True)
                    self.shape_diameter_input.setValue(element.diameter)
                    self.shape_diameter_input.blockSignals(False)
                else:
                    # 椭圆：显示宽度和高度
                    self.shape_type_label.setText("椭圆")
                    logger.debug(f"[属性面板] 显示宽度/高度字段")

                    self.shape_diameter_input.setVisible(False)
                    self.shape_width_input.setVisible(True)
                    self.shape_height_input.setVisible(True)

                    self.shape_width_input.blockSignals(True)
                    self.shape_height_input.blockSignals(True)
                    self.shape_width_input.setValue(element.config.width)
                    self.shape_height_input.setValue(element.config.height)
                    self.shape_width_input.blockSignals(False)
                    self.shape_height_input.blockSignals(False)

                # 始终显示填充和厚度
                self.shape_fill_input.setVisible(True)
                self.shape_fill_input.setChecked(element.config.fill)
                self.shape_thickness_input.setValue(element.config.border_thickness)

            elif isinstance(element, LineElement):
                # 线条：显示位置 (X,Y)、结束位置 (结束 X, 结束 Y)、厚度
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(True)
                self.image_group.setVisible(False)

                self.shape_type_label.setText("线条")

                # 隐藏宽度/高度/填充
                self.shape_width_input.setVisible(False)
                self.shape_height_input.setVisible(False)
                self.shape_fill_input.setVisible(False)

                # 显示结束 X、结束 Y
                self.line_end_x_input.setVisible(True)
                self.line_end_y_input.setVisible(True)

                # 设置值
                self.shape_thickness_input.setValue(element.config.thickness)

                # 将结束位置从毫米转换为当前单位
                end_x_display = UnitConverter.mm_to_unit(element.config.x2, current_unit)
                end_y_display = UnitConverter.mm_to_unit(element.config.y2, current_unit)

                self.line_end_x_input.blockSignals(True)
                self.line_end_x_input.setDecimals(decimals)
                self.line_end_x_input.setSingleStep(step)
                self.line_end_x_input.setSuffix(f" {current_unit.value}")
                self.line_end_x_input.setValue(end_x_display)
                self.line_end_x_input.blockSignals(False)

                self.line_end_y_input.blockSignals(True)
                self.line_end_y_input.setDecimals(decimals)
                self.line_end_y_input.setSingleStep(step)
                self.line_end_y_input.setSuffix(f" {current_unit.value}")
                self.line_end_y_input.setValue(end_y_display)
                self.line_end_y_input.blockSignals(False)

                logger.debug(f"[属性-线条] 结束位置: ({element.config.x2:.2f}, {element.config.y2:.2f})mm")
            else:
                # 恢复宽度/高度，隐藏结束 X/结束 Y
                self.shape_width_input.setVisible(True)
                self.shape_height_input.setVisible(True)
                self.shape_fill_input.setVisible(True)
                self.line_end_x_input.setVisible(False)
                self.line_end_y_input.setVisible(False)

            self.blockSignals(False)
        else:
            self.setEnabled(False)
            logger.debug("属性面板已停用")

    def _on_property_change(self, prop_name, value):
        """处理属性更改"""
        if not self.current_element:
            return

        main_window = self._get_main_window()
        if not main_window:
            return

        current_unit = main_window.current_unit

        # 更新元素
        if prop_name == 'x':
            # 在保存前转换回毫米
            x_mm = UnitConverter.unit_to_mm(value, current_unit)
            self.current_element.config.x = x_mm

            logger.debug(f"[属性面板] X 更改: {value:.2f}{current_unit.value} = {x_mm:.2f}mm")

            if self.current_graphics_item:
                x_px = int(x_mm * self.current_graphics_item.dpi / 25.4)
                self.current_graphics_item.setPos(
                    x_px,
                    self.current_graphics_item.pos().y()
                )

        elif prop_name == 'y':
            y_mm = UnitConverter.unit_to_mm(value, current_unit)
            self.current_element.config.y = y_mm

            logger.debug(f"[属性面板] Y 更改: {value:.2f}{current_unit.value} = {y_mm:.2f}mm")

            if self.current_graphics_item:
                y_px = int(y_mm * self.current_graphics_item.dpi / 25.4)
                self.current_graphics_item.setPos(
                    self.current_graphics_item.pos().x(),
                    y_px
                )

        elif prop_name == 'text':
            self.current_element.text = value
            if self.current_graphics_item:
                self.current_graphics_item.update_text(value)

        elif prop_name == 'font_size':
            self.current_element.font_size = value
            if self.current_graphics_item:
                self.current_graphics_item.update_font_size(value)

        elif prop_name == 'data_field':
            self.current_element.data_field = value
            if self.current_graphics_item:
                self.current_graphics_item.update_display_text()

        elif prop_name == 'barcode_data':
            self.current_element.data = value

            # 关键：更改 CODE128 数据时重新计算宽度！
            if hasattr(self.current_element, 'calculate_real_width'):
                real_width = self.current_element.calculate_real_width(dpi=203)
                self.barcode_width_input.blockSignals(True)
                self.barcode_width_input.setValue(int(real_width))
                self.barcode_width_input.blockSignals(False)

                if self.current_graphics_item:
                    self.current_graphics_item.update_size(real_width, self.current_element.height)

                logger.debug(f"[属性-条码] 数据更改，新宽度: {real_width:.1f}mm")

        elif prop_name == 'barcode_module_width':
            # 关键：更改模块宽度会影响实际宽度！
            if hasattr(self.current_element, 'module_width'):
                self.current_element.module_width = value

                # 重新计算实际宽度
                real_width = self.current_element.calculate_real_width(dpi=203)

                # 无信号更新属性面板宽度
                self.barcode_width_input.blockSignals(True)
                self.barcode_width_input.setValue(int(real_width))
                self.barcode_width_input.blockSignals(False)

                # 更新图形项
                if self.current_graphics_item:
                    self.current_graphics_item.update_size(real_width, self.current_element.height)

                logger.debug(f"[属性-条码] 模块宽度更改: {value} 点 -> {real_width:.1f}mm")

        elif prop_name == 'barcode_height':
            self.current_element.height = value
            if self.current_graphics_item:
                self.current_graphics_item.update_size(self.current_element.width, value)

        elif prop_name == 'barcode_data_field':
            self.current_element.data_field = value

        elif prop_name == 'circle_diameter':
            # 圆形直径更改
            from core.elements.shape_element import CircleElement

            if isinstance(self.current_element, CircleElement):
                old_is_circle = self.current_element.is_circle
                self.current_element.diameter = value
                new_is_circle = self.current_element.is_circle

                logger.debug(f"[属性面板] 直径更改: {value:.2f}mm")

                # 更新图形项
                if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                    self.current_graphics_item.update_from_element()

                # 检查形状是否改变（直径始终 is_circle=True）
                if old_is_circle == new_is_circle:
                    logger.debug(f"[属性面板] 形状未改变，无需刷新面板")

        elif prop_name == 'shape_width':
            from core.elements.shape_element import CircleElement

            if isinstance(self.current_element, CircleElement):
                # 圆形：使用 set_width() 检测切换
                old_is_circle = self.current_element.is_circle
                self.current_element.set_width(value)
                new_is_circle = self.current_element.is_circle

                logger.debug(f"[属性面板] 宽度更改: {value:.2f}mm")

                # 更新图形项
                if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                    self.current_graphics_item.update_from_element()

                # 如果变为椭圆 → 重绘面板
                if old_is_circle and not new_is_circle:
                    logger.info(f"[属性面板] 圆形 -> 椭圆，刷新面板")
                    self.set_element(self.current_element, self.current_graphics_item)
            else:
                # 矩形或其他元素
                self.current_element.config.width = value
                if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                    self.current_graphics_item.update_from_element()

        elif prop_name == 'shape_height':
            from core.elements.shape_element import CircleElement

            if isinstance(self.current_element, CircleElement):
                # 圆形：使用 set_height() 检测切换
                old_is_circle = self.current_element.is_circle
                self.current_element.set_height(value)
                new_is_circle = self.current_element.is_circle

                logger.debug(f"[属性面板] 高度更改: {value:.2f}mm")

                # 更新图形项
                if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                    self.current_graphics_item.update_from_element()

                # 如果变为圆形 → 重绘面板
                if not old_is_circle and new_is_circle:
                    logger.info(f"[属性面板] 椭圆 -> 圆形，刷新面板")
                    self.set_element(self.current_element, self.current_graphics_item)
            else:
                # 矩形或其他元素
                self.current_element.config.height = value
                if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                    self.current_graphics_item.update_from_element()

        elif prop_name == 'shape_fill':
            self.current_element.config.fill = value
            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                self.current_graphics_item.update_from_element()

        elif prop_name == 'shape_thickness':
            if hasattr(self.current_element.config, 'border_thickness'):
                self.current_element.config.border_thickness = value
            elif hasattr(self.current_element.config, 'thickness'):
                # 线条元素
                self.current_element.config.thickness = value
            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                self.current_graphics_item.update_from_element()

        elif prop_name == 'line_end_x':
            # 线条结束 X - 从当前单位转换为毫米
            end_x_mm = UnitConverter.unit_to_mm(value, current_unit)
            self.current_element.config.x2 = end_x_mm

            logger.debug(f"[属性-线条] 结束 X 更改: {value:.2f}{current_unit.value} = {end_x_mm:.2f}mm")

            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                self.current_graphics_item.update_from_element()

        elif prop_name == 'line_end_y':
            # 线条结束 Y - 从当前单位转换为毫米
            end_y_mm = UnitConverter.unit_to_mm(value, current_unit)
            self.current_element.config.y2 = end_y_mm

            logger.debug(f"[属性-线条] 结束 Y 更改: {value:.2f}{current_unit.value} = {end_y_mm:.2f}mm")

            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                self.current_graphics_item.update_from_element()

        # 属性更改信号
        self.property_changed.emit(prop_name, value)

        logger.info(f"属性 '{prop_name}' 更改为 '{value}'")

    def update_position(self, x_mm, y_mm):
        """更新 UI 中的位置（从 position_changed 信号调用）"""
        # 阻塞信号以避免触发 _on_property_change
        self.x_input.blockSignals(True)
        self.y_input.blockSignals(True)

        self.x_input.setValue(x_mm)
        self.y_input.setValue(y_mm)

        self.x_input.blockSignals(False)
        self.y_input.blockSignals(False)

        logger.debug(f"属性面板位置已更新: ({x_mm:.1f}, {y_mm:.1f})")

    def _on_bold_changed(self, state):
        """处理粗体复选框更改"""
        if self.current_element and hasattr(self.current_element, 'bold'):
            self.current_element.bold = (state == 2)  # 2 = Qt.Checked

            # 更新图形项
            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_display'):
                self.current_graphics_item.update_display()

            logger.debug(f"[属性面板] 粗体更改: {self.current_element.bold}")

    def _on_underline_changed(self, state):
        """处理下划线复选框更改"""
        if self.current_element and hasattr(self.current_element, 'underline'):
            self.current_element.underline = (state == 2)  # 2 = Qt.Checked

            # 更新图形项
            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_display'):
                self.current_graphics_item.update_display()

            logger.debug(f"[属性面板] 下划线更改: {self.current_element.underline}")

    def _on_font_family_changed(self, index):
        """字体族更改处理程序"""
        if not self.current_element or not hasattr(self.current_element, 'font_family'):
            return

        font = self.font_family_combo.currentData()  # ZplFont 枚举

        logger.debug(f"[属性面板] 字体族更改: {font.zpl_code} ({font.display_name})")

        # 更新元素
        self.current_element.font_family = font

        # 更新画布可视化
        if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_font_family'):
            self.current_graphics_item.update_font_family()
            logger.debug(f"[属性面板] 图形项字体已更新")

        logger.debug(f"[属性面板] 元素字体族已更新为 {self.current_element.font_family.zpl_code}")

    def _on_image_width_changed(self, value):
        """更新图片宽度"""
        if self.current_element and hasattr(self.current_element.config, 'width'):
            logger.debug(f"[属性-图片] 宽度更改: {value}mm")
            self.current_element.config.width = value
            if self.current_graphics_item:
                self.current_graphics_item.update_from_element()

    def _on_image_height_changed(self, value):
        """更新图片高度"""
        if self.current_element and hasattr(self.current_element.config, 'height'):
            logger.debug(f"[属性-图片] 高度更改: {value}mm")
            self.current_element.config.height = value
            if self.current_graphics_item:
                self.current_graphics_item.update_from_element()

    def _on_change_image(self):
        """更改图片"""
        from PySide6.QtWidgets import QFileDialog
        import base64

        if not self.current_element:
            return

        logger.debug(f"[属性-图片] 打开更改图片对话框")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择新图片",
            "",
            "图片 (*.png *.jpg *.jpeg *.bmp);;所有文件 (*)"
        )

        if not file_path:
            return

        logger.debug(f"[属性-图片] 选择新图片: {file_path}")

        try:
            # 转换为 base64
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
                image_data = base64.b64encode(image_bytes).decode('utf-8')

            # 更新元素
            self.current_element.config.image_path = file_path
            self.current_element.config.image_data = image_data

            # 更新图形项
            if self.current_graphics_item:
                self.current_graphics_item.update_from_element()

            logger.info(f"图片已更改: {file_path}")

        except Exception as e:
            logger.error(f"[属性-图片] 更改图片失败: {e}")

    def _get_main_window(self):
        """获取主窗口"""
        widget = self.parent()
        while widget and not hasattr(widget, 'current_unit'):
            widget = widget.parent()
        return widget

    def update_for_unit(self, new_unit):
        """单位更改时更新属性面板（不更改元素）"""
        if not self.current_element or not self.current_graphics_item:
            return

        # 只需再次调用 set_element
        self.set_element(self.current_element, self.current_graphics_item)