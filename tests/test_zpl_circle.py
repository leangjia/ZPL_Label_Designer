# -*- coding: utf-8 -*-
"""Умный тест ZPL генерации для Circle/Ellipse"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.elements.shape_element import CircleElement
from zpl.generator import ZPLGenerator
from utils.logger import logger
import re


class ZPLCircleAnalyzer:
    """Анализатор логов ZPL генерации"""
    
    @staticmethod
    def parse_zpl_logs(log_content):
        """Парсить логи ZPL генерации"""
        # [ZPL-CIRCLE] Circle: diameter=10.00mm → 80dots
        circle_logs = re.findall(
            r'\[ZPL-CIRCLE\] Circle: diameter=([\d.]+)mm → ([\d]+)dots',
            log_content
        )
        
        # [ZPL-CIRCLE] Ellipse: w=15.00mm, h=10.00mm → 118x80dots
        ellipse_logs = re.findall(
            r'\[ZPL-CIRCLE\] Ellipse: w=([\d.]+)mm, h=([\d.]+)mm → ([\d]+)x([\d]+)dots',
            log_content
        )
        
        # [ZPL-CIRCLE] Generated Circle: ^FO0,0^GC80,8,B^FS
        generated_circle = re.findall(
            r'\[ZPL-CIRCLE\] Generated Circle: (.+)',
            log_content
        )
        
        # [ZPL-CIRCLE] Generated Ellipse: ^FO0,0^GE118,80,8,B^FS
        generated_ellipse = re.findall(
            r'\[ZPL-CIRCLE\] Generated Ellipse: (.+)',
            log_content
        )
        
        return {
            'circle': [{'diameter_mm': float(m[0]), 'diameter_dots': int(m[1])} for m in circle_logs],
            'ellipse': [{'w_mm': float(m[0]), 'h_mm': float(m[1]), 'w_dots': int(m[2]), 'h_dots': int(m[3])} for m in ellipse_logs],
            'generated_circle': generated_circle,
            'generated_ellipse': generated_ellipse
        }
    
    @staticmethod
    def detect_issues(logs_dict):
        """Детектировать проблемы в ZPL"""
        issues = []
        
        # 1. CIRCLE: должна быть команда ^GC
        if logs_dict['circle']:
            if not any('^GC' in z for z in logs_dict['generated_circle']):
                issues.append({
                    'type': 'CIRCLE_NO_GC_COMMAND',
                    'desc': f"Circle log есть, но ^GC команда НЕ сгенерирована"
                })
            
            # Проверка dots conversion (203 DPI)
            expected_dots = int(logs_dict['circle'][-1]['diameter_mm'] * 203 / 25.4)
            actual_dots = logs_dict['circle'][-1]['diameter_dots']
            if abs(expected_dots - actual_dots) > 2:
                issues.append({
                    'type': 'CIRCLE_DOTS_CONVERSION_WRONG',
                    'desc': f"Expected {expected_dots}dots, got {actual_dots}dots"
                })
        
        # 2. ELLIPSE: должна быть команда ^GE
        if logs_dict['ellipse']:
            if not any('^GE' in z for z in logs_dict['generated_ellipse']):
                issues.append({
                    'type': 'ELLIPSE_NO_GE_COMMAND',
                    'desc': f"Ellipse log есть, но ^GE команда НЕ сгенерирована"
                })
        
        # 3. ZPL SYNTAX: проверка формата команды
        for zpl_cmd in logs_dict['generated_circle']:
            if not re.match(r'\^FO\d+,\d+\^GC\d+,\d+,[BW]\^FS', zpl_cmd):
                issues.append({
                    'type': 'CIRCLE_ZPL_SYNTAX_WRONG',
                    'desc': f"Неправильный формат: {zpl_cmd}"
                })
        
        for zpl_cmd in logs_dict['generated_ellipse']:
            if not re.match(r'\^FO\d+,\d+\^GE\d+,\d+,\d+,[BW]\^FS', zpl_cmd):
                issues.append({
                    'type': 'ELLIPSE_ZPL_SYNTAX_WRONG',
                    'desc': f"Неправильный формат: {zpl_cmd}"
                })
        
        return issues


def test_zpl_circle():
    """Умный тест ZPL генерации для Circle/Ellipse"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    generator = ZPLGenerator(dpi=203)
    
    print("=" * 60)
    print("[TEST] ZPL Circle/Ellipse Generation")
    print("=" * 60)
    
    # Label config
    label_config = {
        'width': 28.0,
        'height': 28.0,
        'dpi': 203
    }
    
    # ТЕСТ 1: Circle
    print("\n[TEST 1] Generate ZPL for Circle (diameter=10.0mm)")
    circle = CircleElement()
    circle.config.x = 0.0
    circle.config.y = 0.0
    circle.diameter = 10.0
    circle.config.border_thickness = 1.0
    circle.config.fill = True
    
    zpl_circle = generator.generate([circle], label_config)
    print(f"  Generated: {zpl_circle}")
    
    # ТЕСТ 2: Ellipse
    print("\n[TEST 2] Generate ZPL for Ellipse (width=15.0mm, height=10.0mm)")
    ellipse = CircleElement()
    ellipse.config.x = 0.0
    ellipse.config.y = 0.0
    ellipse.config.width = 15.0
    ellipse.config.height = 10.0
    ellipse.config.border_thickness = 1.0
    ellipse.config.fill = True
    
    zpl_ellipse = generator.generate([ellipse], label_config)
    print(f"  Generated: {zpl_ellipse}")
    
    # Читать логи
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Анализ
    analyzer = ZPLCircleAnalyzer()
    logs = analyzer.parse_zpl_logs(new_logs)
    issues = analyzer.detect_issues(logs)
    
    # Результат
    print("\n" + "=" * 60)
    print("[ZPL CIRCLE/ELLIPSE] LOG ANALYSIS")
    print("=" * 60)
    print(f"Circle ZPL commands: {len(logs['generated_circle'])}")
    print(f"Ellipse ZPL commands: {len(logs['generated_ellipse'])}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] ZPL GENERATION HAS ISSUES")
        return 1
    
    print("\n[OK] ZPL generation for Circle/Ellipse works correctly")
    
    # Финальная проверка ZPL формата
    assert '^GC' in zpl_circle, "Circle ZPL must contain ^GC"
    assert '^GE' in zpl_ellipse, "Ellipse ZPL must contain ^GE"
    
    print("\nFinal verification:")
    print(f"  Circle ZPL contains ^GC: {'^GC' in zpl_circle}")
    print(f"  Ellipse ZPL contains ^GE: {'^GE' in zpl_ellipse}")
    
    return 0


if __name__ == "__main__":
    exit(test_zpl_circle())
