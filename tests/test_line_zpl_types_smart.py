# -*- coding: utf-8 -*-
"""Умный тест Line ZPL - Horizontal/Vertical/Diagonal"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.elements.shape_element import LineElement, LineConfig
import re


class LineTypeAnalyzer:
    """Анализатор ZPL для 3 типов линий"""
    
    @staticmethod
    def test_line_types():
        """Тестировать 3 типа линий"""
        
        test_cases = [
            {
                'name': 'HORIZONTAL',
                'start': (10, 10),
                'end': (25, 10),
                'expected_command': 'GB',  # ^GB для горизонтальной
                'description': 'y1 == y2, должен использовать ^GB'
            },
            {
                'name': 'VERTICAL',
                'start': (10, 10),
                'end': (10, 25),
                'expected_command': 'GB',  # ^GB для вертикальной
                'description': 'x1 == x2, должен использовать ^GB'
            },
            {
                'name': 'DIAGONAL \\',
                'start': (10, 10),
                'end': (25, 20),
                'expected_command': 'GD',  # ^GD для диагональной
                'description': 'diagonal, должен использовать ^GD'
            },
            {
                'name': 'DIAGONAL /',
                'start': (10, 20),
                'end': (25, 10),
                'expected_command': 'GD',  # ^GD для диагональной
                'description': 'diagonal, должен использовать ^GD'
            }
        ]
        
        results = []
        issues = []
        
        for case in test_cases:
            x1, y1 = case['start']
            x2, y2 = case['end']
            
            # Создать Line
            config = LineConfig(x=x1, y=y1, x2=x2, y2=y2, thickness=4.0)
            line = LineElement(config)
            
            # Генерировать ZPL
            zpl = line.to_zpl(dpi=203)
            
            # Парсить команду из ZPL
            # Ищем ^GB или ^GD
            gb_match = re.search(r'\^GB\d+,\d+,\d+,[BW],\d+', zpl)
            gd_match = re.search(r'\^GD\d+,\d+,\d+,[BW],[LR]', zpl)
            
            if gb_match:
                actual_command = 'GB'
                command_str = gb_match.group(0)
            elif gd_match:
                actual_command = 'GD'
                command_str = gd_match.group(0)
            else:
                issues.append({
                    'type': 'ZPL_PARSE_ERROR',
                    'case': case['name'],
                    'desc': 'Не удалось найти ^GB или ^GD в ZPL'
                })
                continue
            
            expected = case['expected_command']
            
            result = {
                'case': case['name'],
                'start': case['start'],
                'end': case['end'],
                'expected': expected,
                'actual': actual_command,
                'match': actual_command == expected,
                'command': command_str,
                'description': case['description']
            }
            
            results.append(result)
            
            if not result['match']:
                issues.append({
                    'type': 'COMMAND_MISMATCH',
                    'case': case['name'],
                    'desc': f"Expected ^{expected}, got ^{actual_command} - {case['description']}"
                })
        
        return results, issues


def test_line_zpl_types():
    """Умный тест ZPL команд для линий"""
    
    print("=" * 60)
    print("[TEST] Line ZPL - Horizontal/Vertical/Diagonal")
    print("=" * 60)
    
    analyzer = LineTypeAnalyzer()
    results, issues = analyzer.test_line_types()
    
    # Вывод результатов
    print("\n" + "=" * 60)
    print("LINE TYPE TEST RESULTS")
    print("=" * 60)
    
    for result in results:
        status = "[OK]" if result['match'] else "[FAIL]"
        print(f"\n{status} {result['case']}")
        print(f"  Start: {result['start']}, End: {result['end']}")
        print(f"  {result['description']}")
        print(f"  Expected: ^{result['expected']}, Actual: ^{result['actual']}")
        print(f"  ZPL: {result['command']}")
    
    # Итог
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total = len(results)
    passed = sum(1 for r in results if r['match'])
    
    print(f"Total cases: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] LINE ZPL HAS ISSUES")
        return 1
    
    print("\n[OK] All line types use correct ZPL commands")
    print("Horizontal/Vertical -> ^GB, Diagonal -> ^GD")
    print("Preview will now match Canvas perfectly!")
    return 0


if __name__ == "__main__":
    exit(test_line_zpl_types())
