import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import time
import os
import requests
import json
from funasr import AutoModel
import pyaudio
import numpy as np

class OCRApp:
    def __init__(self, root, load_model=True):
        self.root = root
        self.root.title("OCR音频识别系统")
        self.root.geometry("800x600")
        
        # 文件分类
        self.file_categories = {
            "发票类": ["发票", "税票", "收据"],
            "合同类": ["合同", "协议", "结算"],
            "证书类": ["证书", "资质", "许可"],
            "其他类": ["其他", "未分类"]
        }
        
        # 音频参数
        self.SAMPLE_RATE = 16000
        self.CHUNK_DURATION_MS = 600
        self.CHUNK_SIZE_SAMPLES = int(self.SAMPLE_RATE * self.CHUNK_DURATION_MS / 1000)
        self.CHANNELS = 1
        self.FORMAT = pyaudio.paInt16
        
        # 状态变量
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.recorded_text = ""
        self.selected_file = None
        self.selected_category = None
        
        # 初始化模型
        self.model = None
        if load_model:
            try:
                self.model = AutoModel(model="E:\Huggingface\models\paraformer-zh-streaming", disable_update=True)
            except Exception as e:
                print(f"模型加载失败: {e}")
                self.model = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 文件上传区域
        file_frame = ttk.LabelFrame(main_frame, text="文件上传", padding="10")
        file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(file_frame, text="选择文件", command=self.select_file).grid(row=0, column=0, padx=(0, 10))
        self.file_label = ttk.Label(file_frame, text="未选择文件")
        self.file_label.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        # 文件分类
        ttk.Label(file_frame, text="文件分类:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0))
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(file_frame, textvariable=self.category_var, 
                                         values=list(self.file_categories.keys()), state="readonly")
        self.category_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(10, 0))
        
        # 音频录制区域
        audio_frame = ttk.LabelFrame(main_frame, text="音频录制", padding="10")
        audio_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        button_frame = ttk.Frame(audio_frame)
        button_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        self.record_button = ttk.Button(button_frame, text="开始录音", command=self.toggle_recording)
        self.record_button.grid(row=0, column=0, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="清除录音", command=self.clear_recording)
        self.clear_button.grid(row=0, column=1)
        
        # 录音状态
        self.status_label = ttk.Label(audio_frame, text="未录音")
        self.status_label.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        # 识别结果显示
        ttk.Label(audio_frame, text="识别结果:").grid(row=2, column=0, sticky=tk.W)
        self.text_area = tk.Text(audio_frame, height=8, width=60)
        self.text_area.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # 滚动条
        scrollbar = ttk.Scrollbar(audio_frame, orient="vertical", command=self.text_area.yview)
        scrollbar.grid(row=3, column=2, sticky=(tk.N, tk.S))
        self.text_area.configure(yscrollcommand=scrollbar.set)
        
        # 处理区域
        process_frame = ttk.LabelFrame(main_frame, text="处理选项", padding="10")
        process_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # API配置
        ttk.Label(process_frame, text="OCR API地址:").grid(row=0, column=0, sticky=tk.W)
        self.api_var = tk.StringVar(value="http://localhost:5000/upload")
        ttk.Entry(process_frame, textvariable=self.api_var, width=50).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0))
        
        # 处理按钮
        self.process_button = ttk.Button(process_frame, text="发送OCR处理", command=self.process_ocr)
        self.process_button.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        # 添加进度条
        self.progress_var = tk.StringVar(value="")
        self.progress_label = ttk.Label(process_frame, textvariable=self.progress_var, foreground="blue")
        self.progress_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        # 结果显示区域
        result_frame = ttk.LabelFrame(main_frame, text="处理结果", padding="10")
        result_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.result_area = tk.Text(result_frame, height=10, width=60)
        self.result_area.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        result_scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_area.yview)
        result_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_area.configure(yscrollcommand=result_scrollbar.set)
        
        # 配置权重
        main_frame.columnconfigure(1, weight=1)
        file_frame.columnconfigure(1, weight=1)
        audio_frame.columnconfigure(1, weight=1)
        process_frame.columnconfigure(1, weight=1)
        result_frame.columnconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def select_file(self):
        """选择文件"""
        file_path = filedialog.askopenfilename(
            title="选择要处理的文件",
            filetypes=[
                ("图片文件", "*.jpg *.jpeg *.png *.bmp *.tiff"),
                ("PDF文件", "*.pdf"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            self.selected_file = file_path
            filename = os.path.basename(file_path)
            self.file_label.config(text=f"已选择: {filename}")
            
            # 自动分类
            self.auto_categorize_file(filename)
    
    def auto_categorize_file(self, filename):
        """根据文件名自动分类"""
        filename_lower = filename.lower()
        
        for category, keywords in self.file_categories.items():
            for keyword in keywords:
                if keyword in filename_lower:
                    self.category_var.set(category)
                    return
        
        # 默认分类
        self.category_var.set("其他类")
    
    def toggle_recording(self):
        """切换录音状态"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """开始录音"""
        if not self.model:
            messagebox.showerror("错误", "语音识别模型未加载\n\n可能的解决方案:\n1. 重启程序并等待模型加载完成\n2. 检查模型路径是否正确\n3. 确保有足够的内存和存储空间")
            return
        
        self.is_recording = True
        self.record_button.config(text="停止录音")
        self.status_label.config(text="正在录音...")
        
        # 启动音频采集线程
        self.audio_thread = threading.Thread(target=self.audio_callback, daemon=True)
        self.audio_thread.start()
        
        # 启动音频处理线程
        self.process_thread = threading.Thread(target=self.process_audio, daemon=True)
        self.process_thread.start()
    
    def stop_recording(self):
        """停止录音"""
        self.is_recording = False
        self.record_button.config(text="开始录音")
        self.status_label.config(text="录音完成")
    
    def clear_recording(self):
        """清除录音"""
        self.recorded_text = ""
        self.text_area.delete(1.0, tk.END)
        self.status_label.config(text="未录音")
    
    def audio_callback(self):
        """音频采集回调函数"""
        p = pyaudio.PyAudio()
        
        try:
            stream = p.open(
                format=self.FORMAT,
                channels=self.CHANNELS,
                rate=self.SAMPLE_RATE,
                input=True,
                frames_per_buffer=self.CHUNK_SIZE_SAMPLES
            )
            
            while self.is_recording:
                data = stream.read(self.CHUNK_SIZE_SAMPLES, exception_on_overflow=False)
                audio_data = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                self.audio_queue.put(audio_data)
                
        except Exception as e:
            print(f"音频采集错误: {e}")
        finally:
            if 'stream' in locals():
                stream.stop_stream()
                stream.close()
            p.terminate()
    
    def process_audio(self):
        """音频处理函数"""
        cache = {}
        chunk_count = 0
        
        try:
            while self.is_recording:
                try:
                    speech_chunk = self.audio_queue.get(timeout=1.0)
                    chunk_count += 1
                    
                    res = self.model.generate(
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
                            # 更新界面（需要在主线程中执行）
                            self.root.after(0, self.update_text_display, text)
                            
                except queue.Empty:
                    continue
                    
        except Exception as e:
            pass
    
    def update_text_display(self, text):
        """更新文本显示"""
        self.text_area.insert(tk.END, text + "\n")
        self.text_area.see(tk.END)
        self.recorded_text += text + " "
    
    def process_ocr(self):
        """处理OCR请求"""
        if not self.selected_file:
            messagebox.showerror("错误", "请先选择文件")
            return
        
        if not self.category_var.get():
            messagebox.showerror("错误", "请选择文件分类")
            return
        
        # 禁用处理按钮，显示处理状态
        self.process_button.config(state="disabled", text="处理中...")
        self.progress_var.set("正在准备数据...")
        self.result_area.delete(1.0, tk.END)
        self.result_area.insert(tk.END, "正在发送请求，请稍候...\n")
        
        # 在后台线程中执行OCR处理
        ocr_thread = threading.Thread(target=self._process_ocr_thread, daemon=True)
        ocr_thread.start()
    
    def _process_ocr_thread(self):
        """在后台线程中处理OCR请求"""
        try:
            # 更新进度
            self.root.after(0, self.progress_var.set, "正在准备数据...")
            
            # 准备数据
            data = {
                "category": self.category_var.get(),
                "audio_text": self.recorded_text.strip(),
                "file_info": {
                    "name": os.path.basename(self.selected_file),
                    "size": os.path.getsize(self.selected_file)
                }
            }
            
            # 更新进度
            self.root.after(0, self.progress_var.set, "正在发送请求...")
            
            # 发送文件和数据
            with open(self.selected_file, 'rb') as f:
                files = {'file': (os.path.basename(self.selected_file), f)}
                response = requests.post(
                    self.api_var.get(),
                    files=files,
                    data={'metadata': json.dumps(data)},
                    timeout=300  # 设置超时为5分钟（300秒）
                )
            
            # 更新进度
            self.root.after(0, self.progress_var.set, "正在处理响应...")
            
            # 在主线程中处理响应
            if response.status_code == 200:
                try:
                    result = response.json()
                    self.root.after(0, self._handle_success_response, result)
                except json.JSONDecodeError:
                    error_msg = f"服务器返回了非JSON格式的响应:\n{response.text}"
                    self.root.after(0, self._handle_error_response, error_msg)
            else:
                error_msg = f"请求失败，状态码: {response.status_code}\n错误信息: {response.text}"
                self.root.after(0, self._handle_error_response, error_msg)
                
        except requests.exceptions.Timeout:
            error_msg = "请求超时，请检查网络连接或服务器状态"
            self.root.after(0, self._handle_error_response, error_msg)
        except requests.exceptions.ConnectionError:
            error_msg = "连接失败，请检查API地址是否正确或服务器是否正在运行"
            self.root.after(0, self._handle_error_response, error_msg)
        except requests.exceptions.RequestException as e:
            error_msg = f"网络请求错误: {str(e)}"
            self.root.after(0, self._handle_error_response, error_msg)
        except Exception as e:
            error_msg = f"处理失败: {str(e)}"
            self.root.after(0, self._handle_error_response, error_msg)
    
    def _handle_success_response(self, result):
        """处理成功响应（在主线程中执行）"""
        self.progress_var.set("处理完成")
        self.display_result(result)
        self.process_button.config(state="normal", text="发送OCR处理")
        # 3秒后清除进度信息
        self.root.after(3000, lambda: self.progress_var.set(""))
    
    def _handle_error_response(self, error_msg):
        """处理错误响应（在主线程中执行）"""
        self.progress_var.set("处理失败")
        self.result_area.delete(1.0, tk.END)
        self.result_area.insert(tk.END, error_msg)
        self.process_button.config(state="normal", text="发送OCR处理")
        # 3秒后清除进度信息
        self.root.after(3000, lambda: self.progress_var.set(""))
    
    def display_result(self, result):
        """显示处理结果"""
        self.result_area.delete(1.0, tk.END)
        
        result_text = f"处理状态: {result.get('status', 'Unknown')}\n"
        result_text += f"处理时间: {result.get('processing_time', 'Unknown')}\n"
        result_text += f"文件分类: {self.category_var.get()}\n"
        result_text += f"音频内容: {self.recorded_text.strip()}\n"
        result_text += "-" * 50 + "\n"
        result_text += "OCR识别结果:\n"
        
        # 安全处理result字段，确保它是字符串格式
        ocr_result = result.get('result', '无结果')
        if isinstance(ocr_result, dict):
            # 如果是字典，格式化为可读的字符串
            result_text += json.dumps(ocr_result, ensure_ascii=False, indent=2)
        elif isinstance(ocr_result, (list, tuple)):
            # 如果是列表或元组，转换为字符串
            result_text += str(ocr_result)
        else:
            # 如果是其他类型，转换为字符串
            result_text += str(ocr_result)
        
        self.result_area.insert(tk.END, result_text)

def main():
    try:
        import sys
        
        # 检查命令行参数
        load_model = True
        if "--no-model" in sys.argv:
            load_model = False
        
        root = tk.Tk()
        app = OCRApp(root, load_model=load_model)
        root.mainloop()
        
    except Exception as e:
        print(f"应用程序启动失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
