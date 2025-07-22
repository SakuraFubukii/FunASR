// OCR识别系统前端脚本

// 全局变量
let socket;
let audioContext;
let mediaStream;
let scriptProcessor;
let selectedFile = null;
let isRecording = false;
let recordedText = "";
let lastEditTime = 0; // 记录最后一次编辑时间

// DOM元素
document.addEventListener('DOMContentLoaded', () => {
    // 连接WebSocket
    connectSocket();
    
    // 初始化页面交互
    initializeUI();
    
    // 初始化复制按钮
    initCopyButton();
});

function connectSocket() {
    // 连接WebSocket
    socket = io();
    
    // 设置WebSocket事件监听
    socket.on('connect', () => {
        console.log('已连接到服务器');
    });
    
    socket.on('disconnect', () => {
        console.log('已断开与服务器的连接');
        updateStatus('已断开连接');
    });
    
    socket.on('model_status', (data) => {
        if (data.status === 'ready') {
            console.log('模型已准备好');
        } else {
            console.error('模型加载失败:', data.message);
            updateStatus('模型加载失败');
            showError('语音识别模型加载失败，请刷新页面或联系管理员');
        }
    });
    
    socket.on('recognition_result', (data) => {
        updateRecognitionText(data.text);
    });
    
    socket.on('recording_status', (data) => {
        if (data.status === 'started') {
            updateStatus('正在录音...');
        } else if (data.status === 'stopped') {
            updateStatus('录音完成');
        } else if (data.status === 'cleared') {
            updateStatus('未录音');
        }
    });
    
    socket.on('recording_complete', (data) => {
        recordedText = data.text;
    });
    
    socket.on('file_category', (data) => {
        document.getElementById('category-select').value = data.category;
    });
    
    socket.on('error', (data) => {
        showError(data.message);
    });
}

function initializeUI() {
    // 文件上传按钮
    const selectFileBtn = document.getElementById('select-file-btn');
    const fileInput = document.getElementById('file-input');
    const dropArea = document.getElementById('drop-area');
    
    selectFileBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    // 文件选择处理
    fileInput.addEventListener('change', (e) => {
        handleFileSelect(e.target.files);
    });
    
    // 拖放功能
    dropArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.add('active');
    });
    
    dropArea.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.remove('active');
    });
    
    dropArea.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        dropArea.classList.remove('active');
        
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            handleFileSelect(e.dataTransfer.files);
        }
    });
    
    // 录音按钮
    const recordButton = document.getElementById('record-button');
    recordButton.addEventListener('click', toggleRecording);
    
    // 清除按钮
    const clearButton = document.getElementById('clear-button');
    clearButton.addEventListener('click', clearRecording);
    
    // 音频识别结果实时编辑监听
    const recognitionResult = document.getElementById('recognition-result');
    recognitionResult.addEventListener('input', debounce(function() {
        // 获取编辑后的文本
        const editedText = recognitionResult.value;
        // 保存到全局变量
        recordedText = editedText;
        // 自动保存编辑的文本
        saveEditedText();
    }, 1000)); // 1秒延迟，避免频繁发送
    
    // 发送处理按钮
    const processButton = document.getElementById('process-button');
    processButton.addEventListener('click', processOCR);
}

// 处理文件选择
function handleFileSelect(files) {
    if (files.length > 0) {
        selectedFile = files[0];
        document.getElementById('file-name').textContent = `已选择: ${selectedFile.name}`;
        
        // 通知服务器检查文件
        socket.emit('check_file', { filename: selectedFile.name });
    }
}

// 防抖函数
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

async function toggleRecording() {
    if (!isRecording) {
        await startRecording();
    } else {
        stopRecording();
    }
}

async function startRecording() {
    try {
        // 请求麦克风权限
        mediaStream = await navigator.mediaDevices.getUserMedia({ 
            audio: {
                sampleRate: 16000,
                channelCount: 1,
                echoCancellation: true,
                noiseSuppression: true
            } 
        });
        
        // 初始化音频上下文 - 确保采样率与后端一致
        audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
        
        // 创建音频节点
        const sourceNode = audioContext.createMediaStreamSource(mediaStream);
        
        // 使用与桌面端一致的音频块大小：600ms = 9600样本 (16kHz)
        // 但Web Audio API要求缓冲区大小为2的幂，所以使用16384，然后截取9600样本
        const DESKTOP_CHUNK_SIZE = 9600;  // 600ms × 16kHz，与桌面端一致
        const BUFFER_SIZE = 16384;        // 2的幂，满足Web Audio API要求
        console.log(`使用缓冲区大小: ${BUFFER_SIZE}, 音频块大小: ${DESKTOP_CHUNK_SIZE}`);
        scriptProcessor = audioContext.createScriptProcessor(BUFFER_SIZE, 1, 1);
        
        // 连接节点
        sourceNode.connect(scriptProcessor);
        scriptProcessor.connect(audioContext.destination);
        
        // 处理音频数据
        scriptProcessor.onaudioprocess = (e) => {
            if (!isRecording) return;
            
            // 获取音频数据
            const input = e.inputBuffer.getChannelData(0);
            
            // 截取前9600样本，与桌面端保持一致
            const audioData = new Float32Array(DESKTOP_CHUNK_SIZE);
            for (let i = 0; i < DESKTOP_CHUNK_SIZE && i < input.length; i++) {
                audioData[i] = input[i];
            }
            
            // 计算音频质量指标
            let maxAbs = 0;
            for (let i = 0; i < audioData.length; i++) {
                const abs = Math.abs(audioData[i]);
                if (abs > maxAbs) maxAbs = abs;
            }
            
            // 只有在数据明显超出正常范围时才进行归一化
            if (maxAbs > 1.0) {
                console.warn(`音频信号过载，最大值=${maxAbs.toFixed(4)}，进行归一化`);
                for (let i = 0; i < audioData.length; i++) {
                    audioData[i] /= maxAbs;
                }
            }
            
            // 输出调试信息到控制台（每10次只输出一次，避免过多日志）
            if (!this.logCounter) this.logCounter = 0;
            if (audioData.length > 0 && (this.logCounter++ % 10) === 0) {
                console.log(`音频数据: 长度=${audioData.length}, 采样率=${audioContext.sampleRate}, 最大值=${maxAbs.toFixed(4)}`);
            }
            
            // 将音频数据转为Base64并发送
            const arrayBuffer = audioData.buffer;
            const base64Audio = arrayBufferToBase64(arrayBuffer);
            socket.emit('audio_data', { 
                audio: base64Audio, 
                bufferSize: audioData.length,
                expectedChunkSize: DESKTOP_CHUNK_SIZE
            });
        };
        
        // 通知服务器开始录音
        socket.emit('start_recording');
        
        // 更新UI
        isRecording = true;
        document.getElementById('record-button').textContent = '停止录音';
        updateStatus('正在录音...');
        
        // 清空识别结果
        document.getElementById('recognition-result').value = '';
        recordedText = '';
        
    } catch (error) {
        console.error('启动录音失败:', error);
        showError(`启动录音失败: ${error.message}`);
    }
}

function stopRecording() {
    // 停止录音
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
    
    if (scriptProcessor) {
        scriptProcessor.disconnect();
    }
    
    if (audioContext) {
        audioContext.close();
    }
    
    // 通知服务器停止录音
    socket.emit('stop_recording');
    
    // 更新UI
    isRecording = false;
    document.getElementById('record-button').textContent = '开始录音';
    updateStatus('录音完成');
}

function clearRecording() {
    // 清除录音文本
    document.getElementById('recognition-result').value = '';
    recordedText = '';
    
    // 通知服务器清除录音
    socket.emit('clear_recording');
    
    updateStatus('未录音');
}

function processOCR() {
    if (!selectedFile) {
        showError('请先选择文件');
        return;
    }
    
    const category = document.getElementById('category-select').value;
    if (!category) {
        showError('请选择文件分类');
        return;
    }
    
    // 更新UI
    const processButton = document.getElementById('process-button');
    processButton.disabled = true;
    processButton.textContent = '处理中...';
    
    updateProgress('正在准备数据...');
    document.getElementById('processing-status').textContent = '处理状态：发送请求中...';
    document.getElementById('result-area').textContent = '正在发送请求，请稍候...';
    
    // 获取当前编辑框中的文本（可能已被用户编辑）
    const currentText = document.getElementById('recognition-result').value;
    recordedText = currentText; // 更新全局变量
    
    // 获取API地址
    const apiUrl = document.getElementById('api-url').value;
    
    // 创建数据对象，与桌面端保持一致
    const data = {
        category: category,
        audio_text: recordedText,
        file_info: {
            name: selectedFile.name,
            size: selectedFile.size
        }
    };
    
    // 打印发送的数据内容到控制台
    console.log("发送到OCR API的数据:", data);
    
    // 创建表单数据
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('metadata', JSON.stringify(data));
    
    // 直接发送请求到OCR服务器
    fetch(apiUrl, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(result => {
        updateProgress('处理完成');
        document.getElementById('processing-status').textContent = '处理状态：完成';
        displayResult(result);
        
        // 恢复按钮状态
        processButton.disabled = false;
        processButton.textContent = '发送OCR处理';
        
        // 3秒后清除进度信息
        setTimeout(() => {
            updateProgress('');
        }, 3000);
    })
    .catch(error => {
        updateProgress('处理失败');
        document.getElementById('processing-status').textContent = '处理状态：失败';
        document.getElementById('result-area').textContent = `处理失败: ${error.message}`;
        
        // 恢复按钮状态
        processButton.disabled = false;
        processButton.textContent = '发送OCR处理';
        
        // 3秒后清除进度信息
        setTimeout(() => {
            updateProgress('');
        }, 3000);
    });
}

function updateRecognitionText(text) {
    const textarea = document.getElementById('recognition-result');
    textarea.value += text + '\n';
    textarea.scrollTop = textarea.scrollHeight;
}

function updateStatus(status) {
    document.getElementById('status-label').textContent = status;
}

function updateProgress(message) {
    document.getElementById('progress-label').textContent = message;
}

function saveEditedText() {
    // 获取当前时间
    const now = Date.now();
    
    // 如果距离上次编辑不到1秒，则不处理
    if (now - lastEditTime < 1000) {
        return;
    }
    
    // 更新最后编辑时间
    lastEditTime = now;
    
    // 获取编辑后的文本
    const editedText = document.getElementById('recognition-result').value;
    
    // 保存到全局变量
    recordedText = editedText;
    
    // 发送到服务器
    socket.emit('update_recognition_text', { text: editedText });
    
    // 显示保存状态
    updateStatus('自动保存中...');
    
    // 设置监听，只添加一次
    if (!saveEditedText.hasListener) {
        socket.on('recognition_updated', (data) => {
            if (data.success) {
                updateStatus('已自动保存');
                
                // 2秒后恢复状态
                setTimeout(() => {
                    if (!isRecording) {
                        updateStatus('录音完成');
                    }
                }, 2000);
            } else {
                showError(`保存失败: ${data.message || '未知错误'}`);
            }
        });
        saveEditedText.hasListener = true;
    }
}

function displayResult(result) {
    const resultArea = document.getElementById('result-area');
    const processingStatus = document.getElementById('processing-status');
    
    // 更新处理状态信息
    processingStatus.textContent = `处理状态: ${result.status || 'Unknown'} | 处理时间: ${result.processing_time || 'Unknown'} | 文件分类: ${document.getElementById('category-select').value}`;
    
    // 格式化并显示结果
    let formattedResult = '';
    
    // 处理OCR结果
    const ocrResult = result.result;
    
    if (typeof ocrResult === 'string') {
        // 检查是否为JSON字符串
        try {
            const parsedJson = JSON.parse(ocrResult);
            if (parsedJson && typeof parsedJson === 'object' && parsedJson.result) {
                // 如果是包含result字段的JSON，只提取result内容
                formattedResult = formatOcrText(parsedJson.result);
            } else {
                // 普通JSON，格式化显示
                formattedResult = JSON.stringify(parsedJson, null, 2);
            }
        } catch (e) {
            // 不是JSON字符串，直接处理文本格式
            formattedResult = formatOcrText(ocrResult);
        }
    } else if (typeof ocrResult === 'object') {
        if (ocrResult && ocrResult.result) {
            // 如果是包含result字段的对象，只提取result内容
            formattedResult = formatOcrText(ocrResult.result);
        } else {
            // 普通对象，格式化显示
            formattedResult = JSON.stringify(ocrResult, null, 2);
        }
    } else {
        formattedResult = formatOcrText(String(ocrResult));
    }
    
    resultArea.textContent = formattedResult;
}

// 格式化OCR文本的辅助函数
function formatOcrText(text) {
    if (!text || typeof text !== 'string') {
        return String(text || '');
    }
    
    // 将转义的换行符转换为实际换行符
    let formatted = text.replace(/\\n/g, '\n');
    
    // 将转义的制表符转换为实际制表符
    formatted = formatted.replace(/\\t/g, '\t');
    
    // 将转义的引号转换为实际引号
    formatted = formatted.replace(/\\"/g, '"');
    formatted = formatted.replace(/\\'/g, "'");
    
    // 将转义的反斜杠转换为实际反斜杠
    formatted = formatted.replace(/\\\\/g, '\\');
    
    return formatted;
}

function showError(message) {
    alert(message);
}

// 辅助函数: ArrayBuffer转Base64
function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}

// 初始化复制按钮功能
function initCopyButton() {
    const copyButton = document.getElementById('copy-result');
    copyButton.addEventListener('click', () => {
        const resultArea = document.getElementById('result-area');
        const text = resultArea.textContent;
        
        // 使用Clipboard API复制文本
        navigator.clipboard.writeText(text)
            .then(() => {
                // 临时改变按钮文本以提供反馈
                const originalText = copyButton.textContent;
                copyButton.textContent = '已复制!';
                
                // 2秒后恢复原始文本
                setTimeout(() => {
                    copyButton.textContent = originalText;
                }, 2000);
            })
            .catch(err => {
                console.error('复制失败:', err);
                showError('复制失败，请手动选择文本并复制');
            });
    });
}
