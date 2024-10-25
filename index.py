from flask import Flask, render_template, request, send_from_directory, jsonify
import yt_dlp
import os
import threading

app = Flask(__name__)

# Configura o diretório temporário para os downloads
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
    
    arquivos = os.listdir(app.config['UPLOAD_FOLDER'])
    return render_template("index.html", download_completo=download_completo, arquivos=arquivos)

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

@app.route("/downloads/<filename>")
def downloads(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# Novo endpoint para retornar a lista de arquivos em JSON
@app.route("/atualizar_arquivos")
def atualizar_arquivos():
    arquivos = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify(arquivos)

@app.route("/favicon.ico")
def favicon():
    return app.send_static_file('favicon.ico')

if __name__ == "__main__":
    app.run(debug=True)
