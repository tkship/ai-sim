"""AI 接口模块

提供通用的 AI API 调用接口，支持多种格式
"""
import httpx
from typing import Dict, List, Optional, Any
import json


class AIInterface:
    """AI 接口类

    支持调用多种格式的 AI API
    """

    def __init__(
        self,
        url: str = "https://api.example.com/v1/chat",
        api_key: str = "",
        format_type: str = "openai",
        model: str = "gpt-3.5-turbo",
        timeout: int = 30,
    ):
        """初始化 AI 接口

        Args:
            url: API 地址
            api_key: API Key
            format_type: 请求格式（openai, anthropic, generic）
            model: 模型名称
            timeout: 请求超时（秒）
        """
        self.url = url
        self.api_key = api_key
        self.format_type = format_type
        self.model = model
        self.timeout = timeout

        self.client = httpx.Client(timeout=timeout)

    def _build_openai_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict:
        """构建 OpenAI 格式的请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            请求数据
        """
        return {
            "model": kwargs.get("model", self.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 1000),
        }

    def _build_anthropic_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict:
        """构建 Anthropic 格式的请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            请求数据
        """
        # 将消息转换为 Anthropic 格式
        system_message = ""
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            elif msg["role"] == "user":
                user_messages.append({"role": "user", "content": msg["content"]})
            elif msg["role"] == "assistant":
                user_messages.append({"role": "assistant", "content": msg["content"]})

        return {
            "model": kwargs.get("model", self.model),
            "system": system_message,
            "messages": user_messages,
            "max_tokens": kwargs.get("max_tokens", 1000),
        }

    def _build_generic_request(self, messages: List[Dict[str, str]], **kwargs) -> Dict:
        """构建通用 JSON 格式的请求

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            请求数据
        """
        # 简单地将消息合并为 prompt
        prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])

        return {
            "prompt": prompt,
            "model": kwargs.get("model", self.model),
            **kwargs,
        }

    def _extract_openai_response(self, response_data: Dict) -> str:
        """提取 OpenAI 格式的响应

        Args:
            response_data: 响应数据

        Returns:
            响应文本
        """
        return response_data.get("choices", [{}])[0].get("message", {}).get("content", "")

    def _extract_anthropic_response(self, response_data: Dict) -> str:
        """提取 Anthropic 格式的响应

        Args:
            response_data: 响应数据

        Returns:
            响应文本
        """
        return response_data.get("content", [{}])[0].get("text", "")

    def _extract_generic_response(self, response_data: Dict) -> str:
        """提取通用格式的响应

        Args:
            response_data: 响应数据

        Returns:
            响应文本
        """
        # 尝试常见的响应字段
        if "response" in response_data:
            return response_data["response"]
        elif "text" in response_data:
            return response_data["text"]
        elif "output" in response_data:
            return response_data["output"]
        elif "completion" in response_data:
            return response_data["completion"]
        elif "result" in response_data:
            return response_data["result"]
        else:
            # 返回整个 JSON 字符串
            return json.dumps(response_data, ensure_ascii=False)

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """发送聊天请求

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            **kwargs: 其他参数

        Returns:
            AI 的响应文本

        Raises:
            httpx.HTTPError: 请求失败
            ValueError: 响应格式错误
        """
        # 构建请求
        if self.format_type == "openai":
            request_data = self._build_openai_request(messages, **kwargs)
        elif self.format_type == "anthropic":
            request_data = self._build_anthropic_request(messages, **kwargs)
        else:  # generic
            request_data = self._build_generic_request(messages, **kwargs)

        # 构建请求头
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        # 发送请求
        try:
            response = self.client.post(
                self.url,
                json=request_data,
                headers=headers,
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise

        # 解析响应
        response_data = response.json()

        # 提取响应文本
        if self.format_type == "openai":
            return self._extract_openai_response(response_data)
        elif self.format_type == "anthropic":
            return self._extract_anthropic_response(response_data)
        else:  # generic
            return self._extract_generic_response(response_data)

    def close(self) -> None:
        """关闭 HTTP 客户端"""
        self.client.close()

    def __enter__(self):
        """支持上下文管理器"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持上下文管理器"""
        self.close()


class MockAIInterface(AIInterface):
    """Mock AI 接口

    用于测试和不连接真实 AI 的情况
    """

    def __init__(self):
        """初始化 Mock 接口"""
        super().__init__(url="", format_type="mock")

    def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """返回预设的模拟响应

        Args:
            messages: 消息列表
            **kwargs: 其他参数

        Returns:
            模拟的响应
        """
        # 返回一个模拟的 JSON 响应
        return json.dumps({
            "action_thought": "决定打坐修炼，恢复灵力",
            "scene_description": "灵气充盈，周围的草木在风中轻轻摇曳",
            "attribute_deltas": {
                "health": 0,
                "spirit_power": 5,
            },
            "item_changes": {
                "obtained": [],
                "lost": [],
            },
        }, ensure_ascii=False)
