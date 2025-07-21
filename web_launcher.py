#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR音频识别系统Web版启动器
"""

import sys
import os
import subprocess
import importlib.util

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
        # 创建web版本的requirements.txt文件
        with open("web/requirements.txt", "w") as f:
            f.write("flask\n")
            f.write("flask-socketio\n")
            f.write("funasr\n")
            f.write("numpy\n")
            f.write("requests\n")
            f.write("werkzeug\n")
            f.write("eventlet\n")
        
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
    
    # 确保web目录下的app.py与主程序使用相同的模型路径
    try:
        with open("web/app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查并更新web/app.py中的模型路径
        # 注意：在字符串比较中，需要考虑转义字符的区别
        escaped_path = "E:\\\\Huggingface\\\\models\\\\paraformer-zh-streaming"  # Python字符串中的双反斜杠
        if f'model="{escaped_path}"' not in content and f"model='{escaped_path}'" not in content:
            print(f"警告: Web应用使用的模型路径可能与主程序不同")
            print("建议确保两者使用相同的模型路径")
            
            # 可以在这里添加自动修复模型路径的代码
            # 这需要谨慎处理，以免破坏app.py文件
    except Exception as e:
        print(f"读取Web应用配置时出错: {e}")
    
    return True

def main():
    """主函数"""
    print("=" * 50)
    print("OCR音频识别系统Web版启动器")
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
        
        # 检查模型目录权限
        model_path = "E:\\Huggingface\\models\\paraformer-zh-streaming"
        if os.path.exists(model_path):
            try:
                files = os.listdir(model_path)
                print(f"模型目录包含{len(files)}个文件")
            except PermissionError:
                print(f"警告: 无法访问模型目录，可能存在权限问题")
        
        # 导入并启动应用
        from web.app import socketio, app
        print("服务器启动中，访问地址: http://localhost:8080")
        print("提示: 使用浏览器访问上述地址，允许麦克风权限以进行音频识别")
        socketio.run(app, host='0.0.0.0', port=8080, debug=True)
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
