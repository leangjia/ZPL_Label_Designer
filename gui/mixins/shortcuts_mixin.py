# -*- coding: utf-8 -*-
"""Mixin для keyboard shortcuts"""

from PySide6.QtWidgets import QCheckBox
from PySide6.QtGui import QShortcut, QKeySequence
from PySide6.QtCore import Qt
from utils.logger import logger


class ShortcutsMixin:
    """Keyboard shortcuts setup and handlers"""
    
    def _setup_shortcuts(self):
        """Keyboard shortcuts"""
        # Zoom in
        zoom_in = QShortcut(QKeySequence("Ctrl++"), self)
        zoom_in.activated.connect(self.canvas.zoom_in)
        
        # Zoom in (альтернативна клавіша)
        zoom_in2 = QShortcut(QKeySequence("Ctrl+="), self)
        zoom_in2.activated.connect(self.canvas.zoom_in)
        
        # Zoom out
        zoom_out = QShortcut(QKeySequence("Ctrl+-"), self)
        zoom_out.activated.connect(self.canvas.zoom_out)
        
        # Reset zoom
        zoom_reset = QShortcut(QKeySequence("Ctrl+0"), self)
        zoom_reset.activated.connect(self.canvas.reset_zoom)
        
        # Snap toggle
        snap_toggle = QShortcut(QKeySequence("Ctrl+G"), self)
        snap_toggle.activated.connect(lambda: self._toggle_snap(0 if self.snap_enabled else 2))
        
        # Font Styles - Bold
        bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_shortcut.activated.connect(self._toggle_bold)
        
        # Font Styles - Underline
        underline_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        underline_shortcut.activated.connect(self._toggle_underline)
        
        # Bold toggle
        bold_toggle = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_toggle.activated.connect(self._toggle_bold)
        
        # Underline toggle
        underline_toggle = QShortcut(QKeySequence("Ctrl+U"), self)
        underline_toggle.activated.connect(self._toggle_underline)
        
        logger.debug("Zoom shortcuts: Ctrl+Plus, Ctrl+Minus, Ctrl+0")
        logger.debug("Snap shortcut: Ctrl+G")
    
    def _toggle_guides(self, state):
        """Перемикач smart guides"""
        self.guides_enabled = (state == 2)
        self.smart_guides.set_enabled(self.guides_enabled)
        logger.debug(f"[GUIDES-TOGGLE] Enabled: {self.guides_enabled}")
    
    def _create_snap_toggle(self):
        """Створити toggle для snap to grid"""
        snap_checkbox = QCheckBox("Snap to Grid")
        snap_checkbox.setChecked(True)
        snap_checkbox.stateChanged.connect(self._toggle_snap)
        
        # Додати до toolbar
        self.toolbar.addSeparator()
        self.toolbar.addWidget(snap_checkbox)
        
        # Smart Guides checkbox
        guides_checkbox = QCheckBox("Smart Guides")
        guides_checkbox.setChecked(True)
        guides_checkbox.stateChanged.connect(self._toggle_guides)
        self.toolbar.addWidget(guides_checkbox)
        
        logger.info("Snap to Grid and Smart Guides toggles created")
        
        # КРИТИЧНО: викликати _toggle_snap щоб встановити snap для існуючих елементів
        self._toggle_snap(2)  # 2 = Qt.Checked
    
    def _toggle_snap(self, state):
        """Увімкнути/вимкнути snap"""
        # state це int: 0=Unchecked, 2=Checked
        self.snap_enabled = (state == 2)  # Qt.Checked = 2
        
        # Оновити всі елементи
        for item in self.graphics_items:
            if hasattr(item, 'snap_enabled'):
                item.snap_enabled = self.snap_enabled
        
        logger.info(f"Snap to Grid: {'ON' if self.snap_enabled else 'OFF'} (items: {len(self.graphics_items)})")
    
    def _toggle_bold(self):
        """Включить/выключить Bold для selected element"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            element = self.selected_item.element
            
            if hasattr(element, 'bold'):
                element.bold = not element.bold
                
                # Обновить графический item
                if hasattr(self.selected_item, 'update_display'):
                    self.selected_item.update_display()
                
                # Обновить PropertyPanel checkbox
                if self.property_panel.current_element == element:
                    self.property_panel.bold_checkbox.blockSignals(True)
                    self.property_panel.bold_checkbox.setChecked(element.bold)
                    self.property_panel.bold_checkbox.blockSignals(False)
                
                logger.debug(f"[SHORTCUT] Bold toggled: {element.bold}")
    
    def _toggle_underline(self):
        """Включить/выключить Underline для selected element"""
        if self.selected_item and hasattr(self.selected_item, 'element'):
            element = self.selected_item.element
            
            if hasattr(element, 'underline'):
                element.underline = not element.underline
                
                # Обновить графический item
                if hasattr(self.selected_item, 'update_display'):
                    self.selected_item.update_display()
                
                # Обновить PropertyPanel checkbox
                if self.property_panel.current_element == element:
                    self.property_panel.underline_checkbox.blockSignals(True)
                    self.property_panel.underline_checkbox.setChecked(element.underline)
                    self.property_panel.underline_checkbox.blockSignals(False)
                
                logger.debug(f"[SHORTCUT] Underline toggled: {element.underline}")
    
    def keyPressEvent(self, event):
        """Keyboard shortcuts"""
        modifiers = event.modifiers()
        key = event.key()
        
        # === ZOOM ===
        if modifiers == Qt.ControlModifier:
            if key in (Qt.Key_Plus, Qt.Key_Equal):
                logger.debug("[SHORTCUT] Ctrl+Plus - Zoom In")
                self.canvas.zoom_in()
            elif key == Qt.Key_Minus:
                logger.debug("[SHORTCUT] Ctrl+Minus - Zoom Out")
                self.canvas.zoom_out()
            elif key == Qt.Key_0:
                logger.debug("[SHORTCUT] Ctrl+0 - Reset Zoom")
                self.canvas.reset_zoom()
            # === SNAP ===
            elif key == Qt.Key_G:
                logger.debug("[SHORTCUT] Ctrl+G - Toggle Snap")
                self.snap_enabled = not self.snap_enabled
                self._toggle_snap(Qt.Checked if self.snap_enabled else Qt.Unchecked)
            # === CLIPBOARD ===
            elif key == Qt.Key_C:
                logger.debug("[SHORTCUT] Ctrl+C - Copy")
                self._copy_selected()
            elif key == Qt.Key_V:
                logger.debug("[SHORTCUT] Ctrl+V - Paste")
                self._paste_from_clipboard()
            elif key == Qt.Key_D:
                logger.debug("[SHORTCUT] Ctrl+D - Duplicate")
                self._duplicate_selected()
            # === UNDO/REDO ===
            elif key == Qt.Key_Z:
                logger.debug("[SHORTCUT] Ctrl+Z - Undo")
                self._undo()
            elif key == Qt.Key_Y:
                logger.debug("[SHORTCUT] Ctrl+Y - Redo")
                self._redo()
        
        # === DELETE ===
        elif key in (Qt.Key_Delete, Qt.Key_Backspace):
            logger.debug(f"[SHORTCUT] {event.key()} - Delete Element")
            self._delete_selected()
        
        # === PRECISION MOVE (Shift + Arrow) ===
        elif modifiers == Qt.ShiftModifier:
            if key == Qt.Key_Left:
                logger.debug("[SHORTCUT] Shift+Left - Move -0.1mm")
                self._move_selected(-0.1, 0)
            elif key == Qt.Key_Right:
                logger.debug("[SHORTCUT] Shift+Right - Move +0.1mm")
                self._move_selected(0.1, 0)
            elif key == Qt.Key_Up:
                logger.debug("[SHORTCUT] Shift+Up - Move -0.1mm")
                self._move_selected(0, -0.1)
            elif key == Qt.Key_Down:
                logger.debug("[SHORTCUT] Shift+Down - Move +0.1mm")
                self._move_selected(0, 0.1)
        
        # === NORMAL MOVE (Arrow) ===
        elif modifiers == Qt.NoModifier:
            if key == Qt.Key_Left:
                logger.debug("[SHORTCUT] Left - Move -1mm")
                self._move_selected(-1, 0)
            elif key == Qt.Key_Right:
                logger.debug("[SHORTCUT] Right - Move +1mm")
                self._move_selected(1, 0)
            elif key == Qt.Key_Up:
                logger.debug("[SHORTCUT] Up - Move -1mm")
                self._move_selected(0, -1)
            elif key == Qt.Key_Down:
                logger.debug("[SHORTCUT] Down - Move +1mm")
                self._move_selected(0, 1)
        
        super().keyPressEvent(event)
