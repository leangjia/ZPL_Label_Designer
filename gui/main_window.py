# -*- coding: utf-8 -*-
"""应用程序主窗口"""

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
    """编辑器主窗口"""

    def __init__(self, template_file=None):
        super().__init__()
        self.setWindowTitle("ZPL 标签设计器")
        self.resize(1200, 700)
        logger.info("主窗口已初始化")

        # 保存模板文件路径用于 UI 初始化后加载
        self._template_file_to_load = template_file

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

        toolbar_settings = settings_manager.load_toolbar_settings()
        label_width_mm = toolbar_settings['label_width']
        label_height_mm = toolbar_settings['label_height']

        # 画布
        self.canvas = CanvasView(width_mm=label_width_mm, height_mm=label_height_mm, dpi=203)
        logger.info(f"画布已创建 ({label_width_mm}x{label_height_mm}mm, DPI 203)")
        self.canvas.bounds_update_callback = self._highlight_element_bounds

        # 侧边栏
        self.sidebar = Sidebar()
        logger.info("侧边栏已创建")

        # 智能参考线
        self.smart_guides = SmartGuides(self.canvas.scene)
        self.guides_enabled = toolbar_settings['smart_guides']
        self.smart_guides.set_enabled(self.guides_enabled)
        logger.info(f"智能参考线已初始化 (启用={self.guides_enabled})")

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
        grid_layout.addWidget(self.sidebar, 0, 0, 2, 1)  # 侧边栏在左侧，跨越 2 行
        grid_layout.addWidget(corner_spacer, 0, 1)
        grid_layout.addWidget(self.h_ruler, 0, 2)
        grid_layout.addWidget(self.v_ruler, 1, 1)
        grid_layout.addWidget(self.canvas, 1, 2)

        self.setCentralWidget(central_widget)
        logger.info("带标尺的中央控件已配置")

        # 操作和菜单
        self._create_actions()
        self._create_menus()

        # 工具栏
        self.toolbar = EditorToolbar(self.actions, self.menus, parent=self)
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
        self.snap_enabled = toolbar_settings['snap_to_grid']

        # 当前显示单位
        unit_value = toolbar_settings['unit']
        try:
            self.current_unit = MeasurementUnit(unit_value)
        except ValueError:
            logger.warning(f"[工具栏持久化] 未知单位 '{unit_value}'，回退到 {DEFAULT_UNIT.value}")
            self.current_unit = DEFAULT_UNIT

        # 连接信号
        self._connect_signals()

        # 从混入类设置 UI 控件
        self._create_snap_toggle()
        self._create_label_size_controls()
        self._create_units_controls()
        self._apply_persisted_toolbar_settings(toolbar_settings)

        # 设置快捷键
        self._setup_shortcuts()

        logger.info("主窗口完全初始化")

        # 如果传入了模板文件则加载
        if self._template_file_to_load:
            self._load_template_from_file(self._template_file_to_load)

    def _connect_signals(self):
        """连接所有信号"""
        # 画布信号
        self.canvas.scene.selectionChanged.connect(self._on_selection_changed)
        self.canvas.cursor_position_changed.connect(self._update_ruler_cursor)
        self.canvas.context_menu_requested.connect(self._show_context_menu)

        # 事件过滤器
        self.canvas.viewport().installEventFilter(self)
        self.canvas.scene.installEventFilter(self)

        # 侧边栏信号
        self.sidebar.element_type_selected.connect(self._on_sidebar_element_selected)

        # 操作信号
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
        self.actions['open_json'].triggered.connect(self._open_json)
        self.actions['preview'].triggered.connect(self._show_preview)
        self.actions['grid_settings'].triggered.connect(self._show_grid_settings)

        logger.info("所有信号已连接")

    def _create_actions(self):
        """创建和配置可重用的操作和菜单"""

        self.actions = {}
        self.menus = {}

        # 基本操作
        add_text_action = QAction("添加文本", self)
        add_text_action.setShortcut(QKeySequence("Ctrl+T"))
        add_text_action.setToolTip("添加文本 (Ctrl+T)")
        self.actions['add_text'] = add_text_action

        add_image_action = QAction("添加图片", self)
        add_image_action.setShortcut(QKeySequence("Ctrl+I"))
        add_image_action.setToolTip("添加图片 (Ctrl+I)")
        self.actions['add_image'] = add_image_action

        save_action = QAction("保存", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.setToolTip("保存模板 (Ctrl+S)")
        self.actions['save'] = save_action

        load_action = QAction("加载", self)
        load_action.setShortcut(QKeySequence.Open)
        load_action.setToolTip("加载模板 (Ctrl+O)")
        self.actions['load'] = load_action

        export_action = QAction("导出 ZPL", self)
        export_action.setShortcut(QKeySequence("Ctrl+E"))
        export_action.setToolTip("导出为 ZPL (Ctrl+E)")
        self.actions['export'] = export_action

        preview_action = QAction("预览", self)
        preview_action.setShortcut(QKeySequence("Ctrl+P"))
        preview_action.setToolTip("预览 (Ctrl+P)")
        self.actions['preview'] = preview_action

        open_json_action = QAction("打开 JSON", self)
        open_json_action.setToolTip("显示模板 JSON")
        self.actions['open_json'] = open_json_action

        # 网格设置
        grid_settings_action = QAction("网格设置...", self)
        grid_settings_action.setToolTip("网格设置")
        self.actions['grid_settings'] = grid_settings_action

        # 条码组
        barcode_menu = QMenu("添加条码", self)
        add_ean13_action = QAction("EAN-13", self)
        add_ean13_action.setToolTip("添加 EAN-13 条码")
        barcode_menu.addAction(add_ean13_action)

        add_code128_action = QAction("Code 128", self)
        add_code128_action.setToolTip("添加 Code 128 条码")
        barcode_menu.addAction(add_code128_action)

        add_qrcode_action = QAction("QR 码", self)
        add_qrcode_action.setToolTip("添加 QR 码")
        barcode_menu.addAction(add_qrcode_action)

        barcode_menu_action = QAction("添加条码", self)
        barcode_menu_action.setToolTip("添加条码")
        barcode_menu_action.setMenu(barcode_menu)

        self.menus['barcode'] = barcode_menu
        self.actions['add_ean13'] = add_ean13_action
        self.actions['add_code128'] = add_code128_action
        self.actions['add_qrcode'] = add_qrcode_action
        self.actions['barcode_menu'] = barcode_menu_action

        # 形状组
        shape_menu = QMenu("添加形状", self)
        add_rectangle_action = QAction("矩形", self)
        add_rectangle_action.setToolTip("添加矩形")
        shape_menu.addAction(add_rectangle_action)

        add_circle_action = QAction("圆形", self)
        add_circle_action.setToolTip("添加圆形")
        shape_menu.addAction(add_circle_action)

        add_line_action = QAction("线条", self)
        add_line_action.setToolTip("添加线条")
        shape_menu.addAction(add_line_action)

        shape_menu_action = QAction("添加形状", self)
        shape_menu_action.setToolTip("添加形状")
        shape_menu_action.setMenu(shape_menu)

        self.menus['shape'] = shape_menu
        self.actions['add_rectangle'] = add_rectangle_action
        self.actions['add_circle'] = add_circle_action
        self.actions['add_line'] = add_line_action
        self.actions['shape_menu'] = shape_menu_action

    def _create_menus(self):
        """使用现有操作创建主菜单"""

        menubar = self.menuBar()
        menubar.clear()

        file_menu = menubar.addMenu("文件")
        file_menu.addAction(self.actions['save'])
        file_menu.addAction(self.actions['load'])
        file_menu.addSeparator()
        file_menu.addAction(self.actions['export'])
        file_menu.addAction(self.actions['open_json'])
        file_menu.addAction(self.actions['preview'])

        insert_menu = menubar.addMenu("插入")
        insert_menu.addAction(self.actions['add_text'])
        insert_menu.addMenu(self.menus['barcode'])
        insert_menu.addMenu(self.menus['shape'])
        insert_menu.addAction(self.actions['add_image'])

        view_menu = menubar.addMenu("视图")
        view_menu.addAction(self.actions['grid_settings'])

    def _apply_persisted_toolbar_settings(self, toolbar_settings):
        """应用在会话间保存的工具栏设置"""

        show_grid = toolbar_settings['show_grid']
        snap_to_grid = toolbar_settings['snap_to_grid']
        smart_guides = toolbar_settings['smart_guides']
        saved_unit = self.current_unit

        if isinstance(toolbar_settings.get('unit'), str):
            try:
                saved_unit = MeasurementUnit(toolbar_settings['unit'])
            except ValueError:
                logger.warning(
                    f"[工具栏持久化] 无效单位 '{toolbar_settings['unit']}'，"
                    f"回退到 {self.current_unit.value}"
                )
                saved_unit = self.current_unit

        # 应用显示网格状态
        if hasattr(self, 'grid_checkbox'):
            self.grid_checkbox.blockSignals(True)
            self.grid_checkbox.setChecked(show_grid)
            self.grid_checkbox.blockSignals(False)

            # 强制应用到画布
            self.grid_visible = show_grid
            if hasattr(self.canvas, 'set_grid_visible'):
                self.canvas.set_grid_visible(show_grid)
                # 如果网格应该可见则强制重绘
                if show_grid and not self.canvas.grid_items:
                    logger.debug("[工具栏持久化] 强制网格重绘")
                    self.canvas._draw_grid()
            logger.debug(f"[工具栏持久化] 显示网格已应用: {show_grid}")

        # 应用网格吸附状态
        if hasattr(self, 'snap_checkbox'):
            self.snap_checkbox.blockSignals(True)
            self.snap_checkbox.setChecked(snap_to_grid)
            self.snap_checkbox.blockSignals(False)

            # 强制应用
            self.snap_enabled = snap_to_grid
            # 更新所有现有元素
            for item in self.graphics_items:
                if hasattr(item, 'snap_enabled'):
                    item.snap_enabled = snap_to_grid
            logger.debug(f"[工具栏持久化] 网格吸附已应用: {snap_to_grid} (项目: {len(self.graphics_items)})")

        # 应用智能参考线状态
        if hasattr(self, 'guides_checkbox'):
            self.guides_checkbox.blockSignals(True)
            self.guides_checkbox.setChecked(smart_guides)
            self.guides_checkbox.blockSignals(False)

            # 强制应用
            self.guides_enabled = smart_guides
            if hasattr(self, 'smart_guides'):
                self.smart_guides.set_enabled(smart_guides)
            logger.debug(f"[工具栏持久化] 智能参考线已应用: {smart_guides}")

        # 以当前单位应用标签尺寸值
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

        # 应用单位选择（通过 _on_unit_changed 更新微调框/标尺）
        if hasattr(self, 'units_combobox'):
            index = self.units_combobox.findData(saved_unit)
            if index != -1:
                self.units_combobox.blockSignals(True)
                self.units_combobox.setCurrentIndex(index)
                self.units_combobox.blockSignals(False)

                # 强制应用到标尺
                self.current_unit = saved_unit

                # 直接应用到标尺
                if hasattr(self.canvas, 'h_ruler') and self.canvas.h_ruler:
                    self.canvas.h_ruler.set_unit(saved_unit)
                    logger.debug(f"[工具栏持久化] 水平标尺单位设置为: {saved_unit.value}")

                if hasattr(self.canvas, 'v_ruler') and self.canvas.v_ruler:
                    self.canvas.v_ruler.set_unit(saved_unit)
                    logger.debug(f"[工具栏持久化] 垂直标尺单位设置为: {saved_unit.value}")

                # 更新微调框后缀
                self._update_label_size_spinboxes(saved_unit, saved_unit)

        # 将画布标签尺寸与持久化值同步
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
        从侧边栏选择元素的处理程序。

        Args:
            element_type: 元素类型 ('text', 'barcode', 'rectangle', 等)
        """
        logger.debug(f"[侧边栏] 选择的元素: {element_type}")

        # 路由到相应的创建方法
        if element_type == 'text':
            self._add_text()
        elif element_type == 'barcode':
            # 默认添加 EAN-13
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
            logger.warning(f"[侧边栏] 未知元素类型: {element_type}")

        logger.debug(f"[侧边栏] 元素 {element_type} 添加成功")

    def _show_grid_settings(self):
        """显示网格设置对话框"""
        from gui.grid_settings_dialog import GridSettingsDialog

        dialog = GridSettingsDialog(self.canvas.grid_config, parent=self)
        if dialog.exec():
            new_config = dialog.get_config()
            self.canvas.set_grid_config(new_config)
            self.canvas._redraw_grid()

            logger.debug(f"[网格设置] 应用了新配置: {new_config}")