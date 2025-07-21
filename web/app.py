#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR音频识别系统Web应用
"""

import os
import json
import time
import numpy as np
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename
import threading
import queue
from funasr import AutoModel
import base64

# 初始化Flask应用和SocketIO
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ocr-audio-recognition-system'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 限制上传文件大小为16MB
socketio = SocketIO(app, cors_allowed_origins="*")

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 允许的文件类型
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf'}

# 文件分类
FILE_CATEGORIES = {
    "发票类": ["发票", "税票", "收据"],
    "合同类": ["合同", "协议", "结算"],
    "证书类": ["证书", "资质", "许可"],
    "其他类": ["其他", "未分类"]
}

# 音频参数
SAMPLE_RATE = 16000
# Web端使用8192作为缓冲区大小（2的幂）
CHUNK_SIZE = 8192

# 模型实例和音频队列字典，用于多用户同时访问
models = {}
audio_queues = {}
recorded_texts = {}

def allowed_file(filename):
    """检查文件类型是否允许上传"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def auto_categorize_file(filename):
    """根据文件名自动分类"""
    filename_lower = filename.lower()
    
    for category, keywords in FILE_CATEGORIES.items():
        for keyword in keywords:
            if keyword in filename_lower:
                return category
    
    # 默认分类
    return "其他类"

def initialize_model(sid):
    """为每个用户会话初始化模型"""
    if sid not in models:
        try:
            # 根据实际情况调整模型路径
            models[sid] = AutoModel(model="E:\Huggingface\models\paraformer-zh-streaming", disable_update=True)
            audio_queues[sid] = queue.Queue()
            recorded_texts[sid] = ""
            return True
        except Exception as e:
            print(f"模型加载失败: {e}")
            return False
    return True

def process_audio(sid):
    """音频处理函数"""
    if sid not in models or sid not in audio_queues:
        return
        
    cache = {}
    chunk_count = 0
    
    try:
        while True:
            try:
                # 从队列获取音频数据
                speech_chunk = audio_queues[sid].get(timeout=1.0)
                
                if speech_chunk is None:  # 结束信号
                    break
                
                chunk_count += 1
                print(f"处理音频块 {chunk_count}, 形状={speech_chunk.shape}")
                    
                # 处理音频块
                res = models[sid].generate(
                    input=speech_chunk,
                    cache=cache,
                    is_final=False,
                    chunk_size=[0, 10, 5],
                    encoder_chunk_look_back=4,
                    decoder_chunk_look_back=1
                )
                
                if res and len(res) > 0:
                    text = res[0].get('text', '')
                    if text.strip():
                        # 将识别结果通过WebSocket发送给客户端
                        recorded_texts[sid] += text + " "
                        socketio.emit('recognition_result', {'text': text}, room=sid)
                
            except queue.Empty:
                continue
                
    except Exception as e:
        print(f"音频处理错误: {e}")
        
    finally:
        # 清理资源
        if sid in audio_queues:
            while not audio_queues[sid].empty():
                audio_queues[sid].get()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html', categories=list(FILE_CATEGORIES.keys()))

@app.route('/upload', methods=['POST'])
def upload_file():
    """处理文件上传和OCR请求"""
    if 'file' not in request.files:
        return jsonify({'status': 'error', 'message': '没有文件上传'}), 400
        
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'status': 'error', 'message': '未选择文件'}), 400
        
    if not file or not allowed_file(file.filename):
        return jsonify({'status': 'error', 'message': '不支持的文件类型'}), 400
    
    try:
        # 保存上传文件
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 获取表单数据
        category = request.form.get('category', auto_categorize_file(filename))
        audio_text = request.form.get('audio_text', '')
        api_url = request.form.get('api_url', 'http://localhost:8080/upload')
        
        # TODO: 这里应该调用实际的OCR API处理文件
        # 模拟处理过程
        time.sleep(2)  # 模拟处理时间
        
        # 返回处理结果
        result = {
            'status': 'success',
            'processing_time': '2.0秒',
            'result': f'文件 {filename} 已成功处理，分类为 {category}，音频文本: {audio_text[:50]}...',
            'file_path': filepath
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """处理WebSocket连接"""
    print(f'客户端连接: {request.sid}')
    # 初始化模型
    if initialize_model(request.sid):
        emit('model_status', {'status': 'ready'})
    else:
        emit('model_status', {'status': 'error', 'message': '模型加载失败'})

@socketio.on('disconnect')
def handle_disconnect():
    """处理WebSocket断开连接"""
    print(f'客户端断开连接: {request.sid}')
    sid = request.sid
    
    # 清理资源
    if sid in audio_queues:
        audio_queues[sid].put(None)  # 发送结束信号
    
    # 删除会话相关资源
    if sid in models:
        del models[sid]
    if sid in recorded_texts:
        del recorded_texts[sid]

@socketio.on('start_recording')
def handle_start_recording():
    """开始录音"""
    sid = request.sid
    
    if not initialize_model(sid):
        emit('error', {'message': '模型初始化失败'})
        return
    
    # 清空之前的录音文本
    recorded_texts[sid] = ""
    
    # 启动音频处理线程
    threading.Thread(target=process_audio, args=(sid,), daemon=True).start()
    
    emit('recording_status', {'status': 'started'})

@socketio.on('stop_recording')
def handle_stop_recording():
    """停止录音"""
    sid = request.sid
    
    if sid in audio_queues:
        audio_queues[sid].put(None)  # 发送结束信号
    
    # 返回完整的录音文本
    if sid in recorded_texts:
        emit('recording_complete', {'text': recorded_texts[sid]})
    
    emit('recording_status', {'status': 'stopped'})

@socketio.on('clear_recording')
def handle_clear_recording():
    """清除录音"""
    sid = request.sid
    
    if sid in recorded_texts:
        recorded_texts[sid] = ""
    
    emit('recording_status', {'status': 'cleared'})

@socketio.on('audio_data')
def handle_audio_data(data):
    """处理音频数据"""
    sid = request.sid
    
    if sid not in audio_queues:
        return
    
    try:
        # 解析Base64音频数据
        audio_bytes = base64.b64decode(data['audio'])
        buffer_size = data.get('bufferSize', 8192)
        
        # 确保使用正确的数据类型和归一化方法，与桌面端保持一致
        audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
        
        # 检查和确保音频数据的范围在[-1.0, 1.0]之间
        max_abs = np.max(np.abs(audio_data))
        if max_abs > 1.0:
            audio_data = audio_data / max_abs  # 归一化到[-1.0, 1.0]范围
        
        # 如果音频数据为空或异常，记录并返回
        if audio_data.size == 0:
            print(f"警告: 收到空的音频数据")
            return
            
        # 添加调试信息（每10次只输出一次，避免日志过多）
        if not hasattr(handle_audio_data, 'log_counter'):
            handle_audio_data.log_counter = 0
        if handle_audio_data.log_counter % 10 == 0:
            print(f"接收音频数据: 形状={audio_data.shape}, 最小值={np.min(audio_data):.4f}, 最大值={np.max(audio_data):.4f}, 缓冲区大小={buffer_size}")
        handle_audio_data.log_counter += 1
        
        # 将音频数据放入队列
        audio_queues[sid].put(audio_data)
        
    except Exception as e:
        print(f"音频数据处理错误: {e}")
        import traceback
        traceback.print_exc()



@socketio.on('check_file')
def handle_check_file(data):
    """检查文件并返回自动分类结果"""
    filename = data.get('filename', '')
    category = auto_categorize_file(filename)
    emit('file_category', {'category': category})

@socketio.on('update_recognition_text')
def handle_update_recognition_text(data):
    """处理用户手动编辑的音频识别文本"""
    sid = request.sid
    new_text = data.get('text', '')
    
    # 更新保存的文本
    if sid in recorded_texts:
        recorded_texts[sid] = new_text
        emit('recognition_updated', {'success': True})
    else:
        emit('recognition_updated', {'success': False, 'message': '未找到会话数据'})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)
