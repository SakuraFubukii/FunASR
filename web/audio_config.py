#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
音频识别配置文件
用于调整音频识别的各种参数以优化准确率
"""

class AudioConfig:
    """音频识别参数配置类"""
    
    # 基础音频参数
    SAMPLE_RATE = 16000
    
    # 音频块配置（这些参数直接影响识别准确率）
    CHUNK_DURATION_MS = 400  # 音频块持续时间（毫秒）- 较短的块提高响应性
    OVERLAP_DURATION_MS = 200  # 重叠持续时间（毫秒）- 解决块边界问题
    
    # 计算得出的参数
    @property
    def CHUNK_SIZE(self):
        return int(self.SAMPLE_RATE * self.CHUNK_DURATION_MS / 1000)
    
    @property 
    def OVERLAP_SIZE(self):
        return int(self.SAMPLE_RATE * self.OVERLAP_DURATION_MS / 1000)
    
    # FunASR模型参数（重要：这些参数需要根据模型和使用场景调优）
    CHUNK_SIZE_PARAMS = [0, 10, 5]  # [0, 10, 5] 适合流式识别
    ENCODER_CHUNK_LOOK_BACK = 7     # 编码器回望块数，增加有助于提高准确性
    DECODER_CHUNK_LOOK_BACK = 2     # 解码器回望块数，增加有助于语义连贯性
    
    # 音频质量检测参数
    MIN_ENERGY_THRESHOLD = 0.001    # 最小能量阈值，用于静音检测
    MIN_ZCR_THRESHOLD = 0.01        # 最小零交叉率阈值
    MAX_SILENCE_DURATION = 2.0      # 最大静音持续时间（秒）
    
    # 音频预处理参数
    ENABLE_DC_REMOVAL = True        # 启用直流分量去除
    ENABLE_SIMPLE_DENOISING = True  # 启用简单降噪
    DENOISING_WINDOW_SIZE = 3       # 降噪窗口大小
    
    # Web Audio API参数
    WEB_BUFFER_SIZE = 8192          # Web Audio API缓冲区大小（必须是2的幂）
    
    # 调试和监控参数
    LOG_INTERVAL = 20               # 每N个块输出一次日志
    AUDIO_QUALITY_REPORT_INTERVAL = 50  # 每N个块发送一次音频质量报告
    
    # 高级优化参数
    ADAPTIVE_THRESHOLD = True       # 启用自适应阈值
    CONTEXT_MEMORY_SIZE = 5         # 保持的上下文记忆块数
    ENABLE_VAD = True               # 启用语音活动检测(Voice Activity Detection)

class ModelConfig:
    """模型相关配置"""
    
    # 模型路径
    MODEL_PATH = "E:\\Huggingface\\models\\paraformer-zh-streaming"
    
    # 模型优化参数
    DISABLE_UPDATE = True
    USE_GPU = False  # 如果有GPU可以设置为True
    
    # 批处理参数
    BATCH_SIZE = 1  # 流式识别通常使用1

class PerformanceConfig:
    """性能优化配置"""
    
    # 线程配置
    MAX_WORKER_THREADS = 4
    AUDIO_QUEUE_MAX_SIZE = 100
    
    # 内存管理
    MAX_BUFFER_SIZE_MB = 50
    CLEANUP_INTERVAL = 300  # 清理间隔（秒）

# 预设配置
class PresetConfigs:
    """预设配置，用于不同的使用场景"""
    
    @staticmethod
    def get_high_accuracy_config():
        """高准确率配置（可能会增加延迟）"""
        config = AudioConfig()
        config.CHUNK_DURATION_MS = 600  # 更长的块
        config.OVERLAP_DURATION_MS = 300  # 更多的重叠
        config.ENCODER_CHUNK_LOOK_BACK = 10
        config.DECODER_CHUNK_LOOK_BACK = 3
        config.MIN_ENERGY_THRESHOLD = 0.0005  # 更敏感的静音检测
        return config
    
    @staticmethod
    def get_low_latency_config():
        """低延迟配置（可能会牺牲一些准确率）"""
        config = AudioConfig()
        config.CHUNK_DURATION_MS = 200  # 更短的块
        config.OVERLAP_DURATION_MS = 100  # 较少的重叠
        config.ENCODER_CHUNK_LOOK_BACK = 4
        config.DECODER_CHUNK_LOOK_BACK = 1
        config.MIN_ENERGY_THRESHOLD = 0.002  # 不太敏感的静音检测
        return config
    
    @staticmethod
    def get_balanced_config():
        """平衡配置（默认推荐）"""
        return AudioConfig()  # 使用默认值

# 使用示例和说明
"""
参数调优指南：

1. 块大小调优：
   - CHUNK_DURATION_MS: 200-800ms 范围内调整
     * 更短 (200-400ms): 响应更快，但可能影响长词准确性
     * 更长 (600-800ms): 准确性更好，但响应稍慢
   
2. 重叠大小调优：
   - OVERLAP_DURATION_MS: 通常设为块大小的30-50%
     * 更多重叠: 减少块边界错误，但增加计算量
     * 更少重叠: 计算效率高，但可能有边界问题

3. 模型回望参数调优：
   - ENCODER_CHUNK_LOOK_BACK: 4-10 范围内调整
     * 更大: 更好的上下文理解，但增加延迟
     * 更小: 更快响应，但可能丢失上下文
   
   - DECODER_CHUNK_LOOK_BACK: 1-3 范围内调整
     * 更大: 更好的语义连贯性
     * 更小: 更快的解码速度

4. 静音检测调优：
   - MIN_ENERGY_THRESHOLD: 根据环境噪音调整
     * 噪音环境: 增大阈值 (0.002-0.005)
     * 安静环境: 减小阈值 (0.0005-0.001)

5. 性能vs准确性权衡：
   - 高准确性: 使用 get_high_accuracy_config()
   - 低延迟: 使用 get_low_latency_config()
   - 平衡: 使用 get_balanced_config()

调试技巧：
1. 监控日志中的音频质量指标
2. 观察块边界处的识别错误
3. 根据实际使用场景调整参数
4. 可以A/B测试不同配置的效果
"""
