# -*- coding: utf-8 -*-
"""
Етап 1: Тест створення Sidebar та emit сигналів
"""
import sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject

# Додати шлях проекту
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from gui.sidebar import Sidebar
from utils.logger import logger


class SignalReceiver(QObject):
    """Тестовий приймач сигналів"""
    
    def __init__(self):
        super().__init__()
        self.received_signals = []
    
    def on_element_selected(self, element_type):
        self.received_signals.append(element_type)
        logger.debug(f"[TEST] Received signal: {element_type}")


def test_sidebar_creation():
    """Тест 1: Створення Sidebar"""
    print("=" * 60)
    print("TEST 1: Sidebar Creation")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    try:
        sidebar = Sidebar()
        
        # Перевірки
        assert sidebar is not None, "Sidebar не створено"
        assert sidebar.width() == 100, f"Width = {sidebar.width()}, очікується 100"
        
        print("[OK] Sidebar створено успішно")
        print(f"[OK] Width = {sidebar.width()}px")
        return True
        
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


def test_sidebar_signals():
    """Тест 2: Сигнали Sidebar"""
    print("\n" + "=" * 60)
    print("TEST 2: Sidebar Signals")
    print("=" * 60)
    
    app = QApplication.instance() or QApplication(sys.argv)
    
    # Лог файл
    log_file = Path(r'D:\AiKlientBank\1C_Zebra\logs\zpl_designer.log')
    file_size_before = log_file.stat().st_size if log_file.exists() else 0
    
    try:
        sidebar = Sidebar()
        receiver = SignalReceiver()
        
        # Підключити сигнал
        sidebar.element_type_selected.connect(receiver.on_element_selected)
        
        # Емітувати через приватний метод
        sidebar._on_button_clicked('text')
        app.processEvents()
        
        sidebar._on_button_clicked('barcode')
        app.processEvents()
        
        # Читати НОВІ логи
        with open(log_file, 'r', encoding='utf-8') as f:
            f.seek(file_size_before)
            new_logs = f.read()
        
        # Аналіз логів
        issues = []
        
        # Перевірка 1: Сигнал text
        if "[SIDEBAR] Button clicked: text" not in new_logs:
            issues.append("Немає логу '[SIDEBAR] Button clicked: text'")
        
        if "[SIDEBAR] Signal emitted: element_type_selected('text')" not in new_logs:
            issues.append("Немає логу emit сигналу 'text'")
        
        # Перевірка 2: Сигнал barcode
        if "[SIDEBAR] Button clicked: barcode" not in new_logs:
            issues.append("Немає логу '[SIDEBAR] Button clicked: barcode'")
        
        # Перевірка 3: Receiver отримав сигнали
        if len(receiver.received_signals) != 2:
            issues.append(f"Receiver отримав {len(receiver.received_signals)} сигналів, очікується 2")
        
        if receiver.received_signals != ['text', 'barcode']:
            issues.append(f"Signals = {receiver.received_signals}, очікується ['text', 'barcode']")
        
        # Вивід результатів
        print(f"Logs analyzed: {len(new_logs)} chars")
        print(f"Signals received: {receiver.received_signals}")
        
        if issues:
            print(f"\n[FAIL] Detected {len(issues)} issue(s):")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        print("\n[OK] Всі сигнали працюють коректно")
        return True
        
    except Exception as e:
        print(f"[FAIL] {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = True
    
    if not test_sidebar_creation():
        success = False
    
    if not test_sidebar_signals():
        success = False
    
    sys.exit(0 if success else 1)
