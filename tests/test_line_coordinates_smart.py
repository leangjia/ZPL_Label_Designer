# -*- coding: utf-8 -*-
"""
УМНЫЙ ТЕСТ: Line Coordinates Smart Test
Проверка правильности координат Line элемента через анализ DEBUG логов
"""

import sys
import re
from pathlib import Path

# Добавить корень проекта в путь
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import logger

class LineLogAnalyzer:
    """Анализатор логов для Line координат"""
    
    @staticmethod
    def parse_line_coords_logs(log_content):
        """Извлечь [LINE-COORDS] логи"""
        # [LINE-COORDS] Element: (10.00, 10.00) -> (30.00, 25.00)mm
        element_pattern = r'\[LINE-COORDS\] Element: \(([\d.]+), ([\d.]+)\) -> \(([\d.]+), ([\d.]+)\)mm'
        # [LINE-COORDS] setPos: (80.00, 80.00)px
        setpos_pattern = r'\[LINE-COORDS\] setPos: \(([\d.]+), ([\d.]+)\)px'
        # [LINE-COORDS] setLine: (0, 0) -> (160.00, 120.00)px
        setline_pattern = r'\[LINE-COORDS\] setLine: \(0, 0\) -> \(([\d.]+), ([\d.]+)\)px'
        
        element_matches = re.findall(element_pattern, log_content)
        setpos_matches = re.findall(setpos_pattern, log_content)
        setline_matches = re.findall(setline_pattern, log_content)
        
        return {
            'element': [(float(m[0]), float(m[1]), float(m[2]), float(m[3])) for m in element_matches],
            'setpos': [(float(m[0]), float(m[1])) for m in setpos_matches],
            'setline': [(float(m[0]), float(m[1])) for m in setline_matches]
        }
    
    @staticmethod
    def parse_line_update_logs(log_content):
        """Извлечь [LINE-UPDATE] логи"""
        element_pattern = r'\[LINE-UPDATE\] Element: \(([\d.]+), ([\d.]+)\) -> \(([\d.]+), ([\d.]+)\)mm'
        setpos_pattern = r'\[LINE-UPDATE\] setPos: \(([\d.]+), ([\d.]+)\)px'
        setline_pattern = r'\[LINE-UPDATE\] setLine: \(0, 0\) -> \(([\d.]+), ([\d.]+)\)px'
        
        element_matches = re.findall(element_pattern, log_content)
        setpos_matches = re.findall(setpos_pattern, log_content)
        setline_matches = re.findall(setline_pattern, log_content)
        
        return {
            'element': [(float(m[0]), float(m[1]), float(m[2]), float(m[3])) for m in element_matches],
            'setpos': [(float(m[0]), float(m[1])) for m in setpos_matches],
            'setline': [(float(m[0]), float(m[1])) for m in setline_matches]
        }
    
    @staticmethod
    def parse_prop_line_logs(log_content):
        """Извлечь [PROP-LINE] логи о изменениях"""
        end_x_pattern = r'\[PROP-LINE\] End X changed: ([\d.]+)mm = ([\d.]+)mm'
        end_y_pattern = r'\[PROP-LINE\] End Y changed: ([\d.]+)mm = ([\d.]+)mm'
        
        end_x_matches = re.findall(end_x_pattern, log_content)
        end_y_matches = re.findall(end_y_pattern, log_content)
        
        return {
            'end_x': [(float(m[0]), float(m[1])) for m in end_x_matches],
            'end_y': [(float(m[0]), float(m[1])) for m in end_y_matches]
        }
    
    @staticmethod
    def detect_issues(coords_logs, update_logs, prop_logs, dpi=203):
        """Детектировать проблемы в координатах Line"""
        issues = []
        
        if not coords_logs['element']:
            return issues
        
        # DPI конверсия константа
        mm_to_px = lambda mm: mm * dpi / 25.4
        
        # ПРОБЛЕМА 1: LINE_COORDS_CALCULATION_ERROR - setLine != (x2-x1, y2-y1)
        if coords_logs['element'] and coords_logs['setline']:
            x1, y1, x2, y2 = coords_logs['element'][-1]
            setline_x, setline_y = coords_logs['setline'][-1]
            
            expected_line_x = mm_to_px(x2 - x1)
            expected_line_y = mm_to_px(y2 - y1)
            
            if abs(setline_x - expected_line_x) > 1.0:  # 1px допуск
                issues.append({
                    'type': 'LINE_COORDS_CALCULATION_ERROR',
                    'desc': f'setLine X={setline_x:.2f}px, expected={(x2-x1):.2f}mm = {expected_line_x:.2f}px'
                })
            
            if abs(setline_y - expected_line_y) > 1.0:
                issues.append({
                    'type': 'LINE_COORDS_CALCULATION_ERROR',
                    'desc': f'setLine Y={setline_y:.2f}px, expected={(y2-y1):.2f}mm = {expected_line_y:.2f}px'
                })
        
        # ПРОБЛЕМА 2: LINE_POS_MISMATCH - setPos != (x1, y1)
        if coords_logs['element'] and coords_logs['setpos']:
            x1, y1, x2, y2 = coords_logs['element'][-1]
            setpos_x, setpos_y = coords_logs['setpos'][-1]
            
            expected_pos_x = mm_to_px(x1)
            expected_pos_y = mm_to_px(y1)
            
            if abs(setpos_x - expected_pos_x) > 1.0:
                issues.append({
                    'type': 'LINE_POS_MISMATCH',
                    'desc': f'setPos X={setpos_x:.2f}px, expected={x1:.2f}mm = {expected_pos_x:.2f}px'
                })
            
            if abs(setpos_y - expected_pos_y) > 1.0:
                issues.append({
                    'type': 'LINE_POS_MISMATCH',
                    'desc': f'setPos Y={setpos_y:.2f}px, expected={y1:.2f}mm = {expected_pos_y:.2f}px'
                })
        
        # ПРОБЛЕМА 3: UPDATE_NOT_APPLIED - после изменения PropertyPanel нет [LINE-UPDATE]
        if prop_logs['end_x'] or prop_logs['end_y']:
            if not update_logs['element']:
                issues.append({
                    'type': 'LINE_UPDATE_NOT_APPLIED',
                    'desc': 'PropertyPanel changed End X/Y but [LINE-UPDATE] logs not found'
                })
        
        # ПРОБЛЕМА 4: UPDATE_CALCULATION_ERROR - update_from_element использует неправильные формулы
        if update_logs['element'] and update_logs['setline']:
            x1, y1, x2, y2 = update_logs['element'][-1]
            setline_x, setline_y = update_logs['setline'][-1]
            
            expected_line_x = mm_to_px(x2 - x1)
            expected_line_y = mm_to_px(y2 - y1)
            
            if abs(setline_x - expected_line_x) > 1.0:
                issues.append({
                    'type': 'UPDATE_CALCULATION_ERROR',
                    'desc': f'update_from_element: setLine X={setline_x:.2f}px, expected={(x2-x1):.2f}mm = {expected_line_x:.2f}px'
                })
            
            if abs(setline_y - expected_line_y) > 1.0:
                issues.append({
                    'type': 'UPDATE_CALCULATION_ERROR',
                    'desc': f'update_from_element: setLine Y={setline_y:.2f}px, expected={(y2-y1):.2f}mm = {expected_line_y:.2f}px'
                })
        
        return issues


def test_line_coordinates_smart():
    """УМНЫЙ ТЕСТ: проверка Line координат через LogAnalyzer"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    # 1. Размер файла логов ДО теста
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # 2. Создать Line элемент
    logger.info("=" * 60)
    logger.info("LINE COORDINATES SMART TEST")
    logger.info("=" * 60)
    logger.info("Step 1: Creating Line element...")
    
    window._add_line()
    app.processEvents()
    
    if not window.elements:
        logger.error("[ERROR] No elements created!")
        return 1
    
    line_element = window.elements[0]
    graphics_item = window.graphics_items[0]
    
    logger.info(f"Line created: from ({line_element.config.x:.2f}, {line_element.config.y:.2f}) to ({line_element.config.x2:.2f}, {line_element.config.y2:.2f})")
    
    # Выбрать элемент
    graphics_item.setSelected(True)
    app.processEvents()
    
    # 3. Изменить End X, End Y
    logger.info("Step 2: Changing End X to 30.0mm...")
    window.property_panel.line_end_x_input.setValue(30.0)
    app.processEvents()
    
    logger.info("Step 3: Changing End Y to 25.0mm...")
    window.property_panel.line_end_y_input.setValue(25.0)
    app.processEvents()
    
    # 4. Читать НОВЫЕ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # 5. Анализировать логи
    analyzer = LineLogAnalyzer()
    coords_logs = analyzer.parse_line_coords_logs(new_logs)
    update_logs = analyzer.parse_line_update_logs(new_logs)
    prop_logs = analyzer.parse_prop_line_logs(new_logs)
    
    logger.info("=" * 60)
    logger.info("LOG ANALYSIS")
    logger.info("=" * 60)
    logger.info(f"[LINE-COORDS] logs found: {len(coords_logs['element'])}")
    logger.info(f"[LINE-UPDATE] logs found: {len(update_logs['element'])}")
    logger.info(f"[PROP-LINE] changes found: End X={len(prop_logs['end_x'])}, End Y={len(prop_logs['end_y'])}")
    
    # 6. Детектировать проблемы
    issues = analyzer.detect_issues(coords_logs, update_logs, prop_logs)
    
    logger.info("=" * 60)
    logger.info("ISSUE DETECTION")
    logger.info("=" * 60)
    
    if issues:
        logger.error(f"DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            logger.error(f"  {issue['type']}: {issue['desc']}")
        logger.info("\n[FAILURE] LINE COORDINATES TEST - ISSUES FOUND")
        return 1
    
    logger.info("[OK] No issues detected")
    logger.info("[OK] Line coordinates are correct")
    
    # 7. Проверить финальные значения
    logger.info("=" * 60)
    logger.info("FINAL VERIFICATION")
    logger.info("=" * 60)
    logger.info(f"Element config: ({line_element.config.x:.2f}, {line_element.config.y:.2f}) -> ({line_element.config.x2:.2f}, {line_element.config.y2:.2f})mm")
    logger.info(f"Expected: (10.00, 10.00) -> (30.00, 25.00)mm")
    
    if abs(line_element.config.x2 - 30.0) > 0.1:
        logger.error(f"[ERROR] End X mismatch: {line_element.config.x2:.2f} != 30.00")
        return 1
    
    if abs(line_element.config.y2 - 25.0) > 0.1:
        logger.error(f"[ERROR] End Y mismatch: {line_element.config.y2:.2f} != 25.00")
        return 1
    
    logger.info("[OK] Final values match")
    
    logger.info("=" * 60)
    logger.info("[SUCCESS] LINE COORDINATES SMART TEST PASSED")
    logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit_code = test_line_coordinates_smart()
    sys.exit(exit_code)
