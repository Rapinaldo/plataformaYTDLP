# 🔻 YT-DLP Web Downloader - Guia de Instalação e Uso

Este pacote contém os scripts auxiliares para automatizar a instalação e execução da interface gráfica do `yt-dlp` baseada em `Gradio`.

## ⚠️ Pré-requisitos (O que você precisa ter instalado antes)

1. **Python 3.8 ou superior**:
   - É obrigatório ter a linguagem Python instalada.
   - **MUITO IMPORTANTE:** Durante a instalação do Python no Windows, lembre-se de marcar a caixa de seleção **"Add python.exe to PATH"** na primeira tela do instalador.
   - [Baixe o Python aqui](https://www.python.org/downloads/).

2. **Windows 10 ou 11**:
   - O instalador tenta baixar o FFmpeg de forma automática utilizando o `winget`, que é nativo em versões recentes do Windows.

## ⚙️ Como Instalar (Faça apenas na primeira vez)

1. Certifique-se de que o arquivo principal em Python (aquele com o código do Gradio, salve-o como `app.py`) esteja exatamente na **mesma pasta** destes arquivos `.bat`.
2. Dê um duplo clique em **`install.bat`**.
3. O script irá:
   - Verificar se o Python está instalado no sistema.
   - Criar uma pasta isolada chamada `venv` (Ambiente Virtual). Isso impede que os pacotes do projeto interfiram em outras instalações do seu computador.
   - Baixar e instalar o `gradio` e o `yt-dlp`.
   - Tentar instalar o **FFmpeg** no seu sistema. O FFmpeg é uma ferramenta de fundo essencial para extrair o áudio no formato `.mp3` e para juntar áudio com vídeos de alta resolução (1080p, por exemplo).

*(Nota: Caso a instalação automática do FFmpeg falhe, baixe-o manualmente no site oficial e adicione a pasta `bin` nas Variáveis de Ambiente do Windows).*

## 🚀 Como Executar o Aplicativo (Dia a dia)

1. Sempre que quiser abrir a plataforma de download, dê um duplo clique no arquivo **`run.bat`**.
2. O script vai carregar o ambiente virtual e iniciar o servidor do painel.
3. Um endereço local (como `http://127.0.0.1:7860/`) será gerado no terminal. A página costuma abrir automaticamente, mas se não abrir, basta copiar e colar esse link no seu navegador de preferência.

## 📂 Estrutura de Arquivos Esperada

Para que tudo funcione corretamente, sua pasta deve ficar com a seguinte organização:

```text
/Sua-Pasta-De-Downloads/
├── app.py          <-- (O arquivo Python que contém o código do Gradio)
├── install.bat     <-- (Este arquivo que instala as dependências)
├── run.bat         <-- (O atalho para abrir o aplicativo)
├── README.md       <-- (Este guia)
└── venv/           <-- (Pasta gerada automaticamente pelo install.bat)
```
