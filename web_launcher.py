#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR音频识别系统启动器 - Web版本
"""

import sys
import os
import subprocess
import importlib.util
import webbrowser
import time
import threading

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_package(package_name):
    """检查包是否已安装"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        return False

def check_model_path():
    """检查模型路径"""
    model_path = r"E:\Huggingface\models\paraformer-zh-streaming"
    if not os.path.exists(model_path):
        print(f"警告: 模型路径不存在 {model_path}")
        print("请确保已下载Paraformer模型到指定路径")
        return False
    return True

def check_port_available(port):
    """检查端口是否可用"""
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def open_browser():
    """延迟打开浏览器"""
    time.sleep(2)  # 等待服务器启动
    webbrowser.open('http://localhost:8080')

def main():
    """主函数"""
    print("=" * 60)
    print("OCR音频识别系统启动器 - Web版本")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return
    
    # 检查必要的包
    required_packages = ['flask', 'flask_socketio', 'funasr', 'numpy', 'requests', 'werkzeug']
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
            print("请手动安装依赖包: pip install -r requirements.txt")
            input("按回车键退出...")
            return
    
    # 检查模型路径
    if not check_model_path():
        response = input("是否继续启动? (模型可能无法正常工作) (y/n): ").lower()
        if response != 'y':
            return
    
    # 检查端口
    port = 8080
    if not check_port_available(port):
        print(f"警告: 端口 {port} 已被占用")
        response = input("是否尝试使用其他端口? (y/n): ").lower()
        if response == 'y':
            for test_port in range(8081, 8090):
                if check_port_available(test_port):
                    port = test_port
                    break
            else:
                print("无法找到可用端口")
                input("按回车键退出...")
                return
    
    print(f"服务器将在端口 {port} 启动")
    print("=" * 60)
    
    # 启动Web应用
    print("正在启动OCR音频识别Web系统...")
    print("提示:")
    print("- 系统启动后会自动打开浏览器")
    print("- 如果浏览器未自动打开，请手动访问: http://localhost:8080")
    print("- 按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        # 在新线程中打开浏览器
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # 导入并启动Flask应用
        import app
        
        # 修改端口
        if port != 8080:
            # 动态修改app.py中的端口
            print(f"使用端口: {port}")
        
        # 启动应用
        app.socketio.run(app.app, host='0.0.0.0', port=port, debug=False)
        
    except ImportError as e:
        print(f"导入Web应用失败: {e}")
        print("请确保 app.py 文件存在")
        input("按回车键退出...")
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"程序运行错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
