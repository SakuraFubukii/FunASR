// OCR音频识别系统 - 主要JavaScript文件

class OCRApp {
    constructor() {
        this.socket = io();
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioStream = null;
        this.selectedFile = null;
        this.recordedText = '';
        
        this.initializeElements();
        this.bindEvents();
        this.initializeSocket();
    }
    
    initializeElements() {
        // 文件上传相关
        this.uploadArea = document.getElementById('uploadArea');
        this.fileInput = document.getElementById('fileInput');
        this.fileInfo = document.getElementById('fileInfo');
        this.fileName = document.getElementById('fileName');
        this.fileSize = document.getElementById('fileSize');
        this.removeFileBtn = document.getElementById('removeFile');
        this.categorySelect = document.getElementById('categorySelect');
        
        // 录音相关
        this.recordBtn = document.getElementById('recordBtn');
        this.clearBtn = document.getElementById('clearBtn');
        this.recordingStatus = document.getElementById('recordingStatus');
        this.textArea = document.getElementById('textArea');
        
        // 处理相关
        this.apiUrl = document.getElementById('apiUrl');
        this.processBtn = document.getElementById('processBtn');
        this.progressInfo = document.getElementById('progressInfo');
        this.progressFill = document.getElementById('progressFill');
        this.progressText = document.getElementById('progressText');
        
        // 结果相关
        this.resultArea = document.getElementById('resultArea');
        this.loadingOverlay = document.getElementById('loadingOverlay');
        this.messageContainer = document.getElementById('messageContainer');
        
        // 调试：检查元素是否存在
        console.log('Upload area element:', this.uploadArea);
        console.log('File input element:', this.fileInput);
        console.log('All elements initialized');
    }
    
    bindEvents() {
        // 文件上传事件
        this.uploadArea.addEventListener('click', () => {
            console.log('Upload area clicked');
            this.fileInput.click();
        });
        
        this.uploadArea.addEventListener('dragover', (e) => {
            console.log('Drag over');
            this.handleDragOver(e);
        });
        
        this.uploadArea.addEventListener('dragleave', (e) => {
            console.log('Drag leave');
            this.handleDragLeave(e);
        });
        
        this.uploadArea.addEventListener('drop', (e) => {
            console.log('Drop event');
            this.handleDrop(e);
        });
        
        this.fileInput.addEventListener('change', (e) => {
            console.log('File input change');
            this.handleFileSelect(e);
        });
        
        this.removeFileBtn.addEventListener('click', this.removeFile.bind(this));
        
        // 录音事件
        this.recordBtn.addEventListener('click', this.toggleRecording.bind(this));
        this.clearBtn.addEventListener('click', this.clearRecording.bind(this));
        
        // 处理事件
        this.processBtn.addEventListener('click', this.processOCR.bind(this));
    }
    
    initializeSocket() {
        // Socket.IO 事件监听
        this.socket.on('connect', () => {
            console.log('连接到服务器');
        });
        
        this.socket.on('disconnect', () => {
            console.log('与服务器断开连接');
            this.showMessage('与服务器断开连接', 'warning');
        });
        
        this.socket.on('recording_started', () => {
            this.updateRecordingStatus('recording', '正在录音...');
        });
        
        this.socket.on('recording_stopped', () => {
            this.updateRecordingStatus('stopped', '录音完成');
        });
        
        this.socket.on('recording_cleared', () => {
            this.updateRecordingStatus('cleared', '未录音');
            this.textArea.value = '';
            this.recordedText = '';
        });
        
        this.socket.on('speech_result', (data) => {
            this.textArea.value = data.accumulated_text;
            this.recordedText = data.accumulated_text;
        });
        
        this.socket.on('recording_error', (data) => {
            this.showMessage(data.error, 'error');
            this.stopRecording();
        });
    }
    
    // 文件处理方法
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Drag over event handled');
        this.uploadArea.classList.add('dragover');
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Drag leave event handled');
        this.uploadArea.classList.remove('dragover');
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        console.log('Drop event handled');
        this.uploadArea.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        console.log('Dropped files:', files.length);
        
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        console.log('File input changed');
        const file = e.target.files[0];
        if (file) {
            console.log('Selected file:', file.name);
            this.handleFile(file);
        }
    }
    
    handleFile(file) {
        console.log('Processing file:', file.name, 'Type:', file.type, 'Size:', file.size);
        
        // 检查文件类型 - 更宽松的检查
        const allowedTypes = [
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/bmp', 'image/tiff', 'image/tif',
            'application/pdf'
        ];
        
        // 也检查文件扩展名
        const fileName = file.name.toLowerCase();
        const allowedExtensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.pdf'];
        const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        
        if (!allowedTypes.includes(file.type) && !hasValidExtension) {
            this.showMessage(`不支持的文件类型: ${file.type}，文件名: ${file.name}`, 'error');
            console.error('Unsupported file type:', file.type, 'filename:', file.name);
            return;
        }
        
        // 检查文件大小 (50MB)
        if (file.size > 50 * 1024 * 1024) {
            this.showMessage('文件大小不能超过50MB', 'error');
            console.error('File too large:', file.size);
            return;
        }
        
        console.log('File validation passed, uploading...');
        this.uploadFile(file);
    }
    
    async uploadFile(file) {
        console.log('Starting file upload for:', file.name);
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            this.showLoading();
            console.log('Sending upload request...');
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            console.log('Upload response status:', response.status);
            
            if (!response.ok) {
                throw new Error(`Upload failed with status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Upload result:', result);
            
            if (result.success) {
                this.selectedFile = result.filename;
                this.fileName.textContent = result.filename;
                this.fileSize.textContent = this.formatFileSize(result.file_size);
                this.categorySelect.value = result.suggested_category;
                
                this.uploadArea.style.display = 'none';
                this.fileInfo.style.display = 'flex';
                
                this.showMessage('文件上传成功', 'success');
                console.log('File uploaded successfully');
            } else {
                this.showMessage(result.error || '上传失败', 'error');
                console.error('Upload failed:', result);
            }
        } catch (error) {
            console.error('Upload error:', error);
            this.showMessage(`文件上传失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    removeFile() {
        this.selectedFile = null;
        this.fileInput.value = '';
        this.uploadArea.style.display = 'block';
        this.fileInfo.style.display = 'none';
        this.categorySelect.value = '';
    }
    
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }
    
    // 录音相关方法
    async toggleRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            this.stopRecording();
        }
    }
    
    async startRecording() {
        try {
            // 请求麦克风权限
            this.audioStream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                }
            });
            
            // 创建 MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            // 设置数据处理
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.processAudioData(event.data);
                }
            };
            
            // 开始录音
            this.mediaRecorder.start(600); // 每600ms发送一次数据
            this.isRecording = true;
            
            // 更新UI
            this.recordBtn.innerHTML = '<i class="fas fa-stop"></i><span>停止录音</span>';
            this.recordBtn.classList.remove('btn-primary');
            this.recordBtn.classList.add('btn-danger');
            
            // 通知服务器开始录音
            this.socket.emit('start_recording');
            
        } catch (error) {
            this.showMessage('无法访问麦克风: ' + error.message, 'error');
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            
            // 停止音频流
            if (this.audioStream) {
                this.audioStream.getTracks().forEach(track => track.stop());
            }
            
            // 更新UI
            this.recordBtn.innerHTML = '<i class="fas fa-microphone"></i><span>开始录音</span>';
            this.recordBtn.classList.remove('btn-danger');
            this.recordBtn.classList.add('btn-primary');
            
            // 通知服务器停止录音
            this.socket.emit('stop_recording');
        }
    }
    
    async processAudioData(audioBlob) {
        try {
            // 转换为ArrayBuffer
            const arrayBuffer = await audioBlob.arrayBuffer();
            
            // 创建音频上下文来解码音频
            const audioContext = new (window.AudioContext || window.webkitAudioContext)({
                sampleRate: 16000
            });
            
            const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);
            
            // 获取音频数据
            const audioData = audioBuffer.getChannelData(0);
            
            // 转换为int16并编码为base64
            const int16Array = new Int16Array(audioData.length);
            for (let i = 0; i < audioData.length; i++) {
                int16Array[i] = Math.max(-32768, Math.min(32767, audioData[i] * 32768));
            }
            
            // 转换为base64
            const audioBase64 = btoa(String.fromCharCode.apply(null, new Uint8Array(int16Array.buffer)));
            
            // 发送到服务器
            this.socket.emit('audio_data', { audio: audioBase64 });
            
        } catch (error) {
            console.error('音频处理错误:', error);
        }
    }
    
    clearRecording() {
        this.socket.emit('clear_recording');
    }
    
    updateRecordingStatus(status, text) {
        this.recordingStatus.className = `recording-status ${status}`;
        this.recordingStatus.innerHTML = `<i class="fas fa-circle"></i><span>${text}</span>`;
    }
    
    // OCR处理方法
    async processOCR() {
        if (!this.selectedFile) {
            this.showMessage('请先选择文件', 'error');
            return;
        }
        
        if (!this.categorySelect.value) {
            this.showMessage('请选择文件分类', 'error');
            return;
        }
        
        const data = {
            filename: this.selectedFile,
            category: this.categorySelect.value,
            audio_text: this.recordedText,
            api_url: this.apiUrl.value
        };
        
        try {
            this.setProcessing(true);
            this.showProgress('正在发送OCR请求...', 30);
            
            const response = await fetch('/api/process_ocr', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            this.showProgress('正在处理...', 70);
            
            const result = await response.json();
            
            if (result.success) {
                this.showProgress('处理完成', 100);
                this.displayResult(result);
                this.showMessage('OCR处理完成', 'success');
            } else {
                this.showMessage(result.error, 'error');
                this.displayError(result.error);
            }
            
        } catch (error) {
            this.showMessage('处理失败: ' + error.message, 'error');
            this.displayError('网络错误: ' + error.message);
        } finally {
            this.setProcessing(false);
            setTimeout(() => this.hideProgress(), 3000);
        }
    }
    
    setProcessing(processing) {
        this.processBtn.disabled = processing;
        if (processing) {
            this.processBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i><span>处理中...</span>';
        } else {
            this.processBtn.innerHTML = '<i class="fas fa-play"></i><span>发送OCR处理</span>';
        }
    }
    
    showProgress(text, percentage = 0) {
        this.progressInfo.style.display = 'block';
        this.progressText.textContent = text;
        this.progressFill.style.width = percentage + '%';
    }
    
    hideProgress() {
        this.progressInfo.style.display = 'none';
    }
    
    displayResult(result) {
        this.resultArea.innerHTML = '';
        
        // 创建结果内容
        const resultContent = document.createElement('div');
        resultContent.className = 'result-content';
        
        // 添加基本信息
        resultContent.appendChild(this.createResultItem('处理状态', result.result?.status || 'success'));
        resultContent.appendChild(this.createResultItem('处理时间', result.processing_time || 'Unknown'));
        resultContent.appendChild(this.createResultItem('文件分类', result.category));
        resultContent.appendChild(this.createResultItem('音频内容', result.audio_text || '无'));
        
        // 添加分隔线
        const separator = document.createElement('div');
        separator.style.borderTop = '2px solid #e2e8f0';
        separator.style.margin = '1.5rem 0';
        resultContent.appendChild(separator);
        
        // 添加OCR结果标题
        const ocrTitle = document.createElement('div');
        ocrTitle.className = 'result-label';
        ocrTitle.textContent = 'OCR识别结果:';
        ocrTitle.style.fontSize = '1.1rem';
        ocrTitle.style.marginBottom = '1rem';
        resultContent.appendChild(ocrTitle);
        
        // 格式化并显示OCR结果
        const ocrResult = this.formatOCRResult(result.result?.result || result.result);
        const ocrContent = document.createElement('div');
        ocrContent.className = 'result-value';
        ocrContent.style.whiteSpace = 'pre-wrap';
        ocrContent.style.background = '#f8fafc';
        ocrContent.style.padding = '1rem';
        ocrContent.style.borderRadius = '0.5rem';
        ocrContent.style.border = '1px solid #e2e8f0';
        ocrContent.textContent = ocrResult;
        resultContent.appendChild(ocrContent);
        
        this.resultArea.appendChild(resultContent);
    }
    
    createResultItem(label, value) {
        const item = document.createElement('div');
        item.className = 'result-item';
        
        const labelDiv = document.createElement('div');
        labelDiv.className = 'result-label';
        labelDiv.textContent = label;
        
        const valueDiv = document.createElement('div');
        valueDiv.className = 'result-value';
        valueDiv.textContent = value;
        
        item.appendChild(labelDiv);
        item.appendChild(valueDiv);
        
        return item;
    }
    
    formatOCRResult(ocrData) {
        if (typeof ocrData === 'object' && ocrData !== null) {
            // 如果是对象，格式化为键值对
            const lines = [];
            for (const [key, value] of Object.entries(ocrData)) {
                lines.push(`${key}: ${value}`);
            }
            return lines.join('\n');
        } else if (typeof ocrData === 'string') {
            // 如果是字符串，尝试解析JSON或直接返回
            try {
                const parsed = JSON.parse(ocrData);
                if (typeof parsed === 'object') {
                    return this.formatOCRResult(parsed);
                }
            } catch (e) {
                // 不是JSON，直接返回
            }
            return ocrData;
        } else {
            return String(ocrData || '无结果');
        }
    }
    
    displayError(error) {
        this.resultArea.innerHTML = `
            <div class="result-content">
                <div class="result-item" style="border-left-color: #dc2626;">
                    <div class="result-label">错误信息</div>
                    <div class="result-value" style="color: #dc2626;">${error}</div>
                </div>
            </div>
        `;
    }
    
    // 工具方法
    showLoading() {
        this.loadingOverlay.style.display = 'flex';
    }
    
    hideLoading() {
        this.loadingOverlay.style.display = 'none';
    }
    
    showMessage(message, type = 'info') {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${type}`;
        
        const iconClass = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        }[type] || 'fas fa-info-circle';
        
        messageDiv.innerHTML = `
            <i class="${iconClass}"></i>
            <span>${message}</span>
        `;
        
        this.messageContainer.appendChild(messageDiv);
        
        // 3秒后自动移除
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 3000);
    }
}

// 初始化应用
document.addEventListener('DOMContentLoaded', () => {
    new OCRApp();
});
