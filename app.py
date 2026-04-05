import os, uuid
from flask import Flask, render_template, request, send_file, after_this_request
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = "downloads"

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    unique_id = str(uuid.uuid4())[:8]
    
    ydl_opts = {
        'format': 'best',
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s_{unique_id}.%(ext)s',
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)

        @after_this_request
        def cleanup(response):
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"Error cleaning up: {e}")
            return response

        return send_file(path, as_attachment=True)
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
  
