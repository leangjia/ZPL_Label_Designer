# -*- coding: utf-8 -*-
"""LogAnalyzer для Barcode тестів"""

import re
from typing import Dict, List, Any


class BarcodeLogAnalyzer:
    """Аналізатор логів для Barcode елементів"""
    
    @staticmethod
    def parse_real_width_logs(log_content: str) -> List[Dict[str, Any]]:
        """Парсинг логів calculate_real_width()
        
        Pattern: [BARCODE-EAN13/CODE128] Real width: 26.3mm (105 modules * 2 dots)
        """
        pattern = r'\[BARCODE-(EAN13|CODE128)\] Real width: ([\d.]+)mm \((\d+) modules \* (\d+) dots(?:, data_len=(\d+))?\)'
        matches = re.findall(pattern, log_content)
        
        results = []
        for m in matches:
            barcode_type = m[0]
            width_mm = float(m[1])
            modules = int(m[2])
            module_width_dots = int(m[3])
            data_len = int(m[4]) if m[4] else None
            
            results.append({
                'type': barcode_type,
                'width_mm': width_mm,
                'modules': modules,
                'module_width_dots': module_width_dots,
                'data_len': data_len
            })
        
        return results
    
    @staticmethod
    def parse_canvas_item_logs(log_content: str) -> List[Dict[str, Any]]:
        """Парсинг логів GraphicsBarcodeItem
        
        Pattern: [BARCODE-ITEM] Using REAL width: 26.3mm -> 210px
        """
        pattern = r'\[BARCODE-ITEM\] Using (REAL width|element\.width): ([\d.]+)mm -> (\d+)px'
        matches = re.findall(pattern, log_content)
        
        results = []
        for m in matches:
            source = m[0]
            width_mm = float(m[1])
            width_px = int(m[2])
            
            results.append({
                'source': source,
                'width_mm': width_mm,
                'width_px': width_px,
                'uses_real_width': 'REAL' in source
            })
        
        return results
    
    @staticmethod
    def parse_zpl_generation_logs(log_content: str) -> List[Dict[str, Any]]:
        """Парсинг логів to_zpl()
        
        Patterns:
        - Position: (10.0, 10.0)mm -> (79, 79)dots
        - Height: 15.0mm -> 119dots
        - Data: '1234567890123'
        - Real width: 26.3mm (will be used on print)
        - Generated: ^FO79,79 | ^BY2 | ^BEN,119,Y,N | ^FD1234567890123^FS
        """
        results = []
        
        # Знайти всі блоки ZPL generation для кожного типу
        ean13_blocks = re.findall(
            r'\[BARCODE-ZPL-EAN13\] Position: \(([\d.]+), ([\d.]+)\)mm.*?'
            r'\[BARCODE-ZPL-EAN13\] Height: ([\d.]+)mm.*?'
            r'\[BARCODE-ZPL-EAN13\] Data: \'([^\']+)\'.*?'
            r'\[BARCODE-ZPL-EAN13\] Real width: ([\d.]+)mm.*?'
            r'\[BARCODE-ZPL-EAN13\] Generated: (.+)',
            log_content,
            re.DOTALL
        )
        
        for block in ean13_blocks:
            results.append({
                'type': 'EAN13',
                'position_mm': (float(block[0]), float(block[1])),
                'height_mm': float(block[2]),
                'data': block[3],
                'real_width_mm': float(block[4]),
                'zpl': block[5].strip()
            })
        
        code128_blocks = re.findall(
            r'\[BARCODE-ZPL-CODE128\] Position: \(([\d.]+), ([\d.]+)\)mm.*?'
            r'\[BARCODE-ZPL-CODE128\] Height: ([\d.]+)mm.*?'
            r'\[BARCODE-ZPL-CODE128\] Data: \'([^\']+)\' \(len=(\d+)\).*?'
            r'\[BARCODE-ZPL-CODE128\] Real width: ([\d.]+)mm.*?'
            r'\[BARCODE-ZPL-CODE128\] Generated: (.+)',
            log_content,
            re.DOTALL
        )
        
        for block in code128_blocks:
            results.append({
                'type': 'CODE128',
                'position_mm': (float(block[0]), float(block[1])),
                'height_mm': float(block[2]),
                'data': block[3],
                'data_len': int(block[4]),
                'real_width_mm': float(block[5]),
                'zpl': block[6].strip()
            })
        
        return results
    
    @staticmethod
    def detect_issues(real_width_logs: List[Dict], canvas_logs: List[Dict], zpl_logs: List[Dict]) -> List[Dict[str, str]]:
        """Детектувати проблеми у Barcode логіці"""
        issues = []
        
        # === ISSUE 1: Real width calculation incorrect ===
        for log in real_width_logs:
            # Перевірити формулу: width_mm = modules * module_width_dots * 25.4 / 203
            expected_width = log['modules'] * log['module_width_dots'] * 25.4 / 203
            actual_width = log['width_mm']
            
            if abs(expected_width - actual_width) > 0.1:
                issues.append({
                    'type': 'REAL_WIDTH_CALC_INCORRECT',
                    'desc': f"{log['type']}: calculated {actual_width:.1f}mm, expected {expected_width:.1f}mm"
                })
        
        # === ISSUE 2: Canvas NOT using real width ===
        for log in canvas_logs:
            if not log['uses_real_width']:
                issues.append({
                    'type': 'CANVAS_NOT_USING_REAL_WIDTH',
                    'desc': f"Canvas uses element.width instead of calculate_real_width()"
                })
        
        # === ISSUE 3: Canvas width != Real width ===
        if real_width_logs and canvas_logs:
            real_width = real_width_logs[-1]['width_mm']
            canvas_width = canvas_logs[-1]['width_mm']
            
            if abs(real_width - canvas_width) > 0.1:
                issues.append({
                    'type': 'CANVAS_REAL_MISMATCH',
                    'desc': f"Canvas shows {canvas_width:.1f}mm, but real is {real_width:.1f}mm"
                })
        
        # === ISSUE 4: ZPL generation incorrect ===
        for log in zpl_logs:
            # Перевірити що ZPL містить ^BY{module_width}
            if '^BY' not in log['zpl']:
                issues.append({
                    'type': 'ZPL_MISSING_BY',
                    'desc': f"{log['type']}: ZPL missing ^BY command"
                })
            
            # Перевірити що data у ZPL співпадає
            if log['data'] not in log['zpl']:
                issues.append({
                    'type': 'ZPL_DATA_MISMATCH',
                    'desc': f"{log['type']}: Data '{log['data']}' not in ZPL"
                })
        
        # === ISSUE 5: CODE128 - data_len changes NOT reflected in width ===
        code128_real_logs = [l for l in real_width_logs if l['type'] == 'CODE128']
        if len(code128_real_logs) >= 2:
            # Перевірити що при зміні data_len змінюється width
            log1 = code128_real_logs[0]
            log2 = code128_real_logs[1]
            
            if log1['data_len'] != log2['data_len']:
                # data_len змінився - width ПОВИНЕН змінитися
                if abs(log1['width_mm'] - log2['width_mm']) < 0.1:
                    issues.append({
                        'type': 'CODE128_DATA_CHANGE_NO_WIDTH_UPDATE',
                        'desc': f"Data len changed {log1['data_len']} -> {log2['data_len']}, but width unchanged"
                    })
        
        return issues
