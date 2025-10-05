# -*- coding: utf-8 -*-
"""УМНИЙ ТЕСТ: Image Support з LogAnalyzer"""

import sys
import re
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QPixmap, QColor
from gui.main_window import MainWindow
from core.elements.image_element import ImageElement, GraphicsImageItem, ImageConfig


class ImageSupportLogAnalyzer:
    """Аналізатор логів для image support"""
    
    @staticmethod
    def parse_image_elem_logs(log):
        """[IMAGE-ELEM] logs"""
        created = re.findall(r'\[IMAGE-ELEM\] Created: pos=\(([\d.]+), ([\d.]+)\)mm, size=\((\d+)x(\d+)\)mm', log)
        return {
            'created': [(float(m[0]), float(m[1]), int(m[2]), int(m[3])) for m in created]
        }
    
    @staticmethod
    def parse_image_item_logs(log):
        """[IMAGE-ITEM] logs"""
        created = re.findall(r'\[IMAGE-ITEM\] Created at: \(([\d.]+), ([\d.]+)\)mm', log)
        loaded_base64 = len(re.findall(r'\[IMAGE-ITEM\] Loaded from base64', log))
        loaded_file = len(re.findall(r'\[IMAGE-ITEM\] Loaded from file', log))
        placeholder = len(re.findall(r'\[IMAGE-ITEM\] Created placeholder', log))
        displayed = re.findall(r'\[IMAGE-ITEM\] Displayed: size=\((\d+)x(\d+)\)px', log)
        load_error = len(re.findall(r'\[IMAGE-ITEM\] Load error:', log))
        
        return {
            'created': [(float(m[0]), float(m[1])) for m in created],
            'loaded_base64': loaded_base64,
            'loaded_file': loaded_file,
            'placeholder': placeholder,
            'displayed': [(int(m[0]), int(m[1])) for m in displayed],
            'load_error': load_error
        }
    
    @staticmethod
    def parse_image_convert_logs(log):
        """[IMAGE-CONVERT] logs"""
        loaded_base64 = len(re.findall(r'\[IMAGE-CONVERT\] Loaded from base64', log))
        loaded_file = len(re.findall(r'\[IMAGE-CONVERT\] Loaded from file:', log))
        original_size = re.findall(r'\[IMAGE-CONVERT\] Original size: \((\d+), (\d+)\), mode: (\w+)', log)
        resized = len(re.findall(r'\[IMAGE-CONVERT\] Resized to:', log))
        grayscale = len(re.findall(r'\[IMAGE-CONVERT\] Converted to grayscale', log))
        dithered = len(re.findall(r'\[IMAGE-CONVERT\] Applied dithering', log))
        hex_length = re.findall(r'\[IMAGE-CONVERT\] Hex data length: (\d+) chars \((\d+) bytes\)', log)
        convert_error = len(re.findall(r'\[IMAGE-CONVERT\] Error:', log))
        
        return {
            'loaded_base64': loaded_base64,
            'loaded_file': loaded_file,
            'original_size': [(int(m[0]), int(m[1]), m[2]) for m in original_size],
            'resized': resized,
            'grayscale': grayscale,
            'dithered': dithered,
            'hex_length': [(int(m[0]), int(m[1])) for m in hex_length],
            'convert_error': convert_error
        }
    
    @staticmethod
    def parse_image_zpl_logs(log):
        """[IMAGE-ZPL] logs"""
        position = re.findall(r'\[IMAGE-ZPL\] Position: \((\d+), (\d+)\) dots', log)
        size = re.findall(r'\[IMAGE-ZPL\] Size: \((\d+)x(\d+)\) dots', log)
        generated = re.findall(r'\[IMAGE-ZPL\] Generated: total_bytes=(\d+), bytes_per_row=(\d+)', log)
        no_data = len(re.findall(r'\[IMAGE-ZPL\] No image data or path', log))
        failed = len(re.findall(r'\[IMAGE-ZPL\] Failed to convert image', log))
        
        return {
            'position': [(int(m[0]), int(m[1])) for m in position],
            'size': [(int(m[0]), int(m[1])) for m in size],
            'generated': [(int(m[0]), int(m[1])) for m in generated],
            'no_data': no_data,
            'failed': failed
        }
    
    @staticmethod
    def detect_issues(elem_logs, item_logs, convert_logs, zpl_logs, 
                     elements_count_before, elements_count_after):
        """Детектувати 6 типів проблем"""
        issues = []
        
        # === ISSUE 1: ELEMENT створено, але ITEM НЕ створено ===
        if len(elem_logs['created']) > 0:
            if len(item_logs['created']) != len(elem_logs['created']):
                issues.append({
                    'type': 'ELEMENT_ITEM_MISMATCH',
                    'desc': f"Elements created={len(elem_logs['created'])}, but items={len(item_logs['created'])}"
                })
        
        # === ISSUE 2: ITEM створено, але IMAGE НЕ loaded ===
        if len(item_logs['created']) > 0:
            loaded = item_logs['loaded_base64'] + item_logs['loaded_file']
            if loaded != len(item_logs['created']):
                issues.append({
                    'type': 'IMAGE_NOT_LOADED',
                    'desc': f"Items created={len(item_logs['created'])}, but loaded={loaded}"
                })
        
        # === ISSUE 3: CONVERT: завантажено, але НЕ конвертовано ===
        if len(convert_logs['original_size']) > 0:
            if convert_logs['dithered'] != len(convert_logs['original_size']):
                issues.append({
                    'type': 'CONVERT_NOT_COMPLETED',
                    'desc': f"Original images={len(convert_logs['original_size'])}, but dithered={convert_logs['dithered']}"
                })
        
        # === ISSUE 4: HEX_DATA занадто короткий ===
        if len(convert_logs['hex_length']) > 0:
            for hex_chars, hex_bytes in convert_logs['hex_length']:
                if hex_chars < 100:  # Мінімум 50 bytes = 100 hex chars
                    issues.append({
                        'type': 'HEX_DATA_TOO_SHORT',
                        'desc': f"Hex length: {hex_chars} chars ({hex_bytes} bytes) - too short!"
                    })
        
        # === ISSUE 5: ZPL FORMAT неправильний ===
        if len(zpl_logs['generated']) > 0:
            for total_bytes, bytes_per_row in zpl_logs['generated']:
                # Перевірити чи total_bytes розумний
                if total_bytes < 10:
                    issues.append({
                        'type': 'ZPL_FORMAT_INCORRECT',
                        'desc': f"total_bytes={total_bytes} is too small"
                    })
        
        # === ISSUE 6: ELEMENTS_COUNT НЕ збільшилась ===
        if len(elem_logs['created']) > 0:
            expected_count = elements_count_before + len(elem_logs['created'])
            if elements_count_after != expected_count:
                issues.append({
                    'type': 'ELEMENTS_COUNT_WRONG',
                    'desc': f"Before={elements_count_before}, after={elements_count_after}, expected={expected_count}"
                })
        
        return issues


def test_image_support_smart():
    """Умний тест image support з LogAnalyzer"""
    
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    log_file.parent.mkdir(exist_ok=True)
    
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.processEvents()
    
    print("=" * 60)
    print("[STAGE 10] IMAGE SUPPORT - LOG ANALYSIS")
    print("=" * 60)
    
    # Створити test image якщо немає
    test_image_path = Path(r'D:\AiKlientBank\1C_Zebra\tests\test_image.png')
    
    if not test_image_path.exists():
        test_image_path.parent.mkdir(exist_ok=True)
        pixmap = QPixmap(100, 100)
        pixmap.fill(QColor(200, 200, 200))
        pixmap.save(str(test_image_path))
        print(f"[SETUP] Created test image: {test_image_path}")
    
    # ============ ТЕСТ: Add Image ============
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    elements_count_before = len(window.elements)
    
    print(f"\n[TEST] Add image element:")
    print(f"Elements before: {elements_count_before}")
    
    # Створити ImageElement програмно
    import base64
    with open(test_image_path, 'rb') as f:
        image_bytes = f.read()
        image_data = base64.b64encode(image_bytes).decode('utf-8')
    
    config = ImageConfig(
        x=15.0,
        y=15.0,
        width=25.0,
        height=25.0,
        image_path=str(test_image_path),
        image_data=image_data
    )
    image_element = ImageElement(config)
    
    graphics_item = GraphicsImageItem(image_element, dpi=203)
    graphics_item.snap_enabled = window.snap_enabled
    
    from core.undo_commands import AddElementCommand
    command = AddElementCommand(window, image_element, graphics_item)
    window.undo_stack.push(command)
    app.processEvents()
    
    elements_count_after = len(window.elements)
    print(f"Elements after: {elements_count_after}")
    
    # Читати логи (Add phase)
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        add_logs = f.read()
    
    # ============ ТЕСТ: ZPL Generation ============
    file_size_before = log_file.stat().st_size
    
    print(f"\n[TEST] ZPL generation for image:")
    
    zpl_code = image_element.to_zpl(dpi=203)
    print(f"ZPL length: {len(zpl_code)} chars")
    
    # Перевірити наявність ^GFA
    if '^GFA' in zpl_code:
        print("[OK] ZPL contains ^GFA command")
    else:
        print("[ERROR] ZPL does NOT contain ^GFA command")
    
    # Читати логи (ZPL phase)
    with open(log_file, 'r', encoding='utf-8') as f:
        f.seek(file_size_before)
        zpl_logs_text = f.read()
    
    # ============ АНАЛІЗ ЛОГІВ ============
    full_log = add_logs + zpl_logs_text
    
    analyzer = ImageSupportLogAnalyzer()
    elem_logs = analyzer.parse_image_elem_logs(full_log)
    item_logs = analyzer.parse_image_item_logs(full_log)
    convert_logs = analyzer.parse_image_convert_logs(full_log)
    zpl_logs = analyzer.parse_image_zpl_logs(full_log)
    
    print(f"\n{'=' * 60}")
    print("LOG ANALYSIS")
    print(f"{'=' * 60}")
    print(f"[IMAGE-ELEM] created: {len(elem_logs['created'])}")
    print(f"[IMAGE-ITEM] created: {len(item_logs['created'])}")
    print(f"[IMAGE-ITEM] loaded: base64={item_logs['loaded_base64']}, file={item_logs['loaded_file']}")
    print(f"[IMAGE-CONVERT] original_size: {len(convert_logs['original_size'])}")
    print(f"[IMAGE-CONVERT] grayscale: {convert_logs['grayscale']}")
    print(f"[IMAGE-CONVERT] dithered: {convert_logs['dithered']}")
    print(f"[IMAGE-CONVERT] hex_length: {convert_logs['hex_length']}")
    print(f"[IMAGE-ZPL] position: {zpl_logs['position']}")
    print(f"[IMAGE-ZPL] size: {zpl_logs['size']}")
    print(f"[IMAGE-ZPL] generated: {zpl_logs['generated']}")
    
    # Детектувати проблеми
    issues = analyzer.detect_issues(
        elem_logs, item_logs, convert_logs, zpl_logs,
        elements_count_before, elements_count_after
    )
    
    if issues:
        print(f"\n[FAILURE] DETECTED {len(issues)} ISSUE(S):")
        for issue in issues:
            print(f"  [{issue['type']}] {issue['desc']}")
        print(f"\n{'=' * 60}")
        return 1
    
    print(f"\n[OK] Image support works correctly")
    print(f"{'=' * 60}")
    return 0


if __name__ == "__main__":
    sys.exit(test_image_support_smart())
