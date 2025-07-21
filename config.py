# OCR音频识别系统 - Web版本配置文件

import os

class Config:
    """应用配置类"""
    
    # Flask基本配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-change-in-production'
    
    # 文件上传配置
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {
        'jpg', 'jpeg', 'png', 'bmp', 'tiff', 'pdf'
    }
    
    # 服务器配置
    HOST = '0.0.0.0'
    PORT = 8080
    DEBUG = False
    
    # 模型配置
    ASR_MODEL_PATH = r"E:\Huggingface\models\paraformer-zh-streaming"
    
    # 音频配置
    SAMPLE_RATE = 16000
    CHUNK_DURATION_MS = 600
    
    # OCR API配置
    DEFAULT_OCR_API = "http://localhost:5000/upload"
    
    # 文件分类配置
    FILE_CATEGORIES = {
        "发票类": ["发票", "税票", "收据"],
        "合同类": ["合同", "协议", "结算"],
        "证书类": ["证书", "资质", "许可"],
        "其他类": ["其他", "未分类"]
    }
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 确保上传目录存在
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True

# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
