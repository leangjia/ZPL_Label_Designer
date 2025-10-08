# -*- coding: utf-8 -*-
"""
Тест Line Element End Position - проверка управления конечной точкой линии
"""

import sys
from pathlib import Path

# Добавить корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger

def test_line_end_position():
    """Проверка End Position полей для Line элемента"""
    
    logger.info("=" * 60)
    logger.info("TEST: Line End Position")
    logger.info("=" * 60)
    
    # 1. Создать приложение
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # 2. Добавить Line элемент
    logger.info("Adding Line element...")
    window._add_line()
    app.processEvents()
    
    # 3. Выбрать Line
    if not window.elements:
        logger.error("[ERROR] No elements created!")
        return 1
    
    line_element = window.elements[0]
    graphics_item = window.graphics_items[0]
    
    logger.info(f"Line created: from ({line_element.config.x:.2f}, {line_element.config.y:.2f}) to ({line_element.config.x2:.2f}, {line_element.config.y2:.2f})")
    
    # Выбрать элемент
    graphics_item.setSelected(True)
    app.processEvents()
    
    # 4. Проверить PropertyPanel
    property_panel = window.property_panel
    
    if not property_panel.isEnabled():
        logger.error("[ERROR] PropertyPanel not enabled!")
        return 1
    
    if not property_panel.shape_group.isVisible():
        logger.error("[ERROR] Shape Properties not visible!")
        return 1
    
    # 5. Проверить видимость End X, End Y
    if not property_panel.line_end_x_input.isVisible():
        logger.error("[ERROR] End X input not visible!")
        return 1
    
    if not property_panel.line_end_y_input.isVisible():
        logger.error("[ERROR] End Y input not visible!")
        return 1
    
    logger.info("[OK] End X, End Y inputs visible")
    
    # 6. Проверить значения
    end_x_value = property_panel.line_end_x_input.value()
    end_y_value = property_panel.line_end_y_input.value()
    
    logger.info(f"PropertyPanel End X: {end_x_value:.2f}mm, End Y: {end_y_value:.2f}mm")
    logger.info(f"Element config x2: {line_element.config.x2:.2f}mm, y2: {line_element.config.y2:.2f}mm")
    
    if abs(end_x_value - line_element.config.x2) > 0.1:
        logger.error(f"[ERROR] End X mismatch: panel={end_x_value:.2f}, element={line_element.config.x2:.2f}")
        return 1
    
    if abs(end_y_value - line_element.config.y2) > 0.1:
        logger.error(f"[ERROR] End Y mismatch: panel={end_y_value:.2f}, element={line_element.config.y2:.2f}")
        return 1
    
    logger.info("[OK] End position values match")
    
    # 7. Изменить End X
    logger.info("Changing End X to 30.0mm...")
    property_panel.line_end_x_input.setValue(30.0)
    app.processEvents()
    
    if abs(line_element.config.x2 - 30.0) > 0.1:
        logger.error(f"[ERROR] End X not updated: {line_element.config.x2:.2f}")
        return 1
    
    logger.info(f"[OK] End X updated: {line_element.config.x2:.2f}mm")
    
    # 8. Изменить End Y
    logger.info("Changing End Y to 25.0mm...")
    property_panel.line_end_y_input.setValue(25.0)
    app.processEvents()
    
    if abs(line_element.config.y2 - 25.0) > 0.1:
        logger.error(f"[ERROR] End Y not updated: {line_element.config.y2:.2f}")
        return 1
    
    logger.info(f"[OK] End Y updated: {line_element.config.y2:.2f}mm")
    
    # 9. Проверить что Width/Height/Fill скрыты
    if property_panel.shape_width_input.isVisible():
        logger.error("[ERROR] Width input should be hidden for Line!")
        return 1
    
    if property_panel.shape_height_input.isVisible():
        logger.error("[ERROR] Height input should be hidden for Line!")
        return 1
    
    if property_panel.shape_fill_input.isVisible():
        logger.error("[ERROR] Fill checkbox should be hidden for Line!")
        return 1
    
    logger.info("[OK] Width/Height/Fill hidden for Line")
    
    # 10. Финал
    logger.info("=" * 60)
    logger.info("[SUCCESS] All tests passed!")
    logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit_code = test_line_end_position()
    sys.exit(exit_code)
