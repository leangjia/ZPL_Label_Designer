# -*- coding: utf-8 -*-
"""Mixin для label size та units configuration"""

from PySide6.QtWidgets import QWidget, QDoubleSpinBox, QPushButton, QHBoxLayout, QLabel, QComboBox
from utils.logger import logger
from utils.unit_converter import MeasurementUnit, UnitConverter
from config import DEFAULT_UNIT, UNIT_DECIMALS, UNIT_STEPS, CONFIG


class LabelConfigMixin:
    """Label size & units configuration"""
    
    def _create_label_size_controls(self):
        """Створити controls для зміни розміру етикетки"""
        from config import CONFIG
        
        # Container widget
        label_size_widget = QWidget()
        layout = QHBoxLayout(label_size_widget)
        layout.setContentsMargins(5, 0, 5, 0)
        layout.setSpacing(5)
        
        # Label
        layout.addWidget(QLabel("Label Size (mm):"))
        
        # Width SpinBox
        layout.addWidget(QLabel("W:"))
        self.width_spinbox = QDoubleSpinBox()
        self.width_spinbox.setRange(CONFIG['MIN_LABEL_WIDTH_MM'], CONFIG['MAX_LABEL_WIDTH_MM'])
        self.width_spinbox.setValue(self.canvas.width_mm)
        self.width_spinbox.setDecimals(1)
        self.width_spinbox.setSingleStep(1.0)
        self.width_spinbox.setFixedWidth(70)
        layout.addWidget(self.width_spinbox)
        
        # Height SpinBox
        layout.addWidget(QLabel("H:"))
        self.height_spinbox = QDoubleSpinBox()
        self.height_spinbox.setRange(CONFIG['MIN_LABEL_HEIGHT_MM'], CONFIG['MAX_LABEL_HEIGHT_MM'])
        self.height_spinbox.setValue(self.canvas.height_mm)
        self.height_spinbox.setDecimals(1)
        self.height_spinbox.setSingleStep(1.0)
        self.height_spinbox.setFixedWidth(70)
        layout.addWidget(self.height_spinbox)
        
        # Apply Button
        apply_button = QPushButton("Apply")
        apply_button.clicked.connect(self._apply_label_size)
        apply_button.setFixedWidth(60)
        layout.addWidget(apply_button)
        
        # Додати до toolbar
        self.toolbar.addSeparator()
        self.toolbar.addWidget(label_size_widget)
        
        logger.info(f"Label Size controls created (range: {CONFIG['MIN_LABEL_WIDTH_MM']}-{CONFIG['MAX_LABEL_WIDTH_MM']}mm)")
    
    def _apply_label_size(self):
        """Застосувати новий розмір етикетки"""
        width_mm = self.width_spinbox.value()
        height_mm = self.height_spinbox.value()
        
        logger.debug(f"[SIZE-APPLY] User request: {width_mm}x{height_mm}mm")
        
        # Перевірити чи змінилось
        if width_mm == self.canvas.width_mm and height_mm == self.canvas.height_mm:
            logger.debug(f"[SIZE-APPLY] No change, skipping")
            return
        
        # Застосувати до canvas
        self.canvas.set_label_size(width_mm, height_mm)
        
        # Оновити лінейки
        self.h_ruler.set_length(width_mm)
        self.v_ruler.set_length(height_mm)
        
        logger.info(f"[SIZE-APPLY] Label size updated: {width_mm}x{height_mm}mm")
    
    def _create_units_controls(self):
        """Створити контроли для вибору одиниць вимірювання"""
        # Units ComboBox
        units_label = QLabel("Units:")
        self.units_combobox = QComboBox()
        
        # Додати всі варіанти
        for unit in MeasurementUnit:
            self.units_combobox.addItem(unit.value.upper(), unit)
        
        # Встановити дефолтний
        index = self.units_combobox.findData(self.current_unit)
        self.units_combobox.setCurrentIndex(index)
        
        # Підключити сигнал
        self.units_combobox.currentIndexChanged.connect(self._on_unit_changed)
        
        # Додати до toolbar
        self.toolbar.addSeparator()
        self.toolbar.addWidget(units_label)
        self.toolbar.addWidget(self.units_combobox)
        
        logger.debug(f"[UNITS] Initialized: {self.current_unit.value}")
    
    def _on_unit_changed(self, index):
        """Units ComboBox змінено"""
        old_unit = self.current_unit
        new_unit = self.units_combobox.itemData(index)
        
        logger.info(f"[UNITS] Changed: {old_unit.value} -> {new_unit.value}")
        
        self.current_unit = new_unit
        
        # 1. Оновити Label Size SpinBoxes
        self._update_label_size_spinboxes(old_unit, new_unit)
        
        # 2. Оновити PropertyPanel (якщо є selected element)
        if self.selected_item and hasattr(self.selected_item, 'element'):
            self.property_panel.update_for_unit(new_unit)
        
        # 3. Оновити Rulers
        if hasattr(self.canvas, 'h_ruler') and self.canvas.h_ruler:
            self.canvas.h_ruler.set_unit(new_unit)
        
        if hasattr(self.canvas, 'v_ruler') and self.canvas.v_ruler:
            self.canvas.v_ruler.set_unit(new_unit)
        
        logger.info(f"[UNITS] Update completed")
    
    def _update_label_size_spinboxes(self, old_unit, new_unit):
        """Оновити Label Size SpinBoxes при зміні units"""
        # Отримати поточні значення в MM (завжди зберігаємо в MM!)
        width_mm = UnitConverter.unit_to_mm(
            self.width_spinbox.value(), 
            old_unit
        )
        height_mm = UnitConverter.unit_to_mm(
            self.height_spinbox.value(), 
            old_unit
        )
        
        # Конвертувати в нові units
        width_new = UnitConverter.mm_to_unit(width_mm, new_unit)
        height_new = UnitConverter.mm_to_unit(height_mm, new_unit)
        
        # Оновити SpinBoxes
        from config import CONFIG
        decimals = UNIT_DECIMALS[new_unit]
        step = UNIT_STEPS[new_unit]
        
        # Width
        self.width_spinbox.blockSignals(True)
        self.width_spinbox.setDecimals(decimals)
        self.width_spinbox.setSingleStep(step)
        self.width_spinbox.setSuffix(f" {new_unit.value}")
        
        # Range в нових units
        min_width, max_width = UnitConverter.get_range_in_unit(
            CONFIG['MIN_LABEL_WIDTH_MM'], 
            CONFIG['MAX_LABEL_WIDTH_MM'], 
            new_unit
        )
        self.width_spinbox.setRange(min_width, max_width)
        self.width_spinbox.setValue(width_new)
        self.width_spinbox.blockSignals(False)
        
        # Height (аналогічно)
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
        
        logger.debug(f"[UNITS] Label size updated: {width_new:.2f}x{height_new:.2f} {new_unit.value}")
