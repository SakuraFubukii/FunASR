#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR音频识别系统Web启动器
"""

import sys
import os
import subprocess
import importlib.util
import webbrowser
import threading
import time
import argparse

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def open_browser(url, delay=2):
    """延迟打开浏览器"""
    def _open():
        time.sleep(delay)
        try:
            print(f"正在打开浏览器: {url}")
            # 尝试打开默认浏览器
            webbrowser.open(url)
            print("✓ 浏览器已打开")
        except Exception as e:
            print(f"✗ 自动打开浏览器失败: {e}")
            print(f"请手动在浏览器中访问: {url}")
    
    # 在后台线程中打开浏览器
    thread = threading.Thread(target=_open, daemon=True)
    thread.start()

def check_package(package_name):
    """检查包是否已安装"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        # 安装依赖包
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "web/requirements.txt"])
        print("依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        return False

def check_model_path():
    """检查模型路径"""
    model_path = "E:\\Huggingface\\models\\paraformer-zh-streaming"
    if not os.path.exists(model_path):
        print(f"警告: 模型路径不存在 {model_path}")
        print("请确保已下载Paraformer模型到指定路径")
        return False
    
    return True

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='OCR音频识别系统Web启动器')
    parser.add_argument('--debug', action='store_true', help='启用debug模式')
    parser.add_argument('--no-browser', action='store_true', help='不自动打开浏览器')
    parser.add_argument('--port', type=int, default=8080, help='服务器端口 (默认: 8080)')
    args = parser.parse_args()
    
    print("=" * 50)
    print("OCR音频识别系统Web启动器")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return
    
    # 检查必要的包
    required_packages = ['flask', 'flask_socketio', 'funasr', 'numpy', 'requests']
    missing_packages = []
    
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少以下包: {', '.join(missing_packages)}")
        response = input("是否自动安装? (y/n): ").lower()
        if response == 'y':
            if not install_requirements():
                input("按回车键退出...")
                return
        else:
            print("请手动安装依赖包: pip install -r web/requirements.txt")
            input("按回车键退出...")
            return
    
    # 检查模型路径
    if not check_model_path():
        response = input("是否继续启动? (模型可能无法正常工作) (y/n): ").lower()
        if response != 'y':
            return
    
    # 确保上传目录存在
    os.makedirs("web/uploads", exist_ok=True)
    
    # 启动Web服务
    print("启动OCR音频识别系统Web版...")
    try:
        # 输出系统信息
        print(f"Python版本: {sys.version}")
        print(f"当前工作目录: {os.getcwd()}")
        
        # 导入并启动应用
        from web.app import socketio, app
        
        # 设置服务器URL
        server_url = f"http://localhost:{args.port}"
        print(f"服务器地址: {server_url}")
        print("提示: 请在浏览器中允许麦克风权限以进行音频识别")
        print("-" * 50)
        
        # 根据参数决定是否自动打开浏览器
        if not args.no_browser:
            if not args.debug or os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
                print("🌐 准备自动打开浏览器...")
                open_browser(server_url, delay=2)
        
        print("🚀 启动Web服务器...")
        # 启动服务器
        socketio.run(app, host='0.0.0.0', port=args.port, debug=args.debug)
    except ImportError as e:
        print(f"导入Web应用程序失败: {e}")
        input("按回车键退出...")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
