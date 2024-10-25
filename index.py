from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os
import threading

app = Flask(__name__)

# Configura o diretório temporário no Vercel
app.config['UPLOAD_FOLDER'] = '/tmp/downloads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Variável global para indicar o status do download
download_completo = False

@app.route("/", methods=["GET", "POST"])
def index():
    global download_completo
    if request.method == "POST":
        url = request.form["url"]
        try:
            # Inicia uma thread separada para o download
            download_thread = threading.Thread(target=download_video, args=(url,))
            download_thread.start()
            download_completo = False  # Reseta o status do download
            return render_template("index.html", message="Download iniciado em background!")
        except Exception as e:
            return render_template("index.html", message=f"Erro ao iniciar download: {e}")
    return render_template("index.html", download_completo=download_completo)

def download_video(url):
    global download_completo
    ydl_opts = {
        'format': 'best',
        'outtmpl': os.path.join(app.config['UPLOAD_FOLDER'], '%(title)s.%(ext)s')
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Limpa a pasta de downloads antes de iniciar o download
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        # Inicia o download
        ydl.download([url])
    download_completo = True  # Define o status do download como completo

@app.route("/downloads")
def downloads():
    global download_completo
    if download_completo:
        arquivos = os.listdir(app.config['UPLOAD_FOLDER'])
        if arquivos:
            ultimo_arquivo = max(arquivos, key=lambda x: os.path.getctime(os.path.join(app.config['UPLOAD_FOLDER'], x)))
            return send_from_directory(app.config['UPLOAD_FOLDER'], ultimo_arquivo, as_attachment=True)
        else:
            return "Nenhum arquivo encontrado", 404
    else:
        return "Download ainda não concluído", 202  # Código 202 para "Accepted"

if __name__ == "__main__":
    app.run(debug=True)
