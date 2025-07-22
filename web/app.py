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

def format_ocr_result(ocr_response):
    """
    格式化OCR响应结果
    处理JSON响应中的result字段，并将转义字符转换为实际字符
    """
    try:
        # 如果输入是字符串，尝试解析为JSON
        if isinstance(ocr_response, str):
            try:
                parsed_response = json.loads(ocr_response)
            except json.JSONDecodeError:
                # 如果不是JSON，直接处理文本
                return ocr_response.replace('\\n', '\n').replace('\\t', '\t')
        else:
            parsed_response = ocr_response
        
        # 如果响应包含result字段，提取并格式化
        if isinstance(parsed_response, dict) and 'result' in parsed_response:
            result_text = parsed_response['result']
            if isinstance(result_text, str):
                # 将转义的换行符转换为实际换行符
                formatted_text = result_text.replace('\\n', '\n')
                formatted_text = formatted_text.replace('\\t', '\t')
                formatted_text = formatted_text.replace('\\"', '"')
                formatted_text = formatted_text.replace("\\'", "'")
                formatted_text = formatted_text.replace('\\\\', '\\')
                return formatted_text
            else:
                return str(result_text)
        else:
            # 如果没有result字段，返回原始响应
            return json.dumps(parsed_response, ensure_ascii=False, indent=2)
            
    except Exception as e:
        print(f"格式化OCR结果时出错: {e}")
        return str(ocr_response)

def call_ocr_api(file_path, category, audio_text):
    """
    调用OCR API处理文件
    这里应该替换为实际的OCR API调用
    """
    # TODO: 替换为实际的OCR API调用
    # 现在返回模拟的结果，格式与您提供的示例一致
    mock_response = {
        "result": "发票号码：051002100204\\n机器编号：127011985051\\n开票日期：2022年06月08日\\n购买方名称：中国石油天然气股份有限公司西南油气田分公司川西北气矿\\n购买方纳税人识别号：91510781720845511K\\n购买方地址：江油市李白大道南一段517号\\n购买方电话：0816-3611151\\n购买方开户行及账号：江油市工行明月新城支行2308422509100002749\\n货物或应税劳务、服务名称：餐饮服务餐饮费\\n规格型号：无\\n单位：顿\\n数量：1\\n单价：1665.00\\n金额：￥1665.00\\n税率：免税\\n税额：0.00\\n合计（小写）：￥1665.00\\n价税合计（大写）：壹仟陆佰陆拾伍圆整\\n校验码：14075 23769 4451927788\\n销售方名称：苍溪县鸳溪镇双双农家乐\\n销售方纳税人识别号：92510824MA639P198U\\n销售方地址：苍溪县鸳溪镇口梁村四组\\n销售方电话：18383961723\\n销售方开户行及账号：四川农商银行鸳溪支行6214590782007087422\\n复核：杨洪双\\n开票人：杨洪双\\n收款人：杨洪双\\n发票专用章编号：5108245053742"
    }
    
    # 格式化结果
    formatted_result = format_ocr_result(mock_response)
    
    return {
        'status': 'success',
        'ocr_result': formatted_result,
        'category': category,
        'audio_text': audio_text,
        'file_path': file_path
    }

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
# 与桌面端保持一致的音频块大小（600ms）
DESKTOP_CHUNK_SIZE = int(SAMPLE_RATE * 600 / 1000)  # 9600 samples
# Web Audio API使用的缓冲区大小（2的幂）
WEB_BUFFER_SIZE = 16384

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
    """音频处理函数 - 与桌面端保持一致的参数"""
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
                    
                # 使用与桌面端完全一致的参数处理音频块
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
        import traceback
        traceback.print_exc()
        
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
        metadata = request.form.get('metadata', '{}')
        metadata_dict = json.loads(metadata)
        
        category = metadata_dict.get('category', auto_categorize_file(filename))
        audio_text = metadata_dict.get('audio_text', '')
        
        # 打印接收到的数据
        print("接收到的OCR处理请求数据:")
        print(f"文件名: {filename}")
        print(f"分类: {category}")
        print(f"音频文本: {audio_text}")
        print(f"元数据: {json.dumps(metadata_dict, ensure_ascii=False, indent=2)}")
        
        # 调用OCR API处理文件
        print("开始OCR处理...")
        ocr_result = call_ocr_api(filepath, category, audio_text)
        
        # 返回处理结果
        result = {
            'status': ocr_result['status'],
            'processing_time': '2.0秒',  # 实际应该计算处理时间
            'result': ocr_result['ocr_result'],  # 只返回格式化后的OCR文本
            'category': ocr_result['category'],
            'file_path': ocr_result['file_path']
        }
        
        print(f"OCR处理完成，结果长度: {len(result['result'])}")
        return jsonify(result)
        
    except Exception as e:
        print(f"处理文件上传时出错: {e}")
        import traceback
        traceback.print_exc()
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
        buffer_size = data.get('bufferSize', DESKTOP_CHUNK_SIZE)
        expected_chunk_size = data.get('expectedChunkSize', DESKTOP_CHUNK_SIZE)
        
        # 前端发送的是Float32Array格式的音频数据（已经归一化到[-1.0, 1.0]范围）
        audio_data = np.frombuffer(audio_bytes, dtype=np.float32)
        
        # 如果音频数据为空或异常，记录并返回
        if audio_data.size == 0:
            print(f"警告: 收到空的音频数据")
            return
        
        # 验证音频数据范围
        max_abs = np.max(np.abs(audio_data))
        if max_abs > 1.0:
            print(f"警告: 音频数据超出范围 [-1.0, 1.0], max_abs={max_abs:.4f}, 进行归一化")
            audio_data = audio_data / max_abs
        
        # 确保音频数据长度与桌面端一致（9600样本）
        if audio_data.size != DESKTOP_CHUNK_SIZE:
            print(f"警告: 音频块大小不匹配，期望={DESKTOP_CHUNK_SIZE}, 实际={audio_data.size}")
            if audio_data.size < DESKTOP_CHUNK_SIZE:
                # 填充零到目标长度
                padded_audio = np.zeros(DESKTOP_CHUNK_SIZE, dtype=np.float32)
                padded_audio[:audio_data.size] = audio_data
                audio_data = padded_audio
            else:
                # 截断到目标长度
                audio_data = audio_data[:DESKTOP_CHUNK_SIZE]
            print(f"已调整音频块大小到: {audio_data.size}")
        
        # 计算音频质量指标
        rms = np.sqrt(np.mean(audio_data ** 2))
        min_val = np.min(audio_data)
        max_val = np.max(audio_data)
            
        # 添加调试信息（每10次只输出一次，避免日志过多）
        if not hasattr(handle_audio_data, 'log_counter'):
            handle_audio_data.log_counter = 0
        if handle_audio_data.log_counter % 10 == 0:
            print(f"接收音频数据: 形状={audio_data.shape}, 范围=[{min_val:.4f}, {max_val:.4f}], RMS={rms:.6f}, 期望块大小={expected_chunk_size}")
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
