:: WPS-Zotero — Installer / Instalador / 安装程序
:: Runs as Administrator / Ejecutar como Administrador / 以管理员身份运行

@echo off
chcp 65001 > nul

:: ─────────────────────────────────────────────
:: Auto-elevate to Administrator if not already
:: ─────────────────────────────────────────────
net session > nul 2>&1
if %errorLevel% neq 0 (
    echo Requesting administrator privileges...
    echo Solicitando privilegios de administrador...
    echo 正在请求管理员权限...
    echo.
    powershell -Command "Start-Process '%~f0' -Verb RunAs"
    exit /b
)

:: ─────────────────────────────────────────────
:: Check Python
:: ─────────────────────────────────────────────
echo Checking Python installation...
echo Verificando instalacion de Python...
echo 检查Python安装...
echo.

where python > nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Python not found in PATH.
    echo [ERROR] Python no encontrado en PATH.
    echo [ERROR] 未找到Python，请先安装Python并添加到PATH。
    echo.
    echo Please install Python 3 from https://www.python.org
    echo and make sure to check "Add Python to PATH" during installation.
    echo.
    echo Por favor instala Python 3 desde https://www.python.org
    echo y asegurate de marcar "Add Python to PATH" durante la instalacion.
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo Found / Encontrado / 已找到: %PYVER%
echo.

:: ─────────────────────────────────────────────
:: Menu
:: ─────────────────────────────────────────────
:MENU
cls
echo ============================================
echo   WPS-Zotero v0.2.0
echo ============================================
echo.
echo   [EN] Select an option:
echo   [ES] Selecciona una opcion:
echo   [ZH] 请选择操作：
echo.
echo   1.  Install   /  Instalar    /  安装插件
echo   2.  Uninstall /  Desinstalar /  卸载插件
echo   3.  Exit      /  Salir       /  退出
echo.
echo ============================================
echo.

set /p choice= Option / Opcion / 选项 (1, 2, 3): 

if "%choice%"=="1" goto INSTALL
if "%choice%"=="2" goto UNINSTALL
if "%choice%"=="3" goto EXIT

echo.
echo [!] Invalid option. Please enter 1, 2 or 3.
echo [!] Opcion invalida. Por favor ingresa 1, 2 o 3.
echo [!] 无效选项，请输入 1、2 或 3。
echo.
timeout /t 2 > nul
goto MENU

:: ─────────────────────────────────────────────
:INSTALL
cls
echo ============================================
echo   Installing... / Instalando... / 安装中...
echo ============================================
echo.
python install.py
echo.
if %errorLevel% equ 0 (
    echo [OK] Installation complete. Restart WPS to apply.
    echo [OK] Instalacion completa. Reinicia WPS para aplicar.
    echo [OK] 安装完成，请重启WPS以应用更改。
) else (
    echo [ERROR] Installation failed. Check the output above.
    echo [ERROR] La instalacion fallo. Revisa la salida de arriba.
    echo [ERROR] 安装失败，请查看上方输出。
)
echo.
pause
goto MENU

:: ─────────────────────────────────────────────
:UNINSTALL
cls
echo ============================================
echo   Uninstalling... / Desinstalando... / 卸载中...
echo ============================================
echo.
python install.py -u
echo.
if %errorLevel% equ 0 (
    echo [OK] Uninstall complete.
    echo [OK] Desinstalacion completa.
    echo [OK] 卸载完成。
) else (
    echo [ERROR] Uninstall failed. Check the output above.
    echo [ERROR] La desinstalacion fallo. Revisa la salida de arriba.
    echo [ERROR] 卸载失败，请查看上方输出。
)
echo.
pause
goto MENU

:: ─────────────────────────────────────────────
:EXIT
echo.
echo   Goodbye! / Hasta luego! / 再见！
echo.
timeout /t 2 > nul
exit