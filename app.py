import gradio as gr
import yt_dlp
import os

def download_media(urls_text, media_type, video_quality, video_format, audio_format, output_path):
    if not urls_text.strip():
        return "Nenhum link fornecido. Por favor, insira pelo menos um link."
    
    # Separa os links por quebra de linha
    url_list = [url.strip() for url in urls_text.split('\n') if url.strip()]
    
    # Verifica e cria o diretório de saída se não existir
    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path)
        except Exception as e:
            return f"Erro ao criar o diretório de destino: {e}"

    # Configuração base do yt-dlp
    ydl_opts = {
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'ignoreerrors': True, # Pula para o próximo caso um link dê erro
    }

    # Configurações específicas para Vídeo
    if media_type == "Vídeo":
        quality_map = {
            "Melhor disponível": "bestvideo+bestaudio/best",
            "1080p": "bestvideo[height<=1080]+bestaudio/best",
            "720p": "bestvideo[height<=720]+bestaudio/best",
            "480p": "bestvideo[height<=480]+bestaudio/best",
            "360p": "bestvideo[height<=360]+bestaudio/best",
        }
        ydl_opts['format'] = quality_map.get(video_quality, 'best')
        
        if video_format != "Padrão (qualquer)":
            ydl_opts['merge_output_format'] = video_format

    # Configurações específicas para Áudio
    elif media_type == "Áudio":
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192', # Qualidade padrão do áudio
        }]

    success_count = 0
    errors = []

    # Inicia o download
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in url_list:
            try:
                # O yt-dlp retorna um código de erro diferente de 0 se falhar
                error_code = ydl.download([url])
                if error_code == 0:
                    success_count += 1
                else:
                    errors.append(f"Erro ao baixar: {url}")
            except Exception as e:
                errors.append(f"Erro no link {url}: {str(e)}")

    # Formata a mensagem de retorno
    result_msg = f"✅ Concluído! {success_count} de {len(url_list)} arquivos baixados com sucesso na pasta:\n{os.path.abspath(output_path)}"
    
    if errors:
        result_msg += "\n\n⚠️ Avisos/Erros:\n" + "\n".join(errors)
        
    return result_msg

# --- Interface Gráfica com Gradio ---
with gr.Blocks(title="Downloader de Mídia local") as app:
    gr.Markdown("# 🔻 YT-DLP Web Downloader")
    gr.Markdown("Cole os links abaixo (um por linha) e configure as opções de download.")

    with gr.Row():
        with gr.Column(scale=2):
            urls_input = gr.Textbox(
                label="Links dos Vídeos (um por linha)", 
                lines=8, 
                placeholder="https://www.youtube.com/watch?v=..."
            )
            
            output_dir_input = gr.Textbox(
                label="Pasta de Destino", 
                value="./downloads", 
                info="Caminho absoluto ou relativo onde os arquivos serão salvos."
            )
            
            download_btn = gr.Button("Iniciar Download", variant="primary")
            
        with gr.Column(scale=1):
            media_type = gr.Radio(
                choices=["Vídeo", "Áudio"], 
                value="Vídeo", 
                label="O que você deseja baixar?"
            )
            
            # Agrupamento de opções de Vídeo
            with gr.Group(visible=True) as video_options:
                video_quality = gr.Dropdown(
                    choices=["Melhor disponível", "1080p", "720p", "480p", "360p"], 
                    value="Melhor disponível", 
                    label="Qualidade do Vídeo"
                )
                video_format = gr.Dropdown(
                    choices=["Padrão (qualquer)", "mp4", "mkv", "webm"], 
                    value="mp4", 
                    label="Formato do Vídeo"
                )
                
            # Agrupamento de opções de Áudio
            with gr.Group(visible=False) as audio_options:
                audio_format = gr.Dropdown(
                    choices=["mp3", "wav", "m4a", "flac"], 
                    value="mp3", 
                    label="Formato do Áudio"
                )

    status_output = gr.Textbox(label="Status do Download", lines=4, interactive=False)

    # Lógica para mostrar/esconder opções baseadas na escolha (Áudio ou Vídeo)
    def toggle_options(choice):
        if choice == "Vídeo":
            return gr.update(visible=True), gr.update(visible=False)
        else:
            return gr.update(visible=False), gr.update(visible=True)

    media_type.change(
        fn=toggle_options, 
        inputs=media_type, 
        outputs=[video_options, audio_options]
    )

    # Ação do botão
    download_btn.click(
        fn=download_media,
        inputs=[
            urls_input, 
            media_type, 
            video_quality, 
            video_format, 
            audio_format, 
            output_dir_input
        ],
        outputs=status_output
    )

# Roda a aplicação
if __name__ == "__main__":
    app.launch()