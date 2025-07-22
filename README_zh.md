# OCR音频识别系统 Web版

这是一个基于Web的OCR音频识别系统，集成了文件上传、自动分类、语音识别和OCR处理功能。用户可以通过Web界面上传文件，录制音频指令，然后将文件内容和音频内容一起发送给OCR接口进行处理。

本系统专为Web环境设计，提供简洁直观的界面，支持流式语音识别及文档处理功能。

## 功能特点

### 1. 文件上传与自动分类

- 支持图片文件（jpg, jpeg, png, bmp, tiff）和PDF文件
- 自动将文件分为四大类：
  - **发票类**: 发票、税票、收据等财务文档
  - **合同类**: 合同、协议、结算书等法律文档  
  - **证书类**: 证书、资质、许可证等证明文档
  - **其他类**: 无法明确分类的其他文档

### 2. 实时语音识别

- 基于FunASR的Paraformer模型
- 实时音频采集和处理
- 支持中文语音识别
- 可视化显示识别结果

### 3. 综合OCR处理

- 将文件字节流和音频文字同时发送给OCR接口
- 支持自定义OCR API地址
- 实时显示处理结果

## 文件结构

```plaintext
├── web_launcher.py            # Web应用启动器
├── config.json                # 系统配置文件
├── web/                       # Web应用目录
│   ├── app.py                 # Flask Web应用主程序
│   ├── audio_config.py        # 音频配置
│   ├── requirements.txt       # Web应用依赖包列表
│   ├── templates/             # HTML模板目录
│   │   └── index.html         # 主页模板
│   ├── static/                # 静态资源目录
│   │   ├── css/               # CSS样式文件
│   │   │   └── style.css      # 主样式表
│   │   └── js/                # JavaScript脚本
│   │       └── app.js         # 主脚本文件
│   └── uploads/               # Web应用文件上传目录
├── uploads/                   # 文件上传目录
├── README.md                  # 英文说明文档
└── README_zh.md               # 中文说明文档
```

## 安装与配置

### 1. 安装依赖

```bash
pip install -r web/requirements.txt
```

### 2. 配置语音识别模型

下载Paraformer模型并在config.json中更新路径:

```json
{
  "model_config": {
    "model_path": "您的模型路径",
    ...
  }
}
```

## 使用方法

### 1. 启动Web服务

```bash
python web_launcher.py
```

命令行参数:

- `--debug`: 启用debug模式
- `--no-browser`: 不自动打开浏览器
- `--port PORT`: 指定服务器端口 (默认: 8080)

### 2. 访问Web界面

1. **打开浏览器**: 访问 `http://localhost:8080` (或您指定的端口)
2. **上传文件**: 点击"选择文件"按钮上传文档
3. **录制音频**: 点击"开始录音"按钮并说出您的指令
4. **查看结果**: 系统将显示OCR识别结果

## 系统要求

- Python 3.7+
- FunASR 库
- Flask 和 Flask-SocketIO
- 网络浏览器 (Chrome 推荐)
- 麦克风 (用于语音识别)

## 贡献

欢迎提交问题报告和功能建议。如果您想贡献代码，请遵循以下步骤:
1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 开启一个 Pull Request
