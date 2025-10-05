# -*- coding: utf-8 -*-
"""Умний тест для ЕТАП 13: Label Size з LogAnalyzer"""

import sys
import re
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF

# Додати project root до sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow


class LabelSizeLogAnalyzer:
    """Аналізатор логів для Label Size functionality"""
    
    @staticmethod
    def parse_label_size_logs(log_content):
        """Парсити [LABEL-SIZE] логи"""
        pattern = r'\[LABEL-SIZE\] (Before|Request|Width|Height|After): (.+)'
        matches = re.findall(pattern, log_content)
        
        logs = {}
        for stage, data in matches:
            logs[stage] = data.strip()
        
        return logs
    
    @staticmethod
    def parse_size_apply_logs(log_content):
        """Парсити [SIZE-APPLY] логи"""
        pattern = r'\[SIZE-APPLY\] (User request|No change|Label size updated): (.+)'
        matches = re.findall(pattern, log_content)
        
        logs = {}
        for stage, data in matches:
            logs[stage] = data.strip()
        
        return logs
    
    @staticmethod
    def parse_ruler_logs(log_content):
        """Парсити [RULER-H/V] set_length логи"""
        h_pattern = r'\[RULER-H\] set_length: ([\d.]+)mm -> ([\d.]+)mm'
        v_pattern = r'\[RULER-V\] set_length: ([\d.]+)mm -> ([\d.]+)mm'
        
        h_matches = re.findall(h_pattern, log_content)
        v_matches = re.findall(v_pattern, log_content)
        
        return {
            'horizontal': [(float(m[0]), float(m[1])) for m in h_matches],
            'vertical': [(float(m[0]), float(m[1])) for m in v_matches]
        }
    
    @staticmethod
    def parse_template_load_logs(log_content):
        """Парсити [LOAD-TEMPLATE] логи"""
        pattern = r'\[LOAD-TEMPLATE\] (.+): (.+)'
        matches = re.findall(pattern, log_content)
        
        logs = {}
        for key, value in matches:
            logs[key] = value.strip()
        
        return logs
    
    @staticmethod
    def detect_issues(label_logs, apply_logs, ruler_logs, canvas_size, spinbox_values):
        """Детектувати 5 типів проблем"""
        issues = []
        
        # 1. CANVAS_SIZE_MISMATCH - canvas розмір != запит
        if 'Request' in label_logs:
            requested = label_logs['Request']
            # Parse "50.0x40.0mm"
            match = re.match(r'([\d.]+)x([\d.]+)mm', requested)
            if match:
                req_w, req_h = float(match.group(1)), float(match.group(2))
                canvas_w, canvas_h = canvas_size
                
                if abs(req_w - canvas_w) > 0.1 or abs(req_h - canvas_h) > 0.1:
                    issues.append({
                        'type': 'CANVAS_SIZE_MISMATCH',
                        'desc': f'Request: {req_w}x{req_h}mm, Canvas: {canvas_w}x{canvas_h}mm'
                    })
        
        # 2. RULER_LENGTH_MISMATCH - ruler length != canvas size
        if ruler_logs['horizontal']:
            h_new = ruler_logs['horizontal'][-1][1]  # Останнє значення
            if abs(h_new - canvas_size[0]) > 0.1:
                issues.append({
                    'type': 'RULER_LENGTH_MISMATCH_H',
                    'desc': f'Ruler H: {h_new}mm, Canvas W: {canvas_size[0]}mm'
                })
        
        if ruler_logs['vertical']:
            v_new = ruler_logs['vertical'][-1][1]
            if abs(v_new - canvas_size[1]) > 0.1:
                issues.append({
                    'type': 'RULER_LENGTH_MISMATCH_V',
                    'desc': f'Ruler V: {v_new}mm, Canvas H: {canvas_size[1]}mm'
                })
        
        # 3. SPINBOX_VALUE_INCORRECT - spinbox != canvas
        spinbox_w, spinbox_h = spinbox_values
        if abs(spinbox_w - canvas_size[0]) > 0.1:
            issues.append({
                'type': 'SPINBOX_WIDTH_INCORRECT',
                'desc': f'Spinbox: {spinbox_w}mm, Canvas: {canvas_size[0]}mm'
            })
        
        if abs(spinbox_h - canvas_size[1]) > 0.1:
            issues.append({
                'type': 'SPINBOX_HEIGHT_INCORRECT',
                'desc': f'Spinbox: {spinbox_h}mm, Canvas: {canvas_size[1]}mm'
            })
        
        # 4. SIZE_CONVERSION_ERROR - перевірка mm_to_px формули
        if 'Width' in label_logs:
            # Parse "50.0mm = 397px"
            width_log = label_logs['Width']
            match = re.match(r'([\d.]+)mm = ([\d]+)px', width_log)
            if match:
                mm_val = float(match.group(1))
                px_val = int(match.group(2))
                
                # Formula: px = mm * 203 / 25.4
                expected_px = int(mm_val * 203 / 25.4)
                
                if abs(px_val - expected_px) > 2:  # 2px tolerance
                    issues.append({
                        'type': 'SIZE_CONVERSION_ERROR_WIDTH',
                        'desc': f'Width: {mm_val}mm -> {px_val}px, expected {expected_px}px'
                    })
        
        if 'Height' in label_logs:
            height_log = label_logs['Height']
            match = re.match(r'([\d.]+)mm = ([\d]+)px', height_log)
            if match:
                mm_val = float(match.group(1))
                px_val = int(match.group(2))
                expected_px = int(mm_val * 203 / 25.4)
                
                if abs(px_val - expected_px) > 2:
                    issues.append({
                        'type': 'SIZE_CONVERSION_ERROR_HEIGHT',
                        'desc': f'Height: {mm_val}mm -> {px_val}px, expected {expected_px}px'
                    })
        
        return issues


def test_label_size_smart():
    """Умний тест Label Size з LogAnalyzer"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    # Розмір файлу логів ДО тесту
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    # Створити застосунок
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("="*60)
    print("[LABEL-SIZE SMART TEST]")
    print("="*60)
    
    # TEST 1: Змінити розмір через GUI
    print("\n[TEST 1] Change size via spinboxes: 50x40mm")
    window.width_spinbox.setValue(50.0)
    window.height_spinbox.setValue(40.0)
    app.processEvents()
    
    # Прямий виклик _apply_label_size
    window._apply_label_size()
    app.processEvents()
    
    # Зчитати НОВІ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Парсити логи
    analyzer = LabelSizeLogAnalyzer()
    label_logs = analyzer.parse_label_size_logs(new_logs)
    apply_logs = analyzer.parse_size_apply_logs(new_logs)
    ruler_logs = analyzer.parse_ruler_logs(new_logs)
    
    # Отримати поточний стан
    canvas_size = (window.canvas.width_mm, window.canvas.height_mm)
    spinbox_values = (window.width_spinbox.value(), window.height_spinbox.value())
    
    print(f"\n[CANVAS] Size: {canvas_size[0]}x{canvas_size[1]}mm")
    print(f"[SPINBOX] Values: W={spinbox_values[0]}, H={spinbox_values[1]}")
    print(f"[RULER-H] Length: {window.h_ruler.length_mm}mm")
    print(f"[RULER-V] Length: {window.v_ruler.length_mm}mm")
    
    # Детектувати проблеми
    issues = analyzer.detect_issues(label_logs, apply_logs, ruler_logs, canvas_size, spinbox_values)
    
    # Вивід результатів
    print("\n" + "="*60)
    print("[LOG ANALYSIS RESULTS]")
    print("="*60)
    print(f"Label Size logs: {len(label_logs)} entries")
    print(f"Size Apply logs: {len(apply_logs)} entries")
    print(f"Ruler logs: H={len(ruler_logs['horizontal'])}, V={len(ruler_logs['vertical'])}")
    
    if issues:
        print(f"\n[FAILURE] DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        return 1
    else:
        print("\n[OK] Label Size functionality works correctly")
        return 0


if __name__ == '__main__':
    exit_code = test_label_size_smart()
    print(f"\n[EXIT CODE] {exit_code}")
    sys.exit(exit_code)
