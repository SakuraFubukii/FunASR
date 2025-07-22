# OCR Audio Recognition System Web Version

[English](README.md)|[中文](README_zh.md)

This is a web-based OCR audio recognition system that integrates file upload, automatic classification, speech recognition, and OCR processing. Users can upload files, record audio instructions, and send both file content and audio text to the OCR interface for processing through a web interface.

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
├── paraformer.py             # Speech recognition module
├── file_classifier.py        # File classification analysis tool
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

Ensure the Paraformer model is downloaded to the specified path:

```text
E:\Huggingface\models\paraformer-zh-streaming
```

### 3. Configure Web Browser

Ensure your web browser allows microphone access for real-time speech recognition.

## Usage

### Starting the Web Application

```bash
python web_launcher.py
```

The launcher automatically checks Python environment, dependencies, and model paths, providing complete environment validation before starting the web server.

### Command Line Options

```bash
python web_launcher.py [options]
```

Options:
- `--debug`: Enable debug mode
- `--no-browser`: Don't automatically open the browser
- `--port PORT`: Specify server port (default: 8080)

### Using the Web Interface

1. **Open Browser**: Navigate to http://localhost:8080 (or the port you specified)
2. **Upload File**: Click "Upload File" button to select a document for processing
3. **Record Audio**: Click the microphone icon and speak your processing requirements
4. **Send for Processing**: Configure OCR API address if needed, click "Send for Processing"
5. **View Results**: Check OCR processing results in the result area

## API Interface Format

Data format sent by the system to OCR interface:

```json
{
  "file": "file byte stream",
  "metadata": {
    "category": "File category (Invoice/Contract/Certificate/Other)",
    "audio_text": "Transcribed text from recorded audio", 
    "file_info": {
      "name": "filename",
      "size": "file size"
    }
  }
}
```

Expected API response format:

```json
{
  "status": "success",
  "processing_time": "processing time",
  "result": "OCR recognition result"
}
```

## File Classification Rules

The system uses keyword matching for automatic classification:

| Category | Keywords | Description |
|----------|----------|-------------|
| Invoice | 发票、税票、收据、开票、税额、金额、购买方、销售方 | Finance-related documents |
| Contract | 合同、协议、结算、审定书、建设、施工、甲方、乙方 | Legal documents |
| Certificate | 证书、资质、许可、认证、等保、测评、资格 | Certification documents |
| Other | - | Documents that cannot be clearly classified |

## Audio Instruction Examples

Based on different file types, recommend using the following audio instructions:

- **Invoice Category**: "Please identify key information from this invoice, including date of issue, amount, buyer and seller information"
- **Contract Category**: "Please extract party information, contract amount, and main terms from the contract"
- **Certificate Category**: "Please identify the certificate type, issuing authority, validity period, and relevant qualification information"
- **Other Category**: "Please identify all important text content and key information in the document"

## System Requirements

- Python 3.7+
- Modern web browser with microphone access support
- Audio input device (microphone)
- Network connection (for accessing OCR API)

## Troubleshooting

### Common Issues

1. **Model Loading Failed**
   - Check if model path is correct
   - Ensure funasr package is installed

2. **Audio Recording Failed**
   - Check if browser microphone permissions are allowed
   - Check if microphone is working properly
   - Test microphone in browser settings

3. **Web Server Failed to Start**
   - Check if port is already in use
   - Ensure Flask and Flask-SocketIO are installed
   - Check Python version compatibility

4. **OCR Interface Call Failed**
   - Check if API address is correct
   - Confirm network connection is normal
   - Check if API service is running

## Development Notes

- `web_launcher.py`: Web application launcher script
- `web/app.py`: Main Flask application with routes and socket handlers
- `paraformer.py`: Speech recognition module
- `file_classifier.py`: File classification analysis tool
- `web/static/js/app.js`: Client-side JavaScript for audio recording and UI
- `web/templates/index.html`: Main web interface template

## Extended Features

Features that could be considered for addition:

- Support for more file formats
- Add more file categories
- Optimize speech recognition accuracy
- Add result export functionality
- Support batch file processing
- User authentication and saved history
- Responsive design for mobile devices