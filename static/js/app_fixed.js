// OCR音频识别系统 - 增强版JavaScript文件

class OCRApp {
    constructor() {
        this.debug = true; // 启用调试模式
        this.socket = null;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioStream = null;
        this.selectedFile = null;
        this.recordedText = '';
        
        this.log('OCRApp初始化开始');
        this.initializeElements();
        this.bindEvents();
        this.initializeSocket();
        this.log('OCRApp初始化完成');
    }
    
    log(message, type = 'info') {
        if (this.debug) {
            const timestamp = new Date().toLocaleTimeString();
            console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
        }
    }
    
    initializeElements() {
        this.log('开始初始化DOM元素');
        
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
        
        // 检查关键元素是否存在
        const criticalElements = {
            'uploadArea': this.uploadArea,
            'fileInput': this.fileInput,
            'recordBtn': this.recordBtn,
            'processBtn': this.processBtn
        };
        
        let missingElements = [];
        for (const [name, element] of Object.entries(criticalElements)) {
            if (!element) {
                missingElements.push(name);
                this.log(`❌ 元素 ${name} 未找到`, 'error');
            } else {
                this.log(`✅ 元素 ${name} 找到`, 'success');
            }
        }
        
        if (missingElements.length > 0) {
            this.showMessage(`页面元素缺失: ${missingElements.join(', ')}`, 'error');
            return false;
        }
        
        this.log('DOM元素初始化完成');
        return true;
    }
    
    bindEvents() {
        this.log('开始绑定事件');
        
        try {
            // 文件上传事件
            if (this.uploadArea && this.fileInput) {
                this.uploadArea.addEventListener('click', () => {
                    this.log('上传区域被点击');
                    this.fileInput.click();
                });
                
                this.uploadArea.addEventListener('dragover', (e) => {
                    this.handleDragOver(e);
                });
                
                this.uploadArea.addEventListener('dragleave', (e) => {
                    this.handleDragLeave(e);
                });
                
                this.uploadArea.addEventListener('drop', (e) => {
                    this.handleDrop(e);
                });
                
                this.fileInput.addEventListener('change', (e) => {
                    this.handleFileSelect(e);
                });
                
                this.log('✅ 文件上传事件绑定完成');
            }
            
            if (this.removeFileBtn) {
                this.removeFileBtn.addEventListener('click', this.removeFile.bind(this));
                this.log('✅ 移除文件事件绑定完成');
            }
            
            // 录音事件
            if (this.recordBtn && this.clearBtn) {
                this.recordBtn.addEventListener('click', this.toggleRecording.bind(this));
                this.clearBtn.addEventListener('click', this.clearRecording.bind(this));
                this.log('✅ 录音事件绑定完成');
            }
            
            // 处理事件
            if (this.processBtn) {
                this.processBtn.addEventListener('click', this.processOCR.bind(this));
                this.log('✅ 处理事件绑定完成');
            }
            
            this.log('事件绑定完成');
        } catch (error) {
            this.log(`事件绑定失败: ${error.message}`, 'error');
            this.showMessage('页面初始化失败，请刷新页面重试', 'error');
        }
    }
    
    initializeSocket() {
        this.log('开始初始化Socket连接');
        
        try {
            // 检查Socket.IO是否加载
            if (typeof io === 'undefined') {
                this.log('Socket.IO未加载', 'error');
                this.showMessage('Socket.IO未加载，实时功能可能无法使用', 'warning');
                return;
            }
            
            this.socket = io({
                timeout: 10000,
                transports: ['websocket', 'polling']
            });
            
            // Socket.IO 事件监听
            this.socket.on('connect', () => {
                this.log('✅ 已连接到服务器');
                this.showMessage('服务器连接成功', 'success');
            });
            
            this.socket.on('disconnect', () => {
                this.log('❌ 与服务器断开连接', 'error');
                this.showMessage('与服务器断开连接', 'warning');
            });
            
            this.socket.on('connect_error', (error) => {
                this.log(`连接错误: ${error.message}`, 'error');
                this.showMessage('无法连接到服务器', 'error');
            });
            
            this.socket.on('recording_started', () => {
                this.updateRecordingStatus('recording', '正在录音...');
            });
            
            this.socket.on('recording_stopped', () => {
                this.updateRecordingStatus('stopped', '录音完成');
            });
            
            this.socket.on('recording_cleared', () => {
                this.updateRecordingStatus('cleared', '未录音');
                if (this.textArea) this.textArea.value = '';
                this.recordedText = '';
            });
            
            this.socket.on('speech_result', (data) => {
                if (this.textArea) {
                    this.textArea.value = data.accumulated_text;
                    this.recordedText = data.accumulated_text;
                }
            });
            
            this.socket.on('recording_error', (data) => {
                this.log(`录音错误: ${data.error}`, 'error');
                this.showMessage(data.error, 'error');
                this.stopRecording();
            });
            
            this.log('Socket事件监听器设置完成');
        } catch (error) {
            this.log(`Socket初始化失败: ${error.message}`, 'error');
            this.showMessage('实时通信初始化失败', 'error');
        }
    }
    
    // 文件处理方法
    handleDragOver(e) {
        e.preventDefault();
        e.stopPropagation();
        this.log('文件拖拽中');
        if (this.uploadArea) {
            this.uploadArea.classList.add('dragover');
        }
    }
    
    handleDragLeave(e) {
        e.preventDefault();
        e.stopPropagation();
        this.log('文件拖拽离开');
        if (this.uploadArea) {
            this.uploadArea.classList.remove('dragover');
        }
    }
    
    handleDrop(e) {
        e.preventDefault();
        e.stopPropagation();
        this.log('文件拖拽放下');
        
        if (this.uploadArea) {
            this.uploadArea.classList.remove('dragover');
        }
        
        const files = e.dataTransfer.files;
        this.log(`拖拽文件数量: ${files.length}`);
        
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    }
    
    handleFileSelect(e) {
        this.log('文件选择器触发');
        const file = e.target.files[0];
        if (file) {
            this.log(`选择的文件: ${file.name}, 大小: ${file.size}, 类型: ${file.type}`);
            this.handleFile(file);
        }
    }
    
    handleFile(file) {
        this.log(`处理文件: ${file.name}, 类型: ${file.type}, 大小: ${file.size}`);
        
        // 检查文件类型
        const allowedTypes = [
            'image/jpeg', 'image/jpg', 'image/png', 
            'image/bmp', 'image/tiff', 'image/tif',
            'application/pdf'
        ];
        
        const fileName = file.name.toLowerCase();
        const allowedExtensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.pdf'];
        const hasValidExtension = allowedExtensions.some(ext => fileName.endsWith(ext));
        
        if (!allowedTypes.includes(file.type) && !hasValidExtension) {
            const errorMsg = `不支持的文件类型: ${file.type}，文件名: ${file.name}`;
            this.log(errorMsg, 'error');
            this.showMessage(errorMsg, 'error');
            return;
        }
        
        // 检查文件大小 (50MB)
        if (file.size > 50 * 1024 * 1024) {
            const errorMsg = `文件大小不能超过50MB，当前大小: ${this.formatFileSize(file.size)}`;
            this.log(errorMsg, 'error');
            this.showMessage(errorMsg, 'error');
            return;
        }
        
        this.log('文件验证通过，开始上传');
        this.uploadFile(file);
    }
    
    async uploadFile(file) {
        this.log(`开始上传文件: ${file.name}`);
        
        const formData = new FormData();
        formData.append('file', file);
        
        try {
            this.showLoading();
            this.log('发送上传请求到 /api/upload');
            
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });
            
            this.log(`上传响应状态: ${response.status}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`上传失败，状态码: ${response.status}, 响应: ${errorText}`);
            }
            
            const result = await response.json();
            this.log('上传响应数据:', result);
            
            if (result.success) {
                this.selectedFile = result.filename;
                
                if (this.fileName) this.fileName.textContent = result.filename;
                if (this.fileSize) this.fileSize.textContent = this.formatFileSize(result.file_size);
                if (this.categorySelect) this.categorySelect.value = result.suggested_category;
                
                if (this.uploadArea) this.uploadArea.style.display = 'none';
                if (this.fileInfo) this.fileInfo.style.display = 'flex';
                
                this.showMessage('文件上传成功', 'success');
                this.log('✅ 文件上传成功');
            } else {
                const errorMsg = result.error || '上传失败';
                this.log(`上传失败: ${errorMsg}`, 'error');
                this.showMessage(errorMsg, 'error');
            }
        } catch (error) {
            this.log(`上传异常: ${error.message}`, 'error');
            this.showMessage(`文件上传失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
        }
    }
    
    removeFile() {
        this.log('移除文件');
        this.selectedFile = null;
        if (this.fileInput) this.fileInput.value = '';
        if (this.uploadArea) this.uploadArea.style.display = 'block';
        if (this.fileInfo) this.fileInfo.style.display = 'none';
        if (this.categorySelect) this.categorySelect.value = '';
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
        this.log(`切换录音状态，当前状态: ${this.isRecording ? '录音中' : '未录音'}`);
        
        if (this.isRecording) {
            this.stopRecording();
        } else {
            await this.startRecording();
        }
    }
    
    async startRecording() {
        this.log('开始录音');
        
        try {
            // 检查浏览器是否支持
            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                throw new Error('您的浏览器不支持录音功能');
            }
            
            // 请求麦克风权限
            this.audioStream = await navigator.mediaDevices.getUserMedia({ 
                audio: {
                    sampleRate: 16000,
                    channelCount: 1,
                    echoCancellation: true,
                    noiseSuppression: true
                } 
            });
            
            this.log('✅ 麦克风权限获取成功');
            
            // 创建MediaRecorder
            this.mediaRecorder = new MediaRecorder(this.audioStream, {
                mimeType: 'audio/webm;codecs=opus'
            });
            
            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0 && this.socket) {
                    const reader = new FileReader();
                    reader.onload = () => {
                        this.socket.emit('audio_chunk', {
                            audio_data: reader.result.split(',')[1]  // 移除data:audio/webm;base64,前缀
                        });
                    };
                    reader.readAsDataURL(event.data);
                }
            };
            
            this.mediaRecorder.start(600); // 每600ms发送一次数据
            this.isRecording = true;
            
            if (this.socket) {
                this.socket.emit('start_recording');
            }
            
            this.updateRecordingStatus('recording', '正在录音...');
            this.updateRecordButton();
            
            this.log('✅ 录音开始');
            this.showMessage('录音开始', 'success');
            
        } catch (error) {
            this.log(`录音启动失败: ${error.message}`, 'error');
            this.showMessage(`录音失败: ${error.message}`, 'error');
        }
    }
    
    stopRecording() {
        this.log('停止录音');
        
        if (this.mediaRecorder && this.mediaRecorder.state !== 'inactive') {
            this.mediaRecorder.stop();
        }
        
        if (this.audioStream) {
            this.audioStream.getTracks().forEach(track => track.stop());
            this.audioStream = null;
        }
        
        if (this.socket) {
            this.socket.emit('stop_recording');
        }
        
        this.isRecording = false;
        this.updateRecordingStatus('stopped', '录音完成');
        this.updateRecordButton();
        
        this.log('✅ 录音停止');
        this.showMessage('录音完成', 'success');
    }
    
    clearRecording() {
        this.log('清除录音');
        
        if (this.isRecording) {
            this.stopRecording();
        }
        
        if (this.socket) {
            this.socket.emit('clear_recording');
        }
        
        if (this.textArea) this.textArea.value = '';
        this.recordedText = '';
        
        this.updateRecordingStatus('cleared', '未录音');
        
        this.log('✅ 录音已清除');
        this.showMessage('录音已清除', 'info');
    }
    
    updateRecordingStatus(status, text) {
        if (!this.recordingStatus) return;
        
        this.recordingStatus.className = `recording-status ${status}`;
        this.recordingStatus.querySelector('span').textContent = text;
    }
    
    updateRecordButton() {
        if (!this.recordBtn) return;
        
        const icon = this.recordBtn.querySelector('i');
        const span = this.recordBtn.querySelector('span');
        
        if (this.isRecording) {
            this.recordBtn.className = 'btn btn-danger';
            if (icon) icon.className = 'fas fa-stop';
            if (span) span.textContent = '停止录音';
        } else {
            this.recordBtn.className = 'btn btn-primary';
            if (icon) icon.className = 'fas fa-microphone';
            if (span) span.textContent = '开始录音';
        }
    }
    
    // OCR处理
    async processOCR() {
        this.log('开始OCR处理');
        
        if (!this.selectedFile) {
            this.showMessage('请先上传文件', 'warning');
            return;
        }
        
        const category = this.categorySelect ? this.categorySelect.value : '';
        if (!category) {
            this.showMessage('请选择文件分类', 'warning');
            return;
        }
        
        const apiUrl = this.apiUrl ? this.apiUrl.value : 'http://localhost:5000/upload';
        
        try {
            this.showLoading();
            this.showProgress(0, '正在处理...');
            
            const response = await fetch('/api/process_ocr', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    filename: this.selectedFile,
                    category: category,
                    audio_text: this.recordedText,
                    api_url: apiUrl
                })
            });
            
            this.log(`OCR响应状态: ${response.status}`);
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`OCR处理失败，状态码: ${response.status}, 响应: ${errorText}`);
            }
            
            const result = await response.json();
            this.log('OCR响应数据:', result);
            
            if (result.success) {
                this.displayResult(result);
                this.showMessage('OCR处理完成', 'success');
                this.log('✅ OCR处理成功');
            } else {
                this.showMessage(result.error || 'OCR处理失败', 'error');
                this.log(`OCR处理失败: ${result.error}`, 'error');
            }
            
        } catch (error) {
            this.log(`OCR处理异常: ${error.message}`, 'error');
            this.showMessage(`OCR处理失败: ${error.message}`, 'error');
        } finally {
            this.hideLoading();
            this.hideProgress();
        }
    }
    
    displayResult(result) {
        if (!this.resultArea) return;
        
        this.resultArea.innerHTML = `
            <div class="result-content">
                <h3>处理结果</h3>
                <div class="result-item">
                    <strong>文件名:</strong> ${result.filename || '未知'}
                </div>
                <div class="result-item">
                    <strong>分类:</strong> ${result.category || '未分类'}
                </div>
                <div class="result-item">
                    <strong>处理时间:</strong> ${new Date().toLocaleString()}
                </div>
                <div class="result-item">
                    <strong>状态:</strong> <span class="success">处理成功</span>
                </div>
                ${result.ocr_result ? `
                    <div class="result-item">
                        <strong>OCR结果:</strong>
                        <pre class="ocr-result">${result.ocr_result}</pre>
                    </div>
                ` : ''}
                ${result.audio_text ? `
                    <div class="result-item">
                        <strong>音频文本:</strong>
                        <pre class="audio-text">${result.audio_text}</pre>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    // UI辅助方法
    showLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.style.display = 'flex';
        }
    }
    
    hideLoading() {
        if (this.loadingOverlay) {
            this.loadingOverlay.style.display = 'none';
        }
    }
    
    showProgress(percent, text) {
        if (this.progressInfo) {
            this.progressInfo.style.display = 'block';
        }
        if (this.progressFill) {
            this.progressFill.style.width = `${percent}%`;
        }
        if (this.progressText) {
            this.progressText.textContent = text;
        }
    }
    
    hideProgress() {
        if (this.progressInfo) {
            this.progressInfo.style.display = 'none';
        }
    }
    
    showMessage(message, type = 'info') {
        this.log(`显示消息: ${message} (${type})`);
        
        if (!this.messageContainer) {
            // 如果没有消息容器，使用alert作为备选
            alert(message);
            return;
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message message-${type}`;
        
        const iconClass = {
            'success': 'fas fa-check-circle',
            'error': 'fas fa-exclamation-circle',
            'warning': 'fas fa-exclamation-triangle',
            'info': 'fas fa-info-circle'
        }[type] || 'fas fa-info-circle';
        
        messageDiv.innerHTML = `
            <i class="${iconClass}"></i>
            <span>${message}</span>
            <button class="message-close" onclick="this.parentNode.remove()">
                <i class="fas fa-times"></i>
            </button>
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

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('页面DOM加载完成，开始初始化OCR应用');
    
    try {
        // 添加全局错误处理
        window.addEventListener('error', (event) => {
            console.error('全局错误:', event.error);
        });
        
        window.addEventListener('unhandledrejection', (event) => {
            console.error('未处理的Promise拒绝:', event.reason);
        });
        
        // 创建应用实例
        window.ocrApp = new OCRApp();
        console.log('✅ OCR应用初始化成功');
        
    } catch (error) {
        console.error('❌ OCR应用初始化失败:', error);
        alert('应用初始化失败，请刷新页面重试：' + error.message);
    }
});

// 导出到全局作用域以便调试
window.OCRApp = OCRApp;
