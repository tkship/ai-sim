"""AI 接口测试"""
import pytest
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from ai.interface import MockAIInterface
from ai.prompt import PromptBuilder
from ai.parser import AIResponseParser
import json


class TestMockAIInterface:
    """Mock AI 接口测试"""

    def test_chat(self):
        """测试聊天"""
        ai = MockAIInterface()

        messages = [
            {"role": "system", "content": "测试系统"},
            {"role": "user", "content": "测试消息"},
        ]

        response = ai.chat(messages)

        # 检查返回的是 JSON 字符串
        assert "{" in response
        assert "}" in response

    def test_response_format(self):
        """测试响应格式"""
        ai = MockAIInterface()

        messages = [{"role": "user", "content": "测试"}]
        response = ai.chat(messages)

        data = json.loads(response)

        # 检查必需字段
        assert "action_thought" in data
        assert "scene_description" in data
        assert "attribute_deltas" in data
        assert "item_changes" in data


class TestPromptBuilder:
    """提示词构建器测试"""

    def test_initialization(self):
        """测试初始化"""
        world_info = {
            "name": "测试世界",
            "description": "测试描述",
            "round": 0,
            "alive_count": 1,
            "dead_count": 0,
        }

        builder = PromptBuilder(world_info)

        assert builder.world_info == world_info

    def test_build_character_prompt(self):
        """测试构建角色提示词"""
        world_info = {
            "name": "测试世界",
            "description": "测试描述",
            "round": 0,
            "alive_count": 1,
            "dead_count": 0,
        }

        builder = PromptBuilder(world_info)

        character_info = {
            "id": "test_id",
            "name": "测试角色",
            "state": "idle",
            "realm": "炼气初期",
            "health": 100,
            "max_health": 100,
            "health_percent": 1.0,
            "spirit_power": 50,
            "max_spirit_power": 50,
            "spirit_power_percent": 1.0,
            "consciousness": 20,
            "attack_power": 44,
            "defense_power": 35,
            "detection_range": 200,
            "items": ["基础飞剑"],
            "equipped_artifact": "基础飞剑",
            "equipped_technique": None,
            "recent_memories": [],
        }

        prompt = builder.build_character_prompt(character_info)

        # 检查提示词包含角色信息
        assert "测试角色" in prompt
        assert "炼气初期" in prompt
        assert "100 / 100" in prompt



class TestAIResponseParser:
    """AI 响应解析器测试"""

    def test_initialization(self):
        """测试初始化"""
        parser = AIResponseParser(strict_mode=False)
        assert parser.strict_mode is False

    def test_parse_single_response(self):
        """测试解析单个响应"""
        parser = AIResponseParser()

        data = {
            "action_thought": "打坐修炼",
            "scene_description": "灵气充盈",
            "attribute_deltas": {
                "health": 0,
                "spirit_power": 5
            },
            "item_changes": {
                "obtained": [],
                "lost": []
            }
        }

        response_text = json.dumps(data)
        result = parser.parse_single_response(response_text)

        assert result["action_thought"] == "打坐修炼"
        assert result["scene_description"] == "灵气充盈"
        assert result["attribute_deltas"]["spirit_power"] == 5

    def test_clamp_attribute_deltas(self):
        """测试属性增量限制"""
        parser = AIResponseParser()

        deltas = {
            "health": -100,  # 超出限制
            "spirit_power": 200,  # 超出限制
            "consciousness": 5,  # 在范围内
        }

        clamped = parser.clamp_attribute_deltas(deltas)

        # health 范围是 -50 ~ 50
        assert clamped["health"] == -50
        # spirit_power 范围是 -30 ~ 100
        assert clamped["spirit_power"] == 100
        # consciousness 范围是 -10 ~ 10
        assert clamped["consciousness"] == 5

    def test_validate_attribute_deltas(self):
        """测试属性增量验证"""
        parser = AIResponseParser()

        # 合理的增量
        valid_deltas = {
            "health": -10,
            "spirit_power": 5,
        }
        assert parser.validate_attribute_deltas(valid_deltas) is True

        # 不合理的增量
        invalid_deltas = {
            "health": -100,  # 超出范围
        }
        assert parser.validate_attribute_deltas(invalid_deltas) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
