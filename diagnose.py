#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR应用诊断工具
"""

import sys
import os
import time

def check_python_version():
    """检查Python版本"""
    print(f"Python版本: {sys.version}")
    if sys.version_info < (3, 7):
        print("❌ Python版本过低，需要3.7+")
        return False
    print("✅ Python版本检查通过")
    return True

def check_imports():
    """检查必要的包导入"""
    packages = {
        'tkinter': 'GUI界面',
        'numpy': '数值计算',
        'requests': 'HTTP请求',
        'pyaudio': '音频处理',
        'funasr': '语音识别'
    }
    
    print("\n检查包导入:")
    failed_packages = []
    
    for package, desc in packages.items():
        try:
            if package == 'tkinter':
                import tkinter as tk
                # 测试GUI创建
                root = tk.Tk()
                root.withdraw()
                root.destroy()
            elif package == 'pyaudio':
                import pyaudio
                # 测试音频设备
                p = pyaudio.PyAudio()
                p.terminate()
            else:
                __import__(package)
            print(f"✅ {package} ({desc}) - 正常")
        except Exception as e:
            print(f"❌ {package} ({desc}) - 失败: {e}")
            failed_packages.append(package)
    
    return len(failed_packages) == 0

def check_model_path():
    """检查模型路径"""
    model_path = "E:\\Huggingface\\models\\paraformer-zh-streaming"
    print(f"\n检查模型路径: {model_path}")
    
    if os.path.exists(model_path):
        print("✅ 模型路径存在")
        # 检查模型文件
        files = os.listdir(model_path)
        if files:
            print(f"   模型文件数量: {len(files)}")
            return True
        else:
            print("❌ 模型文件夹为空")
            return False
    else:
        print("❌ 模型路径不存在")
        return False

def test_gui_minimal():
    """测试最小GUI"""
    print("\n测试GUI启动:")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("测试窗口")
        root.geometry("300x200")
        
        label = tk.Label(root, text="如果您能看到这个窗口，\nGUI功能正常工作！", 
                        font=("Arial", 12))
        label.pack(expand=True)
        
        def close_test():
            print("✅ GUI测试窗口正常显示和关闭")
            root.destroy()
        
        button = tk.Button(root, text="关闭测试", command=close_test)
        button.pack(pady=10)
        
        print("✅ GUI测试窗口已打开，请手动关闭来完成测试")
        
        # 自动关闭定时器
        root.after(5000, lambda: (print("⏰ 自动关闭测试窗口"), root.destroy()))
        
        root.mainloop()
        return True
        
    except Exception as e:
        print(f"❌ GUI测试失败: {e}")
        return False

def main():
    print("=" * 60)
    print("OCR音频识别系统 - 诊断工具")
    print("=" * 60)
    
    all_checks = []
    
    # 基础检查
    all_checks.append(check_python_version())
    all_checks.append(check_imports())
    all_checks.append(check_model_path())
    
    print("\n" + "=" * 40)
    print("诊断结果汇总:")
    print("=" * 40)
    
    if all(all_checks):
        print("✅ 所有基础检查通过")
        
        # GUI测试
        print("\n进行GUI测试...")
        gui_ok = test_gui_minimal()
        
        if gui_ok:
            print("\n🎉 系统看起来运行正常！")
            print("\n建议的启动方式:")
            print("1. python main.py")
            print("2. python launcher.py")
            print("3. python main.py --no-model  (跳过模型加载)")
        else:
            print("\n⚠️  GUI可能有问题，请检查显示设置")
    else:
        print("❌ 存在问题，请先解决上述错误")
        print("\n常见解决方案:")
        print("1. pip install -r requirements.txt")
        print("2. 检查模型是否正确下载")
        print("3. 确保音频设备正常工作")
    
    input("\n按回车键退出诊断...")

if __name__ == "__main__":
    main()
