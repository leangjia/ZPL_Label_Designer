# -*- coding: utf-8 -*-
"""Script to add Bold/Underline methods to main_window.py"""

# Read main_window.py
with open(r'D:\AiKlientBank\1C_Zebra\gui\main_window.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add shortcuts to _setup_shortcuts()
search_text = "snap_toggle.activated.connect(lambda: self._toggle_snap(0 if self.snap_enabled else 2))"

if search_text in content:
    insert_text = '''
        
        # Font Styles - Bold
        bold_shortcut = QShortcut(QKeySequence("Ctrl+B"), self)
        bold_shortcut.activated.connect(self._toggle_bold)
        
        # Font Styles - Underline
        underline_shortcut = QShortcut(QKeySequence("Ctrl+U"), self)
        underline_shortcut.activated.connect(self._toggle_underline)'''
    
    content = content.replace(search_text, search_text + insert_text)
    print("[OK] Added shortcuts to _setup_shortcuts()")
else:
    print("[ERROR] Could not find snap_toggle line")

# 2. Add methods at the end before closing
new_methods = '''
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
'''

# Find last method end
last_method_marker = 'QMessageBox.critical(self, "Preview", f"Failed to generate preview: {e}")'
last_method_pos = content.rfind(last_method_marker)

if last_method_pos != -1:
    # Find the end of that line
    insert_pos = content.find('\n', last_method_pos) + 1
    
    # Insert methods
    content = content[:insert_pos] + new_methods + content[insert_pos:]
    print("[OK] Added _toggle_bold() and _toggle_underline() methods")
else:
    print("[ERROR] Could not find insertion point")

# Write back
with open(r'D:\AiKlientBank\1C_Zebra\gui\main_window.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("[DONE] main_window.py updated successfully!")
