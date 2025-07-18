from funasr import AutoModel
import pyaudio
import numpy as np
import threading
import queue
import time

# 配置参数
chunk_size = [0, 10, 5]  # [0, 10, 5] 600ms, [0, 8, 4] 480ms
encoder_chunk_look_back = 4  # number of chunks to lookback for encoder self-attention
decoder_chunk_look_back = 1  # number of encoder chunks to lookback for decoder cross-attention

# 音频参数
SAMPLE_RATE = 16000  # 采样率
CHUNK_DURATION_MS = 600  # 每块音频的持续时间（毫秒）
CHUNK_SIZE_SAMPLES = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)  # 每块的样本数
CHANNELS = 1  # 单声道
FORMAT = pyaudio.paInt16  # 16位音频

# 初始化模型
model = AutoModel(model="E:\Huggingface\models\paraformer-zh-streaming")

# 音频队列
audio_queue = queue.Queue()

def audio_callback():
    """音频采集回调函数"""
    p = pyaudio.PyAudio()
    
    try:
        # 打开音频流
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            frames_per_buffer=CHUNK_SIZE_SAMPLES
        )
        
        print("开始录音，按 Ctrl+C 停止...")
        
        while True:
            # 读取音频数据
            data = stream.read(CHUNK_SIZE_SAMPLES, exception_on_overflow=False)
            # 转换为numpy数组并归一化
            audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
            # 放入队列
            audio_queue.put(audio_data)
            
    except KeyboardInterrupt:
        print("\n停止录音")
    finally:
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        p.terminate()

def process_audio():
    """音频处理函数"""
    cache = {}
    chunk_count = 0
    
    print("开始音频识别...")
    
    try:
        while True:
            try:
                # 从队列获取音频数据
                speech_chunk = audio_queue.get(timeout=1.0)
                chunk_count += 1
                
                # 处理音频块
                res = model.generate(
                    input=speech_chunk, 
                    cache=cache, 
                    is_final=False,  # 实时模式下通常设为False
                    chunk_size=chunk_size, 
                    encoder_chunk_look_back=encoder_chunk_look_back, 
                    decoder_chunk_look_back=decoder_chunk_look_back
                )
                
                if res and len(res) > 0:
                    text = res[0].get('text', '')
                    if text.strip():
                        print(f"[块 {chunk_count}] {text}")
                
            except queue.Empty:
                continue
                
    except KeyboardInterrupt:
        print("\n停止音频处理")

if __name__ == "__main__":
    # 创建并启动音频采集线程
    audio_thread = threading.Thread(target=audio_callback, daemon=True)
    audio_thread.start()
    
    # 等待一小段时间让音频采集开始
    time.sleep(1)
    
    # 开始音频处理
    try:
        process_audio()
    except KeyboardInterrupt:
        print("\n程序结束")