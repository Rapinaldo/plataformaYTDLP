@echo off
title YT-DLP Web Downloader
echo Iniciando o YT-DLP Web Downloader...

if not exist venv\Scripts\activate.bat (
    echo ERRO: Ambiente virtual nao encontrado. 
    echo Por favor, execute o arquivo install.bat primeiro para instalar as dependencias.
    pause
    exit /b
)

call venv\Scripts\activate.bat
echo Servidor iniciando, aguarde...
python app.py

pause
