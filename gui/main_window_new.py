# -*- coding: utf-8 -*-
"""应用程序主窗口"""

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

        # 拖拽状态
        self.drag_start_pos = None

        # ZPL 生成器
        self.zpl_generator = ZPLGenerator(dpi=203)
        self.labelary_client = LabelaryClient(dpi=203)
        self.template_manager = TemplateManager()
        logger.info("ZPL 生成器、Labelary 客户端和模板管理器已创建")

        # 画布
        self.canvas = CanvasView(width_mm=28, height_mm=28, dpi=203)
        logger.info("画布已创建 (28x28mm, DPI 203)")

        # 智能参考线
        self.smart_guides = SmartGuides(self.canvas.scene)
        self.guides_enabled = True
        logger.info("智能参考线已初始化")

        # 撤销/重做堆栈
        self.undo_stack = QUndoStack(self)
        logger.debug(f"[撤销堆栈] 已初始化")

        # 标尺
        self.h_ruler = HorizontalRuler(length_mm=28, dpi=203, scale=2.5)
        self.v_ruler = VerticalRuler(length_mm=28, dpi=203, scale=2.5)
        logger.info("标尺已创建")

        # 将标尺链接到画布
        self.canvas.h_ruler = self.h_ruler
        self.canvas.v_ruler = self.v_ruler
        logger.info("标尺已链接到画布")

        # 中央控件布局
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
        logger.info("带标尺的中央控件已配置")

        # 工具栏
        self.toolbar = EditorToolbar(self)
        self.addToolBar(self.toolbar)
        logger.info("工具栏已创建")

        # 属性面板
        self.property_panel = PropertyPanel()
        dock = QDockWidget("属性", self)
        dock.setWidget(self.property_panel)
        dock.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.addDockWidget(Qt.RightDockWidgetArea, dock)
        logger.info("属性面板已创建")

        # 网格吸附
        self.snap_enabled = True

        # 当前显示单位
        self.current_unit = DEFAULT_UNIT

        # 连接信号
        self._connect_signals()

        # 从混入类设置 UI 控件
        self._create_snap_toggle()
        self._create_label_size_controls()
        self._create_units_controls()

        # 设置快捷键
        self._setup_shortcuts()

        logger.info("主窗口完全初始化")

    def _connect_signals(self):
        """连接所有信号"""
        # 画布信号
        self.canvas.scene.selectionChanged.connect(self._on_selection_changed)
        self.canvas.cursor_position_changed.connect(self._update_ruler_cursor)
        self.canvas.context_menu_requested.connect(self._show_context_menu)

        # 事件过滤器
        self.canvas.viewport().installEventFilter(self)
        self.canvas.scene.installEventFilter(self)

        # 工具栏信号
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

        logger.info("所有信号已连接")