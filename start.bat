@echo off
setlocal enabledelayedexpansion
title Memorama Arcade Retro — Servidor Local
echo.
echo  ==========================================
echo   MEMORAMA ARCADE RETRO
echo   Servidor Local para Red WiFi
echo  ==========================================
echo.

:: Cambiar al directorio del bat
cd /d "%~dp0"

set "PORT=8080"

:: Obtener IP local (primera IPv4 que no sea loopback)
set "LOCAL_IP="
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /i "IPv4" ^| findstr /v "127.0.0.1"') do (
  if not defined LOCAL_IP (
    set "RAW=%%A"
    set "LOCAL_IP=!RAW: =!"
  )
)

if not defined LOCAL_IP set "LOCAL_IP=localhost"

echo  IP detectada: !LOCAL_IP!
echo  URL para movil: http://!LOCAL_IP!:!PORT!/index.html
echo.
echo  Presiona Ctrl+C para detener el servidor
echo  ==========================================
echo.

:: Abrir navegador con la IP local para que el QR funcione en movil
start "" cmd /c "timeout /t 2 /nobreak >nul && start http://!LOCAL_IP!:%PORT%/index.html"

:: Levantar servidor (server.py imprime IP y URL al arrancar)
python server.py 2>nul
if %errorlevel% neq 0 (
  py server.py 2>nul
  if %errorlevel% neq 0 (
    python3 server.py 2>nul
    if %errorlevel% neq 0 (
      echo.
      echo  ERROR: No se encontro Python instalado.
      echo  Instala Python desde https://python.org
      echo.
      pause
    )
  )
)
