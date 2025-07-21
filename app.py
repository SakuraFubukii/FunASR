#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR音频识别系统 - Web版本
"""

from flask import Flask, render_template, request, jsonify, session, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import json
import threading
import time
import queue
import numpy as np
import io
import base64
import wave
import sys
import flask
from funasr import AutoModel
import requests
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# 添加CORS支持
CORS(app)

socketio = SocketIO(app, cors_allowed_origins="*")

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 全局变量
asr_model = None
audio_processors = {}  # 存储每个会话的音频处理器

# 文件分类配置
FILE_CATEGORIES = {
    "发票类": ["发票", "税票", "收据"],
    "合同类": ["合同", "协议", "结算"],
    "证书类": ["证书", "资质", "许可"],
    "其他类": ["其他", "未分类"]
}

# 音频参数
SAMPLE_RATE = 16000
CHUNK_DURATION_MS = 600
CHUNK_SIZE_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)

class AudioProcessor:
    """音频处理器"""
    def __init__(self, session_id):
        self.session_id = session_id
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recorded_text = ""
        self.cache = {}
        
    def start_recording(self):
        """开始录音处理"""
        self.is_recording = True
        self.recorded_text = ""
        self.cache = {}
        
    def stop_recording(self):
        """停止录音处理"""
        self.is_recording = False
        
    def process_audio_chunk(self, audio_data):
        """处理音频块"""
        if not self.is_recording or not asr_model:
            return None
            
        try:
            res = asr_model.generate(
                input=audio_data,
                cache=self.cache,
                is_final=False,
                chunk_size=[0, 10, 5],
                encoder_chunk_look_back=4,
                decoder_chunk_look_back=1
            )
            
            if res and len(res) > 0:
                text = res[0].get('text', '')
                if text.strip():
                    self.recorded_text += text + " "
                    return text
        except Exception as e:
            print(f"音频处理错误: {e}")
            
        return None

def load_asr_model():
    """加载ASR模型"""
    global asr_model
    try:
        model_path = r"E:\Huggingface\models\paraformer-zh-streaming"
        if os.path.exists(model_path):
            asr_model = AutoModel(model=model_path, disable_update=True)
            print("ASR模型加载成功")
        else:
            print(f"模型路径不存在: {model_path}")
    except Exception as e:
        print(f"ASR模型加载失败: {e}")
        asr_model = None

def auto_categorize_file(filename):
    """根据文件名自动分类"""
    filename_lower = filename.lower()
    
    for category, keywords in FILE_CATEGORIES.items():
        for keyword in keywords:
            if keyword in filename_lower:
                return category
    
    return "其他类"

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', categories=list(FILE_CATEGORIES.keys()))

@app.route('/debug')
def debug_index():
    """调试版主页"""
    return render_template('index_debug.html', categories=list(FILE_CATEGORIES.keys()))

@app.route('/api/status')
def status():
    """系统状态检查接口"""
    try:
        import funasr
        funasr_version = getattr(funasr, '__version__', 'unknown')
    except ImportError:
        funasr_version = 'not installed'
    
    return jsonify({
        'status': 'running',
        'timestamp': time.time(),
        'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
        'flask_version': flask.__version__,
        'funasr_version': funasr_version,
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'upload_folder_exists': os.path.exists(app.config['UPLOAD_FOLDER']),
        'asr_model_loaded': asr_model is not None,
        'categories': list(FILE_CATEGORIES.keys())
    })

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        print("收到文件上传请求")
        print(f"请求文件: {request.files}")
        print(f"请求表单: {request.form}")
        
        if 'file' not in request.files:
            print("错误: 请求中没有文件")
            return jsonify({'error': '没有文件'}), 400
            
        file = request.files['file']
        print(f"文件对象: {file}")
        print(f"文件名: {file.filename}")
        
        if file.filename == '':
            print("错误: 文件名为空")
            return jsonify({'error': '文件名为空'}), 400
            
        if file:
            filename = secure_filename(file.filename)
            print(f"安全文件名: {filename}")
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            print(f"保存路径: {filepath}")
            
            # 确保目录存在
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            
            file.save(filepath)
            print(f"文件已保存: {filepath}")
            
            # 检查文件是否真的保存了
            if os.path.exists(filepath):
                file_size = os.path.getsize(filepath)
                print(f"文件大小: {file_size} bytes")
                
                # 自动分类
                category = auto_categorize_file(filename)
                print(f"建议分类: {category}")
                
                result = {
                    'success': True,
                    'filename': filename,
                    'suggested_category': category,
                    'file_size': file_size
                }
                print(f"返回结果: {result}")
                return jsonify(result)
            else:
                print("错误: 文件保存失败")
                return jsonify({'error': '文件保存失败'}), 500
            
    except Exception as e:
        print(f"上传异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'文件上传失败: {str(e)}'}), 500

@app.route('/api/process_ocr', methods=['POST'])
def process_ocr():
    """OCR处理接口"""
    try:
        data = request.json
        filename = data.get('filename')
        category = data.get('category')
        audio_text = data.get('audio_text', '')
        api_url = data.get('api_url', 'http://localhost:5000/upload')
        
        if not filename:
            return jsonify({'error': '文件名不能为空'}), 400
            
        if not category:
            return jsonify({'error': '请选择文件分类'}), 400
            
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if not os.path.exists(filepath):
            return jsonify({'error': '文件不存在'}), 404
            
        # 准备数据
        ocr_data = {
            "category": category,
            "audio_text": audio_text.strip(),
            "file_info": {
                "name": filename,
                "size": os.path.getsize(filepath)
            }
        }
        
        # 发送OCR请求
        with open(filepath, 'rb') as f:
            files = {'file': (filename, f)}
            response = requests.post(
                api_url,
                files=files,
                data={'metadata': json.dumps(ocr_data)},
                timeout=300
            )
        
        if response.status_code == 200:
            try:
                result = response.json()
                return jsonify({
                    'success': True,
                    'result': result,
                    'processing_time': result.get('processing_time', 'Unknown'),
                    'category': category,
                    'audio_text': audio_text
                })
            except json.JSONDecodeError:
                return jsonify({
                    'error': f'服务器返回了非JSON格式的响应: {response.text}'
                }), 500
        else:
            return jsonify({
                'error': f'OCR请求失败，状态码: {response.status_code}, 错误信息: {response.text}'
            }), 500
            
    except requests.exceptions.Timeout:
        return jsonify({'error': '请求超时，请检查网络连接或服务器状态'}), 408
    except requests.exceptions.ConnectionError:
        return jsonify({'error': '连接失败，请检查API地址是否正确或服务器是否正在运行'}), 503
    except Exception as e:
        return jsonify({'error': f'处理失败: {str(e)}'}), 500

@socketio.on('start_recording')
def handle_start_recording():
    """开始录音"""
    session_id = request.sid
    
    if not asr_model:
        emit('recording_error', {'error': '语音识别模型未加载'})
        return
        
    if session_id not in audio_processors:
        audio_processors[session_id] = AudioProcessor(session_id)
        
    audio_processors[session_id].start_recording()
    emit('recording_started', {'status': 'recording'})

@socketio.on('stop_recording')
def handle_stop_recording():
    """停止录音"""
    session_id = request.sid
    
    if session_id in audio_processors:
        audio_processors[session_id].stop_recording()
        
    emit('recording_stopped', {'status': 'stopped'})

@socketio.on('audio_data')
def handle_audio_data(data):
    """处理音频数据"""
    session_id = request.sid
    
    if session_id not in audio_processors:
        return
        
    processor = audio_processors[session_id]
    if not processor.is_recording:
        return
        
    try:
        # 解码音频数据 (base64 -> bytes -> numpy array)
        audio_bytes = base64.b64decode(data['audio'])
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
        
        # 处理音频
        text = processor.process_audio_chunk(audio_array)
        if text:
            emit('speech_result', {
                'text': text,
                'accumulated_text': processor.recorded_text
            })
            
    except Exception as e:
        print(f"音频数据处理错误: {e}")
        emit('recording_error', {'error': f'音频处理错误: {str(e)}'})

@socketio.on('clear_recording')
def handle_clear_recording():
    """清除录音"""
    session_id = request.sid
    
    if session_id in audio_processors:
        audio_processors[session_id].recorded_text = ""
        audio_processors[session_id].cache = {}
        
    emit('recording_cleared', {'status': 'cleared'})

@socketio.on('get_recorded_text')
def handle_get_recorded_text():
    """获取录音文本"""
    session_id = request.sid
    
    if session_id in audio_processors:
        text = audio_processors[session_id].recorded_text
        emit('recorded_text', {'text': text})
    else:
        emit('recorded_text', {'text': ''})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    session_id = request.sid
    if session_id in audio_processors:
        del audio_processors[session_id]

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """提供上传文件的访问"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    # 启动时加载模型
    print("正在加载ASR模型...")
    load_asr_model()
    
    # 启动Web服务器
    print("启动Web服务器...")
    socketio.run(app, host='0.0.0.0', port=8080, debug=False)
