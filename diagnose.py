#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR系统诊断工具
"""

import os
import sys
import subprocess
import importlib.util
import socket
import json
import traceback
from pathlib import Path

def check_python_environment():
    """检查Python环境"""
    print("=" * 60)
    print("1. Python环境检查")
    print("=" * 60)
    
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    
    if sys.version_info < (3, 7):
        print("❌ Python版本过低，需要3.7+")
        return False
    else:
        print("✅ Python版本符合要求")
        return True

def check_dependencies():
    """检查依赖包"""
    print("\n" + "=" * 60)
    print("2. 依赖包检查")
    print("=" * 60)
    
    required_packages = [
        'flask', 'flask_socketio', 'flask_cors', 'funasr', 
        'numpy', 'requests', 'werkzeug', 'socketio'
    ]
    
    missing_packages = []
    installed_packages = []
    
    for package in required_packages:
        try:
            spec = importlib.util.find_spec(package)
            if spec is not None:
                print(f"✅ {package}: 已安装")
                installed_packages.append(package)
            else:
                print(f"❌ {package}: 未安装")
                missing_packages.append(package)
        except Exception as e:
            print(f"❌ {package}: 检查失败 - {e}")
            missing_packages.append(package)
    
    return missing_packages, installed_packages

def check_file_permissions():
    """检查文件和目录权限"""
    print("\n" + "=" * 60)
    print("3. 文件权限检查")
    print("=" * 60)
    
    current_dir = Path(__file__).parent
    
    # 检查关键文件
    critical_files = [
        'app.py', 'web_launcher.py', 'templates/index.html',
        'static/js/app.js', 'static/css/style.css'
    ]
    
    for file_path in critical_files:
        full_path = current_dir / file_path
        if full_path.exists():
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    f.read(1)  # 尝试读取
                print(f"✅ {file_path}: 可读")
            except Exception as e:
                print(f"❌ {file_path}: 读取失败 - {e}")
        else:
            print(f"❌ {file_path}: 文件不存在")
    
    # 检查uploads目录
    uploads_dir = current_dir / 'uploads'
    try:
        uploads_dir.mkdir(exist_ok=True)
        # 尝试写入测试文件
        test_file = uploads_dir / 'test_write.txt'
        with open(test_file, 'w') as f:
            f.write('test')
        test_file.unlink()  # 删除测试文件
        print(f"✅ uploads目录: 可读写")
    except Exception as e:
        print(f"❌ uploads目录: 权限问题 - {e}")
    
    # 检查模型路径
    model_path = Path(r"E:\Huggingface\models\paraformer-zh-streaming")
    if model_path.exists():
        try:
            # 尝试列出目录内容
            list(model_path.iterdir())
            print(f"✅ 模型路径: 可访问")
        except Exception as e:
            print(f"❌ 模型路径: 访问失败 - {e}")
    else:
        print(f"❌ 模型路径: 不存在")

def check_network_ports():
    """检查网络端口"""
    print("\n" + "=" * 60)
    print("4. 网络端口检查")
    print("=" * 60)
    
    ports_to_check = [8080, 8081, 8082, 5000]
    
    for port in ports_to_check:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                print(f"✅ 端口 {port}: 可用")
        except OSError:
            print(f"❌ 端口 {port}: 被占用")

def check_admin_privileges():
    """检查管理员权限"""
    print("\n" + "=" * 60)
    print("5. 管理员权限检查")
    print("=" * 60)
    
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            print("✅ 当前以管理员权限运行")
        else:
            print("⚠️ 未以管理员权限运行")
        return is_admin
    except Exception as e:
        print(f"❌ 权限检查失败: {e}")
        return False

def test_flask_import():
    """测试Flask导入"""
    print("\n" + "=" * 60)
    print("6. Flask组件测试")
    print("=" * 60)
    
    try:
        from flask import Flask
        print("✅ Flask: 导入成功")
        
        from flask_socketio import SocketIO
        print("✅ Flask-SocketIO: 导入成功")
        
        from flask_cors import CORS
        print("✅ Flask-CORS: 导入成功")
        
        # 尝试创建简单的Flask应用
        app = Flask(__name__)
        print("✅ Flask应用: 创建成功")
        
        return True
    except Exception as e:
        print(f"❌ Flask组件测试失败: {e}")
        traceback.print_exc()
        return False

def test_funasr_import():
    """测试FunASR导入"""
    print("\n" + "=" * 60)
    print("7. FunASR模块测试")
    print("=" * 60)
    
    try:
        from funasr import AutoModel
        print("✅ FunASR: 导入成功")
        return True
    except Exception as e:
        print(f"❌ FunASR导入失败: {e}")
        traceback.print_exc()
        return False

def generate_fixed_launcher():
    """生成修复后的启动器"""
    print("\n" + "=" * 60)
    print("8. 生成修复方案")
    print("=" * 60)
    
    fixed_launcher = '''#!/usr/bin/env python3
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
'''
    
    with open('web_launcher_fixed.py', 'w', encoding='utf-8') as f:
        f.write(fixed_launcher)
    
    print("✅ 修复版启动器已生成: web_launcher_fixed.py")

def main():
    """主诊断函数"""
    print("OCR系统诊断工具")
    print("正在检查系统状态...\n")
    
    # 执行所有检查
    python_ok = check_python_environment()
    missing_deps, installed_deps = check_dependencies()
    check_file_permissions()
    check_network_ports()
    is_admin = check_admin_privileges()
    flask_ok = test_flask_import()
    funasr_ok = test_funasr_import()
    
    # 生成报告
    print("\n" + "=" * 60)
    print("诊断报告")
    print("=" * 60)
    
    if python_ok:
        print("✅ Python环境: 正常")
    else:
        print("❌ Python环境: 有问题")
    
    if not missing_deps:
        print("✅ 依赖包: 全部安装")
    else:
        print(f"❌ 依赖包: 缺少 {len(missing_deps)} 个")
        print(f"   缺少的包: {', '.join(missing_deps)}")
    
    if flask_ok:
        print("✅ Flask组件: 正常")
    else:
        print("❌ Flask组件: 有问题")
    
    if not is_admin:
        print("⚠️ 管理员权限: 未获取（可能导致文件权限问题）")
    else:
        print("✅ 管理员权限: 已获取")
    
    # 给出建议
    print("\n" + "=" * 60)
    print("修复建议")
    print("=" * 60)
    
    if missing_deps:
        print("1. 安装缺少的依赖包:")
        print("   pip install -r requirements.txt")
        print("   或者:")
        for dep in missing_deps:
            print(f"   pip install {dep}")
    
    if not is_admin:
        print("2. 以管理员身份运行程序:")
        print("   右键点击命令提示符 -> 以管理员身份运行")
        print("   然后再运行 python web_launcher.py")
    
    if not flask_ok:
        print("3. 重新安装Flask相关组件:")
        print("   pip uninstall flask flask-socketio flask-cors")
        print("   pip install flask flask-socketio flask-cors")
    
    # 生成修复版本
    generate_fixed_launcher()
    
    print("\n建议使用修复版启动器: python web_launcher_fixed.py")

if __name__ == "__main__":
    main()
