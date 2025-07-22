# OCR Audio Recognition System Web Version

[English](README.md)|[中文](README_zh.md)

This is a web-based OCR audio recognition system that integrates file upload, automatic classification, speech recognition, and OCR processing. Users can upload files, record audio instructions, and send both file content and audio text to the OCR interface for processing through a web interface.

This system is specifically designed for web environments, providing a clean and intuitive interface with support for streaming speech recognition and document processing capabilities.

## Features

### 1. File Upload and Automatic Classification

- Supports image files (jpg, jpeg, png, bmp, tiff) and PDF files
- Automatically categorizes files into four main types:
  - **Invoice Category**: Invoices, tax receipts, receipts, and other financial documents
  - **Contract Category**: Contracts, agreements, settlement documents, and other legal documents
  - **Certificate Category**: Certificates, qualifications, licenses, and other certification documents
  - **Other Category**: Documents that cannot be clearly classified

### 2. Real-time Speech Recognition

- Based on FunASR's Paraformer model
- Real-time audio capture and processing
- Supports Chinese speech recognition
- Visual display of recognition results

### 3. Integrated OCR Processing

- Sends both file byte stream and audio text to OCR interface
- Supports custom OCR API address
- Real-time display of processing results

## Project Structure

```text
├── web_launcher.py           # Web application launcher
├── config.json               # System configuration file
├── web/                      # Web application directory
│   ├── app.py                # Flask web application main program
│   ├── audio_config.py       # Audio configuration
│   ├── requirements.txt      # Web application dependency list
│   ├── static/               # Static resources
│   │   ├── css/              # CSS stylesheets
│   │   └── js/               # JavaScript scripts
│   ├── templates/            # HTML templates
│   │   └── index.html        # Main page template
│   └── uploads/              # Web application file upload directory
├── uploads/                  # File upload directory
├── README.md                 # Documentation (English)
└── README_zh.md              # Documentation (Chinese)
```

## Installation and Configuration

### 1. Install Dependencies

```bash
pip install -r web/requirements.txt
```

### 2. Configure Speech Recognition Model

Download Paraformer model and update the path in config.json:

```json
{
  "model_config": {
    "model_path": "your-model-path",
    ...
  }
}
```

## Usage Instructions

### 1. Start the Web Service

```bash
python web_launcher.py
```

Command line arguments:

- `--debug`: Enable debug mode
- `--no-browser`: Do not automatically open browser
- `--port PORT`: Set server port (default: 8080)

### 2. Access the Web Interface

1. **Open Browser**: Navigate to `http://localhost:8080` (or the port you specified)
2. **Upload File**: Click on "Choose File" button to upload a document
3. **Record Audio**: Click "Start Recording" button and speak your instructions
4. **View Results**: System will display OCR recognition results

## System Requirements

- Python 3.7+
- FunASR library
- Flask and Flask-SocketIO
- Web browser (Chrome recommended)
- Microphone (for speech recognition)

## Contributing

Issues and feature requests are welcome. If you want to contribute code, please follow these steps:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request
