# -*- coding: utf-8 -*-
"""Test: Open JSON button exists in toolbar"""
import sys
from pathlib import Path

# Добавить корневую директорию в sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow


def test_open_json_button_exists():
    """Проверка что кнопка Open JSON существует в toolbar"""
    app = QApplication.instance() or QApplication(sys.argv)
    window = MainWindow()
    
    # Проверить что action существует
    assert 'open_json' in window.actions, "Action 'open_json' не существует!"
    
    # Проверить что action добавлен в toolbar
    toolbar = window.toolbar
    
    # Проверить что у toolbar есть атрибут open_json_action
    assert hasattr(toolbar, 'open_json_action'), "toolbar.open_json_action НЕ существует!"
    
    # Проверить что это правильный action
    assert toolbar.open_json_action == window.actions['open_json'], "Неправильный action!"
    
    # Проверить что action добавлен в QToolBar (через QToolBar API)
    qt_actions = window.toolbar.actions()  # QToolBar.actions() метод
    open_json_in_toolbar = window.actions['open_json'] in qt_actions
    
    assert open_json_in_toolbar, "Action 'open_json' НЕ найден в QToolBar.actions()!"
    
    # Проверить что action подключен к методу
    assert hasattr(window, '_open_json'), "Метод _open_json НЕ существует!"
    
    print("[OK] Кнопка Open JSON создана правильно")
    print(f"  - Action существует: {True}")
    print(f"  - В toolbar: {True}")
    print(f"  - Метод _open_json: {True}")
    return 0


if __name__ == "__main__":
    sys.exit(test_open_json_button_exists())
