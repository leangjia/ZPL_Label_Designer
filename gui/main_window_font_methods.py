# Temporary file with new methods - to be merged into main_window.py

def _toggle_bold(self):
    """Toggle Bold для selected element"""
    if self.selected_item and hasattr(self.selected_item, 'element'):
        element = self.selected_item.element
        
        if hasattr(element, 'bold'):
            element.bold = not element.bold
            
            # Оновити графічний item
            if hasattr(self.selected_item, 'update_display'):
                self.selected_item.update_display()
            
            # Оновити PropertyPanel checkbox
            if self.property_panel.current_element == element:
                self.property_panel.bold_checkbox.blockSignals(True)
                self.property_panel.bold_checkbox.setChecked(element.bold)
                self.property_panel.bold_checkbox.blockSignals(False)
            
            logger.debug(f"[SHORTCUT] Bold toggled: {element.bold}")

def _toggle_underline(self):
    """Toggle Underline для selected element"""
    if self.selected_item and hasattr(self.selected_item, 'element'):
        element = self.selected_item.element
        
        if hasattr(element, 'underline'):
            element.underline = not element.underline
            
            # Оновити графічний item
            if hasattr(self.selected_item, 'update_display'):
                self.selected_item.update_display()
            
            # Оновити PropertyPanel checkbox
            if self.property_panel.current_element == element:
                self.property_panel.underline_checkbox.blockSignals(True)
                self.property_panel.underline_checkbox.setChecked(element.underline)
                self.property_panel.underline_checkbox.blockSignals(False)
            
            logger.debug(f"[SHORTCUT] Underline toggled: {element.underline}")

# Shortcuts to add in _setup_shortcuts():
#
# # Font Styles - Bold
# bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
# bold_shortcut.activated.connect(self._toggle_bold)
# 
# # Font Styles - Underline
# underline_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
# underline_shortcut.activated.connect(self._toggle_underline)
