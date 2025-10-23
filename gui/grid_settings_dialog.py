# -*- coding: utf-8 -*-
"""网格设置对话框"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                               QDoubleSpinBox, QCheckBox, QComboBox,
                               QPushButton, QGroupBox, QLabel)
from PySide6.QtCore import Qt
from utils.logger import logger
from utils.settings_manager import settings_manager
from config import GridConfig, SnapMode


class GridSettingsDialog(QDialog):
    """网格设置对话框"""

    def __init__(self, grid_config: GridConfig, parent=None):
        super().__init__(parent)
        self.grid_config = grid_config

        self.setWindowTitle("网格设置")
        self.setModal(True)
        self.setMinimumWidth(350)

        self._create_ui()
        self._load_config()

    def _create_ui(self):
        """创建用户界面"""
        layout = QVBoxLayout(self)

        # 网格尺寸分组
        size_group = QGroupBox("网格尺寸")
        size_layout = QFormLayout()

        self.size_x_spin = QDoubleSpinBox()
        self.size_x_spin.setRange(0.5, 10.0)
        self.size_x_spin.setSingleStep(0.5)
        self.size_x_spin.setSuffix(" mm")
        size_layout.addRow("尺寸 X:", self.size_x_spin)

        self.size_y_spin = QDoubleSpinBox()
        self.size_y_spin.setRange(0.5, 10.0)
        self.size_y_spin.setSingleStep(0.5)
        self.size_y_spin.setSuffix(" mm")
        size_layout.addRow("尺寸 Y:", self.size_y_spin)

        size_group.setLayout(size_layout)
        layout.addWidget(size_group)

        # 网格偏移分组
        offset_group = QGroupBox("网格偏移")
        offset_layout = QFormLayout()

        self.offset_x_spin = QDoubleSpinBox()
        self.offset_x_spin.setRange(0.0, 10.0)
        self.offset_x_spin.setSingleStep(0.1)
        self.offset_x_spin.setSuffix(" mm")
        offset_layout.addRow("偏移 X:", self.offset_x_spin)

        self.offset_y_spin = QDoubleSpinBox()
        self.offset_y_spin.setRange(0.0, 10.0)
        self.offset_y_spin.setSingleStep(0.1)
        self.offset_y_spin.setSuffix(" mm")
        offset_layout.addRow("偏移 Y:", self.offset_y_spin)

        offset_group.setLayout(offset_layout)
        layout.addWidget(offset_group)

        # 显示选项
        display_group = QGroupBox("显示")
        display_layout = QVBoxLayout()

        self.display_checkbox = QCheckBox("显示网格线参考线")
        display_layout.addWidget(self.display_checkbox)

        display_group.setLayout(display_layout)
        layout.addWidget(display_group)

        # 吸附模式
        snap_group = QGroupBox("对齐")
        snap_layout = QVBoxLayout()

        self.snap_combo = QComboBox()
        self.snap_combo.addItem("对齐到网格", SnapMode.GRID)
        self.snap_combo.addItem("对齐到对象", SnapMode.OBJECTS)
        self.snap_combo.addItem("不对齐", SnapMode.NONE)
        snap_layout.addWidget(self.snap_combo)

        snap_group.setLayout(snap_layout)
        layout.addWidget(snap_group)

        # 按钮
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)

        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)

    def _load_config(self):
        """将配置加载到用户界面"""
        saved = settings_manager.load_grid_settings()

        self.size_x_spin.setValue(saved["size_x"])
        self.size_y_spin.setValue(saved["size_y"])
        self.offset_x_spin.setValue(saved["offset_x"])
        self.offset_y_spin.setValue(saved["offset_y"])
        self.display_checkbox.setChecked(saved["show_gridlines"])

        # 吸附模式
        for i in range(self.snap_combo.count()):
            if self.snap_combo.itemData(i) == saved["snap_mode"]:
                self.snap_combo.setCurrentIndex(i)
                break

        logger.debug(f"[网格对话框] 已加载保存的设置: {saved}")

    def get_config(self) -> GridConfig:
        """从用户界面获取 GridConfig"""
        config = GridConfig(
            size_x_mm=self.size_x_spin.value(),
            size_y_mm=self.size_y_spin.value(),
            offset_x_mm=self.offset_x_spin.value(),
            offset_y_mm=self.offset_y_spin.value(),
            visible=self.display_checkbox.isChecked(),
            snap_mode=self.snap_combo.currentData()
        )

        logger.debug(f"[网格对话框] 用户设置: 尺寸 X={config.size_x_mm}mm, Y={config.size_y_mm}mm")
        logger.debug(f"[网格对话框] 用户设置: 偏移 X={config.offset_x_mm}mm, Y={config.offset_y_mm}mm")
        logger.debug(f"[网格对话框] 用户设置: 吸附模式={config.snap_mode.value}")

        return config

    def accept(self):
        """确认更改并保存"""

        current_config = self.get_config()
        settings_manager.save_grid_settings(
            {
                "size_x": current_config.size_x_mm,
                "size_y": current_config.size_y_mm,
                "offset_x": current_config.offset_x_mm,
                "offset_y": current_config.offset_y_mm,
                "show_gridlines": current_config.visible,
                "snap_mode": current_config.snap_mode,
            }
        )
        logger.debug(
            "[网格对话框] 确定时保存设置: "
            f"{current_config.size_x_mm}x{current_config.size_y_mm}mm"
        )

        super().accept()