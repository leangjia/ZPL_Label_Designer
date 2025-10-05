# Инструкция по созданию GitHub репозитория для проекта 1C_Zebra

## Предварительная подготовка

### 1. Установка Git (если не установлен)
Скачайте и установите Git с официального сайта: https://git-scm.com/download/win

### 2. Проверка установки
Откройте PowerShell и выполните:
```powershell
git --version
```

## Создание локального репозитория

### 1. Инициализация Git репозитория
```powershell
cd D:\AiKlientBank\1C_Zebra
git init
```

### 2. Настройка пользователя Git (если не настроен)
```powershell
git config --global user.name "Ваше Имя"
git config --global user.email "ваш-email@example.com"
```

### 3. Добавление файлов в репозиторий
```powershell
git add .
git commit -m "Initial commit: ZPL Label Designer v1.0.0"
```

## Создание репозитория на GitHub

### Вариант 1: Через веб-интерфейс GitHub
1. Перейдите на https://github.com
2. Войдите в свой аккаунт
3. Нажмите кнопку "New repository" (зеленая кнопка)
4. Заполните форму:
   - **Repository name:** `1C_Zebra` или `ZPL-Label-Designer`
   - **Description:** `Professional ZPL Label Designer with PySide6 GUI`
   - **Visibility:** Private/Public (по выбору)
   - **НЕ добавляйте** README, .gitignore, license (они уже есть в проекте)
5. Нажмите "Create repository"

### Вариант 2: Через GitHub CLI (если установлен)
```powershell
gh repo create 1C_Zebra --private --description "Professional ZPL Label Designer with PySide6 GUI"
```

## Связывание локального и удаленного репозиториев

### 1. Добавление удаленного репозитория
```powershell
git remote add origin https://github.com/ваш-username/1C_Zebra.git
```

### 2. Отправка кода на GitHub
```powershell
git branch -M main
git push -u origin main
```

## Дополнительные настройки

### 1. Создание .github/workflows для CI/CD (опционально)
```powershell
mkdir .github\workflows
```

Создайте файл `.github/workflows/tests.yml`:
```yaml
name: Tests

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python 3.13
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run smart tests
      run: |
        python tests/run_stages_1_5_smart.py
```

### 2. Добавление topics (тегов) к репозиторию
В настройках репозитория на GitHub добавьте topics:
- `python`
- `pyside6`
- `zpl`
- `label-designer`
- `zebra`
- `gui-application`
- `barcode-generator`

### 3. Настройка branch protection (для team work)
В Settings → Branches → Add rule:
- Branch name pattern: `main`
- ✅ Require pull request reviews before merging
- ✅ Require status checks to pass before merging

## Ежедневная работа с Git

### Добавление изменений
```powershell
git add .
git commit -m "Описание изменений"
git push
```

### Создание feature branch
```powershell
git checkout -b feature/новая-функция
# Внесите изменения
git add .
git commit -m "Добавлена новая функция"
git push -u origin feature/новая-функция
```

### Просмотр статуса
```powershell
git status
git log --oneline
```

## Готовый скрипт для автоматизации

Создайте файл `setup_git.ps1`:
```powershell
# Автоматическая настройка Git репозитория

Write-Host "Настройка Git репозитория для 1C_Zebra..." -ForegroundColor Green

# Проверка Git
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "ОШИБКА: Git не установлен!" -ForegroundColor Red
    Write-Host "Скачайте Git: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# Инициализация
git init
git add .
git commit -m "Initial commit: ZPL Label Designer v1.0.0"

Write-Host "✅ Локальный репозиторий создан" -ForegroundColor Green
Write-Host ""
Write-Host "Следующие шаги:" -ForegroundColor Yellow
Write-Host "1. Создайте репозиторий на GitHub.com"
Write-Host "2. Выполните команды:"
Write-Host "   git remote add origin https://github.com/ваш-username/1C_Zebra.git"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
```

Запустите скрипт:
```powershell
.\setup_git.ps1
```

## Результат

После выполнения всех шагов у вас будет:
- ✅ Локальный Git репозиторий
- ✅ Удаленный репозиторий на GitHub
- ✅ Связанные репозитории с синхронизацией
- ✅ Профессиональный README.md
- ✅ Настроенный .gitignore
- ✅ Готовность к collaborative development

Ваш проект будет доступен по адресу: `https://github.com/ваш-username/1C_Zebra`