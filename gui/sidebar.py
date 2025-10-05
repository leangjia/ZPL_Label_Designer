# -*- coding: utf-8 -*-
"""
Sidebar - боковая панель с элементами для добавления на canvas
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, 
    QLabel, QSpacerItem, QSizePolicy
)
from PySide6.QtCore import Signal, Qt
from utils.logger import logger


class SidebarButton(QPushButton):
    """Кнопка элемента в sidebar"""
    
    def __init__(self, icon_text: str, label_text: str, parent=None):
        super().__init__(parent)
        self.icon_text = icon_text
        self.label_text = label_text
        self._setup_ui()
    
    def _setup_ui(self):
        """Настройка внешнего вида кнопки"""
        # Текст: иконка + название
        self.setText(f"{self.icon_text}\n{self.label_text}")
        
        # Размеры
        self.setFixedSize(80, 70)
        
        # Стиль
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
    Боковая панель с элементами для добавления на canvas.
    
    Signals:
        element_type_selected(str): Тип выбранного элемента ('text', 'barcode', etc.)
    """
    
    # Signal при выборе типа элемента
    element_type_selected = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        logger.debug("[SIDEBAR] Initializing")
        self._setup_ui()
        logger.debug("[SIDEBAR] Initialized successfully")
    
    def _setup_ui(self):
        """Создание UI с кнопками элементов"""
        # Основной layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(10)
        
        # Заголовок
        title = QLabel("Elements")
        title.setStyleSheet("font-weight: bold; font-size: 12pt; padding: 5px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Кнопки элементов
        self._create_element_buttons(layout)
        
        # Spacer внизу
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)
        
        # Фиксированная ширина
        self.setFixedWidth(100)
        self.setStyleSheet("background-color: #fafafa;")
    
    def _create_element_buttons(self, layout):
        """Создать кнопки для всех типов элементов"""
        elements = [
            ("T", "Text", "text"),
            ("|||", "Barcode", "barcode"),
            ("[]", "Rectangle", "rectangle"),
            ("/", "Line", "line"),
            ("O", "Circle", "circle"),
            ("[img]", "Picture", "picture"),
        ]
        
        for icon, label, element_type in elements:
            btn = SidebarButton(icon, label)
            btn.clicked.connect(lambda checked, et=element_type: self._on_button_clicked(et))
            layout.addWidget(btn)
            logger.debug(f"[SIDEBAR] Added button: {element_type}")
    
    def _on_button_clicked(self, element_type: str):
        """Обработчик клика на кнопку элемента"""
        logger.debug(f"[SIDEBAR] Button clicked: {element_type}")
        self.element_type_selected.emit(element_type)
        logger.debug(f"[SIDEBAR] Signal emitted: element_type_selected('{element_type}')")
