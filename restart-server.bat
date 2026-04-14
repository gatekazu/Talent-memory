@echo off
title Reiniciar Servidor — Memorama Arcade Retro
echo.
echo  Cerrando servidor anterior en puerto 8080...

:: Matar proceso que usa el puerto 8080
for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8080 " ^| findstr "LISTENING"') do (
  taskkill /PID %%P /F >nul 2>&1
)

timeout /t 1 /nobreak >nul

echo  Reiniciando...
echo.

:: Relanzar start.bat
call "%~dp0start.bat"
