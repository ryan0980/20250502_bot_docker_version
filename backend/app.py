from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import requests
from pathlib import Path
from dotenv import load_dotenv
from video_separator import separate_video
from video_analyzer import analyze_all_videos
from sum_up import combine_analysis_results
import uuid
import cv2
import numpy as np
import tempfile
import time
from werkzeug.utils import secure_filename

# 加载环境变量
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
else:
    print("Warning: .env file not found, using system environment variables")

app = Flask(__name__)
CORS(app)

# 确保上传目录存在
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('separated_videos', exist_ok=True)

def get_video_frame(video_path, timestamp):
    """获取视频指定时间点的帧"""
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_number = int(timestamp * fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return None
    
    return frame

@app.route('/api/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'video' not in request.files:
        return jsonify({"error": "没有文件被上传"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"error": "没有选择文件"}), 400
    
    if file:
        # 保存文件
        filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filename)
        
        try:
            # 分割视频
            separated_videos = separate_video(filename)
            
            # 分析视频
            analysis_results = analyze_all_videos(separated_videos)
            
            # 汇总分析结果
            combined_result = combine_analysis_results(analysis_results)
            
            return jsonify({
                "message": "File uploaded, split and analyzed successfully",
                "filename": file.filename,
                "separated_videos": separated_videos,
                "analysis_results": analysis_results,
                "combined_result": combined_result
            }), 200
        except Exception as e:
            return jsonify({
                "error": f"处理失败: {str(e)}",
                "filename": file.filename
            }), 500

@app.route('/api/upload-url', methods=['POST'])
def upload_from_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "请提供视频URL"}), 400
    
    url = data['url']
    try:
        # 下载视频
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # 生成唯一文件名
        filename = f"{uuid.uuid4()}.mp4"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 保存文件
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        try:
            # 分割视频
            separated_videos = separate_video(filepath)
            
            # 分析视频
            analysis_results = analyze_all_videos(separated_videos)
            
            # 汇总分析结果
            combined_result = combine_analysis_results(analysis_results)
            
            return jsonify({
                "message": "文件上传、分割和分析成功",
                "filename": filename,
                "separated_videos": separated_videos,
                "analysis_results": analysis_results,
                "combined_result": combined_result
            }), 200
        except Exception as e:
            return jsonify({
                "error": f"处理失败: {str(e)}",
                "filename": filename
            }), 500
            
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"下载视频失败: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"处理失败: {str(e)}"}), 500

@app.route('/api/get_frame', methods=['POST'])
def get_frame():
    try:
        data = request.json
        video_path = data.get('video_path')
        timestamp = float(data.get('timestamp', 0))
        
        if not video_path or not os.path.exists(video_path):
            return jsonify({'error': '视频文件不存在'}), 400
        
        frame = get_video_frame(video_path, timestamp)
        if frame is None:
            return jsonify({'error': '无法获取指定时间点的帧'}), 400
        
        # 将帧保存为临时文件
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg', delete=False)
        cv2.imwrite(temp_file.name, frame)
        
        return send_file(
            temp_file.name,
            mimetype='image/jpeg',
            as_attachment=True,
            download_name=f'frame_{timestamp}.jpg'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000) 