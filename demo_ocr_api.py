#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
演示用OCR API服务器
用于测试OCR音频识别系统的Web版本
"""

from flask import Flask, request, jsonify
import json
import time
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'demo_uploads'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

# 确保上传目录存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 模拟OCR结果数据
DEMO_OCR_RESULTS = {
    "发票类": {
        "发票号码": "No: 12345678",
        "开票日期": "2024-01-15",
        "销售方": "示例科技有限公司",
        "购买方": "客户企业名称",
        "商品名称": "技术服务费",
        "金额": "¥1,000.00",
        "税额": "¥130.00",
        "价税合计": "¥1,130.00",
        "备注": "技术咨询服务"
    },
    "合同类": {
        "合同编号": "HT-2024-001",
        "合同名称": "技术开发合同",
        "甲方": "委托方企业",
        "乙方": "开发方企业", 
        "签订日期": "2024-01-10",
        "合同金额": "¥50,000.00",
        "履行期限": "2024-01-10至2024-06-10",
        "付款方式": "分三期支付",
        "违约责任": "按合同金额的5%承担违约金"
    },
    "证书类": {
        "证书名称": "软件著作权登记证书",
        "登记号": "2024SR123456",
        "软件名称": "OCR识别系统",
        "著作权人": "开发企业名称",
        "开发完成日期": "2023-12-01",
        "首次发表日期": "2024-01-01",
        "登记日期": "2024-01-20",
        "证书编号": "软著登字第123456号"
    },
    "其他类": {
        "文档类型": "通用文档",
        "文档标题": "示例文档",
        "创建日期": "2024-01-15",
        "页数": "3页",
        "主要内容": "这是一个示例文档，包含各种文本信息",
        "关键词": "示例, 文档, 测试",
        "文档大小": "2.5MB"
    }
}

@app.route('/')
def index():
    """API首页"""
    return jsonify({
        "message": "OCR演示API服务器",
        "version": "1.0.0",
        "endpoints": {
            "upload": "/upload - POST - 上传文件进行OCR处理"
        }
    })

@app.route('/upload', methods=['POST'])
def upload_and_process():
    """文件上传和OCR处理接口"""
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '没有文件'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': '文件名为空'}), 400
        
        # 获取元数据
        metadata_str = request.form.get('metadata', '{}')
        try:
            metadata = json.loads(metadata_str)
        except json.JSONDecodeError:
            metadata = {}
        
        # 保存文件
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # 模拟处理时间
            processing_start = time.time()
            time.sleep(1)  # 模拟OCR处理时间
            processing_time = time.time() - processing_start
            
            # 根据分类获取模拟结果
            category = metadata.get('category', '其他类')
            audio_text = metadata.get('audio_text', '')
            
            # 获取对应分类的模拟OCR结果
            ocr_result = DEMO_OCR_RESULTS.get(category, DEMO_OCR_RESULTS['其他类']).copy()
            
            # 如果有音频文本，添加到结果中
            if audio_text.strip():
                ocr_result['音频输入'] = audio_text.strip()
                ocr_result['智能提示'] = f"根据音频内容\"{audio_text[:20]}...\"进行了智能识别优化"
            
            # 构造响应
            response_data = {
                'status': 'success',
                'processing_time': f'{processing_time:.2f}秒',
                'file_info': {
                    'name': filename,
                    'size': os.path.getsize(filepath),
                    'category': category
                },
                'result': ocr_result,
                'metadata': metadata,
                'message': f'成功处理{category}文档'
            }
            
            return jsonify(response_data)
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': f'处理失败: {str(e)}',
            'processing_time': '0秒'
        }), 500

@app.route('/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': time.time(),
        'service': 'OCR Demo API'
    })

@app.errorhandler(413)
def too_large(e):
    """文件过大错误处理"""
    return jsonify({'error': '文件大小超过限制(50MB)'}), 413

@app.errorhandler(404)
def not_found(e):
    """404错误处理"""
    return jsonify({'error': '接口不存在'}), 404

@app.errorhandler(500)
def internal_error(e):
    """500错误处理"""
    return jsonify({'error': '服务器内部错误'}), 500

if __name__ == '__main__':
    print("=" * 50)
    print("OCR演示API服务器")
    print("=" * 50)
    print("服务器地址: http://localhost:5000")
    print("上传接口: http://localhost:5000/upload")
    print("健康检查: http://localhost:5000/health")
    print("=" * 50)
    print("提示: 这是一个演示API，返回模拟的OCR结果")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
