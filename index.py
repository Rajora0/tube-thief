from flask import Flask, Response, request, render_template
import yt_dlp
import threading

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        try:
            return download_video(url)
        except Exception as e:
            return render_template("index.html", message=f"Erro ao iniciar download: {e}")
    return render_template("index.html")

def download_video(url):
    # Configurações do yt-dlp
    ydl_opts = {
        'format': 'best',
        'quiet': True,  # Suprimir a saída de log
    }

    # Captura o nome do vídeo e gera o arquivo no formato de bytes
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        filename = f"{info_dict['title']}.mp4"
        
        # O método 'ydl.download' é modificado para retornar um gerador de bytes
        def generate():
            # Usando a opção de download em fluxo
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.params['progress_hooks'] = [lambda d: None]  # Suprimir o progresso
                ydl.download([url])

        return Response(generate(), mimetype='video/mp4', headers={
            'Content-Disposition': f'attachment; filename="{filename}"'
        })

if __name__ == "__main__":
    app.run(debug=True)
