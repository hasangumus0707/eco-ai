@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

if not exist "backend\.venv\Scripts\python.exe" (
    echo [HATA] Kurulum yapilmamis. Once kurulum.bat dosyasini calistirin.
    pause
    exit /b 1
)
if not exist "frontend\node_modules" (
    echo [HATA] Frontend paketleri eksik. Once kurulum.bat dosyasini calistirin.
    pause
    exit /b 1
)

echo ============================================
echo   ECO AI baslatiliyor...
echo   Iki yeni pencere acilacak: Backend ve Frontend.
echo   Uygulamayi kapatmak icin o iki pencereyi kapatin.
echo ============================================

REM Backend: yapay zeka modeli + API (port 8000)
start "ECO AI - Backend (kapatmayin)" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\python.exe -m uvicorn app.main:app --port 8000"

REM Frontend: web arayuzu (port 5173)
start "ECO AI - Frontend (kapatmayin)" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo Model yukleniyor, tarayici birazdan acilacak...
timeout /t 8 /nobreak >nul
start "" http://localhost:5173

echo.
echo Tarayici acilmadiysa adres cubuguna su adresi yazin: http://localhost:5173
echo Bu pencereyi kapatabilirsiniz.
timeout /t 10 >nul
