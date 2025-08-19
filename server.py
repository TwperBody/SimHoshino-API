#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能体消息处理服务器
整合了消息提取、发送和XML分析功能
"""

import sys
import os
from typing import Optional, List, Dict

# 导入三个核心模块
try:
    # 导入消息发送模块
    from send_message_fixed import (
        send_message,
        enable_adb_keyboard,
        input_text_via_b64,
        get_ui_state_for_coordinates
    )
    
    # 导入消息提取模块
    from message_extractor import (
        MessageExtractor,
        get_agent_previous_message
    )
    
    # 导入主功能模块
    from message_main import (
        get_page_texts,
        get_at_symbol_messages,
        analyze_ui_structure
    )
    
    print("✅ 所有模块导入成功")
    
except ImportError as e:
    print(f"❌ 模块导入失败: {e}")
    print("请确保以下文件存在于当前目录:")
    print("- send_message_fixed.py")
    print("- message_extractor.py")
    print("- message_main.py")
    sys.exit(1)


class MessageServer:
    """智能体消息处理服务器类"""
    
    def __init__(self):
        """初始化聊天器"""
        self.extractor = MessageExtractor()
        print("🚀 消息服务器初始化完成")
    
    def get_agent_previous_message(self, agent_name: str) -> Optional[str]:
        """
        获取指定智能体的上一句消息
        
        Args:
            agent_name (str): 智能体名称
            
        Returns:
            Optional[str]: 上一句消息内容
        """
        print(f"📥 正在获取智能体 '{agent_name}' 的上一句消息...")
        return get_agent_previous_message(agent_name)
    
    def send_message_to_chat(self, message: str) -> bool:
        """
        发送消息到聊天界面
        
        Args:
            message (str): 要发送的消息内容
            
        Returns:
            bool: 发送是否成功
        """
        print(f"📤 正在发送消息: '{message}'")
        return send_message(message)
    
    def get_page_xml_info(self) -> List[str]:
        """
        获取当前页面的所有文本信息
        
        Returns:
            List[str]: 页面文本列表
        """
        print("📱 正在获取页面文本信息...")
        return get_page_texts()
    
    def extract_at_messages(self) -> tuple:
        """
        提取包含@符号的消息及其前一个元素
        
        Returns:
            tuple: (previous_message, at_message) 元组
        """
        return get_at_symbol_messages()
    
    def get_ui_debug_info(self) -> bool:
        """
        获取UI调试信息（截图和XML）
        
        Returns:
            bool: 是否成功获取调试信息
        """
        print("🔧 正在获取UI调试信息...")
        return get_ui_state_for_coordinates()
    
    def check_adb_keyboard_status(self) -> bool:
        """
        检查并启用ADB键盘
        
        Returns:
            bool: ADB键盘是否可用
        """
        print("⌨️ 正在检查ADB键盘状态...")
        return enable_adb_keyboard()
    
    def analyze_ui_structure(self) -> dict:
        """
        分析UI结构，返回详细信息
        
        Returns:
            dict: UI分析结果
        """
        print("🔍 正在分析UI结构...")
        return analyze_ui_structure()


# 交互式测试代码已移除 - 此模块作为库使用
# MessageServer类可以直接导入使用
