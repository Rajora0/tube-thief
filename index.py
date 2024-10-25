from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        url = request.form["url"]
        try:
            # Chama a função para baixar e retornar o vídeo
            return download_video(url)
        except Exception as e:
            return render_template("index.html", message=f"Erro ao iniciar download: {e}")
    return render_template("index.html")

def download_video(url):
    # Configurações do yt-dlp
    ydl_opts = {
        'format': 'best',
        'outtmpl': '/tmp/%(title)s.%(ext)s',  # Salva temporariamente no diretório /tmp
        'noplaylist': True,  # Para garantir que só o vídeo único seja baixado
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Baixa o vídeo
        info_dict = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info_dict)  # Pega o caminho do arquivo baixado

    # Retorna o arquivo para download no navegador
    return send_file(filename, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
