# -*- coding: utf-8 -*-
"""Панель инструментов"""

from PySide6.QtWidgets import QToolBar


class EditorToolbar(QToolBar):
    """Панель инструментов редактора"""

    def __init__(self, actions, menus, parent=None):
        super().__init__("Tools", parent)

        self.actions = actions
        self.menus = menus

        # Add Text
        self.add_text_action = self.actions['add_text']
        self.addAction(self.add_text_action)

        self.addSeparator()

        # Add Barcode menu
        self.barcode_menu_action = self.actions['barcode_menu']
        self.barcode_menu = self.menus['barcode']
        self.barcode_menu_action.setMenu(self.barcode_menu)

        # Добавить к toolbar
        self.addAction(self.barcode_menu_action)

        self.addSeparator()

        # Add Shape menu
        self.shape_menu_action = self.actions['shape_menu']
        self.shape_menu = self.menus['shape']
        self.shape_menu_action.setMenu(self.shape_menu)

        # Добавить к toolbar
        self.addAction(self.shape_menu_action)

        self.addSeparator()

        # Add Image
        self.add_image_action = self.actions['add_image']
        self.addAction(self.add_image_action)

        self.addSeparator()

        # Save
        self.save_action = self.actions['save']
        self.addAction(self.save_action)

        # Load
        self.load_action = self.actions['load']
        self.addAction(self.load_action)

        self.addSeparator()

        # Export ZPL
        self.export_action = self.actions['export']
        self.addAction(self.export_action)

        # Preview
        self.preview_action = self.actions['preview']
        self.addAction(self.preview_action)
