#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR音频识别系统启动器 - 修复版本
"""

import sys
import os
import subprocess
import importlib.util
import webbrowser
import time
import threading
import ctypes

def check_admin_privileges():
    """检查是否以管理员身份运行"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    """以管理员身份重新运行"""
    if check_admin_privileges():
        return True
    
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        return False
    except:
        print("无法获取管理员权限")
        return False

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 7):
        print("错误: 需要Python 3.7或更高版本")
        print(f"当前版本: {sys.version}")
        return False
    return True

def check_package(package_name):
    """检查包是否已安装"""
    try:
        spec = importlib.util.find_spec(package_name)
        return spec is not None
    except Exception:
        return False

def install_requirements():
    """安装依赖包"""
    print("正在安装依赖包...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt", 
            "--user"  # 添加--user参数避免权限问题
        ])
        print("依赖包安装完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"依赖包安装失败: {e}")
        # 尝试单独安装关键包
        critical_packages = ['flask', 'flask-socketio', 'flask-cors', 'requests', 'werkzeug']
        for package in critical_packages:
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
                print(f"✅ {package} 安装成功")
            except:
                print(f"❌ {package} 安装失败")
        return False

def check_and_create_directories():
    """检查并创建必要的目录"""
    directories = ['uploads', 'static/css', 'static/js', 'templates']
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            # 测试写入权限
            test_file = os.path.join(directory, '.test')
            with open(test_file, 'w') as f:
                f.write('test')
            os.remove(test_file)
            print(f"✅ 目录 {directory}: 正常")
        except Exception as e:
            print(f"❌ 目录 {directory}: 权限问题 - {e}")
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
    time.sleep(3)  # 增加等待时间
    try:
        webbrowser.open('http://localhost:8080')
        print("✅ 浏览器已打开")
    except Exception as e:
        print(f"❌ 无法打开浏览器: {e}")

def main():
    """主函数"""
    print("=" * 60)
    print("OCR音频识别系统启动器 - 修复版本")
    print("=" * 60)
    
    # 检查管理员权限
    if not check_admin_privileges():
        print("⚠️ 建议以管理员身份运行以避免权限问题")
        response = input("是否尝试以管理员身份重新运行? (y/n): ").lower()
        if response == 'y':
            if not run_as_admin():
                return
            else:
                print("已以管理员身份运行")
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return
    
    # 检查和创建目录
    if not check_and_create_directories():
        print("❌ 目录权限检查失败")
        input("按回车键退出...")
        return
    
    # 检查必要的包
    required_packages = ['flask', 'flask_socketio', 'flask_cors', 'numpy', 'requests', 'werkzeug']
    missing_packages = []
    
    for package in required_packages:
        if not check_package(package):
            missing_packages.append(package)
    
    if missing_packages:
        print(f"缺少以下包: {', '.join(missing_packages)}")
        response = input("是否自动安装? (y/n): ").lower()
        if response == 'y':
            if not install_requirements():
                print("❌ 依赖安装失败，但会尝试继续运行")
        else:
            print("请手动安装依赖包: pip install -r requirements.txt")
    
    # 检查端口
    port = 8080
    if not check_port_available(port):
        print(f"警告: 端口 {port} 已被占用")
        for test_port in range(8081, 8090):
            if check_port_available(test_port):
                port = test_port
                break
        else:
            print("❌ 无法找到可用端口")
            input("按回车键退出...")
            return
    
    print(f"✅ 服务器将在端口 {port} 启动")
    print("=" * 60)
    
    # 启动Web应用
    print("正在启动OCR音频识别Web系统...")
    print("提示:")
    print("- 系统启动后会自动打开浏览器")
    print("- 如果浏览器未自动打开，请手动访问: http://localhost:" + str(port))
    print("- 按 Ctrl+C 停止服务器")
    print("=" * 60)
    
    try:
        # 在新线程中打开浏览器
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # 导入并启动Flask应用
        import app
        
        print(f"🚀 启动服务器在端口 {port}")
        app.socketio.run(app.app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
        
    except ImportError as e:
        print(f"❌ 导入Web应用失败: {e}")
        print("请确保 app.py 文件存在且无语法错误")
        input("按回车键退出...")
    except Exception as e:
        print(f"❌ 程序运行错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
