# -*- coding: utf-8 -*-
"""标签尺寸和单位配置混入类"""

from PySide6.QtWidgets import QWidget, QDoubleSpinBox, QPushButton, QHBoxLayout, QLabel, QComboBox
from utils.logger import logger
from utils.unit_converter import MeasurementUnit, UnitConverter
from utils.settings_manager import settings_manager
from config import DEFAULT_UNIT, UNIT_DECIMALS, UNIT_STEPS, CONFIG


class LabelConfigMixin:
    """标签尺寸和单位配置"""

    def _create_label_size_controls(self):
        """创建用于更改标签尺寸的控件"""
        from config import CONFIG

        # 容器部件
        label_size_widget = QWidget()
        layout = QHBoxLayout(label_size_widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)

        # 标签
        layout.addWidget(QLabel("标签尺寸:"))

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
        """应用新的标签尺寸"""
        width_mm = self.width_spinbox.value()
        height_mm = self.height_spinbox.value()

        logger.debug(f"[尺寸应用] 用户请求: {width_mm}x{height_mm}mm")

        # 检查是否有变化
        if width_mm == self.canvas.width_mm and height_mm == self.canvas.height_mm:
            logger.debug(f"[尺寸应用] 无变化，跳过")
            return

        # 应用到画布
        self.canvas.set_label_size(width_mm, height_mm)

        logger.info(f"[尺寸应用] 标签尺寸已更新: {width_mm}x{height_mm}mm")
        self._persist_toolbar_settings()

    def _create_units_controls(self):
        """创建测量单位选择控件"""
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
        self._persist_toolbar_settings()

    def _update_label_size_spinboxes(self, old_unit, new_unit):
        """更改单位时更新标签尺寸微调框"""
        # 获取当前的毫米值（始终以毫米存储！）
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

        # 新单位下的范围
        min_width, max_width = UnitConverter.get_range_in_unit(
            CONFIG['MIN_LABEL_WIDTH_MM'],
            CONFIG['MAX_LABEL_WIDTH_MM'],
            new_unit
        )
        self.width_spinbox.setRange(min_width, max_width)
        self.width_spinbox.setValue(width_new)
        self.width_spinbox.blockSignals(False)

        # 高度（类似处理）
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

    def _persist_toolbar_settings(self):
        """将当前工具栏设置保存到 QSettings"""
        show_grid = getattr(self, 'grid_visible', True)
        snap_enabled = getattr(self, 'snap_enabled', True)
        guides_enabled = getattr(self, 'guides_enabled', True)

        label_width = getattr(self.canvas, 'width_mm', CONFIG['DEFAULT_WIDTH_MM'])
        label_height = getattr(self.canvas, 'height_mm', CONFIG['DEFAULT_HEIGHT_MM'])
        unit_value = getattr(getattr(self, 'current_unit', DEFAULT_UNIT), 'value', DEFAULT_UNIT.value)

        settings_manager.save_toolbar_settings(
            {
                'show_grid': show_grid,
                'snap_to_grid': snap_enabled,
                'smart_guides': guides_enabled,
                'label_width': label_width,
                'label_height': label_height,
                'unit': unit_value,
            }
        )
        logger.debug(
            "[工具栏持久化] 已保存: "
            f"网格={show_grid}, 对齐={snap_enabled}, 参考线={guides_enabled}, "
            f"标签={label_width}x{label_height}mm, 单位={unit_value}"
        )