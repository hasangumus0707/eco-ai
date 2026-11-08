@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"

echo ============================================
echo   ECO AI - Kurulum (Windows)
echo   Bu islem yalnizca BIR KEZ yapilir.
echo ============================================
echo.

REM ---------- 1. Python kontrolu ----------
set "PY="
py -3.12 --version >nul 2>&1 && set "PY=py -3.12"
if not defined PY (
    python --version >nul 2>&1 && set "PY=python"
)
if not defined PY (
    echo [HATA] Python bulunamadi.
    echo Python 3.12'yi https://www.python.org/downloads/ adresinden kurun.
    echo Kurulumda "Add python.exe to PATH" kutusunu isaretlemeyi unutmayin.
    pause
    exit /b 1
)
echo [1/4] Python bulundu:
%PY% --version
%PY% -c "import sys; sys.exit(0 if (3,10) <= sys.version_info[:2] <= (3,13) else 1)"
if errorlevel 1 (
    echo [HATA] Python surumu 3.10 ile 3.13 arasinda olmali. Python 3.12 kurmaniz onerilir.
    pause
    exit /b 1
)

REM ---------- 2. Node.js kontrolu ----------
where npm >nul 2>&1
if errorlevel 1 (
    echo [HATA] Node.js bulunamadi. https://nodejs.org adresinden LTS surumunu kurun.
    pause
    exit /b 1
)
echo [2/4] Node.js bulundu:
node --version

REM ---------- 3. Backend: sanal ortam + paketler ----------
echo.
echo [3/4] Backend paketleri kuruluyor. PyTorch buyuk bir paket, 5-10 dakika surebilir...
if not exist "backend\.venv\Scripts\python.exe" (
    %PY% -m venv backend\.venv
    if errorlevel 1 (
        echo [HATA] Sanal ortam olusturulamadi.
        pause
        exit /b 1
    )
)
backend\.venv\Scripts\python.exe -m pip install --upgrade pip --quiet
backend\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
if errorlevel 1 (
    echo [HATA] Python paketleri kurulamadi. Internet baglantinizi kontrol edip tekrar deneyin.
    pause
    exit /b 1
)

REM ---------- 4. Frontend paketleri ----------
echo.
echo [4/4] Frontend paketleri kuruluyor...
pushd frontend
call npm install
if errorlevel 1 (
    popd
    echo [HATA] npm paketleri kurulamadi.
    pause
    exit /b 1
)
popd

REM ---------- Kontrol ----------
echo.
echo Ortam kontrol ediliyor...
pushd backend
.venv\Scripts\python.exe -m training.check_device
popd

echo.
echo ============================================
echo   KURULUM TAMAMLANDI!
echo   Uygulamayi baslatmak icin baslat.bat dosyasina cift tiklayin.
echo ============================================
pause
