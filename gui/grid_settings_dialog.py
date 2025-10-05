# -*- coding: utf-8 -*-
"""Grid Settings Dialog"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                                QDoubleSpinBox, QCheckBox, QComboBox, 
                                QPushButton, QGroupBox, QLabel)
from PySide6.QtCore import Qt
from utils.logger import logger
from config import GridConfig, SnapMode

class GridSettingsDialog(QDialog):
    """Діалог налаштувань сітки"""
    
    def __init__(self, grid_config: GridConfig, parent=None):
        super().__init__(parent)
        self.grid_config = grid_config
        
        self.setWindowTitle("Grid Settings")
        self.setModal(True)
        self.setMinimumWidth(350)
        
        self._create_ui()
        self._load_config()
    
    def _create_ui(self):
        """Створити UI"""
        layout = QVBoxLayout(self)
        
        # Grid Size group
        size_group = QGroupBox("Grid Size")
        size_layout = QFormLayout()
        
        self.size_x_spin = QDoubleSpinBox()
        self.size_x_spin.setRange(0.5, 10.0)
        self.size_x_spin.setSingleStep(0.5)
        self.size_x_spin.setSuffix(" mm")
        size_layout.addRow("Size X:", self.size_x_spin)
        
        self.size_y_spin = QDoubleSpinBox()
        self.size_y_spin.setRange(0.5, 10.0)
        self.size_y_spin.setSingleStep(0.5)
        self.size_y_spin.setSuffix(" mm")
        size_layout.addRow("Size Y:", self.size_y_spin)
        
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Grid Offset group
        offset_group = QGroupBox("Grid Offset")
        offset_layout = QFormLayout()
        
        self.offset_x_spin = QDoubleSpinBox()
        self.offset_x_spin.setRange(0.0, 10.0)
        self.offset_x_spin.setSingleStep(0.1)
        self.offset_x_spin.setSuffix(" mm")
        offset_layout.addRow("Offset X:", self.offset_x_spin)
        
        self.offset_y_spin = QDoubleSpinBox()
        self.offset_y_spin.setRange(0.0, 10.0)
        self.offset_y_spin.setSingleStep(0.1)
        self.offset_y_spin.setSuffix(" mm")
        offset_layout.addRow("Offset Y:", self.offset_y_spin)
        
        offset_group.setLayout(offset_layout)
        layout.addWidget(offset_group)
        
        # Display options
        display_group = QGroupBox("Display")
        display_layout = QVBoxLayout()
        
        self.display_checkbox = QCheckBox("Display gridline guides")
        display_layout.addWidget(self.display_checkbox)
        
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        # Snap mode
        snap_group = QGroupBox("Alignment")
        snap_layout = QVBoxLayout()
        
        self.snap_combo = QComboBox()
        self.snap_combo.addItem("Align to Grid", SnapMode.GRID)
        self.snap_combo.addItem("Align to Objects", SnapMode.OBJECTS)
        self.snap_combo.addItem("Do Not Align", SnapMode.NONE)
        snap_layout.addWidget(self.snap_combo)
        
        snap_group.setLayout(snap_layout)
        layout.addWidget(snap_group)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(ok_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
    
    def _load_config(self):
        """Завантажити config у UI"""
        self.size_x_spin.setValue(self.grid_config.size_x_mm)
        self.size_y_spin.setValue(self.grid_config.size_y_mm)
        self.offset_x_spin.setValue(self.grid_config.offset_x_mm)
        self.offset_y_spin.setValue(self.grid_config.offset_y_mm)
        self.display_checkbox.setChecked(self.grid_config.visible)
        
        # Snap mode
        for i in range(self.snap_combo.count()):
            if self.snap_combo.itemData(i) == self.grid_config.snap_mode:
                self.snap_combo.setCurrentIndex(i)
                break
    
    def get_config(self) -> GridConfig:
        """Отримати GridConfig з UI"""
        config = GridConfig(
            size_x_mm=self.size_x_spin.value(),
            size_y_mm=self.size_y_spin.value(),
            offset_x_mm=self.offset_x_spin.value(),
            offset_y_mm=self.offset_y_spin.value(),
            visible=self.display_checkbox.isChecked(),
            snap_mode=self.snap_combo.currentData()
        )
        
        logger.debug(f"[GRID-DIALOG] User set: Size X={config.size_x_mm}mm, Y={config.size_y_mm}mm")
        logger.debug(f"[GRID-DIALOG] User set: Offset X={config.offset_x_mm}mm, Y={config.offset_y_mm}mm")
        logger.debug(f"[GRID-DIALOG] User set: Snap mode={config.snap_mode.value}")
        
        return config
