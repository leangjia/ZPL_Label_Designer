# -*- coding: utf-8 -*-
"""Панель инструментов"""

from PySide6.QtWidgets import QToolBar, QMenu
from PySide6.QtGui import QAction, QKeySequence

class EditorToolbar(QToolBar):
    """Панель инструментов редактора"""
    
    def __init__(self, parent=None):
        super().__init__("Tools", parent)
        
        # Add Text
        self.add_text_action = QAction("Add Text", self)
        self.add_text_action.setShortcut(QKeySequence("Ctrl+T"))
        self.add_text_action.setToolTip("Добавить текст (Ctrl+T)")
        self.addAction(self.add_text_action)
        
        self.addSeparator()
        
        # Add Barcode menu
        self.barcode_menu_action = QAction("Add Barcode", self)
        self.barcode_menu_action.setToolTip("Добавить штрихкод")
        
        # Создать подменю
        self.barcode_menu = QMenu(self)
        
        self.add_ean13_action = QAction("EAN-13", self)
        self.add_ean13_action.setToolTip("Добавить EAN-13 штрихкод")
        self.barcode_menu.addAction(self.add_ean13_action)
        
        self.add_code128_action = QAction("Code 128", self)
        self.add_code128_action.setToolTip("Добавить Code 128 штрихкод")
        self.barcode_menu.addAction(self.add_code128_action)
        
        self.add_qrcode_action = QAction("QR Code", self)
        self.add_qrcode_action.setToolTip("Добавить QR код")
        self.barcode_menu.addAction(self.add_qrcode_action)
        
        self.barcode_menu_action.setMenu(self.barcode_menu)
        
        # Добавить к toolbar
        self.addAction(self.barcode_menu_action)
        
        self.addSeparator()
        
        # Add Shape menu
        self.shape_menu_action = QAction("Add Shape", self)
        self.shape_menu_action.setToolTip("Добавить фигуру")
        
        # Создать подменю
        self.shape_menu = QMenu(self)
        
        self.add_rectangle_action = QAction("Rectangle", self)
        self.add_rectangle_action.setToolTip("Добавить прямоугольник")
        self.shape_menu.addAction(self.add_rectangle_action)
        
        self.add_circle_action = QAction("Circle", self)
        self.add_circle_action.setToolTip("Добавить круг")
        self.shape_menu.addAction(self.add_circle_action)
        
        self.add_line_action = QAction("Line", self)
        self.add_line_action.setToolTip("Добавить линию")
        self.shape_menu.addAction(self.add_line_action)
        
        self.shape_menu_action.setMenu(self.shape_menu)
        
        # Добавить к toolbar
        self.addAction(self.shape_menu_action)
        
        self.addSeparator()
        
        # Add Image
        self.add_image_action = QAction("Add Image", self)
        self.add_image_action.setShortcut(QKeySequence("Ctrl+I"))
        self.add_image_action.setToolTip("Додати зображення (Ctrl+I)")
        self.addAction(self.add_image_action)
        
        self.addSeparator()
        
        # Save
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.setToolTip("Сохранить шаблон (Ctrl+S)")
        self.addAction(self.save_action)
        
        # Load
        self.load_action = QAction("Load", self)
        self.load_action.setShortcut(QKeySequence.Open)
        self.load_action.setToolTip("Загрузить шаблон (Ctrl+O)")
        self.addAction(self.load_action)
        
        self.addSeparator()
        
        # Export ZPL
        self.export_action = QAction("Export ZPL", self)
        self.export_action.setShortcut(QKeySequence("Ctrl+E"))
        self.export_action.setToolTip("Экспорт в ZPL (Ctrl+E)")
        self.addAction(self.export_action)
        
        # Preview
        self.preview_action = QAction("Preview", self)
        self.preview_action.setShortcut(QKeySequence("Ctrl+P"))
        self.preview_action.setToolTip("Предпросмотр (Ctrl+P)")
        self.addAction(self.preview_action)
