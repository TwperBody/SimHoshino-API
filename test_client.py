import requests
import json

def test_openai_api():
    """测试OpenAI API兼容性"""
    base_url = "http://localhost:5000"
    
    # 测试健康检查
    print("🔍 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"✅ 健康检查: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return
    
    # 测试模型列表
    print("\n🔍 测试模型列表...")
    try:
        response = requests.get(f"{base_url}/v1/models")
        print(f"✅ 模型列表: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"❌ 模型列表失败: {e}")
    
    # 测试聊天完成API
    print("\n🔍 测试聊天完成API...")
    chat_data = {
        "model": "SimHoshino-agent",
        "messages": [
            {"role": "user", "content": "你好，请介绍一下自己"}
        ],
        "stream": False
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=chat_data,
            headers={"Content-Type": "application/json"}
        )
        print(f"✅ 聊天API: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   智能体回复: {result['choices'][0]['message']['content']}")
        else:
            print(f"   错误响应: {response.text}")
    except Exception as e:
        print(f"❌ 聊天API失败: {e}")

def test_stream_api():
    """测试流式API"""
    print("\n🔍 测试流式API...")
    base_url = "http://localhost:5000"
    
    chat_data = {
        "model": "SimHoshino-agent",
        "messages": [
            {"role": "user", "content": "请简单介绍一下你的功能"}
        ],
        "stream": True
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            json=chat_data,
            headers={"Content-Type": "application/json"},
            stream=True
        )
        
        print(f"✅ 流式API: {response.status_code}")
        if response.status_code == 200:
            print("📡 流式响应:")
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 移除 'data: ' 前缀
                        if data_str.strip() == '[DONE]':
                            print("✅ 流式响应完成")
                            break
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    print(f"   内容: {delta['content']}")
                        except json.JSONDecodeError:
                            pass
        else:
            print(f"   错误响应: {response.text}")
    except Exception as e:
        print(f"❌ 流式API失败: {e}")

if __name__ == "__main__":
    print("🧪 SimHoshino OpenAI API 测试客户端")
    print("="*50)
    
    # 基础API测试
    test_openai_api()
    
    # 流式API测试
    test_stream_api()
    
    print("\n" + "="*50)
    print("🎉 测试完成！") 