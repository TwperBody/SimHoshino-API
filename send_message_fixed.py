import os
import subprocess
import time
import sys
import base64

def enable_adb_keyboard():
    """确保ADBKeyboard输入法已启用"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    adb_path = os.path.join(current_dir, "adb.exe")
    
    
    try:
        # 检查当前输入法
        result = subprocess.run(
            [adb_path, "shell", "settings", "get", "secure", "default_input_method"],
            capture_output=True,
            text=True,
            check=True
        )
        
        current_ime = result.stdout.strip()
        target_ime = "com.android.adbkeyboard/.AdbIME"
        
        if target_ime in current_ime:
            print("✅ ADB启动完成")
            return True
        
        # 启用并设置为默认输入法
        subprocess.run([adb_path, "shell", "ime", "enable", target_ime], check=True)
        subprocess.run([adb_path, "shell", "ime", "set", target_ime], check=True)
        
        # 验证设置
        result = subprocess.run(
            [adb_path, "shell", "settings", "get", "secure", "default_input_method"],
            capture_output=True,
            text=True,
            check=True
        )
        
        if target_ime in result.stdout.strip():
            print("✅ ADB已成功注入")
            return True
        else:
            print("❌ 无法连接ADB")
            return False
            
    except Exception as e:
        print(f"❌ 启用输入失败: {str(e)}")
        return False

def input_text_via_b64(text):
    """使用Base64编码输入文本（更可靠的中文输入方法）"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    adb_path = os.path.join(current_dir, "adb.exe")
    
    try:
        # 将文本转换为Base64编码
        b64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        
        print(f"使用Base64编码输入文本: '{text}' → {b64_text}")
        
        # 发送ADB_INPUT_B64广播
        result = subprocess.run(
            [
                adb_path, "shell", 
                "am", "broadcast", "-a", "ADB_INPUT_B64", 
                "--es", "msg", b64_text
            ],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 检查广播结果
        if "Broadcast completed" in result.stdout:
            print("✅ 文本输入成功")
            return True
        else:
            print(f"❌ 文本输入失败: {result.stdout}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 命令执行失败: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ 输入文本时发生错误: {str(e)}")
        return False

def send_message_via_adb_keyboard(text):
    """使用ADBKeyBoard发送消息（完整流程）"""
    # 1. 确保输入法已启用
    if not enable_adb_keyboard():
        print("❌ 无法启用ADB注入")
        return False
    
    # 2. 激活输入框
    current_dir = os.path.dirname(os.path.abspath(__file__))
    adb_path = os.path.join(current_dir, "adb.exe")
    
    input_box_x, input_box_y = 500, 1000  # 输入框坐标
    
    try:
        subprocess.run([adb_path, "shell", "input", "tap", str(input_box_x), str(input_box_y)], check=True)
        time.sleep(0.5)
    except Exception as e:
        print(f"❌ 注入失败: {str(e)}")
        return False
    
    # 3. 使用Base64编码输入文本
    if not input_text_via_b64(text):
        print("❌ 文本注入失败")
        return False
    
    # 4. 发送消息
    send_button_x, send_button_y = 800, 1200  # 发送按钮坐标
    
    print("发送消息...")
    try:
        # 尝试回车键
        subprocess.run([adb_path, "shell", "input", "keyevent", "66"], check=True)
        
        return True
    except:
        try:
            # 尝试发送按钮
            subprocess.run([adb_path, "shell", "input", "tap", str(send_button_x), str(send_button_y)], check=True)
            print("✅ 消息发送成功（发送按钮）")
            return True
        except Exception as e:
            print(f"❌ 发送失败: {str(e)}")
            return False

def get_ui_state_for_coordinates():
    """获取UI状态以确定坐标"""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    adb_path = os.path.join(current_dir, "adb.exe")
    
    print("获取UI状态以确定坐标...")
    
    try:
        # 获取UI层次结构
        subprocess.run([adb_path, "shell", "uiautomator", "dump", "/sdcard/ui.xml"], check=True)
        subprocess.run([adb_path, "pull", "/sdcard/ui.xml"], check=True)
        
        # 获取屏幕截图
        subprocess.run([adb_path, "shell", "screencap", "-p", "/sdcard/screen.png"], check=True)
        subprocess.run([adb_path, "pull", "/sdcard/screen.png"], check=True)
        
        print("✅ UI状态已保存到当前目录")
        print("请查看 screen.png 和 ui.xml 文件以确定正确的坐标")
        return True
    except Exception as e:
        print(f"❌ 获取UI状态失败: {str(e)}")
        return False

def send_message(message: str) -> bool:
    """
    发送消息的主函数
    
    Args:
        message (str): 要发送的消息内容
        
    Returns:
        bool: 发送是否成功
    """
    return send_message_via_adb_keyboard(message)


# 测试代码已移除 - 此模块作为库使用