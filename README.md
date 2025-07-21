# OCR音频识别系统 - Web版

一个基于Web的OCR音频识别系统，支持文件上传、实时音频录制和OCR处理。

## 🚀 快速开始

### 一键启动
```bash
# Windows用户
双击 start_web.bat

# 其他系统用户
python web_launcher.py
```

启动器会自动：
- 检查Python版本和依赖
- 启动Web服务器
- 打开浏览器

## ✨ 功能特性

🎤 **实时音频录制**
- 支持浏览器内音频录制
- 实时语音识别和转文字
- WebSocket实时通信

📁 **智能文件管理**
- 拖拽上传支持
- 多种文件格式 (JPG, PNG, PDF等)
- 自动分类：发票类、合同类、证书类、其他类

🔍 **OCR处理**
- 集成外部OCR API
- 支持多种文档类型
- 结构化结果展示

🎨 **现代化界面**
- 响应式设计，支持桌面和移动设备
- 美观的CSS动画和交互效果
- 直观的用户操作流程

## 📋 使用流程

1. **上传文件** - 点击上传区域或拖拽文件
2. **选择分类** - 系统自动建议或手动选择分类
3. **录制音频** - 可选，说出与文档相关的信息
4. **查看结果** - 系统处理并显示OCR和语音识别结果

## 🔧 系统要求

- Python 3.7+
- 现代浏览器 (Chrome, Firefox, Safari, Edge)
- 麦克风权限 (用于音频录制)

## 📁 项目结构

```
├── app.py                # Flask Web应用主文件
├── web_launcher.py       # Web版启动器
├── config.py            # 配置管理
├── file_classifier.py   # 文件分类工具
├── demo_ocr_api.py      # 演示OCR API
├── start_web.bat        # Windows启动脚本
├── requirements.txt     # 依赖包列表
├── templates/           # HTML模板
│   └── index.html
├── static/             # 静态资源
│   ├── css/style.css
│   └── js/app.js
└── uploads/            # 文件上传目录
```

## 📖 配置说明

编辑 `config.json` 文件来配置系统参数：

```json
{
    "ocr_api_url": "http://localhost:8080/api/ocr",
    "model_path": "E:/Huggingface/models/paraformer-zh-streaming",
    "upload_folder": "uploads",
    "max_file_size": 52428800
}
```

## 🔄 技术栈

- **后端**: Flask + Socket.IO
- **前端**: HTML5 + CSS3 + JavaScript
- **语音识别**: FunASR (Paraformer模型)
- **文件处理**: Werkzeug
- **实时通信**: WebSocket

## 📝 更新日志

### v2.0 - Web版本
- ✅ 从Tkinter桌面应用改为Web界面
- ✅ 响应式设计和现代化UI
- ✅ 保留所有原有功能
- ✅ 提升用户体验和操作便利性

---
