"""
Plataforma de Download de Vídeo com Gradio + yt-dlp
-------------------------------------------------------
Interface web para download de vídeos e áudios usando yt-dlp
com seleção de qualidade, formato e múltiplos links.
"""

import os
import sys
import tempfile
import subprocess
import gradio as gr
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import shutil
import time
from datetime import datetime


# Adiciona o diretório atual ao path para importar yt-dlp
sys.path.insert(0, str(Path(__file__).parent))

# Tenta importar yt-dlp, se não estiver instalado, tenta instalar
try:
    import yt_dlp
except ImportError:
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "yt-dlp"])
        import yt_dlp
    except Exception as e:
        print(f"Não foi possível instalar yt-dlp: {e}")
        print("Instale manualmente com: pip install yt-dlp")
        sys.exit(1)


# --- Configurações ---
DEFAULT_QUALITY = "best"
DEFAULT_AUDIO_FORMAT = "bestaudio"
DEFAULT_VIDEO_FORMAT = "bestvideo+bestaudio/best"
OUTPUT_DIR = tempfile.mkdtemp(prefix="yt_dlp_downloads_")
OS_NAME = "Windows" if sys.platform == "win32" else "Linux"


@dataclass
class VideoInfo:
    """Classe para armazenar informações de um vídeo."""
    url: str
    title: str
    thumbnail: str
    duration: str
    qualities: List[str]
    audio_formats: List[str]
    available_formats: List[str]


# --- Funções de Utilidade ---

def sanitize_filename(filename: str) -> str:
    """Remove caracteres inválidos de nomes de arquivos."""
    valid_chars = "-_.() %s%s%s" % (os.path.sep, os.path.altsep, "")
    valid_chars += "".join(chr(i) for i in range(33, 127))
    return "".join(c for c in filename if c in valid_chars or c.isdigit()).strip()


def get_video_info(url: str, quiet: bool = True) -> Optional[VideoInfo]:
    """Obtém informações sobre um vídeo usando yt-dlp."""
    try:
        ydl_opts = {
            "quiet": quiet,
            "no_warnings": True,
            "extract_flat": False,
            "skip_download": True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            if info is None:
                return None
            
            # Obter qualidades disponíveis
            qualities = []
            if info["formats"]:
                for fmt in info["formats"]:
                    quality = fmt.get("resolution", "unknown")
                    if quality not in qualities:
                        qualities.append(quality)
            
            # Obter formatos de áudio
            audio_formats = []
            if info["formats"]:
                for fmt in info["formats"]:
                    if "acodec" in fmt and fmt["acodec"] != "none":
                        fmt_quality = fmt.get("resolution", "audio")
                        if fmt_quality not in audio_formats:
                            audio_formats.append(fmt_quality)
            
            # Obter formatos de vídeo
            video_formats = []
            if info["formats"]:
                for fmt in info["formats"]:
                    if fmt.get("height") and fmt.get("acodec") == "none":
                        fmt_quality = fmt.get("resolution", "video")
                        if fmt_quality not in video_formats:
                            video_formats.append(fmt_quality)
            
            return VideoInfo(
                url=url,
                title=info.get("title", "Desconhecido"),
                thumbnail=info.get("thumbnail", ""),
                duration=info.get("duration", "N/A") or "N/A",
                qualities=qualities if qualities else ["N/A"],
                audio_formats=audio_formats if audio_formats else ["N/A"],
                available_formats=video_formats + audio_formats if video_formats or audio_formats else ["N/A"],
            )
            
    except Exception as e:
        return None


def get_quality_label(quality: str) -> str:
    """Converte uma string de qualidade para um rótulo amigável."""
    quality_map = {
        "best": "Melhor Qualidade (Best)",
        "4320": "4K (4320p)",
        "2160": "4K (2160p)",
        "1440": "2K (1440p)",
        "1080": "Full HD (1080p)",
        "720": "HD (720p)",
        "480": "SD (480p)",
        "360": "SD (360p)",
        "240": "Low (240p)",
        "144": "Mobile (144p)",
        "220": "High Mobile (220p)",
        "178": "Mobile (178p)",
        "136": "Low Mobile (136p)",
        "96": "Low Mobile (96p)",
        "audio": "Áudio",
    }
    return quality_map.get(quality, quality)


def format_duration(seconds: float) -> str:
    """Converte segundos para formato HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def run_download(
    urls: List[str],
    quality: str,
    format_key: str,
    download_type: str,
    audio_format: str,
    output_dir: str,
    show_progress: bool = False,
) -> List[Dict]:
    """Executa o download de múltiplos vídeos/áudios."""
    results = []
    start_time = time.time()
    
    for idx, url in enumerate(urls):
        try:
            # Prepara as opções de yt-dlp
            ydl_opts = {
                "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
                "format": format_key,
                "noplaylist": True,
                "ignoreerrors": False,
                "progress_hooks": [progress_hook] if show_progress else [],
            }
            
            # Configurações para áudio
            if download_type == "audio":
                ydl_opts["audioformat"] = audio_format
                ydl_opts["postprocessors"] = [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": audio_format,
                    "preferredquality": "192",
                }]
            
            # Configurações para vídeo com qualidade específica
            if quality != "best":
                ydl_opts["format"] = f"{quality}+bestaudio/best"
            
            # Adiciona opções de áudio
            if download_type == "audio":
                ydl_opts["format"] = f"bestaudio[ext={audio_format}]/bestaudio/best"
            
            # Tenta usar ffmpeg se não estiver instalado
            if download_type == "audio":
                ydl_opts["ffmpeg_location"] = "ffmpeg"
            
            # Executa o download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                result = ydl.download([url])
                
                if result == 0:
                    # Tenta encontrar o arquivo baixado
                    files = list(Path(output_dir).glob("*.mp4") + 
                                Path(output_dir).glob("*.webm") +
                                Path(output_dir).glob("*.mp3") +
                                Path(output_dir).glob("*.m4a") +
                                Path(output_dir).glob("*.wav") +
                                Path(output_dir).glob("*.ogg") +
                                Path(output_dir).glob("*.flac"))
                    
                    if files:
                        filename = files[0].name
                        file_size = files[0].stat().st_size
                        results.append({
                            "url": url,
                            "title": ydl_opts.get("outtmpl", "unknown"),
                            "status": "Sucesso",
                            "file": filename,
                            "size": file_size,
                            "duration": ydl_opts.get("format", "")
                        })
                    else:
                        results.append({
                            "url": url,
                            "title": "Desconhecido",
                            "status": "Arquivo não encontrado",
                            "file": "",
                            "size": 0,
                            "duration": ""
                        })
                else:
                    results.append({
                        "url": url,
                        "title": f"Erro {result}",
                        "status": f"Erro: {result}",
                        "file": "",
                        "size": 0,
                        "duration": ""
                    })
            
        except Exception as e:
            results.append({
                "url": url,
                "title": "Erro desconhecido",
                "status": str(e),
                "file": "",
                "size": 0,
                "duration": ""
            })
    
    total_time = time.time() - start_time
    results.append({
        "url": "TOTAL",
        "title": "Resumo",
        "status": f"Tempo total: {format_duration(total_time)}",
        "file": "",
        "size": 0,
        "duration": ""
    })
    
    return results


def progress_hook(d: Dict) -> None:
    """Função de callback para mostrar progresso."""
    if d["status"] == "downloading":
        eta = d.get("eta", "N/A")
        speed = d.get("speed", "N/A")
        downloaded = d.get("downloaded_bytes", 0)
        total = d.get("total_bytes", 0) or d.get("total_bytes_estimate", 0)
        percent = (downloaded / total) * 100 if total > 0 else 0
        print(f"\r  {d['url']}: {percent:.1f}% | {speed} | {format_duration(d['downloaded_bytes'])}/{format_duration(total)} | ETA: {eta}", end="")
    elif d["status"] == "finished":
        print(f"\n  {d['url']}: Concluído")
    elif d["status"] == "error":
        print(f"\n  {d['url']}: Erro - {d.get('error', 'Unknown error')}")


def download_video(url: str, quality: str, format_key: str, output_dir: str) -> Tuple[str, List[Dict]]:
    """Download de vídeo com qualidade específica."""
    if not url:
        return ("", [])
    
    if quality == "best":
        ydl_format = format_key
    else:
        ydl_format = f"{quality}+bestaudio/best"
    
    ydl_opts = {
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "format": ydl_format,
        "noplaylist": True,
        "skip_download": False,
        "progress_hooks": [lambda d: None],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        files = list(Path(output_dir).glob("*.mp4") +
                      Path(output_dir).glob("*.webm") +
                      Path(output_dir).glob("*.mkv"))
        
        if files:
            file_info = files[0].stat().st_size
            return (
                f"Download concluído: {files[0].name}",
                [{"file": files[0].name, "size": file_info}]
            )
        return ("Download concluído (arquivo não encontrado)", [])


def download_audio(url: str, audio_format: str, output_dir: str) -> Tuple[str, List[Dict]]:
    """Download de áudio apenas."""
    if not url:
        return ("", [])
    
    ydl_opts = {
        "outtmpl": os.path.join(output_dir, "%(title)s.%(ext)s"),
        "format": f"bestaudio[ext={audio_format}]/bestaudio/best",
        "noplaylist": True,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": audio_format,
            "preferredquality": "192",
        }],
        "progress_hooks": [lambda d: None],
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        files = list(Path(output_dir).glob("*.mp3") +
                      Path(output_dir).glob("*.m4a") +
                      Path(output_dir).glob("*.wav") +
                      Path(output_dir).glob("*.ogg") +
                      Path(output_dir).glob("*.flac"))
        
        if files:
            file_info = files[0].stat().st_size
            return (
                f"Download concluído: {files[0].name}",
                [{"file": files[0].name, "size": file_info}]
            )
        return ("Download concluído (arquivo não encontrado)", [])


# --- Interface Gradio ---

def create_ui() -> gr.Blocks:
    """Cria e retorna a interface Gradio."""
    
    with gr.Blocks(title="YT-DLP Downloader - Gradio", theme=gr.themes.Soft()) as demo:
        
        gr.Markdown("""
        # 🎬 YT-DLP Downloader - Gradio
        
        Plataforma para download de vídeos e áudios usando **yt-dlp** com interface amigável.
        
        ### Funcionalidades:
        - ✅ Múltiplos links por download
        - ✅ Seleção de qualidade de vídeo
        - ✅ Seleção de formato de áudio
        - ✅ Download de vídeo ou áudio apenas
        - ✅ Escolha do local de saída
        - ✅ Informações detalhadas antes do download
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                gr.Markdown("### 🔗 Insira os Links")
                urls_input = gr.Textbox(
                    label="URLs dos Vídeos",
                    placeholder="Cole os links aqui, um por linha...",
                    lines=6,
                    value="https://www.youtube.com/watch?v=dQw4w9WgXcQ\nhttps://www.youtube.com/watch?v=jfKfPfyJRdk",
                    info="Cole um link por linha. O download será executado para todos os links."
                )
                
                with gr.Row():
                    get_info_btn = gr.Button("🔍 Obter Informações", variant="secondary")
                    clear_btn = gr.Button("🗑️ Limpar", variant="secondary")
            
            with gr.Column(scale=1):
                info_output = gr.Markdown(
                    label="Informações do Vídeo",
                    value="Clique em 'Obter Informações' para ver detalhes sobre os vídeos."
                )
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### ⚙️ Configurações de Download")
                
                with gr.Row():
                    output_dir_input = gr.Textbox(
                        label="📁 Pasta de Saída",
                        value=OUTPUT_DIR,
                        placeholder="C:\Users\\SeuUser\\Downloads" if OS_NAME == "Windows" else "/home/seuuser/Downloads",
                        info="Selecione ou digite o caminho da pasta onde os arquivos serão salvos."
                    )
                
                with gr.Row():
                    download_type = gr.Radio(
                        choices=["video", "audio"],
                        value="video",
                        label="Tipo de Download",
                        info="Vídeo ou apenas áudio"
                    )
                
                with gr.Row():
                    quality = gr.Dropdown(
                        choices=[
                            "best", "4320", "2160", "1440", "1080",
                            "720", "480", "360", "240", "144",
                            "220", "178", "136", "96",
                            "audio"
                        ],
                        value="best",
                        label="Qualidade",
                        info="Melhor qualidade disponível"
                    )
                
                audio_format = gr.Dropdown(
                    choices=["best", "mp3", "m4a", "webm", "opus", "aac", "flac", "wav", "ogg"],
                    value="best",
                    label="Formato de Áudio",
                    info="Qual formato de áudio preferir"
                )
                
                format_key = gr.Dropdown(
                    choices=[
                        "best",
                        "bestvideo+bestaudio/best",
                        "bestvideo/best",
                        "worstvideo/bestaudio/best",
                        "worstaudio/best",
                        "bestaudio/best",
                        "bestaudio/worstvideo/best",
                    ],
                    value="best",
                    label="Formato do Arquivo",
                    info="Formato específico de download"
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Resultados")
                
                with gr.Group():
                    results_output = gr.JSON(
                        label="Status do Download",
                        show_label=False
                    )
                
                with gr.Row():
                    download_btn = gr.Button("⬇️ Iniciar Download", variant="primary", scale=2)
                    download_video_btn = gr.Button("⬇️ Download Rápido (1 vídeo)", variant="secondary", scale=1)
                    download_audio_btn = gr.Button("🎵 Download Rápido (Áudio)", variant="secondary", scale=1)
        
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("### 💾 Arquivos Baixados")
                file_list = gr.Files(label="Arquivos baixados", visible=False)
                clear_files_btn = gr.Button("🗑️ Limpar Arquivos", variant="secondary")
                browse_btn = gr.Button("📂 Escolher Pasta de Saída", variant="primary")
            
            with gr.Column(scale=1):
                gr.Markdown("### 📋 Histórico")
                history_output = gr.Textbox(
                    label="Histórico de Downloads",
                    lines=8,
                    interactive=False
                )
        
        # Eventos
        urls_input.submit(lambda x: x, [urls_input], [urls_input])
        get_info_btn.click(
            fn=get_video_info_wrapper,
            inputs=[urls_input],
            outputs=[info_output]
        )
        download_btn.click(
            fn=run_download,
            inputs=[urls_input, output_dir_input, quality, format_key, download_type, audio_format, OUTPUT_DIR],
            outputs=[results_output]
        )
        download_video_btn.click(
            fn=download_video,
            inputs=[urls_input, quality, format_key, OUTPUT_DIR],
            outputs=[info_output, results_output]
        )
        download_audio_btn.click(
            fn=download_audio,
            inputs=[urls_input, audio_format, OUTPUT_DIR],
            outputs=[info_output, results_output]
        )
        clear_btn.click(
            fn=lambda: "",
            inputs=[],
            outputs=[urls_input]
        )
        clear_files_btn.click(
            fn=lambda: None,
            inputs=[],
            outputs=[file_list]
        )
        
        # Evento para selecionar pasta
        browse_btn.click(
            fn=lambda: os.getcwd(),
            inputs=[],
            outputs=[output_dir_input]
        )
        
        gr.Markdown("""
        ---
        ### 🔧 Instalação
        
        Para rodar esta aplicação localmente:
        ```bash
        pip install gradio yt-dlp
        python app.py
        ```
        
        ### 📝 Requisitos
        
        - **Python 3.9+**
        - **yt-dlp**: `pip install yt-dlp`
        - **FFmpeg**: Necessário para conversão de áudio e formatos específicos.
          - Windows: https://ffmpeg.org/download.html
          - Linux: `sudo apt install ffmpeg`
          - Mac: `brew install ffmpeg`
        - **Permissões**: Certifique-se de ter permissão para escrever no diretório de saída.
        
        ### ⚠️ Notas
        
        - Os arquivos são salvos na pasta especificada em "Pasta de Saída".
        - Certifique-se de ter espaço suficiente no disco.
        - Para downloads de áudio, o FFmpeg é obrigatório.
        """)
    
    return demo


def get_video_info_wrapper(urls_text: str) -> str:
    """Wrapper para obter informações de múltiplos vídeos."""
    urls = [line.strip() for line in urls_text.strip().split('\n') if line.strip()]
    results = []
    
    for url in urls:
        info = get_video_info(url)
        if info:
            results.append(f"""
**{info.title}**
- 🔗 {info.url}
- ⏱️ Duração: {info.duration}
- 📺 Qualidades: {', '.join(info.qualities[:5])}{'...' if len(info.qualities) > 5 else ''}
- 🎵 Áudio: {', '.join(info.audio_formats[:5])}{'...' if len(info.audio_formats) > 5 else ''}
- 📁 Formatos: {', '.join(info.available_formats[:5])}{'...' if len(info.available_formats) > 5 else ''}
- 🖼️ [Miniatura]({info.thumbnail})
""")
        else:
            results.append(f"❌ Erro ao obter info para: {url}")
    
    return "\n\n---\n\n".join(results)


# --- Execução ---

if __name__ == "__main__":
    demo = create_ui()
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False, show_error=True)
