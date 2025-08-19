from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
from datetime import datetime
from server import MessageServer
import uuid
import threading
import secrets
import string
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
CORS(app)

# 配置日志系统
def setup_logging():
    """设置应用日志配置"""
    # 创建日志目录
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            # 控制台输出
            logging.StreamHandler(),
            # 文件输出（带轮转）
            RotatingFileHandler(
                'logs/simhoshino_api.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5,
                encoding='utf-8'
            )
        ]
    )
    
    # 设置Flask应用的日志级别
    app.logger.setLevel(logging.INFO)
    
    return logging.getLogger('SimHoshino')

# 初始化日志系统
logger = setup_logging()

# 初始化消息服务器实例
message_server = MessageServer()

def generate_api_key():
    """生成安全的API密钥"""
    # 生成32位的随机字符串，包含字母和数字
    alphabet = string.ascii_letters + string.digits
    api_key = 'sk-' + ''.join(secrets.choice(alphabet) for _ in range(48))
    return api_key

def load_or_create_api_key():
    """加载已保存的API密钥，如果不存在则生成新的并保存"""
    key_file = "api_key.txt"
    
    # 检查密钥文件是否存在
    if os.path.exists(key_file):
        try:
            with open(key_file, 'r', encoding='utf-8') as f:
                api_key = f.read().strip()
            
            # 验证密钥格式是否正确
            if api_key.startswith('sk-') and len(api_key) == 51:
                print(f"🔑 使用已保存的API密钥")
                return api_key
            else:
                print("⚠️  已保存的API密钥格式不正确，将生成新密钥")
        except Exception as e:
            print(f"⚠️  读取API密钥文件失败: {e}，将生成新密钥")
    
    # 生成新的API密钥
    print("🆕 生成新的API密钥...")
    api_key = generate_api_key()
    
    # 保存到文件
    try:
        with open(key_file, 'w', encoding='utf-8') as f:
            f.write(api_key)
        print(f"💾 API密钥已保存到 {key_file}")
    except Exception as e:
        print(f"⚠️  保存API密钥失败: {e}")
    
    return api_key

class OpenAIAPIServer:
    def __init__(self):
        self.model_name = "SimHoshino-agent"
        self.conversations = {}
        
    def format_openai_response(self, content, model="SimHoshino-agent"):
        """格式化为OpenAI API响应格式"""
        return {
            "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": len(content.split()),
                "total_tokens": len(content.split())
            }
        }
    
    def format_stream_response(self, content, model="SimHoshino-agent"):
        """格式化为流式响应"""
        chat_id = f"chatcmpl-{uuid.uuid4().hex[:8]}"
        timestamp = int(time.time())
        
        # 开始响应
        yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': timestamp, 'model': model, 'choices': [{'index': 0, 'delta': {'role': 'assistant'}, 'finish_reason': None}]})}\n\n"
        
        # 内容响应
        yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': timestamp, 'model': model, 'choices': [{'index': 0, 'delta': {'content': content}, 'finish_reason': None}]})}\n\n"
        
        # 结束响应
        yield f"data: {json.dumps({'id': chat_id, 'object': 'chat.completion.chunk', 'created': timestamp, 'model': model, 'choices': [{'index': 0, 'delta': {}, 'finish_reason': 'stop'}]})}\n\n"
        yield "data: [DONE]\n\n"

# 创建API服务器实例
api_server = OpenAIAPIServer()

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """OpenAI兼容的聊天完成API"""
    request_id = uuid.uuid4().hex[:8]
    client_ip = request.remote_addr
    
    # 记录请求开始
    logger.info(f"[{request_id}] 新的聊天请求 - 客户端IP: {client_ip}")
    
    try:
        data = request.get_json()
        logger.debug(f"[{request_id}] 请求数据: {json.dumps(data, ensure_ascii=False)}")
        
        # 验证必需字段
        if not data or 'messages' not in data:
            error_msg = "Missing required field: messages"
            logger.warning(f"[{request_id}] 请求验证失败: {error_msg}")
            return jsonify({"error": {"message": error_msg, "type": "invalid_request_error"}}), 400
        
        messages = data['messages']
        model = data.get('model', 'SimHoshino-agent')
        stream = data.get('stream', False)
        
        logger.info(f"[{request_id}] 请求参数 - 模型: {model}, 流式: {stream}, 消息数量: {len(messages)}")
        
        # 获取最后一条用户消息
        user_message = None
        for msg in reversed(messages):
            if msg.get('role') == 'user':
                user_message = msg.get('content', '')
                break
        
        if not user_message:
            error_msg = "No user message found"
            logger.warning(f"[{request_id}] 未找到用户消息")
            return jsonify({"error": {"message": error_msg, "type": "invalid_request_error"}}), 400
        
        logger.info(f"[{request_id}] 收到用户消息: {user_message}")
        print(f"📨 收到用户消息: {user_message}")
        
        # 发送消息到智能体
        logger.info(f"[{request_id}] 开始发送消息到智能体")
        success = message_server.send_message_to_chat(user_message)
        if not success:
            error_msg = "Failed to send message to agent"
            logger.error(f"[{request_id}] 消息发送失败: {error_msg}")
            logger.debug(f"[{request_id}] 发送失败详细信息 - 用户消息: {repr(user_message)}")
            
            # 详细调试信息已记录到日志
            
            # 尝试获取更多调试信息
            try:
                if hasattr(message_server, 'get_connection_status'):
                    status = message_server.get_connection_status()
                    logger.debug(f"[{request_id}] 连接状态: {status}")
                    print(f"   - 连接状态: {status}")
                    
                if hasattr(message_server, 'last_error'):
                    logger.debug(f"[{request_id}] 最后错误: {message_server.last_error}")
                    print(f"   - 最后错误: {message_server.last_error}")
                    
            except Exception as debug_e:
                logger.debug(f"[{request_id}] 获取调试信息时出错: {debug_e}")
                
            return jsonify({"error": {"message": error_msg, "type": "internal_server_error"}}), 500
        
        logger.info(f"[{request_id}] 消息发送成功，等待智能体回复...")
        
        # 等待一段时间让智能体处理
        time.sleep(3)
        
        # 获取智能体回复
        logger.info(f"[{request_id}] 开始获取智能体回复")
        previous_msg, at_msg = message_server.extract_at_messages()
        if at_msg and previous_msg:
            agent_name = previous_msg.strip()
            logger.info(f"[{request_id}] 检测到智能体: {agent_name}")
            print(f"🔍 检测到智能体: {agent_name}")
            
            agent_response = message_server.get_agent_previous_message(agent_name)
            if agent_response:
                logger.info(f"[{request_id}] 获取到智能体回复 - 长度: {len(agent_response)}字符")
                logger.debug(f"[{request_id}] 智能体回复内容: {agent_response}")
                
                if stream:
                    logger.info(f"[{request_id}] 返回流式响应")
                    return app.response_class(
                        api_server.format_stream_response(agent_response, model),
                        mimetype='text/plain'
                    )
                else:
                    logger.info(f"[{request_id}] 返回标准响应")
                    return jsonify(api_server.format_openai_response(agent_response, model))
            else:
                error_msg = f"智能体 {agent_name} 暂未回复，请稍后重试"
                logger.warning(f"[{request_id}] 智能体未回复: {error_msg}")
                logger.debug(f"[{request_id}] 智能体详细信息 - 名称: {agent_name}, previous_msg: {repr(previous_msg)}, at_msg: {repr(at_msg)}")
                # 详细调试信息已记录到日志
        else:
            error_msg = "未检测到智能体回复"
            logger.warning(f"[{request_id}] 未检测到智能体回复")
            logger.debug(f"[{request_id}] extract_at_messages返回值 - previous_msg: {repr(previous_msg)}, at_msg: {repr(at_msg)}")
            # 详细调试信息已记录到日志
            
            # 尝试获取更多调试信息
            try:
                # 检查消息服务器的状态
                print(f"   - 消息服务器实例: {message_server}")
                print(f"   - 消息服务器类型: {type(message_server)}")
                
                # 如果有其他调试方法，也可以调用
                if hasattr(message_server, 'get_last_messages'):
                    last_messages = message_server.get_last_messages()
                    logger.debug(f"[{request_id}] 最近消息: {last_messages}")
                    print(f"   - 最近消息: {last_messages}")
                
                if hasattr(message_server, 'get_debug_info'):
                    debug_info = message_server.get_debug_info()
                    logger.debug(f"[{request_id}] 调试信息: {debug_info}")
                    
            except Exception as debug_e:
                logger.debug(f"[{request_id}] 获取调试信息时出错: {debug_e}")
        
        logger.error(f"[{request_id}] 最终错误: {error_msg}")
        
        if stream:
            logger.info(f"[{request_id}] 返回错误流式响应")
            return app.response_class(
                api_server.format_stream_response(error_msg, model),
                mimetype='text/plain'
            )
        else:
            logger.info(f"[{request_id}] 返回错误标准响应")
            return jsonify(api_server.format_openai_response(error_msg, model))
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        
        logger.error(f"[{request_id}] API异常: {str(e)}")
        logger.error(f"[{request_id}] 异常堆栈:\n{error_trace}")
        logger.debug(f"[{request_id}] 请求数据: {repr(request.get_json())}")
        
        # 详细异常信息已记录到日志
        
        # 导入traceback来获取完整的错误堆栈
        print("📋 完整错误堆栈:")
        traceback.print_exc()
        
        error_response = {
            "error": {
                "message": f"Internal server error: {str(e)}",
                "type": "internal_server_error"
            }
        }
        logger.info(f"[{request_id}] 返回异常响应")
        return jsonify(error_response), 500

@app.route('/v1/models', methods=['GET'])
def list_models():
    """列出可用模型"""
    client_ip = request.remote_addr
    logger.info(f"模型列表请求 - 客户端IP: {client_ip}")
    
    response = {
        "object": "list",
        "data": [{
            "id": "SimHoshino-agent",
            "object": "model",
            "created": int(time.time()),
            "owned_by": "SimHoshino"
        }]
    }
    
    logger.debug(f"返回模型列表: {response}")
    return jsonify(response)

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    client_ip = request.remote_addr
    logger.info(f"健康检查请求 - 客户端IP: {client_ip}")
    
    response = {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "server": "SimHoshino OpenAI API Server"
    }
    
    logger.debug(f"健康检查响应: {response}")
    return jsonify(response)

@app.route('/', methods=['GET'])
def index():
    """根路径信息"""
    client_ip = request.remote_addr
    logger.info(f"根路径访问 - 客户端IP: {client_ip}")
    
    response = {
        "message": "SimHoshino OpenAI API Server",
        "version": "1.0.0",
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "models": "/v1/models",
            "health": "/health"
        },
        "documentation": "Compatible with OpenAI API format"
    }
    
    logger.debug(f"根路径响应: {response}")
    return jsonify(response)

if __name__ == '__main__':
    # 只在主进程中显示启动信息，避免调试模式重载时重复显示
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # ASCII艺术字
        print(r"""
 $$$$$$\  $$\               $$\   $$\                     $$\       $$\                     
$$  __$$\ \__|              $$ |  $$ |                    $$ |      \__|                    
$$ /  \__|$$\ $$$$$$\$$$$\  $$ |  $$ | $$$$$$\   $$$$$$$\ $$$$$$$\  $$\ $$$$$$$\   $$$$$$\  
\$$$$$$\  $$ |$$  _$$  _$$\ $$$$$$$$ |$$  __$$\ $$  _____|$$  __$$\ $$ |$$  __$$\ $$  __$$\ 
 \____$$\ $$ |$$ / $$ / $$ |$$  __$$ |$$ /  $$ |\$$$$$$\  $$ |  $$ |$$ |$$ |  $$ |$$ /  $$ |
$$\   $$ |$$ |$$ | $$ | $$ |$$ |  $$ |$$ |  $$ | \____$$\ $$ |  $$ |$$ |$$ |  $$ |$$ |  $$ |
\$$$$$$  |$$ |$$ | $$ | $$ |$$ |  $$ |\$$$$$$  |$$$$$$$  |$$ |  $$ |$$ |$$ |  $$ |\$$$$$$  |
 \______/ \__|\__| \__| \__|\__|  \__| \______/ \_______/ \__|  \__|\__|\__|  \__| \______/ 
                                                                                            
        """)
        
        # 加载或生成API密钥
        logger.info("应用程序启动开始")
        api_key = load_or_create_api_key()
        logger.info(f"API密钥已准备就绪: {api_key[:12]}...")
        
        logger.info("SimHoshino OpenAI API服务器启动中...")
        print("🚀 启动SimHoshino OpenAI API服务器...")
        print("📡 服务器地址: http://localhost:5000")
        print("🔗 API端点: http://localhost:5000/v1/chat/completions")
        print("📋 模型列表: http://localhost:5000/v1/models")
        print("❤️  健康检查: http://localhost:5000/health")
        print("="*60)
        print(f"🔑 API密钥: {api_key}")
        print("="*60)
        
        logger.info("服务器即将在端口5000上启动")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
