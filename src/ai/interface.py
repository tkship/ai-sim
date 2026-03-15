"""
AI 接口和属性变化应用模块
"""
from typing import Optional, Any
from .parser import AIResponse, ResponseParser
from .prompt import PromptBuilder
from ..character import Character


class AIInterface:
    """AI 接口"""

    def __init__(self, api_url: str = "", api_key: str = "", model: str = ""):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model

    async def request_decision(
        self,
        prompt: str
    ) -> Optional[AIResponse]:
        """
        请求 AI 决策（模拟版，实际项目中应该调用真实 API）

        Args:
            prompt: 提示词

        Returns:
            AI 响应或 None
        """
        # 这是模拟实现，实际项目中应该调用真实的 LLM API
        # 这里返回一个简单的示例响应
        import json
        mock_response = {
            "交互概述": "角色选择继续修炼",
            "场景描述": "角色闭目打坐，运转功法修炼...",
            "属性变化": {
                "char_001": {
                    "灵力": 5,
                    "状态": {
                        "新增": [],
                        "移除": []
                    },
                    "法宝变化": [],
                    "物品变化": {
                        "获得": {},
                        "失去": {}
                    }
                }
            }
        }
        json_str = json.dumps(mock_response, ensure_ascii=False)
        return ResponseParser.parse(json_str)


class ChangeApplier:
    """属性变化应用器"""

    @staticmethod
    def apply_to_character(
        character: Character,
        response: AIResponse
    ) -> tuple[Character, list[str]]:
        """
        将 AI 响应中的变化应用到角色

        Args:
            character: 原始角色
            response: AI 响应

        Returns:
            (新角色对象, 变化日志列表)
        """
        logs = []
        new_char = character

        # 查找该角色的变化
        char_change = None
        for cid, change in response.character_changes.items():
            if cid == character.id or cid == character.name:
                char_change = change
                break

        if not char_change:
            return new_char, logs

        # 应用属性变化
        attr = char_change.attributes
        if attr.hp_delta != 0:
            new_attr = new_char.attributes.with_hp_delta(attr.hp_delta)
            new_char = new_char.with_attributes(new_attr)
            logs.append(f"血量变化: {attr.hp_delta:+d}")

        if attr.mp_delta != 0:
            new_attr = new_char.attributes.with_mp_delta(attr.mp_delta)
            new_char = new_char.with_attributes(new_attr)
            logs.append(f"灵力变化: {attr.mp_delta:+d}")

        if attr.spirit_delta != 0:
            new_attr = new_char.attributes.with_spirit_delta(attr.spirit_delta)
            new_char = new_char.with_attributes(new_attr)
            logs.append(f"神识变化: {attr.spirit_delta:+d}")

        # 应用状态变化
        for status in attr.status_add:
            new_attr = new_char.attributes.add_status(status)
            new_char = new_char.with_attributes(new_attr)
            logs.append(f"添加状态: {status}")

        for status in attr.status_remove:
            new_attr = new_char.attributes.remove_status(status)
            new_char = new_char.with_attributes(new_attr)
            logs.append(f"移除状态: {status}")

        # 应用物品变化
        item_change = char_change.item_changes
        for item_name, count in item_change.items_gained.items():
            new_char = new_char.add_item(item_name, count)
            logs.append(f"获得物品: {item_name} ×{count}")

        for item_name, count in item_change.items_lost.items():
            new_char = new_char.remove_item(item_name, count)
            logs.append(f"失去物品: {item_name} ×{count}")

        return new_char, logs

    @staticmethod
    def apply_to_characters(
        characters: list[Character],
        response: AIResponse
    ) -> tuple[list[Character], dict[str, list[str]]]:
        """
        将变化应用到多个角色

        Args:
            characters: 原始角色列表
            response: AI 响应

        Returns:
            (新角色列表, {角色ID: 变化日志列表})
        """
        new_characters = []
        all_logs = {}

        for char in characters:
            new_char, logs = ChangeApplier.apply_to_character(char, response)
            new_characters.append(new_char)
            if logs:
                all_logs[char.id] = logs

        return new_characters, all_logs


class AICoordinator:
    """AI 协调器 - 整合提示词构建、AI 请求、响应解析、变化应用"""

    def __init__(self, ai_interface: AIInterface, prompt_builder: PromptBuilder):
        self.ai_interface = ai_interface
        self.prompt_builder = prompt_builder

    async def process_single_character(
        self,
        character: Character,
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any]
    ) -> tuple[Character, AIResponse, list[str]]:
        """
        处理单个角色的决策流程

        Args:
            character: 角色
            environment: 环境信息
            treasures_data: 法宝数据
            techniques_data: 功法数据

        Returns:
            (新角色, AI响应, 变化日志)
        """
        # 构建提示词
        prompt = self.prompt_builder.build_single_character_prompt(
            character, environment, treasures_data, techniques_data
        )

        # 请求 AI 决策
        response = await self.ai_interface.request_decision(prompt)
        if not response:
            return character, None, []

        # 验证响应
        is_valid, errors = ResponseParser.validate(response)
        if not is_valid:
            return character, response, errors

        # 应用变化
        new_char, logs = ChangeApplier.apply_to_character(character, response)

        return new_char, response, logs

    async def process_interaction_group(
        self,
        characters: list[Character],
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any]
    ) -> tuple[list[Character], AIResponse, dict[str, list[str]]]:
        """
        处理交互组的决策流程

        Args:
            characters: 角色列表
            environment: 环境信息
            treasures_data: 法宝数据
            techniques_data: 功法数据

        Returns:
            (新角色列表, AI响应, {角色ID: 变化日志})
        """
        # 构建提示词
        prompt = self.prompt_builder.build_multi_character_prompt(
            characters, environment, treasures_data, techniques_data
        )

        # 请求 AI 决策
        response = await self.ai_interface.request_decision(prompt)
        if not response:
            return characters, None, {}

        # 验证响应
        is_valid, errors = ResponseParser.validate(response)
        if not is_valid:
            return characters, response, {err: [] for err in errors}

        # 应用变化
        new_chars, logs = ChangeApplier.apply_to_characters(characters, response)

        return new_chars, response, logs
