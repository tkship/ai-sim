"""AI 响应解析模块

解析 AI 返回的 JSON 格式数据
"""
import json
from typing import Dict, List, Optional, Any
import re


class AIResponseParser:
    """AI 响应解析器"""

    def __init__(self, strict_mode: bool = False):
        """初始化解析器

        Args:
            strict_mode: 严格模式，缺失必需字段时会抛出异常
        """
        self.strict_mode = strict_mode

    def parse_single_response(self, response_text: str) -> Dict[str, Any]:
        """解析单个角色的响应

        Args:
            response_text: AI 返回的文本

        Returns:
            解析后的响应字典

        Raises:
            ValueError: JSON 解析失败或格式错误
        """
        # 尝试提取 JSON 部分
        json_str = self._extract_json(response_text)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            if self.strict_mode:
                raise ValueError(f"JSON 解析失败: {e}")
            # 返回默认响应
            return self._get_default_response()

        # 验证必需字段
        required_fields = ["action_thought", "scene_description", "attribute_deltas"]
        for field in required_fields:
            if field not in data:
                if self.strict_mode:
                    raise ValueError(f"缺失必需字段: {field}")
                # 填充默认值
                if field == "action_thought":
                    data[field] = "沉思中..."
                elif field == "scene_description":
                    data[field] = "周围一片寂静"
                elif field == "attribute_deltas":
                    data[field] = {}

        # 规范化属性增量
        if "attribute_deltas" not in data:
            data["attribute_deltas"] = {}
        else:
            # 确保数值类型
            attr_deltas = data["attribute_deltas"]
            for key, value in list(attr_deltas.items()):
                if not isinstance(value, (int, float)):
                    try:
                        attr_deltas[key] = int(value)
                    except (ValueError, TypeError):
                        del attr_deltas[key]

        # 规范化物品变化
        if "item_changes" not in data:
            data["item_changes"] = {"obtained": [], "lost": []}
        else:
            item_changes = data["item_changes"]
            if "obtained" not in item_changes:
                item_changes["obtained"] = []
            if "lost" not in item_changes:
                item_changes["lost"] = []

        return data

    def parse_group_response(self, response_text: str) -> List[Dict[str, Any]]:
        """解析多角色交互组的响应

        Args:
            response_text: AI 返回的文本

        Returns:
            解析后的响应字典列表

        Raises:
            ValueError: JSON 解析失败或格式错误
        """
        # 尝试提取 JSON 部分
        json_str = self._extract_json(response_text)

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            if self.strict_mode:
                raise ValueError(f"JSON 解析失败: {e}")
            # 返回空列表
            return []

        # 确保是数组
        if not isinstance(data, list):
            if self.strict_mode:
                raise ValueError("多角色响应应该是数组格式")
            return []

        # 解析每个角色的响应
        results = []
        for item in data:
            try:
                result = self.parse_single_response(json.dumps(item))
                if "character_id" in item:
                    result["character_id"] = item["character_id"]
                results.append(result)
            except ValueError:
                if self.strict_mode:
                    raise
                continue

        return results

    def _extract_json(self, text: str) -> str:
        """从文本中提取 JSON 部分

        Args:
            text: 原始文本

        Returns:
            JSON 字符串
        """
        # 去除前后空白
        text = text.strip()

        # 检查是否已经是纯 JSON
        if text.startswith("{") or text.startswith("["):
            return text

        # 尝试提取 ```json ... ``` 代码块
        json_block_match = re.search(r"```(?:json)?\s*\n([\s\S]*?)\n```", text)
        if json_block_match:
            return json_block_match.group(1).strip()

        # 尝试查找 { ... } 或 [ ... ]
        brace_match = re.search(r"\{[\s\S]*\}|\[[\s\S]*\]", text)
        if brace_match:
            return brace_match.group(0)

        # 无法提取，返回原文本
        return text

    def _get_default_response(self) -> Dict[str, Any]:
        """获取默认响应"""
        return {
            "action_thought": "沉思中...",
            "scene_description": "周围一片寂静",
            "attribute_deltas": {
                "health": 0,
                "spirit_power": 0,
            },
            "item_changes": {
                "obtained": [],
                "lost": [],
            },
        }

    def validate_attribute_deltas(self, deltas: Dict[str, int]) -> bool:
        """验证属性增量是否合理

        Args:
            deltas: 属性增量字典

        Returns:
            是否合理
        """
        # 检查数值范围
        limits = {
            "health": (-50, 50),
            "spirit_power": (-30, 100),
            "consciousness": (-10, 10),
            "luck": (-5, 5),
        }

        for key, value in deltas.items():
            if key in limits:
                min_val, max_val = limits[key]
                if value < min_val or value > max_val:
                    return False

        return True

    def clamp_attribute_deltas(self, deltas: Dict[str, int]) -> Dict[str, int]:
        """限制属性增量在合理范围内

        Args:
            deltas: 属性增量字典

        Returns:
            限制后的属性增量字典
        """
        limits = {
            "health": (-50, 50),
            "spirit_power": (-30, 100),
            "consciousness": (-10, 10),
            "luck": (-5, 5),
        }

        result = {}
        for key, value in deltas.items():
            if key in limits:
                min_val, max_val = limits[key]
                result[key] = max(min_val, min(max_val, value))
            else:
                result[key] = value

        return result
