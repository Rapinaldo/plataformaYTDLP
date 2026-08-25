@echo off
echo ==========================================
echo Instalador de Dependencias - YT-DLP Web
echo ==========================================
echo.

:: Verifica se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado! Instale o Python antes de continuar.
    echo MUITO IMPORTANTE: Ao instalar o Python, marque a opcao "Add python.exe to PATH".
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b
)

echo [1/4] Criando ambiente virtual (venv)...
python -m venv venv

echo [2/4] Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo [3/4] Instalando bibliotecas Python (Gradio e yt-dlp)...
python -m pip install --upgrade pip >nul 2>&1
pip install gradio yt-dlp

echo.
echo [4/4] Instalando FFmpeg (Necessario para converter audio e juntar 1080p)...
echo Tentando instalar via winget (Gerenciador de pacotes do Windows)...
winget install -e --id Gyan.FFmpeg --accept-source-agreements --accept-package-agreements

echo.
echo ==========================================
echo Instalacao concluida com sucesso!
echo Coloque o arquivo app.py nesta mesma pasta.
echo Para iniciar o aplicativo, execute o arquivo run.bat
echo ==========================================
pause
