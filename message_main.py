import os
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Tuple


class MessageExtractor:
    """智能体消息提取器 - 优化版"""
    
    def __init__(self):
        """初始化提取器，设置ADB路径"""
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.adb_path = os.path.join(current_dir, "adb.exe")
        self.xml_file = Path("ui_dump.xml")
        
    def _capture_ui_data(self, silent: bool = False) -> bool:
        """
        捕获UI数据
        
        Args:
            silent (bool): 是否静默执行
            
        Returns:
            bool: 是否成功捕获数据
        """
        try:
            if not silent:
                print("正在获取页面信息...")
            
            # 获取界面XML并拉取到本地
            subprocess.run([
                self.adb_path, "shell", "uiautomator", "dump", "/sdcard/ui_dump.xml"
            ], check=True, capture_output=True)
            
            subprocess.run([
                self.adb_path, "pull", "/sdcard/ui_dump.xml", "."
            ], check=True, capture_output=True)

            # 验证文件
            if self.xml_file.exists() and self.xml_file.stat().st_size > 0:
                if not silent:
                    print(f"✅ 成功获取数据 ({self.xml_file.stat().st_size:,} 字节)")
                return True
            else:
                if not silent:
                    print("❌ 数据获取失败")
                return False
            
        except Exception as e:
            if not silent:
                print(f"❌ 获取数据失败: {str(e)}")
            return False
    
    def _extract_all_texts(self) -> List[str]:
        """从XML文件中提取所有文本内容"""
        if not self.xml_file.exists():
            return []
            
        try:
            tree = ET.parse(self.xml_file)
            return [
                node.attrib.get("text", "").strip() 
                for node in tree.iter() 
                if node.attrib.get("text", "").strip()
            ]
        except ET.ParseError:
            return []
    
    def get_previous_message(self, agent_name: str, silent: bool = False) -> Optional[str]:
        """
        获取指定智能体的上一句消息
        
        Args:
            agent_name (str): 智能体名称
            silent (bool): 是否静默执行
            
        Returns:
            Optional[str]: 上一句消息内容
        """
        if not self._capture_ui_data(silent=silent):
            return None
        
        texts = self._extract_all_texts()
        if not texts:
            return None
        
        target_pattern = f"发送消息给{agent_name}"
        
        for i, text in enumerate(texts):
            if target_pattern in text and i > 0:
                previous_text = texts[i - 1]
                if not silent:
                    print(f"找到智能体 '{agent_name}' 的上一句消息: {previous_text}")
                return previous_text
        
        if not silent:
            print(f"未找到 '{target_pattern}' 相关内容")
        return None


def get_agent_previous_message(agent_name: str, silent: bool = False) -> Optional[str]:
    """
    便捷函数：获取指定智能体的上一句消息
    
    Args:
        agent_name (str): 智能体名称
        silent (bool): 是否静默执行
        
    Returns:
        Optional[str]: 上一句消息内容
    """
    extractor = MessageExtractor()
    return extractor.get_previous_message(agent_name, silent=silent)


def get_at_symbol_messages(silent: bool = False) -> Tuple[Optional[str], Optional[str]]:
    """
    提取包含@符号的文本元素及其前一个元素
    
    Args:
        silent (bool): 是否静默执行
    
    Returns:
        Tuple[Optional[str], Optional[str]]: (previous_message, at_message)
    """
    extractor = MessageExtractor()
    
    if not extractor._capture_ui_data(silent=silent):
        return (None, None)
    
    texts = extractor._extract_all_texts()
    if not texts:
        return (None, None)
    
    for i, text in enumerate(texts):
        if "@" in text:
            previous_message = texts[i - 1] if i > 0 else None
            return (previous_message, text)
    
    return (None, None)


def get_page_texts(silent: bool = False) -> List[str]:
    """
    获取当前页面的所有文本内容
    
    Args:
        silent (bool): 是否静默执行
    
    Returns:
        List[str]: 所有文本内容列表
    """
    extractor = MessageExtractor()
    
    if not extractor._capture_ui_data(silent=silent):
        return []
    
    texts = extractor._extract_all_texts()
    
    if not silent and texts:
        print(f"📊 共找到 {len(texts)} 个文本元素")
        for i, text in enumerate(texts[:10], 1):  # 显示前10个
            print(f"{i:2d}. {text}")
        if len(texts) > 10:
            print(f"... (还有 {len(texts) - 10} 个文本)")
    
    return texts


def analyze_ui_structure() -> dict:
    """
    分析UI结构，返回详细信息
    
    Returns:
        dict: UI分析结果
    """
    extractor = MessageExtractor()
    
    if not extractor._capture_ui_data():
        return {"error": "无法获取UI数据"}
    
    texts = extractor._extract_all_texts()
    
    # 查找@符号消息
    at_messages = []
    agent_messages = []
    
    for i, text in enumerate(texts):
        if "@" in text:
            at_messages.append({
                "index": i,
                "text": text,
                "previous": texts[i-1] if i > 0 else None
            })
        
        if "发送消息给" in text:
            agent_messages.append({
                "index": i,
                "text": text,
                "previous": texts[i-1] if i > 0 else None
            })
    
    return {
        "total_texts": len(texts),
        "all_texts": texts,
        "at_messages": at_messages,
        "agent_messages": agent_messages,
        "file_size": extractor.xml_file.stat().st_size if extractor.xml_file.exists() else 0
    }


# 测试代码已移除 - 此模块作为库使用 