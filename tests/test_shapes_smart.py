# -*- coding: utf-8 -*-
"""Smart test for STAGE 11 - Shapes with LogAnalyzer"""

import sys
import re
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QPointF

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow
from core.elements.shape_element import RectangleElement, CircleElement, LineElement, ShapeConfig, LineConfig
from utils.logger import logger


class ShapesLogAnalyzer:
    """Analyzer for Shape logs - detects issues in shape logic"""
    
    @staticmethod
    def parse_shape_logs(log_content):
        """Extract shape creation logs"""
        logs = {
            'rect_created': [],
            'circle_created': [],
            'line_created': [],
            'zpl_rect': [],
            'zpl_circle': [],
            'zpl_line': [],
            'item_rect': [],
            'item_circle': [],
            'item_line': []
        }
        
        # [SHAPE-RECT] Created: size=(20x10)mm, fill=False
        rect_pattern = r'\[SHAPE-RECT\] Created: size=\((\d+\.?\d*)x(\d+\.?\d*)\)mm, fill=(True|False)'
        for match in re.finditer(rect_pattern, log_content):
            logs['rect_created'].append({
                'width': float(match.group(1)),
                'height': float(match.group(2)),
                'fill': match.group(3) == 'True'
            })
        
        # [SHAPE-CIRCLE] Created: size=(15x15)mm, fill=False
        circle_pattern = r'\[SHAPE-CIRCLE\] Created: size=\((\d+\.?\d*)x(\d+\.?\d*)\)mm, fill=(True|False)'
        for match in re.finditer(circle_pattern, log_content):
            logs['circle_created'].append({
                'width': float(match.group(1)),
                'height': float(match.group(2)),
                'fill': match.group(3) == 'True'
            })
        
        # [SHAPE-LINE] Created: from (10,10)mm to (25,20)mm
        line_pattern = r'\[SHAPE-LINE\] Created: from \((\d+\.?\d*),(\d+\.?\d*)\)mm to \((\d+\.?\d*),(\d+\.?\d*)\)mm'
        for match in re.finditer(line_pattern, log_content):
            logs['line_created'].append({
                'x1': float(match.group(1)),
                'y1': float(match.group(2)),
                'x2': float(match.group(3)),
                'y2': float(match.group(4))
            })
        
        # [SHAPE-ZPL-RECT] Size: (158x79) dots
        zpl_rect_pattern = r'\[SHAPE-ZPL-RECT\] Size: \((\d+)x(\d+)\) dots'
        for match in re.finditer(zpl_rect_pattern, log_content):
            logs['zpl_rect'].append({
                'width_dots': int(match.group(1)),
                'height_dots': int(match.group(2))
            })
        
        # [SHAPE-ZPL-CIRCLE] Diameter: 119 dots
        zpl_circle_pattern = r'\[SHAPE-ZPL-CIRCLE\] Diameter: (\d+) dots'
        for match in re.finditer(zpl_circle_pattern, log_content):
            logs['zpl_circle'].append({
                'diameter_dots': int(match.group(1))
            })
        
        # [SHAPE-ZPL-LINE] Width: 119, Height: 79 dots
        zpl_line_pattern = r'\[SHAPE-ZPL-LINE\] Width: (\d+), Height: (\d+) dots'
        for match in re.finditer(zpl_line_pattern, log_content):
            logs['zpl_line'].append({
                'width_dots': int(match.group(1)),
                'height_dots': int(match.group(2))
            })
        
        # [SHAPE-ZPL-RECT] Fill=False, thickness=15
        fill_pattern = r'\[SHAPE-ZPL-RECT\] Fill=(True|False), thickness=(\d+)'
        for match in re.finditer(fill_pattern, log_content):
            if logs['zpl_rect']:
                logs['zpl_rect'][-1]['fill'] = match.group(1) == 'True'
                logs['zpl_rect'][-1]['thickness'] = int(match.group(2))
        
        # [SHAPE-ITEM-RECT] Created at: (10.00, 10.00)mm
        item_rect_pattern = r'\[SHAPE-ITEM-RECT\] Created at: \((\d+\.?\d*), (\d+\.?\d*)\)mm'
        for match in re.finditer(item_rect_pattern, log_content):
            logs['item_rect'].append({
                'x': float(match.group(1)),
                'y': float(match.group(2))
            })
        
        # [SHAPE-ITEM-CIRCLE] Created at: (10.00, 10.00)mm
        item_circle_pattern = r'\[SHAPE-ITEM-CIRCLE\] Created at: \((\d+\.?\d*), (\d+\.?\d*)\)mm'
        for match in re.finditer(item_circle_pattern, log_content):
            logs['item_circle'].append({
                'x': float(match.group(1)),
                'y': float(match.group(2))
            })
        
        # [SHAPE-ITEM-LINE] Created: from (10.00,10.00) to (25.00,20.00)mm
        item_line_pattern = r'\[SHAPE-ITEM-LINE\] Created: from \((\d+\.?\d*),(\d+\.?\d*)\) to \((\d+\.?\d*),(\d+\.?\d*)\)mm'
        for match in re.finditer(item_line_pattern, log_content):
            logs['item_line'].append({
                'x1': float(match.group(1)),
                'y1': float(match.group(2)),
                'x2': float(match.group(3)),
                'y2': float(match.group(4))
            })
        
        return logs
    
    @staticmethod
    def detect_issues(logs):
        """Detect issues in shape logs"""
        issues = []
        
        # Issue 1: RECT CREATION != ZPL GENERATION
        if logs['rect_created'] and logs['zpl_rect']:
            created = logs['rect_created'][0]
            zpl = logs['zpl_rect'][0]
            
            # Convert mm to dots: 20mm * 203dpi / 25.4 = 158 dots
            expected_width_dots = int(created['width'] * 203 / 25.4)
            expected_height_dots = int(created['height'] * 203 / 25.4)
            
            if abs(zpl['width_dots'] - expected_width_dots) > 2:
                issues.append({
                    'type': 'RECT_SIZE_MISMATCH',
                    'desc': f"Created width={created['width']}mm ({expected_width_dots} dots), ZPL width={zpl['width_dots']} dots"
                })
            
            if abs(zpl['height_dots'] - expected_height_dots) > 2:
                issues.append({
                    'type': 'RECT_SIZE_MISMATCH',
                    'desc': f"Created height={created['height']}mm ({expected_height_dots} dots), ZPL height={zpl['height_dots']} dots"
                })
        
        # Issue 2: CIRCLE CREATION != ZPL GENERATION
        if logs['circle_created'] and logs['zpl_circle']:
            created = logs['circle_created'][0]
            zpl = logs['zpl_circle'][0]
            
            expected_diameter_dots = int(created['width'] * 203 / 25.4)
            
            if abs(zpl['diameter_dots'] - expected_diameter_dots) > 2:
                issues.append({
                    'type': 'CIRCLE_SIZE_MISMATCH',
                    'desc': f"Created diameter={created['width']}mm ({expected_diameter_dots} dots), ZPL diameter={zpl['diameter_dots']} dots"
                })
        
        # Issue 3: LINE CREATION != ZPL GENERATION
        if logs['line_created'] and logs['zpl_line']:
            created = logs['line_created'][0]
            zpl = logs['zpl_line'][0]
            
            # Calculate expected width/height in dots
            width_mm = abs(created['x2'] - created['x1'])
            height_mm = abs(created['y2'] - created['y1'])
            expected_width_dots = int(width_mm * 203 / 25.4)
            expected_height_dots = int(height_mm * 203 / 25.4)
            
            if abs(zpl['width_dots'] - expected_width_dots) > 2:
                issues.append({
                    'type': 'LINE_SIZE_MISMATCH',
                    'desc': f"Line width={width_mm}mm ({expected_width_dots} dots), ZPL width={zpl['width_dots']} dots"
                })
            
            if abs(zpl['height_dots'] - expected_height_dots) > 2:
                issues.append({
                    'type': 'LINE_SIZE_MISMATCH',
                    'desc': f"Line height={height_mm}mm ({expected_height_dots} dots), ZPL height={zpl['height_dots']} dots"
                })
        
        # Issue 4: FILL LOGIC INCORRECT
        if logs['rect_created'] and logs['zpl_rect']:
            created = logs['rect_created'][0]
            zpl = logs['zpl_rect'][0]
            
            if 'fill' in zpl and 'thickness' in zpl:
                if created['fill']:
                    # Fill: thickness should be = height
                    expected_thickness = int(created['height'] * 203 / 25.4)
                    if abs(zpl['thickness'] - expected_thickness) > 2:
                        issues.append({
                            'type': 'FILL_THICKNESS_INCORRECT',
                            'desc': f"Fill=True but thickness={zpl['thickness']} != height={expected_thickness}"
                        })
                else:
                    # Border: thickness should be = border_thickness (2mm default)
                    expected_thickness = int(2.0 * 203 / 25.4)  # 2mm = ~15 dots
                    if abs(zpl['thickness'] - expected_thickness) > 2:
                        issues.append({
                            'type': 'BORDER_THICKNESS_INCORRECT',
                            'desc': f"Fill=False but thickness={zpl['thickness']} != border={expected_thickness}"
                        })
        
        # Issue 5: GRAPHICS ITEM NOT CREATED
        if logs['rect_created'] and not logs['item_rect']:
            issues.append({
                'type': 'RECT_ITEM_NOT_CREATED',
                'desc': 'RectangleElement created but GraphicsRectangleItem missing'
            })
        
        if logs['circle_created'] and not logs['item_circle']:
            issues.append({
                'type': 'CIRCLE_ITEM_NOT_CREATED',
                'desc': 'CircleElement created but GraphicsCircleItem missing'
            })
        
        if logs['line_created'] and not logs['item_line']:
            issues.append({
                'type': 'LINE_ITEM_NOT_CREATED',
                'desc': 'LineElement created but GraphicsLineItem missing'
            })
        
        return issues


def test_shapes_smart():
    """Smart test for Shapes with log analysis"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    # Get file size BEFORE test
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    print("=" * 60)
    print("[STAGE 11] SHAPES SMART TEST")
    print("=" * 60)
    
    # Create QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("\n[TEST 1] Creating Rectangle...")
    window._add_rectangle()
    app.processEvents()
    
    print("[TEST 2] Creating Circle...")
    window._add_circle()
    app.processEvents()
    
    print("[TEST 3] Creating Line...")
    window._add_line()
    app.processEvents()
    
    print("\n[TEST 4] Generating ZPL...")
    # Generate ZPL for all elements
    zpl_code = window.zpl_generator.generate(
        window.elements,
        {'width': 28, 'height': 28, 'dpi': 203}
    )
    app.processEvents()
    
    print("[TEST 5] Checking elements count...")
    print(f"  Elements created: {len(window.elements)}")
    print(f"  Graphics items: {len(window.graphics_items)}")
    
    if len(window.elements) != 3:
        print(f"  [ERROR] Expected 3 elements, got {len(window.elements)}")
        return 1
    
    if len(window.graphics_items) != 3:
        print(f"  [ERROR] Expected 3 graphics items, got {len(window.graphics_items)}")
        return 1
    
    print("  [OK] All shapes created")
    
    # Read NEW logs only
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        new_logs = f.read()
    
    # Analyze logs
    print("\n[TEST 6] Analyzing logs...")
    analyzer = ShapesLogAnalyzer()
    logs = analyzer.parse_shape_logs(new_logs)
    
    print(f"  Rectangle logs: {len(logs['rect_created'])} created, {len(logs['zpl_rect'])} ZPL, {len(logs['item_rect'])} items")
    print(f"  Circle logs: {len(logs['circle_created'])} created, {len(logs['zpl_circle'])} ZPL, {len(logs['item_circle'])} items")
    print(f"  Line logs: {len(logs['line_created'])} created, {len(logs['zpl_line'])} ZPL, {len(logs['item_line'])} items")
    
    issues = analyzer.detect_issues(logs)
    
    print("\n" + "=" * 60)
    print("[SHAPE LOG ANALYSIS]")
    print("=" * 60)
    
    if issues:
        print(f"\nDETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  {issue['type']}: {issue['desc']}")
        print("\n[FAILURE] SHAPES HAVE ISSUES")
        return 1
    
    print("\n[OK] All shapes work correctly")
    print("  - Rectangle ZPL generation correct")
    print("  - Circle ZPL generation correct")
    print("  - Line ZPL generation correct")
    print("  - Fill/border logic correct")
    print("  - Graphics items created")
    
    return 0


if __name__ == '__main__':
    exit_code = test_shapes_smart()
    sys.exit(exit_code)
