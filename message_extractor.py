import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List


class MessageExtractor:
    """智能体消息提取器"""
    
    def __init__(self):
        """初始化提取器，设置ADB路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.adb_path = os.path.join(current_dir, "adb.exe")
        
    def _capture_ui_data(self) -> bool:
        """
        捕获UI数据（XML和截图）
        
        Returns:
            bool: 是否成功捕获数据
        """
        try:
            # 1. 获取界面XML
            subprocess.run([self.adb_path, "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"], 
                         check=True, capture_output=True)
            
            # 2. 拉取XML到当前目录
            subprocess.run([self.adb_path, "pull", "/sdcard/ui_dump.xml", "."], 
                         check=True, capture_output=True)
            
            return Path("ui_dump.xml").exists()
            
        except subprocess.CalledProcessError:
            return False
    
    def _extract_all_texts(self) -> List[str]:
        """
        从XML文件中提取所有文本内容
        
        Returns:
            List[str]: 所有文本内容列表
        """
        texts = []
        if not Path("ui_dump.xml").exists():
            return texts
            
        try:
            tree = ET.parse("ui_dump.xml")
            for node in tree.iter():
                if text := node.attrib.get("text", "").strip():
                    texts.append(text)
        except ET.ParseError:
            pass
            
        return texts
    
    def get_previous_message(self, agent_name: str) -> Optional[str]:
        """
        获取指定智能体的上一句消息
        
        Args:
            agent_name (str): 智能体名称
            
        Returns:
            Optional[str]: 上一句消息内容，如果没找到则返回None
        """
        # 1. 捕获UI数据
        if not self._capture_ui_data():
            print("错误：无法获取UI数据")
            return None
        
        # 2. 提取所有文本
        texts = self._extract_all_texts()
        if not texts:
            print("错误：未找到任何文本内容")
            return None
        
        # 3. 查找目标模式
        target_pattern = f"发送消息给{agent_name}"
        
        for i, text in enumerate(texts):
            if target_pattern in text:
                # 找到了目标文本，返回上一句
                if i > 0:
                    previous_text = texts[i - 1]
                    print(f"找到智能体 '{agent_name}' 的上一句消息: {previous_text}")
                    return previous_text
                else:
                    print(f"找到了 '{target_pattern}'，但它是第一句，没有上一句")
                    return None
        
        print(f"未找到 '{target_pattern}' 相关内容")
        return None
    
    def get_all_messages_context(self, agent_name: str) -> dict:
        """
        获取指定智能体的完整消息上下文
        
        Args:
            agent_name (str): 智能体名称
            
        Returns:
            dict: 包含上一句消息、目标句和所有文本的字典
        """
        if not self._capture_ui_data():
            return {"error": "无法获取UI数据"}
        
        texts = self._extract_all_texts()
        target_pattern = f"发送消息给{agent_name}"
        
        result = {
            "agent_name": agent_name,
            "target_found": False,
            "previous_message": None,
            "target_message": None,
            "all_texts": texts
        }
        
        for i, text in enumerate(texts):
            if target_pattern in text:
                result["target_found"] = True
                result["target_message"] = text
                if i > 0:
                    result["previous_message"] = texts[i - 1]
                break
        
        return result


def get_agent_previous_message(agent_name: str) -> Optional[str]:
    """
    便捷函数：获取指定智能体的上一句消息
    
    Args:
        agent_name (str): 智能体名称（如 "黍"）
        
    Returns:
        Optional[str]: 上一句消息内容
        
    Example:
        >>> message = get_agent_previous_message("黍")
        >>> print(message)
        "（语气危险）看来，你这只可爱的小白兔，终于落入了我的手里呢～"
    """
    extractor = MessageExtractor()
    return extractor.get_previous_message(agent_name)


# 测试代码已移除 - 此模块作为库使用 