# OCR Audio Recognition System

[English](README.md)|[中文](README_zh.md)

This is a comprehensive system that integrates file upload, automatic classification, speech recognition, and OCR processing. Users can upload files, record audio instructions, and send both file content and audio content to the OCR interface for processing.

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
├── main.py                    # Main program - GUI interface
├── launcher.py               # Python launcher (recommended)
├── paraformer.py             # Original speech recognition module
├── test.py                   # Original test file
├── test_enhanced.py          # Enhanced test file
├── file_classifier.py        # File classification analysis tool
├── config.json               # System configuration file
├── requirements.txt          # Dependency list
├── README.md                 # Documentation (English)
├── README_zh.md              # Documentation (Chinese)
└── output/                   # Sample file directory
    ├── 结算审定书（VR集成应用管理平台）/
    ├── 西南油气田数智分公司单个系统等保测评/
    ├── 资产系统结算审定书1（盖章）/
    ├── IMGCMP20220610141102110/
    ├── IMGCMP20220610141102335/
    └── IMGCMP20220610141102566/
```

## Installation and Configuration

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Speech Recognition Model

Ensure the Paraformer model is downloaded to the specified path:

```text
E:\Huggingface\models\paraformer-zh-streaming
```

### 3. Configure Audio Device

Ensure the system has properly configured audio input device (microphone).

## Usage

### Method 1: Launcher (Recommended)

```bash
python launcher.py
```

The launcher automatically checks Python environment, dependencies, and model paths, providing complete environment validation.

### Method 2: Direct Start

```bash
python main.py
```

1. **Select File**: Click "Select File" button to choose the document to process
2. **File Classification**: System will auto-classify, can also manually adjust
3. **Record Audio**: Click "Start Recording", speak your processing requirements for the document
4. **Send for Processing**: Configure OCR API address, click "Send OCR Processing"
5. **View Results**: Check OCR processing results in the result area

### Method 3: Command Line Testing

```bash
# Basic testing
python test_enhanced.py

# File classification analysis
python file_classifier.py

# Original speech recognition testing
python paraformer.py
```

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
- Windows operating system (with PowerShell configured)
- Audio input device (microphone)
- Network connection (for accessing OCR API)

## Troubleshooting

### Common Issues

1. **Model Loading Failed**
   - Check if model path is correct
   - Ensure funasr package is installed

2. **Audio Recording Failed**
   - Check if microphone is working properly
   - Confirm pyaudio package is correctly installed

3. **OCR Interface Call Failed**
   - Check if API address is correct
   - Confirm network connection is normal
   - Check if API service is running

### Debugging Methods

Run file classification analysis tool to view sample file analysis results:

```bash
python file_classifier.py
```

Run enhanced test tool to verify interface functionality:

```bash
python test_enhanced.py
```

## Development Notes

- `main.py`: Main program, contains complete GUI interface and functional logic
- `paraformer.py`: Original command-line speech recognition program
- `file_classifier.py`: File classification analysis tool for analyzing sample files
- `test_enhanced.py`: Enhanced test program demonstrating complete API call flow

## Extended Features

Features that could be considered for addition:

- Support for more file formats
- Add more file categories
- Optimize speech recognition accuracy
- Add result export functionality
- Support batch file processing