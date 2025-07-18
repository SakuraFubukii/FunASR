#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR音频识别系统启动器
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
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
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
    print("=" * 50)
    print("OCR音频识别系统启动器")
    print("=" * 50)
    
    # 检查Python版本
    if not check_python_version():
        input("按回车键退出...")
        return
    
    # 检查必要的包
    required_packages = ['tkinter', 'funasr', 'pyaudio', 'numpy', 'requests']
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
    
    # 启动主程序
    print("启动OCR音频识别系统...")
    try:
        # 检查tkinter是否可用
        try:
            import tkinter as tk
            print("Tkinter模块检查通过")
            
            # 测试GUI是否可以启动
            test_root = tk.Tk()
            test_root.withdraw()  # 隐藏测试窗口
            test_root.destroy()
            print("GUI环境检查通过")
            
        except Exception as e:
            print(f"GUI环境检查失败: {e}")
            print("可能的解决方案：")
            print("1. 确保系统支持图形界面")
            print("2. 如果使用SSH连接，请启用X11转发")
            input("按回车键退出...")
            return
        
        import main
        main.main()
        
    except ImportError as e:
        print(f"导入主程序失败: {e}")
        input("按回车键退出...")
    except Exception as e:
        print(f"程序运行错误: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()
