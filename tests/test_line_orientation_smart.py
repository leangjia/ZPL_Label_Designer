# -*- coding: utf-8 -*-
"""Умный тест Line ZPL Orientation - Canvas vs Preview"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.elements.shape_element import LineElement, LineConfig
import re


class LineOrientationAnalyzer:
    """Анализатор ZPL orientation для Line"""
    
    @staticmethod
    def test_orientation_cases():
        """Тестировать 4 случая направления линии"""
        
        test_cases = [
            {
                'name': 'RIGHT-DOWN (\\)',
                'start': (10, 10),
                'end': (25, 20),
                'expected_orientation': 'L',
                'description': 'x увеличивается, y увеличивается → L (left lean)'
            },
            {
                'name': 'RIGHT-UP (/)',
                'start': (10, 20),
                'end': (25, 10),
                'expected_orientation': 'R',
                'description': 'x увеличивается, y уменьшается → R (right lean)'
            },
            {
                'name': 'LEFT-DOWN (/)',
                'start': (25, 10),
                'end': (10, 20),
                'expected_orientation': 'R',
                'description': 'x уменьшается, y увеличивается → R (right lean)'
            },
            {
                'name': 'LEFT-UP (\\)',
                'start': (25, 20),
                'end': (10, 10),
                'expected_orientation': 'L',
                'description': 'x уменьшается, y уменьшается → L (left lean)'
            }
        ]
        
        results = []
        issues = []
        
        for case in test_cases:
            x1, y1 = case['start']
            x2, y2 = case['end']
            
            # Создать Line
            config = LineConfig(x=x1, y=y1, x2=x2, y2=y2, thickness=1.0)
            line = LineElement(config)
            
            # Генерировать ZPL
            zpl = line.to_zpl(dpi=203)
            
            # Парсить orientation из ZPL
            # Формат: ^GD{width},{height},{thickness},{color},{orientation}
            match = re.search(r'\^GD\d+,\d+,\d+,[BW],([LR])', zpl)
            
            if not match:
                issues.append({
                    'type': 'ZPL_PARSE_ERROR',
                    'case': case['name'],
                    'desc': 'Не удалось распарсить orientation из ZPL'
                })
                continue
            
            actual_orientation = match.group(1)
            expected = case['expected_orientation']
            
            result = {
                'case': case['name'],
                'start': case['start'],
                'end': case['end'],
                'expected': expected,
                'actual': actual_orientation,
                'match': actual_orientation == expected,
                'description': case['description']
            }
            
            results.append(result)
            
            if not result['match']:
                issues.append({
                    'type': 'ORIENTATION_MISMATCH',
                    'case': case['name'],
                    'desc': f"Expected {expected}, got {actual_orientation} - {case['description']}"
                })
        
        return results, issues


def test_line_orientation():
    """Умный тест ZPL orientation"""
    
    print("=" * 60)
    print("[TEST] Line ZPL Orientation - Canvas vs Preview")
    print("=" * 60)
    
    analyzer = LineOrientationAnalyzer()
    results, issues = analyzer.test_orientation_cases()
    
    # Вывод результатов
    print("\n" + "=" * 60)
    print("ORIENTATION TEST RESULTS")
    print("=" * 60)
    
    for result in results:
        status = "[OK]" if result['match'] else "[FAIL]"
        print(f"\n{status} {result['case']}")
        print(f"  Start: {result['start']}, End: {result['end']}")
        print(f"  {result['description']}")
        print(f"  Expected: {result['expected']}, Actual: {result['actual']}")
    
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
        print("\n[FAILURE] LINE ORIENTATION HAS ISSUES")
        return 1
    
    print("\n[OK] All orientation cases work correctly")
    print("Canvas direction now matches Preview direction!")
    return 0


if __name__ == "__main__":
    exit(test_line_orientation())
