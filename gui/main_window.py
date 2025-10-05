# -*- coding: utf-8 -*-
"""Главное окно приложения"""

from PySide6.QtWidgets import (QMainWindow, QDockWidget, QWidget, QGridLayout, QMenu)
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QUndoStack
from .canvas_view import CanvasView
from .toolbar import EditorToolbar
from .sidebar import Sidebar
from .property_panel import PropertyPanel
from .smart_guides import SmartGuides
from .rulers import HorizontalRuler, VerticalRuler
from .mixins import (
    ElementCreationMixin,
    SelectionMixin,
    TemplateMixin,
    ClipboardMixin,
    ShortcutsMixin,
    LabelConfigMixin,
    UIHelpersMixin
)
from core.template_manager import TemplateManager
from zpl.generator import ZPLGenerator
from integration.labelary_client import LabelaryClient
from utils.logger import logger
from utils.unit_converter import MeasurementUnit, UnitConverter
from utils.settings_manager import settings_manager
from config import DEFAULT_UNIT


class MainWindow(QMainWindow, 
                 ElementCreationMixin,
                 SelectionMixin,
                 TemplateMixin,
                 ClipboardMixin,
                 ShortcutsMixin,
                 LabelConfigMixin,
                 UIHelpersMixin):
    """Главное окно редактора"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ZPL Label Designer")
        self.resize(1200, 700)
        logger.info("MainWindow initialized")
        
        # Список элементов и графических элементов
        self.elements = []
        self.graphics_items = []
        self.selected_item = None
        
        # Clipboard для copy/paste
        self.clipboard_element = None
        
        # Drag state
        self.drag_start_pos = None
        
        # ZPL Generator
        self.zpl_generator = ZPLGenerator(dpi=203)
        self.labelary_client = LabelaryClient(dpi=203)
        self.template_manager = TemplateManager()
        logger.info("ZPL Generator, Labelary Client and Template Manager created")
        
        toolbar_settings = settings_manager.load_toolbar_settings()
        label_width_mm = toolbar_settings['label_width']
        label_height_mm = toolbar_settings['label_height']

        # Canvas
        self.canvas = CanvasView(width_mm=label_width_mm, height_mm=label_height_mm, dpi=203)
        logger.info(f"Canvas created ({label_width_mm}x{label_height_mm}mm, DPI 203)")
        self.canvas.bounds_update_callback = self._highlight_element_bounds
        
        # Sidebar
        self.sidebar = Sidebar()
        logger.info("Sidebar created")
        
        # Smart Guides
        self.smart_guides = SmartGuides(self.canvas.scene)
        self.guides_enabled = toolbar_settings['smart_guides']
        self.smart_guides.set_enabled(self.guides_enabled)
        logger.info(f"Smart Guides initialized (enabled={self.guides_enabled})")
        
        # Undo/Redo Stack
        self.undo_stack = QUndoStack(self)
        logger.debug(f"[UNDO-STACK] Initialized")
        
        # Rulers
        self.h_ruler = HorizontalRuler(length_mm=28, dpi=203, scale=2.5)
        self.v_ruler = VerticalRuler(length_mm=28, dpi=203, scale=2.5)
        logger.info("Rulers created")
        
        # Link rulers to canvas
        self.canvas.h_ruler = self.h_ruler
        self.canvas.v_ruler = self.v_ruler
        logger.info("Rulers linked to canvas")
        
        # Central widget layout
        central_widget = QWidget()
        grid_layout = QGridLayout(central_widget)
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        
        corner_spacer = QWidget()
        corner_spacer.setFixedSize(25, 25)
        grid_layout.addWidget(self.sidebar, 0, 0, 2, 1)  # Sidebar ЗЛІВА, spans 2 rows
        grid_layout.addWidget(corner_spacer, 0, 1)
        grid_layout.addWidget(self.h_ruler, 0, 2)
        grid_layout.addWidget(self.v_ruler, 1, 1)
        grid_layout.addWidget(self.canvas, 1, 2)
        
        self.setCentralWidget(central_widget)
        logger.info("Central widget with rulers configured")
        
        # Actions & menus
        self._create_actions()
        self._create_menus()

        # Toolbar
        self.toolbar = EditorToolbar(self.actions, self.menus, parent=self)
        self.addToolBar(self.toolbar)
        logger.info("Toolbar created")
        
        # Property panel
        self.property_panel = PropertyPanel()
        dock = QDockWidget("Properties", self)
        dock.setWidget(self.property_panel)
        dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        logger.info("Property panel created")
        
        # Snap to grid
        self.snap_enabled = toolbar_settings['snap_to_grid']

        # Current display unit
        unit_value = toolbar_settings['unit']
        try:
            self.current_unit = MeasurementUnit(unit_value)
        except ValueError:
            logger.warning(f"[TOOLBAR-PERSIST] Unknown unit '{unit_value}', fallback to {DEFAULT_UNIT.value}")
            self.current_unit = DEFAULT_UNIT
        
        # Connect signals
        self._connect_signals()
        
        # Setup UI controls from mixins
        self._create_snap_toggle()
        self._create_label_size_controls()
        self._create_units_controls()
        self._apply_persisted_toolbar_settings(toolbar_settings)
        
        # Setup shortcuts
        self._setup_shortcuts()
        
        logger.info("MainWindow fully initialized")
    
    def _connect_signals(self):
        """Connect all signals"""
        # Canvas signals
        self.canvas.scene.selectionChanged.connect(self._on_selection_changed)
        self.canvas.cursor_position_changed.connect(self._update_ruler_cursor)
        self.canvas.context_menu_requested.connect(self._show_context_menu)
        
        # Event filters
        self.canvas.viewport().installEventFilter(self)
        self.canvas.scene.installEventFilter(self)
        
        # Sidebar signals
        self.sidebar.element_type_selected.connect(self._on_sidebar_element_selected)
        
        # Actions signals
        self.actions['add_text'].triggered.connect(self._add_text)
        self.actions['add_ean13'].triggered.connect(self._add_ean13)
        self.actions['add_code128'].triggered.connect(self._add_code128)
        self.actions['add_qrcode'].triggered.connect(self._add_qrcode)
        self.actions['add_rectangle'].triggered.connect(self._add_rectangle)
        self.actions['add_circle'].triggered.connect(self._add_circle)
        self.actions['add_line'].triggered.connect(self._add_line)
        self.actions['add_image'].triggered.connect(self._add_image)
        self.actions['save'].triggered.connect(self._save_template)
        self.actions['load'].triggered.connect(self._load_template)
        self.actions['export'].triggered.connect(self._export_zpl)
        self.actions['preview'].triggered.connect(self._show_preview)
        self.actions['grid_settings'].triggered.connect(self._show_grid_settings)

        logger.info("All signals connected")

    def _create_actions(self):
        """Create and configure reusable actions and menus."""

        self.actions = {}
        self.menus = {}

        # Basic actions
        add_text_action = QAction("Add Text", self)
        add_text_action.setShortcut(QKeySequence("Ctrl+T"))
        add_text_action.setToolTip("Добавить текст (Ctrl+T)")
        self.actions['add_text'] = add_text_action

        add_image_action = QAction("Add Image", self)
        add_image_action.setShortcut(QKeySequence("Ctrl+I"))
        add_image_action.setToolTip("Додати зображення (Ctrl+I)")
        self.actions['add_image'] = add_image_action

        save_action = QAction("Save", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setToolTip("Сохранить шаблон (Ctrl+S)")
        self.actions['save'] = save_action

        load_action = QAction("Load", self)
        load_action.setShortcut(QKeySequence.Open)
        load_action.setToolTip("Загрузить шаблон (Ctrl+O)")
        self.actions['load'] = load_action

        export_action = QAction("Export ZPL", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.setToolTip("Экспорт в ZPL (Ctrl+E)")
        self.actions['export'] = export_action

        preview_action = QAction("Preview", self)
        preview_action.setShortcut(QKeySequence("Ctrl+P"))
        preview_action.setToolTip("Предпросмотр (Ctrl+P)")
        self.actions['preview'] = preview_action

        # Grid Settings
        grid_settings_action = QAction("Grid Settings...", self)
        grid_settings_action.setToolTip("Налаштування сітки")
        self.actions['grid_settings'] = grid_settings_action

        # Barcode group
        barcode_menu = QMenu("Add Barcode", self)
        add_ean13_action = QAction("EAN-13", self)
        add_ean13_action.setToolTip("Добавить EAN-13 штрихкод")
        barcode_menu.addAction(add_ean13_action)

        add_code128_action = QAction("Code 128", self)
        add_code128_action.setToolTip("Добавить Code 128 штрихкод")
        barcode_menu.addAction(add_code128_action)

        add_qrcode_action = QAction("QR Code", self)
        add_qrcode_action.setToolTip("Добавить QR код")
        barcode_menu.addAction(add_qrcode_action)

        barcode_menu_action = QAction("Add Barcode", self)
        barcode_menu_action.setToolTip("Добавить штрихкод")
        barcode_menu_action.setMenu(barcode_menu)

        self.menus['barcode'] = barcode_menu
        self.actions['add_ean13'] = add_ean13_action
        self.actions['add_code128'] = add_code128_action
        self.actions['add_qrcode'] = add_qrcode_action
        self.actions['barcode_menu'] = barcode_menu_action

        # Shape group
        shape_menu = QMenu("Add Shape", self)
        add_rectangle_action = QAction("Rectangle", self)
        add_rectangle_action.setToolTip("Добавить прямоугольник")
        shape_menu.addAction(add_rectangle_action)

        add_circle_action = QAction("Circle", self)
        add_circle_action.setToolTip("Добавить круг")
        shape_menu.addAction(add_circle_action)

        add_line_action = QAction("Line", self)
        add_line_action.setToolTip("Добавить линию")
        shape_menu.addAction(add_line_action)

        shape_menu_action = QAction("Add Shape", self)
        shape_menu_action.setToolTip("Добавить фигуру")
        shape_menu_action.setMenu(shape_menu)

        self.menus['shape'] = shape_menu
        self.actions['add_rectangle'] = add_rectangle_action
        self.actions['add_circle'] = add_circle_action
        self.actions['add_line'] = add_line_action
        self.actions['shape_menu'] = shape_menu_action

    def _create_menus(self):
        """Create the main menu using existing actions."""

        menubar = self.menuBar()
        menubar.clear()

        file_menu = menubar.addMenu("File")
        file_menu.addAction(self.actions['save'])
        file_menu.addAction(self.actions['load'])
        file_menu.addSeparator()
        file_menu.addAction(self.actions['export'])
        file_menu.addAction(self.actions['preview'])

        insert_menu = menubar.addMenu("Insert")
        insert_menu.addAction(self.actions['add_text'])
        insert_menu.addMenu(self.menus['barcode'])
        insert_menu.addMenu(self.menus['shape'])
        insert_menu.addAction(self.actions['add_image'])

        view_menu = menubar.addMenu("View")
        view_menu.addAction(self.actions['grid_settings'])

    def _apply_persisted_toolbar_settings(self, toolbar_settings):
        """Застосувати налаштування toolbar, збережені між сесіями"""

        show_grid = toolbar_settings['show_grid']
        snap_to_grid = toolbar_settings['snap_to_grid']
        smart_guides = toolbar_settings['smart_guides']
        saved_unit = self.current_unit

        if isinstance(toolbar_settings.get('unit'), str):
            try:
                saved_unit = MeasurementUnit(toolbar_settings['unit'])
            except ValueError:
                logger.warning(
                    f"[TOOLBAR-PERSIST] Invalid unit '{toolbar_settings['unit']}',"
                    f" fallback to {self.current_unit.value}"
                )
                saved_unit = self.current_unit

        # Apply Show Grid state
        if hasattr(self, 'grid_checkbox'):
            self.grid_checkbox.blockSignals(True)
            self.grid_checkbox.setChecked(show_grid)
            self.grid_checkbox.blockSignals(False)
            
            # Принудительно применить к canvas
            self.grid_visible = show_grid
            if hasattr(self.canvas, 'set_grid_visible'):
                self.canvas.set_grid_visible(show_grid)
                # Принудительный redraw если grid должна быть видна
                if show_grid and not self.canvas.grid_items:
                    logger.debug("[TOOLBAR-PERSIST] Forcing grid redraw")
                    self.canvas._draw_grid()
            logger.debug(f"[TOOLBAR-PERSIST] Show Grid applied: {show_grid}")

        # Apply Snap to Grid state
        if hasattr(self, 'snap_checkbox'):
            self.snap_checkbox.blockSignals(True)
            self.snap_checkbox.setChecked(snap_to_grid)
            self.snap_checkbox.blockSignals(False)
            
            # Принудительно применить
            self.snap_enabled = snap_to_grid
            # Обновить ВСЕ существующие элементы
            for item in self.graphics_items:
                if hasattr(item, 'snap_enabled'):
                    item.snap_enabled = snap_to_grid
            logger.debug(f"[TOOLBAR-PERSIST] Snap to Grid applied: {snap_to_grid} (items: {len(self.graphics_items)})")

        # Apply Smart Guides state
        if hasattr(self, 'guides_checkbox'):
            self.guides_checkbox.blockSignals(True)
            self.guides_checkbox.setChecked(smart_guides)
            self.guides_checkbox.blockSignals(False)
            
            # Принудительно применить
            self.guides_enabled = smart_guides
            if hasattr(self, 'smart_guides'):
                self.smart_guides.set_enabled(smart_guides)
            logger.debug(f"[TOOLBAR-PERSIST] Smart Guides applied: {smart_guides}")

        # Apply label size values in current unit
        width_mm = toolbar_settings['label_width']
        height_mm = toolbar_settings['label_height']

        if hasattr(self, 'width_spinbox') and hasattr(self, 'height_spinbox'):
            if saved_unit != MeasurementUnit.MM:
                width_value = UnitConverter.mm_to_unit(width_mm, saved_unit)
                height_value = UnitConverter.mm_to_unit(height_mm, saved_unit)
            else:
                width_value = width_mm
                height_value = height_mm

            self.width_spinbox.blockSignals(True)
            self.height_spinbox.blockSignals(True)
            self.width_spinbox.setValue(width_value)
            self.height_spinbox.setValue(height_value)
            self.width_spinbox.blockSignals(False)
            self.height_spinbox.blockSignals(False)

        # Apply unit selection (updates spinboxes/rulers via _on_unit_changed)
        if hasattr(self, 'units_combobox'):
            index = self.units_combobox.findData(saved_unit)
            if index != -1:
                self.units_combobox.blockSignals(True)
                self.units_combobox.setCurrentIndex(index)
                self.units_combobox.blockSignals(False)
                
                # Принудительно применить к rulers
                self.current_unit = saved_unit
                
                # Применить к rulers НАПРЯМУЮ
                if hasattr(self.canvas, 'h_ruler') and self.canvas.h_ruler:
                    self.canvas.h_ruler.set_unit(saved_unit)
                    logger.debug(f"[TOOLBAR-PERSIST] H Ruler unit set to: {saved_unit.value}")
                
                if hasattr(self.canvas, 'v_ruler') and self.canvas.v_ruler:
                    self.canvas.v_ruler.set_unit(saved_unit)
                    logger.debug(f"[TOOLBAR-PERSIST] V Ruler unit set to: {saved_unit.value}")
                
                # Обновить spinboxes суффиксы
                self._update_label_size_spinboxes(saved_unit, saved_unit)

        # Sync canvas label size with persisted values
        if hasattr(self, 'canvas'):
            if abs(self.canvas.width_mm - width_mm) > 0.001 or abs(self.canvas.height_mm - height_mm) > 0.001:
                self.canvas.set_label_size(width_mm, height_mm)

        settings_manager.save_toolbar_settings(
            {
                'show_grid': show_grid,
                'snap_to_grid': snap_to_grid,
                'smart_guides': smart_guides,
                'label_width': width_mm,
                'label_height': height_mm,
                'unit': saved_unit.value,
            }
        )
    
    def _on_sidebar_element_selected(self, element_type: str):
        """
        Обробник вибору елемента з sidebar.
        
        Args:
            element_type: Тип елемента ('text', 'barcode', 'rectangle', etc.)
        """
        logger.debug(f"[SIDEBAR] Element selected: {element_type}")
        
        # Роутинг до відповідного методу створення
        if element_type == 'text':
            self._add_text()
        elif element_type == 'barcode':
            # За замовчуванням додаємо EAN-13
            self._add_ean13()
        elif element_type == 'rectangle':
            self._add_rectangle()
        elif element_type == 'circle':
            self._add_circle()
        elif element_type == 'line':
            self._add_line()
        elif element_type == 'picture':
            self._add_image()
        else:
            logger.warning(f"[SIDEBAR] Unknown element type: {element_type}")
        
        logger.debug(f"[SIDEBAR] Element {element_type} added successfully")
    
    def _show_grid_settings(self):
        """Показати діалог налаштувань сітки"""
        from gui.grid_settings_dialog import GridSettingsDialog
        
        dialog = GridSettingsDialog(self.canvas.grid_config, parent=self)
        if dialog.exec():
            new_config = dialog.get_config()
            self.canvas.set_grid_config(new_config)
            self.canvas._redraw_grid()
            
            logger.debug(f"[GRID-SETTINGS] Applied new config: {new_config}")
