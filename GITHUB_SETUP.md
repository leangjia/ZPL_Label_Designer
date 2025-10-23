# 1C_Zebra 项目 GitHub 仓库创建指南

## 准备工作

### 1. 安装 Git（如果尚未安装）
从官方网站下载并安装 Git：https://git-scm.com/download/win

### 2. 验证安装
打开 PowerShell 并执行：
```powershell
git --version
```

## 创建本地仓库

### 1. 初始化 Git 仓库
```powershell
cd D:\AiKlientBank\1C_Zebra
git init
```

### 2. 配置 Git 用户（如果尚未配置）
```powershell
git config --global user.name "您的姓名"
git config --global user.email "您的邮箱@example.com"
```

### 3. 添加文件到仓库
```powershell
git add .
git commit -m "初始提交：ZPL 标签设计器 v1.0.0"
```

## 在 GitHub 上创建仓库

### 方法一：通过 GitHub 网页界面
1. 访问 https://github.com
2. 登录您的账户
3. 点击 "New repository"（绿色按钮）
4. 填写表单：
   - **仓库名称：** `1C_Zebra` 或 `ZPL-Label-Designer`
   - **描述：** `基于 PySide6 GUI 的专业 ZPL 标签设计器`
   - **可见性：** 私有/公开（根据选择）
   - **不要添加** README、.gitignore、license（项目中已存在）
5. 点击 "Create repository"

### 方法二：通过 GitHub CLI（如果已安装）
```powershell
gh repo create 1C_Zebra --private --description "基于 PySide6 GUI 的专业 ZPL 标签设计器"
```

## 关联本地和远程仓库

### 1. 添加远程仓库
```powershell
git remote add origin https://github.com/您的用户名/1C_Zebra.git
```

### 2. 推送代码到 GitHub
```powershell
git branch -M main
git push -u origin main
```

## 附加配置

### 1. 创建 .github/workflows 用于 CI/CD（可选）
```powershell
mkdir .github\workflows
```

创建文件 `.github/workflows/tests.yml`：
```yaml
name: 测试

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  测试:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: 设置 Python 3.13
      uses: actions/setup-python@v4
      with:
        python-version: '3.13'
    
    - name: 安装依赖
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: 运行智能测试
      run: |
        python tests/run_stages_1_5_smart.py
```

### 2. 为仓库添加主题标签
在 GitHub 仓库设置中添加主题标签：
- `python`
- `pyside6`
- `zpl`
- `label-designer`
- `zebra`
- `gui-application`
- `barcode-generator`

### 3. 配置分支保护（团队协作）
在 Settings → Branches → Add rule：
- 分支名称模式：`main`
- ✅ 合并前需要拉取请求审查
- ✅ 合并前需要通过状态检查

## 日常 Git 工作流程

### 添加更改
```powershell
git add .
git commit -m "更改描述"
git push
```

### 创建功能分支
```powershell
git checkout -b feature/新功能
# 进行更改
git add .
git commit -m "添加了新功能"
git push -u origin feature/新功能
```

### 查看状态
```powershell
git status
git log --oneline
```

## 自动化设置脚本

创建文件 `setup_git.ps1`：
```powershell
# 自动设置 1C_Zebra 的 Git 仓库

Write-Host "正在为 1C_Zebra 设置 Git 仓库..." -ForegroundColor Green

# 检查 Git
if (!(Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "错误：Git 未安装！" -ForegroundColor Red
    Write-Host "请下载 Git：https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

# 初始化
git init
git add .
git commit -m "初始提交：ZPL 标签设计器 v1.0.0"

Write-Host "✅ 本地仓库已创建" -ForegroundColor Green
Write-Host ""
Write-Host "后续步骤：" -ForegroundColor Yellow
Write-Host "1. 在 GitHub.com 上创建仓库"
Write-Host "2. 执行以下命令："
Write-Host "   git remote add origin https://github.com/您的用户名/1C_Zebra.git"
Write-Host "   git branch -M main"
Write-Host "   git push -u origin main"
```

运行脚本：
```powershell
.\setup_git.ps1
```

## 完成结果

完成所有步骤后，您将拥有：
- ✅ 本地 Git 仓库
- ✅ GitHub 上的远程仓库
- ✅ 已关联并同步的仓库
- ✅ 专业的 README.md 文件
- ✅ 配置好的 .gitignore 文件
- ✅ 准备好进行协作开发

您的项目将可通过以下地址访问：`https://github.com/您的用户名/1C_Zebra`