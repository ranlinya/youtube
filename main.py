from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from pytube import YouTube
import os

app = Flask(__name__, 
    template_folder='templates',
    static_folder='static'
)
CORS(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download_video():
    try:
        url = request.json.get('url')
        if not url:
            return jsonify({'error': '请提供YouTube URL'}), 400
            
        yt = YouTube(url)
        video = yt.streams.get_highest_resolution()
        
        # 获取视频信息
        video_info = {
            'title': yt.title,
            'duration': yt.length,
            'uploader': yt.author,
            'filesize': video.filesize,
            'file_path': video.default_filename
        }
        
        # 下载视频到临时目录
        download_path = os.path.join(os.getcwd(), 'downloads')
        os.makedirs(download_path, exist_ok=True)
        video.download(download_path)
        
        return jsonify(video_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(e):
    return "404 - 页面未找到", 404

@app.errorhandler(500)
def server_error(e):
    return "500 - 服务器错误", 500

if __name__ == '__main__':
    app.run(debug=True)