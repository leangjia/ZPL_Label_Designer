# -*- coding: utf-8 -*-
"""Smoke test після рефакторингу MainWindow"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger


def test_refactoring_smoke():
    """Smoke test: MainWindow створюється без помилок"""
    
    logger.info("=" * 60)
    logger.info("REFACTORING SMOKE TEST")
    logger.info("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        # Створити MainWindow
        logger.info("Creating MainWindow with mixins...")
        window = MainWindow()
        
        # Перевірити що все на місці
        assert hasattr(window, 'canvas'), "Canvas missing!"
        assert hasattr(window, 'toolbar'), "Toolbar missing!"
        assert hasattr(window, 'property_panel'), "Property panel missing!"
        assert hasattr(window, 'h_ruler'), "Horizontal ruler missing!"
        assert hasattr(window, 'v_ruler'), "Vertical ruler missing!"
        
        logger.info("[OK] All components present")
        
        # Перевірити mixins методи
        assert hasattr(window, '_add_text'), "_add_text method missing!"
        assert hasattr(window, '_save_template'), "_save_template method missing!"
        assert hasattr(window, '_copy_selected'), "_copy_selected method missing!"
        assert hasattr(window, '_setup_shortcuts'), "_setup_shortcuts method missing!"
        assert hasattr(window, '_on_selection_changed'), "_on_selection_changed method missing!"
        assert hasattr(window, '_create_label_size_controls'), "_create_label_size_controls method missing!"
        assert hasattr(window, '_undo'), "_undo method missing!"
        
        logger.info("[OK] All mixin methods present")
        
        # Test добавления элемента
        logger.info("Testing element creation...")
        initial_count = len(window.elements)
        window._add_text()
        app.processEvents()
        
        assert len(window.elements) == initial_count + 1, "Element not added!"
        logger.info("[OK] Element creation works")
        
        # Test _on_selection_changed
        logger.info("Testing selection...")
        window.canvas.scene.clearSelection()
        app.processEvents()
        assert window.selected_item is None, "Selection should be None!"
        logger.info("[OK] Selection works")
        
        logger.info("=" * 60)
        logger.info("[SUCCESS] REFACTORING SMOKE TEST PASSED")
        logger.info("=" * 60)
        
        return 0
        
    except Exception as e:
        logger.error(f"[ERROR] Smoke test failed: {e}", exc_info=True)
        logger.info("=" * 60)
        logger.info("[FAILURE] REFACTORING SMOKE TEST FAILED")
        logger.info("=" * 60)
        return 1


if __name__ == '__main__':
    sys.exit(test_refactoring_smoke())
