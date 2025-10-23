# -*- coding: utf-8 -*-
"""
侧边栏 - 包含可添加到画布的元素的侧面板
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton,
    QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from utils.logger import logger


class SidebarButton(QPushButton):
    """侧边栏中的元素按钮"""

    def __init__(self, icon_text: str, label_text: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.label_text = label_text
        self._setup_ui()

    def _setup_ui(self):
        """设置按钮外观"""
        # 文本: 图标 + 名称
        self.setText(f"{self.icon_text}\n{self.label_text}")

        # 尺寸
        self.setFixedSize(80, 70)

        # 样式
        self.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 2px solid #e0e0e0;
                border-radius: 5px;
                padding: 5px;
                font-size: 10pt;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border: 2px solid #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)


class Sidebar(QWidget):
    """
    包含可添加到画布的元素的侧边栏。

    信号:
        element_type_selected(str): 选择的元素类型 ('text', 'barcode', 等)
    """

    # 选择元素类型时的信号
    element_type_selected = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("[SIDEBAR] 正在初始化")
        self._setup_ui()
        logger.debug("[SIDEBAR] 初始化成功")

    def _setup_ui(self):
        """创建带有元素按钮的用户界面"""
        # 主布局
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)

        # 标题
        title = QLabel("元素")
        title.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 元素按钮
        self._create_element_buttons(layout)

        # 底部间隔
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        # 固定宽度
        self.setFixedWidth(100)
        self.setStyleSheet("background-color: #fafafa;")

    def _create_element_buttons(self, layout):
        """为所有元素类型创建按钮"""
        elements = [
            ("T", "文本", "text"),
            ("|||", "条码", "barcode"),
            ("[]", "矩形", "rectangle"),
            ("/", "线条", "line"),
            ("O", "圆形", "circle"),
            ("[img]", "图片", "picture"),
        ]

        for icon, label, element_type in elements:
            btn = SidebarButton(icon, label)
            btn.clicked.connect(lambda checked, et=element_type: self._on_button_clicked(et))
            layout.addWidget(btn)
            logger.debug(f"[SIDEBAR] 已添加按钮: {element_type}")

    def _on_button_clicked(self, element_type: str):
        """元素按钮点击处理程序"""
        logger.debug(f"[SIDEBAR] 按钮被点击: {element_type}")
        self.element_type_selected.emit(element_type)
        logger.debug(f"[SIDEBAR] 信号已发出: element_type_selected('{element_type}')")