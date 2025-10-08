# -*- coding: utf-8 -*-
"""Умный тест логики Circle <-> Ellipse с анализом логов"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.elements.shape_element import CircleElement
from utils.logger import logger
import re


class CircleLogAnalyzer:
    """Анализатор логов Circle element"""
    
    @staticmethod
    def parse_circle_logs(log_content):
        """Парсить логи изменения Circle"""
        # [CIRCLE] Set diameter: 15.00mm
        diameter_logs = re.findall(r'\[CIRCLE\] Set diameter: ([\d.]+)mm', log_content)
        
        # [CIRCLE] After diameter set: w=15.00, h=15.00, is_circle=True
        after_logs = re.findall(
            r'\[CIRCLE\] After diameter set: w=([\d.]+), h=([\d.]+), is_circle=(True|False)',
            log_content
        )
        
        # [CIRCLE] Set width: 20.00mm
        width_logs = re.findall(r'\[CIRCLE\] Set width: ([\d.]+)mm', log_content)
        
        # [CIRCLE] Set height: 20.00mm
        height_logs = re.findall(r'\[CIRCLE\] Set height: ([\d.]+)mm', log_content)
        
        # [CIRCLE] Shape change: True -> False
        shape_change_logs = re.findall(r'\[CIRCLE\] Shape change: (True|False) -> (True|False)', log_content)
        
        return {
            'diameter': [float(x) for x in diameter_logs],
            'after_diameter': [
                {'w': float(m[0]), 'h': float(m[1]), 'is_circle': m[2] == 'True'}
                for m in after_logs
            ],
            'width': [float(x) for x in width_logs],
            'height': [float(x) for x in height_logs],
            'shape_changes': [{'from': m[0] == 'True', 'to': m[1] == 'True'} for m in shape_change_logs]
        }
    
    @staticmethod
    def detect_issues(logs_dict, circle):
        """Детектировать проблемы в логике"""
        issues = []
        
        # 1. DIAMETER SET: width != height после установки diameter
        if logs_dict['after_diameter']:
            last = logs_dict['after_diameter'][-1]
            if abs(last['w'] - last['h']) > 0.1:
                issues.append({
                    'type': 'DIAMETER_NOT_SYNCED',
                    'desc': f"После diameter={last['w']}, width={last['w']} но height={last['h']}"
                })
        
        # 2. SHAPE CHANGE: финальный is_circle НЕ соответствует последнему shape change
        if logs_dict['shape_changes']:
            # Проверяем ПОСЛЕДНИЙ shape change
            last_sc = logs_dict['shape_changes'][-1]
            expected_final = last_sc['to']  # Последнее состояние из логов
            actual_final = circle.is_circle
            
            if expected_final != actual_final:
                issues.append({
                    'type': 'SHAPE_CHANGE_NOT_APPLIED',
                    'desc': f"Последний shape change показал is_circle={expected_final}, но финал is_circle={actual_final}"
                })
        
        # 3. IS_CIRCLE: property НЕ соответствует width/height
        expected_is_circle = abs(circle.config.width - circle.config.height) < 0.1
        if circle.is_circle != expected_is_circle:
            issues.append({
                'type': 'IS_CIRCLE_MISMATCH',
                'desc': f"is_circle={circle.is_circle}, но w={circle.config.width}, h={circle.config.height}"
            })
        
        return issues


def test_circle_ellipse_logic():
    """Умный тест логики Circle <-> Ellipse с анализом логов"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    # Размер логов ДО теста
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    print("=" * 60)
    print("[TEST] Starting Circle <-> Ellipse logic test")
    print("=" * 60)
    
    # ТЕСТ 1: Создать Circle через diameter
    print("\n[TEST 1] Create Circle with diameter=15.0mm")
    circle = CircleElement()
    circle.diameter = 15.0
    print(f"  Result: width={circle.config.width:.2f}mm, height={circle.config.height:.2f}mm, is_circle={circle.is_circle}")
    
    # ТЕСТ 2: Изменить width -> должен стать Ellipse
    print("\n[TEST 2] Change width to 20.0mm (should become Ellipse)")
    circle.set_width(20.0)
    print(f"  Result: width={circle.config.width:.2f}mm, height={circle.config.height:.2f}mm, is_circle={circle.is_circle}")
    
    # ТЕСТ 3: Вернуть height=width -> должен стать Circle
    print("\n[TEST 3] Change height to 20.0mm (should become Circle again)")
    circle.set_height(20.0)
    print(f"  Result: width={circle.config.width:.2f}mm, height={circle.config.height:.2f}mm, is_circle={circle.is_circle}")
    
    # Читать НОВЫЕ логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализировать логи
    analyzer = CircleLogAnalyzer()
    logs = analyzer.parse_circle_logs(new_logs)
    issues = analyzer.detect_issues(logs, circle)
    
    # Вывод результатов
    print("\n" + "=" * 60)
    print("[CIRCLE <-> ELLIPSE] LOG ANALYSIS")
    print("=" * 60)
    print(f"Diameter set logs: {len(logs['diameter'])}")
    print(f"Width change logs: {len(logs['width'])}")
    print(f"Height change logs: {len(logs['height'])}")
    print(f"Shape changes: {len(logs['shape_changes'])}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] CIRCLE LOGIC HAS ISSUES")
        return 1
    
    print("\n[OK] Circle <-> Ellipse logic works correctly")
    
    # Финальная проверка состояния
    print(f"\nFinal state:")
    print(f"  width={circle.config.width:.2f}mm, height={circle.config.height:.2f}mm")
    print(f"  is_circle={circle.is_circle}")
    print(f"  diameter={circle.diameter if circle.diameter else 'N/A'}")
    
    assert circle.is_circle == True, "Expected Circle after height=width"
    assert abs(circle.config.width - 20.0) < 0.01, f"Expected width=20.0, got {circle.config.width}"
    
    return 0


if __name__ == "__main__":
    exit(test_circle_ellipse_logic())
