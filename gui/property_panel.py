# -*- coding: utf-8 -*-
"""Панель свойств элемента"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                               QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout, QComboBox)
from PySide6.QtCore import Signal
from utils.logger import logger
from utils.unit_converter import UnitConverter
from config import UNIT_DECIMALS, UNIT_STEPS
from core.elements.text_element import ZplFont

class PropertyPanel(QWidget):
    """Панель свойств выбранного элемента"""
    
    property_changed = Signal(str, object)  # (property_name, new_value)
    
    def __init__(self):
        super().__init__()
        self.current_element = None
        self.current_graphics_item = None
        self._setup_ui()
        logger.info("PropertyPanel initialized")
    
    def _setup_ui(self):
        """Создать UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # === Position Group ===
        pos_group = QGroupBox("Position")
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
        
        # === Text Properties Group ===
        text_group = QGroupBox("Text Properties")
        text_form = QFormLayout()
        
        self.text_input = QLineEdit()
        self.text_input.textChanged.connect(
            lambda v: self._on_property_change('text', v)
        )
        text_form.addRow("Text:", self.text_input)
        
        # Font Family dropdown
        self.font_family_combo = QComboBox()
        for font in ZplFont:
            self.font_family_combo.addItem(font.display_name, font)
        self.font_family_combo.currentIndexChanged.connect(self._on_font_family_changed)
        text_form.addRow("Font:", self.font_family_combo)
        
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(10, 100)
        self.font_size_input.valueChanged.connect(
            lambda v: self._on_property_change('font_size', v)
        )
        text_form.addRow("Font Size:", self.font_size_input)
        
        self.placeholder_input = QLineEdit()
        self.placeholder_input.setPlaceholderText("{{FIELD_NAME}}")
        self.placeholder_input.textChanged.connect(
            lambda v: self._on_property_change('data_field', v if v else None)
        )
        text_form.addRow("Placeholder:", self.placeholder_input)
        
        # Font Styles
        from PySide6.QtWidgets import QCheckBox
        
        styles_label = QLabel("Styles:")
        text_form.addRow(styles_label)
        
        self.bold_checkbox = QCheckBox("Bold (Ctrl+B)")
        self.bold_checkbox.stateChanged.connect(self._on_bold_changed)
        text_form.addRow("", self.bold_checkbox)
        
        self.italic_checkbox = QCheckBox("Italic [Requires font upload to printer]")
        self.italic_checkbox.setEnabled(False)
        self.italic_checkbox.setToolTip("ZPL does not support italic without uploading italic font to printer")
        text_form.addRow("", self.italic_checkbox)
        
        self.underline_checkbox = QCheckBox("Underline (Ctrl+U)")
        self.underline_checkbox.stateChanged.connect(self._on_underline_changed)
        text_form.addRow("", self.underline_checkbox)
        
        text_group.setLayout(text_form)
        self.text_group = text_group
        
        # === Barcode Properties Group ===
        barcode_group = QGroupBox("Barcode Properties")
        barcode_form = QFormLayout()
        
        self.barcode_type_label = QLabel()
        barcode_form.addRow("Type:", self.barcode_type_label)
        
        self.barcode_data_input = QLineEdit()
        self.barcode_data_input.textChanged.connect(
            lambda v: self._on_property_change('barcode_data', v)
        )
        barcode_form.addRow("Data:", self.barcode_data_input)
        
        self.barcode_width_input = QSpinBox()
        self.barcode_width_input.setRange(10, 100)
        self.barcode_width_input.setSuffix(" mm")
        self.barcode_width_input.setReadOnly(True)  # READ-ONLY! Width вичисляється автоматично
        self.barcode_width_input.setStyleSheet("QSpinBox { background-color: #f0f0f0; }")
        self.barcode_width_input.setToolTip("Width calculated automatically based on Module Width")
        barcode_form.addRow("Width:", self.barcode_width_input)
        
        # КРИТИЧНО: Module Width для контролю реальної ширини!
        self.barcode_module_width_input = QSpinBox()
        self.barcode_module_width_input.setRange(1, 5)
        self.barcode_module_width_input.setSuffix(" dots")
        self.barcode_module_width_input.setToolTip("Module width (^BY parameter). Smaller = narrower barcode.")
        self.barcode_module_width_input.valueChanged.connect(
            lambda v: self._on_property_change('barcode_module_width', v)
        )
        barcode_form.addRow("Module Width:", self.barcode_module_width_input)
        
        self.barcode_height_input = QSpinBox()
        self.barcode_height_input.setRange(10, 100)
        self.barcode_height_input.setSuffix(" mm")
        self.barcode_height_input.valueChanged.connect(
            lambda v: self._on_property_change('barcode_height', v)
        )
        barcode_form.addRow("Height:", self.barcode_height_input)
        
        self.barcode_placeholder_input = QLineEdit()
        self.barcode_placeholder_input.setPlaceholderText("{{FIELD_NAME}}")
        self.barcode_placeholder_input.textChanged.connect(
            lambda v: self._on_property_change('barcode_data_field', v if v else None)
        )
        barcode_form.addRow("Placeholder:", self.barcode_placeholder_input)
        
        barcode_group.setLayout(barcode_form)
        barcode_group.setVisible(False)
        self.barcode_group = barcode_group
        
        # === Shape Properties Group ===
        shape_group = QGroupBox("Shape Properties")
        shape_form = QFormLayout()
        
        self.shape_type_label = QLabel()
        shape_form.addRow("Type:", self.shape_type_label)
        
        # Diameter field (тільки для Circle коли is_circle=True)
        self.shape_diameter_input = QDoubleSpinBox()
        self.shape_diameter_input.setRange(1, 100)
        self.shape_diameter_input.setDecimals(1)
        self.shape_diameter_input.setSingleStep(0.5)
        self.shape_diameter_input.setSuffix(" mm")
        self.shape_diameter_input.valueChanged.connect(
            lambda v: self._on_property_change('circle_diameter', v)
        )
        shape_form.addRow("Diameter:", self.shape_diameter_input)
        
        self.shape_width_input = QDoubleSpinBox()
        self.shape_width_input.setRange(1, 100)
        self.shape_width_input.setDecimals(1)
        self.shape_width_input.setSingleStep(0.5)
        self.shape_width_input.setSuffix(" mm")
        self.shape_width_input.valueChanged.connect(
            lambda v: self._on_property_change('shape_width', v)
        )
        shape_form.addRow("Width:", self.shape_width_input)
        
        self.shape_height_input = QDoubleSpinBox()
        self.shape_height_input.setRange(1, 100)
        self.shape_height_input.setDecimals(1)
        self.shape_height_input.setSingleStep(0.5)
        self.shape_height_input.setSuffix(" mm")
        self.shape_height_input.valueChanged.connect(
            lambda v: self._on_property_change('shape_height', v)
        )
        shape_form.addRow("Height:", self.shape_height_input)
        
        from PySide6.QtWidgets import QCheckBox
        self.shape_fill_input = QCheckBox()
        self.shape_fill_input.stateChanged.connect(
            lambda v: self._on_property_change('shape_fill', v == 2)
        )
        shape_form.addRow("Fill:", self.shape_fill_input)
        
        self.shape_thickness_input = QDoubleSpinBox()
        self.shape_thickness_input.setRange(0.5, 10)
        self.shape_thickness_input.setDecimals(1)
        self.shape_thickness_input.setSingleStep(0.5)
        self.shape_thickness_input.setSuffix(" mm")
        self.shape_thickness_input.valueChanged.connect(
            lambda v: self._on_property_change('shape_thickness', v)
        )
        shape_form.addRow("Thickness:", self.shape_thickness_input)
        
        # End Position fields (only for Line)
        self.line_end_x_input = QDoubleSpinBox()
        self.line_end_x_input.setRange(0, 100)
        self.line_end_x_input.setDecimals(1)
        self.line_end_x_input.setSingleStep(0.5)
        self.line_end_x_input.setSuffix(" mm")
        self.line_end_x_input.valueChanged.connect(
            lambda v: self._on_property_change('line_end_x', v)
        )
        shape_form.addRow("End X:", self.line_end_x_input)
        
        self.line_end_y_input = QDoubleSpinBox()
        self.line_end_y_input.setRange(0, 100)
        self.line_end_y_input.setDecimals(1)
        self.line_end_y_input.setSingleStep(0.5)
        self.line_end_y_input.setSuffix(" mm")
        self.line_end_y_input.valueChanged.connect(
            lambda v: self._on_property_change('line_end_y', v)
        )
        shape_form.addRow("End Y:", self.line_end_y_input)
        
        shape_group.setLayout(shape_form)
        shape_group.setVisible(False)
        self.shape_group = shape_group
        
        # Сховати End X, End Y за замовчуванням (тільки для Line)
        self.line_end_x_input.setVisible(False)
        self.line_end_y_input.setVisible(False)
        
        # Сховати Diameter за замовчуванням (тільки для Circle коли is_circle=True)
        self.shape_diameter_input.setVisible(False)
        
        # === IMAGE PROPERTIES ===
        image_group = QGroupBox("Image Properties")
        image_layout = QFormLayout()
        
        # Width
        self.image_width_input = QDoubleSpinBox()
        self.image_width_input.setRange(1, 200)
        self.image_width_input.setDecimals(1)
        self.image_width_input.setSingleStep(1.0)
        self.image_width_input.setSuffix(" mm")
        self.image_width_input.valueChanged.connect(self._on_image_width_changed)
        image_layout.addRow("Width:", self.image_width_input)
        
        # Height
        self.image_height_input = QDoubleSpinBox()
        self.image_height_input.setRange(1, 200)
        self.image_height_input.setDecimals(1)
        self.image_height_input.setSingleStep(1.0)
        self.image_height_input.setSuffix(" mm")
        self.image_height_input.valueChanged.connect(self._on_image_height_changed)
        image_layout.addRow("Height:", self.image_height_input)
        
        # Change Image button
        from PySide6.QtWidgets import QPushButton
        self.change_image_btn = QPushButton("Change Image...")
        self.change_image_btn.clicked.connect(self._on_change_image)
        image_layout.addRow("", self.change_image_btn)
        
        image_group.setLayout(image_layout)
        image_group.setVisible(False)
        self.image_group = image_group
        
        # Собрать layout
        layout.addWidget(pos_group)
        layout.addWidget(text_group)
        layout.addWidget(barcode_group)
        layout.addWidget(shape_group)
        layout.addWidget(image_group)
        layout.addStretch()
        
        self.setLayout(layout)
        self.setMinimumWidth(250)
        
        # Изначально заблокировать
        self.setEnabled(False)
    
    def set_element(self, element, graphics_item):
        """Отобразить свойства элемента"""
        self.current_element = element
        self.current_graphics_item = graphics_item
        
        # Подключить position_changed сигнал
        if graphics_item and hasattr(graphics_item, 'position_changed'):
            try:
                graphics_item.position_changed.disconnect()
            except:
                pass
            graphics_item.position_changed.connect(self.update_position)
        
        if element:
            self.setEnabled(True)
            logger.debug(f"Property panel activated for element at ({element.config.x}, {element.config.y})")
            
            # Отримати current unit з MainWindow
            main_window = self._get_main_window()
            if not main_window:
                return
            
            current_unit = main_window.current_unit
            decimals = UNIT_DECIMALS[current_unit]
            step = UNIT_STEPS[current_unit]
            
            # Заблокировать сигналы чтобы не вызвать изменения
            self.blockSignals(True)
            
            # Конвертувати значення з MM в current unit
            x_display = UnitConverter.mm_to_unit(element.config.x, current_unit)
            y_display = UnitConverter.mm_to_unit(element.config.y, current_unit)
            
            # Оновити Position group
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
            
            # Определить тип элемента
            from core.elements.text_element import TextElement
            from core.elements.barcode_element import BarcodeElement
            from core.elements.shape_element import RectangleElement, CircleElement, LineElement
            
            if isinstance(element, TextElement):
                # Показать только Text Properties
                self.text_group.setVisible(True)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(False)
                
                self.text_input.setText(element.text)
                
                # Font Family dropdown
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
                
                # Загрузить стили шрифта
                self.bold_checkbox.setChecked(element.bold)
                self.underline_checkbox.setChecked(element.underline)
                logger.debug(f"[PROP-PANEL] Loaded styles: Bold={element.bold}, Underline={element.underline}")
            
            elif isinstance(element, BarcodeElement):
                # Показать только Barcode Properties
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(True)
                self.shape_group.setVisible(False)
                
                self.barcode_type_label.setText(element.barcode_type)
                self.barcode_data_input.setText(element.data)
                
                # КРИТИЧНО: Використовувати REAL width!
                if hasattr(element, 'calculate_real_width'):
                    real_width = element.calculate_real_width(dpi=203)
                    self.barcode_width_input.setValue(int(real_width))
                    logger.debug(f"[PROP-BARCODE] Width (REAL): {real_width:.1f}mm")
                else:
                    self.barcode_width_input.setValue(int(element.width))
                    logger.debug(f"[PROP-BARCODE] Width (element): {element.width}mm")
                
                self.barcode_height_input.setValue(int(element.height))
                
                # КРИТИЧНО: Встановити module_width!
                if hasattr(element, 'module_width'):
                    self.barcode_module_width_input.setValue(element.module_width)
                    logger.debug(f"[PROP-BARCODE] Module width: {element.module_width} dots")
                else:
                    self.barcode_module_width_input.setValue(2)  # default
                    logger.debug(f"[PROP-BARCODE] Module width: 2 dots (default)")
                
                self.barcode_placeholder_input.setText(
                    element.data_field if element.data_field else ""
                )
            
            elif hasattr(element.config, 'image_path'):
                # Image element
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(False)
                self.image_group.setVisible(True)
                
                # Заповнити поля
                self.image_width_input.blockSignals(True)
                self.image_height_input.blockSignals(True)
                
                self.image_width_input.setValue(element.config.width)
                self.image_height_input.setValue(element.config.height)
                
                self.image_width_input.blockSignals(False)
                self.image_height_input.blockSignals(False)
                
                logger.debug(f"[PROP-IMAGE] Set properties: {element.config.width}x{element.config.height}mm")
            
            elif isinstance(element, RectangleElement):
                # Rectangle: показать Width/Height/Fill/Thickness
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(True)
                self.image_group.setVisible(False)
                
                self.shape_type_label.setText("Rectangle")
                
                # Сховати Diameter, показати Width/Height
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
                # Circle: динамічне переключення Diameter ↔ Width/Height
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(True)
                self.image_group.setVisible(False)
                
                # Сховати End X/End Y (для Line)
                self.line_end_x_input.setVisible(False)
                self.line_end_y_input.setVisible(False)
                
                logger.debug(f"[PROP-PANEL] Update circle: is_circle={element.is_circle}")
                
                if element.is_circle:
                    # КОЛО: показати тільки Diameter
                    self.shape_type_label.setText("Circle")
                    logger.debug(f"[PROP-PANEL] Showing DIAMETER field")
                    
                    self.shape_diameter_input.setVisible(True)
                    self.shape_width_input.setVisible(False)
                    self.shape_height_input.setVisible(False)
                    
                    self.shape_diameter_input.blockSignals(True)
                    self.shape_diameter_input.setValue(element.diameter)
                    self.shape_diameter_input.blockSignals(False)
                else:
                    # ЕЛІПС: показати Width і Height
                    self.shape_type_label.setText("Ellipse")
                    logger.debug(f"[PROP-PANEL] Showing WIDTH/HEIGHT fields")
                    
                    self.shape_diameter_input.setVisible(False)
                    self.shape_width_input.setVisible(True)
                    self.shape_height_input.setVisible(True)
                    
                    self.shape_width_input.blockSignals(True)
                    self.shape_height_input.blockSignals(True)
                    self.shape_width_input.setValue(element.config.width)
                    self.shape_height_input.setValue(element.config.height)
                    self.shape_width_input.blockSignals(False)
                    self.shape_height_input.blockSignals(False)
                
                # Fill і Thickness показуємо завжди
                self.shape_fill_input.setVisible(True)
                self.shape_fill_input.setChecked(element.config.fill)
                self.shape_thickness_input.setValue(element.config.border_thickness)
            
            elif isinstance(element, LineElement):
                # Line: показати Position (X,Y), End Position (End X, End Y), Thickness
                self.text_group.setVisible(False)
                self.barcode_group.setVisible(False)
                self.shape_group.setVisible(True)
                self.image_group.setVisible(False)
                
                self.shape_type_label.setText("Line")
                
                # Сховати Width/Height/Fill
                self.shape_width_input.setVisible(False)
                self.shape_height_input.setVisible(False)
                self.shape_fill_input.setVisible(False)
                
                # Показати End X, End Y
                self.line_end_x_input.setVisible(True)
                self.line_end_y_input.setVisible(True)
                
                # Встановити значення
                self.shape_thickness_input.setValue(element.config.thickness)
                
                # Конвертувати end position з MM в current unit
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
                
                logger.debug(f"[PROP-LINE] End position: ({element.config.x2:.2f}, {element.config.y2:.2f})mm")
            else:
                # Відновити width/height, сховати End X/End Y
                self.shape_width_input.setVisible(True)
                self.shape_height_input.setVisible(True)
                self.shape_fill_input.setVisible(True)
                self.line_end_x_input.setVisible(False)
                self.line_end_y_input.setVisible(False)
            
            self.blockSignals(False)
        else:
            self.setEnabled(False)
            logger.debug("Property panel deactivated")
    
    def _on_property_change(self, prop_name, value):
        """Обработка изменения свойства"""
        if not self.current_element:
            return
        
        main_window = self._get_main_window()
        if not main_window:
            return
        
        current_unit = main_window.current_unit
        
        # Обновить элемент
        if prop_name == 'x':
            # Конвертувати назад в MM перед збереженням
            x_mm = UnitConverter.unit_to_mm(value, current_unit)
            self.current_element.config.x = x_mm
            
            logger.debug(f"[PROP-PANEL] X changed: {value:.2f}{current_unit.value} = {x_mm:.2f}mm")
            
            if self.current_graphics_item:
                x_px = int(x_mm * self.current_graphics_item.dpi / 25.4)
                self.current_graphics_item.setPos(
                    x_px, 
                    self.current_graphics_item.pos().y()
                )
        
        elif prop_name == 'y':
            y_mm = UnitConverter.unit_to_mm(value, current_unit)
            self.current_element.config.y = y_mm
            
            logger.debug(f"[PROP-PANEL] Y changed: {value:.2f}{current_unit.value} = {y_mm:.2f}mm")
            
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
            
            # КРИТИЧНО: При зміні data для CODE128 - пересчитати width!
            if hasattr(self.current_element, 'calculate_real_width'):
                real_width = self.current_element.calculate_real_width(dpi=203)
                self.barcode_width_input.blockSignals(True)
                self.barcode_width_input.setValue(int(real_width))
                self.barcode_width_input.blockSignals(False)
                
                if self.current_graphics_item:
                    self.current_graphics_item.update_size(real_width, self.current_element.height)
                
                logger.debug(f"[PROP-BARCODE] Data changed, new width: {real_width:.1f}mm")
        
        elif prop_name == 'barcode_module_width':
            # КРИТИЧНО: Зміна module_width впливає на реальну ширину!
            if hasattr(self.current_element, 'module_width'):
                self.current_element.module_width = value
                
                # Пересчитати REAL width
                real_width = self.current_element.calculate_real_width(dpi=203)
                
                # Оновити PropertyPanel width без сигналу
                self.barcode_width_input.blockSignals(True)
                self.barcode_width_input.setValue(int(real_width))
                self.barcode_width_input.blockSignals(False)
                
                # Оновити GraphicsItem
                if self.current_graphics_item:
                    self.current_graphics_item.update_size(real_width, self.current_element.height)
                
                logger.debug(f"[PROP-BARCODE] Module width changed: {value} dots -> {real_width:.1f}mm")
        
        elif prop_name == 'barcode_height':
            self.current_element.height = value
            if self.current_graphics_item:
                self.current_graphics_item.update_size(self.current_element.width, value)
        
        elif prop_name == 'barcode_data_field':
            self.current_element.data_field = value
        
        elif prop_name == 'circle_diameter':
            # Circle diameter змінено
            from core.elements.shape_element import CircleElement
            
            if isinstance(self.current_element, CircleElement):
                old_is_circle = self.current_element.is_circle
                self.current_element.diameter = value
                new_is_circle = self.current_element.is_circle
                
                logger.debug(f"[PROP-PANEL] Diameter changed: {value:.2f}mm")
                
                # Оновити graphics item
                if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                    self.current_graphics_item.update_from_element()
                
                # Перевірити чи форма змінилася (diameter завжди is_circle=True)
                if old_is_circle == new_is_circle:
                    logger.debug(f"[PROP-PANEL] Shape unchanged, no panel refresh")
        
        elif prop_name == 'shape_width':
            from core.elements.shape_element import CircleElement
            
            if isinstance(self.current_element, CircleElement):
                # Circle: використовуємо set_width() для детекції переключення
                old_is_circle = self.current_element.is_circle
                self.current_element.set_width(value)
                new_is_circle = self.current_element.is_circle
                
                logger.debug(f"[PROP-PANEL] Width changed: {value:.2f}mm")
                
                # Оновити graphics item
                if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                    self.current_graphics_item.update_from_element()
                
                # Якщо став Ellipse → перерисувати panel
                if old_is_circle and not new_is_circle:
                    logger.info(f"[PROP-PANEL] Circle -> Ellipse, refreshing panel")
                    self.set_element(self.current_element, self.current_graphics_item)
            else:
                # Rectangle або інші елементи
                self.current_element.config.width = value
                if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                    self.current_graphics_item.update_from_element()
        
        elif prop_name == 'shape_height':
            from core.elements.shape_element import CircleElement
            
            if isinstance(self.current_element, CircleElement):
                # Circle: використовуємо set_height() для детекції переключення
                old_is_circle = self.current_element.is_circle
                self.current_element.set_height(value)
                new_is_circle = self.current_element.is_circle
                
                logger.debug(f"[PROP-PANEL] Height changed: {value:.2f}mm")
                
                # Оновити graphics item
                if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                    self.current_graphics_item.update_from_element()
                
                # Якщо став Circle → перерисувати panel
                if not old_is_circle and new_is_circle:
                    logger.info(f"[PROP-PANEL] Ellipse -> Circle, refreshing panel")
                    self.set_element(self.current_element, self.current_graphics_item)
            else:
                # Rectangle або інші елементи
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
                # Line element
                self.current_element.config.thickness = value
            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                self.current_graphics_item.update_from_element()
        
        elif prop_name == 'line_end_x':
            # Line End X - конвертувати з current unit в MM
            end_x_mm = UnitConverter.unit_to_mm(value, current_unit)
            self.current_element.config.x2 = end_x_mm
            
            logger.debug(f"[PROP-LINE] End X changed: {value:.2f}{current_unit.value} = {end_x_mm:.2f}mm")
            
            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                self.current_graphics_item.update_from_element()
        
        elif prop_name == 'line_end_y':
            # Line End Y - конвертувати з current unit в MM
            end_y_mm = UnitConverter.unit_to_mm(value, current_unit)
            self.current_element.config.y2 = end_y_mm
            
            logger.debug(f"[PROP-LINE] End Y changed: {value:.2f}{current_unit.value} = {end_y_mm:.2f}mm")
            
            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_from_element'):
                self.current_graphics_item.update_from_element()
        
        # Сигнал об изменении
        self.property_changed.emit(prop_name, value)
        
        logger.info(f"Property '{prop_name}' changed to '{value}'")
    
    def update_position(self, x_mm, y_mm):
        """Обновить позицию в UI (вызывается из position_changed сигнала)"""
        # Блокировать сигналы чтобы не вызвать _on_property_change
        self.x_input.blockSignals(True)
        self.y_input.blockSignals(True)
        
        self.x_input.setValue(x_mm)
        self.y_input.setValue(y_mm)
        
        self.x_input.blockSignals(False)
        self.y_input.blockSignals(False)
        
        logger.debug(f"PropertyPanel position updated: ({x_mm:.1f}, {y_mm:.1f})")
    
    def _on_bold_changed(self, state):
        """Обработка изменения Bold checkbox"""
        if self.current_element and hasattr(self.current_element, 'bold'):
            self.current_element.bold = (state == 2)  # 2 = Qt.Checked
            
            # Обновить графический item
            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_display'):
                self.current_graphics_item.update_display()
            
            logger.debug(f"[PROP-PANEL] Bold changed: {self.current_element.bold}")
    
    def _on_underline_changed(self, state):
        """Обработка изменения Underline checkbox"""
        if self.current_element and hasattr(self.current_element, 'underline'):
            self.current_element.underline = (state == 2)  # 2 = Qt.Checked
            
            # Обновить графический item
            if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_display'):
                self.current_graphics_item.update_display()
            
            logger.debug(f"[PROP-PANEL] Underline changed: {self.current_element.underline}")
    
    def _on_font_family_changed(self, index):
        """Обробник зміни font family"""
        if not self.current_element or not hasattr(self.current_element, 'font_family'):
            return
        
        font = self.font_family_combo.currentData()  # ZplFont enum
        
        logger.debug(f"[PROP-PANEL] Font family changed: {font.zpl_code} ({font.display_name})")
        
        # Оновити element
        self.current_element.font_family = font
        
        # Оновити Canvas візуалізацію
        if self.current_graphics_item and hasattr(self.current_graphics_item, 'update_font_family'):
            self.current_graphics_item.update_font_family()
            logger.debug(f"[PROP-PANEL] Graphics item font updated")
        
        logger.debug(f"[PROP-PANEL] Element font_family updated to {self.current_element.font_family.zpl_code}")
    
    def _on_image_width_changed(self, value):
        """Оновити ширину зображення"""
        if self.current_element and hasattr(self.current_element.config, 'width'):
            logger.debug(f"[PROP-IMAGE] Width changed: {value}mm")
            self.current_element.config.width = value
            if self.current_graphics_item:
                self.current_graphics_item.update_from_element()
    
    def _on_image_height_changed(self, value):
        """Оновити висоту зображення"""
        if self.current_element and hasattr(self.current_element.config, 'height'):
            logger.debug(f"[PROP-IMAGE] Height changed: {value}mm")
            self.current_element.config.height = value
            if self.current_graphics_item:
                self.current_graphics_item.update_from_element()
    
    def _on_change_image(self):
        """Змінити зображення"""
        from PySide6.QtWidgets import QFileDialog
        import base64
        
        if not self.current_element:
            return
        
        logger.debug(f"[PROP-IMAGE] Opening change image dialog")
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select New Image",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;All Files (*)"
        )
        
        if not file_path:
            return
        
        logger.debug(f"[PROP-IMAGE] Selected new image: {file_path}")
        
        try:
            # Конвертувати у base64
            with open(file_path, 'rb') as f:
                image_bytes = f.read()
                image_data = base64.b64encode(image_bytes).decode('utf-8')
            
            # Оновити element
            self.current_element.config.image_path = file_path
            self.current_element.config.image_data = image_data
            
            # Оновити graphics item
            if self.current_graphics_item:
                self.current_graphics_item.update_from_element()
            
            logger.info(f"Image changed: {file_path}")
            
        except Exception as e:
            logger.error(f"[PROP-IMAGE] Failed to change image: {e}")
    
    def _get_main_window(self):
        """Отримати MainWindow"""
        widget = self.parent()
        while widget and not hasattr(widget, 'current_unit'):
            widget = widget.parent()
        return widget
    
    def update_for_unit(self, new_unit):
        """Оновити PropertyPanel при зміні units (БЕЗ зміни element)"""
        if not self.current_element or not self.current_graphics_item:
            return
        
        # Просто викликати set_element знову
        self.set_element(self.current_element, self.current_graphics_item)
