@echo off
echo 🚀 启动SimHoshino OpenAI API服务器...
echo.

:: 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

:: 安装依赖
echo 📦 安装Python依赖...
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ 依赖安装失败
    pause
    exit /b 1
)

echo.
echo ✅ 依赖安装完成
echo.

:: 启动服务器
echo 🌟 启动API服务器...
python main.py

pause 