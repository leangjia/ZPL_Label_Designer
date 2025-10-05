# -*- coding: utf-8 -*-
"""Главное окно приложения"""

from PySide6.QtWidgets import (QMainWindow, QDockWidget, QWidget, QGridLayout)
from PySide6.QtCore import Qt
from PySide6.QtGui import QUndoStack
from .canvas_view import CanvasView
from .toolbar import EditorToolbar
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
from utils.unit_converter import MeasurementUnit
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
        
        # Canvas
        self.canvas = CanvasView(width_mm=28, height_mm=28, dpi=203)
        logger.info("Canvas created (28x28mm, DPI 203)")
        
        # Smart Guides
        self.smart_guides = SmartGuides(self.canvas.scene)
        self.guides_enabled = True
        logger.info("Smart Guides initialized")
        
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
        grid_layout.addWidget(corner_spacer, 0, 0)
        grid_layout.addWidget(self.h_ruler, 0, 1)
        grid_layout.addWidget(self.v_ruler, 1, 0)
        grid_layout.addWidget(self.canvas, 1, 1)
        
        self.setCentralWidget(central_widget)
        logger.info("Central widget with rulers configured")
        
        # Toolbar
        self.toolbar = EditorToolbar(self)
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
        self.snap_enabled = True
        
        # Current display unit
        self.current_unit = DEFAULT_UNIT
        
        # Connect signals
        self._connect_signals()
        
        # Setup UI controls from mixins
        self._create_snap_toggle()
        self._create_label_size_controls()
        self._create_units_controls()
        
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
        
        # Toolbar signals
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
        
        logger.info("All signals connected")
