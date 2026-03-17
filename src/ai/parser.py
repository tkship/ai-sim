"""
AI 响应解析模块
"""
import json
from typing import Any, Optional
from dataclasses import dataclass, field


@dataclass
class AttributeChange:
    """属性变化"""
    hp_delta: int = 0
    mp_delta: int = 0
    spirit_delta: int = 0
    status_add: list[str] = field(default_factory=list)
    status_remove: list[str] = field(default_factory=list)


@dataclass
class TreasureChange:
    """法宝变化"""
    treasure_name: str
    wear_delta: int = 0
    durability_delta: int = 0
    injected_spirit: Optional[int] = None
    description: str = ""


@dataclass
class ItemChange:
    """物品变化"""
    items_gained: dict[str, int] = field(default_factory=dict)
    items_lost: dict[str, int] = field(default_factory=dict)


@dataclass
class PositionChange:
    """位置变化。"""
    x: Optional[float] = None
    y: Optional[float] = None
    dx: float = 0.0
    dy: float = 0.0


@dataclass
class CharacterChange:
    """单个角色的变化"""
    character_id: str
    attributes: AttributeChange = field(default_factory=AttributeChange)
    treasure_changes: list[TreasureChange] = field(default_factory=list)
    item_changes: ItemChange = field(default_factory=ItemChange)
    position: PositionChange = field(default_factory=PositionChange)


@dataclass
class AIResponse:
    """AI 响应"""
    interaction_summary: str = ""
    scene_description: str = ""
    character_changes: dict[str, CharacterChange] = field(default_factory=dict)
    environment_changes: dict[str, Any] = field(default_factory=dict)
    raw_json: dict = None


class ResponseParser:
    """AI 响应解析器"""

    @staticmethod
    def parse(json_str: str) -> Optional[AIResponse]:
        """
        解析 AI 响应 JSON

        Args:
            json_str: JSON 字符串

        Returns:
            AIResponse 对象或 None
        """
        try:
            data = json.loads(json_str)
            return ResponseParser._parse_dict(data)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _parse_dict(data: dict) -> AIResponse:
        """从字典解析"""
        response = AIResponse()
        response.raw_json = data

        # 交互概述
        response.interaction_summary = data.get("交互概述", data.get("summary", ""))

        # 场景描述
        response.scene_description = data.get("场景描述", data.get("scene", ""))

        # 属性变化
        attr_changes = data.get("属性变化", data.get("attribute_changes", {}))

        if attr_changes:
            for char_id, char_data in attr_changes.items():
                char_change = CharacterChange(character_id=char_id)

                # 数值属性变化
                char_change.attributes.hp_delta = char_data.get("血量", char_data.get("hp", 0))
                char_change.attributes.mp_delta = char_data.get("灵力", char_data.get("mp", 0))
                char_change.attributes.spirit_delta = char_data.get("神识", char_data.get("spirit", 0))

                # 状态变化
                status_data = char_data.get("状态", char_data.get("status", {}))
                if isinstance(status_data, dict):
                    char_change.attributes.status_add = status_data.get("新增", status_data.get("add", []))
                    char_change.attributes.status_remove = status_data.get("移除", status_data.get("remove", []))

                # 法宝变化
                treasure_data = char_data.get("法宝变化", char_data.get("treasure_changes", []))
                for t_data in treasure_data:
                    t_change = TreasureChange(
                        treasure_name=t_data.get("法宝名称", t_data.get("name", "")),
                        wear_delta=t_data.get("损耗度变化", t_data.get("wear_delta", 0)),
                        durability_delta=t_data.get("耐久度变化", t_data.get("durability_delta", 0)),
                        injected_spirit=t_data.get("当前注入灵力", t_data.get("injected_spirit")),
                        description=t_data.get("说明", "")
                    )
                    char_change.treasure_changes.append(t_change)

                # 物品变化
                item_data = char_data.get("物品变化", char_data.get("item_changes", {}))
                if isinstance(item_data, dict):
                    char_change.item_changes.items_gained = item_data.get("获得", item_data.get("gained", {}))
                    char_change.item_changes.items_lost = item_data.get("失去", item_data.get("lost", {}))

                # 位置变化（绝对坐标或位移）
                pos_data = char_data.get("位置", char_data.get("position", {}))
                if isinstance(pos_data, dict):
                    char_change.position.x = pos_data.get("x")
                    char_change.position.y = pos_data.get("y")
                    char_change.position.dx = float(pos_data.get("dx", 0.0))
                    char_change.position.dy = float(pos_data.get("dy", 0.0))

                response.character_changes[char_id] = char_change

        # 环境变化
        response.environment_changes = data.get("环境变化", data.get("environment_changes", {}))

        return response

    @staticmethod
    def validate(response: AIResponse) -> tuple[bool, list[str]]:
        """
        验证 AI 响应是否有效

        Args:
            response: AI 响应对象

        Returns:
            (是否有效, 错误列表)
        """
        errors = []

        if not response.scene_description:
            errors.append("缺少场景描述")

        if not response.interaction_summary:
            errors.append("缺少交互概述")

        return len(errors) == 0, errors
