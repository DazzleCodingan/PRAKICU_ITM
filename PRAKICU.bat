@echo off
setlocal
cd /d "%~dp0"
set "LOG_FILE=%~dp0otomatis.log"

echo [%date% %time%] Memulai pembaruan prakiraan.>>"%LOG_FILE%"
echo Menjalankan EKSTRAK.py...>>"%LOG_FILE%"
python "%~dp0EKSTRAK.py" >>"%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo EKSTRAK.py gagal. Periksa "%LOG_FILE%".
    exit /b 1
)

echo Menjalankan POSISI.py...>>"%LOG_FILE%"
python "%~dp0POSISI.py" >>"%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo POSISI.py gagal. Periksa "%LOG_FILE%".
    exit /b 1
)

echo Menjalankan KIRIM_EMAIL.py...>>"%LOG_FILE%"
python "%~dp0KIRIM_EMAIL.py" >>"%LOG_FILE%" 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Pengiriman email gagal. Periksa "%LOG_FILE%".
    exit /b 1
)

echo [%date% %time%] Pembaruan dan pengiriman selesai.>>"%LOG_FILE%"
exit /b 0
