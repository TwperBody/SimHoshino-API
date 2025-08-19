# SimHoshino-API
Translate the Hoshino Platform into an API interface for integration 简单将星野AI平台转换为API使用

<p align="center">
<a href="https://github.com/TwperBody/SimHoshino-API">
<img src="https://github.com/TwperBody/SimHoshino-API/blob/main/sim.png" alt="SimHoshino"/>
</a>

# SimHoshino API 服务器

## 📖 简介

这是一个与OpenAI API完全兼容的服务器，可以将您现有的星野AI智能体消息处理系统包装成标准的OpenAI API接口。

由于大小和避规原因，仓库中并不带有镜像，请使用(releases)[https://github.com/TwperBody/SimHoshino-API/releases]
## 🚀 快速开始

### 1. 启动服务器

**方法：手动启动**
```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务器
python main.py
```
运行 dnplayer.exe并登录星野，打开模型的对话界面，尝试发送一条消息，检查是否能够正常响应。


### 2. 验证服务器状态

服务器启动后，访问以下地址验证：
- 健康检查: http://localhost:5000/health
- 服务器信息: http://localhost:5000/
- 模型列表: http://localhost:5000/v1/models

## 📡 API 端点

### 1. 聊天完成 `/v1/chat/completions`

**请求示例：**
```json
POST http://localhost:5000/v1/chat/completions
Content-Type: application/json

{
  "model": "SimHoshino-agent",
  "messages": [
    {"role": "user", "content": "你好，请介绍一下自己"}
  ],
  "stream": false
}
```

**响应示例：**
```json
{
  "id": "chatcmpl-12345678",
  "object": "chat.completion",
  "created": 1699123456,
  "model": "SimHoshino-agent",
  "choices": [{
    "index": 0,
    "message": {
      "role": "assistant",
      "content": "您好！我是忍冬智能体..."
    },
    "finish_reason": "stop"
  }],
  "usage": {
    "prompt_tokens": 10,
    "completion_tokens": 50,
    "total_tokens": 60
  }
}
```

### 2. 流式响应

设置 `"stream": true` 可启用流式响应(暂时不支持)


### 3. 模型列表 `/v1/models`

```json
GET http://localhost:5000/v1/models
```

## 🔧 配置与集成

### 在现有应用中使用

将API基础URL设置为 `http://localhost:5000`，即可在任何支持OpenAI API的应用中使用：

**Python示例：**
```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:5000/v1",
    api_key="not-needed"  # 可以是任意值
)

response = client.chat.completions.create(
    model="SimHoshino-agent",
    messages=[
        {"role": "user", "content": "你好！"}
    ]
)

print(response.choices[0].message.content)
```

**curl示例：**
```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "SimHoshino-agent",
    "messages": [{"role": "user", "content": "你好"}],
    "stream": false
  }'
```

## 🧪 测试

运行测试客户端验证功能：
```bash
python test_client.py
```

## 🔍 故障排除

### 常见问题

1. **智能体未回复**
   - 确保智能体系统正在运行
   - 检查智能体是否在线
   - 增加等待时间（目前为3秒）

2. **无法检测智能体**
   - 确保页面中有@符号消息
   - 检查智能体名称是否正确

3. **端口占用**
   - 修改main.py中的端口号
   - 或关闭占用5000端口的其他程序

### 调试模式

服务器默认运行在调试模式，会输出详细的日志信息：
- 📨 收到的用户消息
- ✅ 消息发送状态
- 🔍 检测到的智能体
- ✅ 智能体回复内容

## 📈 性能优化

- **并发处理**：支持多个客户端同时请求
- **错误恢复**：自动处理网络异常和超时
- **资源管理**：合理的内存和CPU使用

## 🔒 安全注意事项

- 服务器默认绑定到所有网络接口（0.0.0.0）
- 生产环境建议：
  - 使用反向代理（nginx）
  - 添加身份验证
  - 启用HTTPS
  - 限制访问IP

## 📞 技术支持

如遇问题，请检查：
1. Python版本（建议3.8+）
2. 依赖包是否正确安装
3. 智能体系统是否正常运行
4. 网络连接是否正常

---

##特别感谢

[senzhk/ADBKeyBoard](https://github.com/senzhk/ADBKeyBoard/tree/master?tab=GPL-2.0-1-ov-file)


**版本**: 1.0.0  
**兼容性**: OpenAI API v1  
**许可证**: GPL-2.0
