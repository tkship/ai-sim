"""物品系统模块

包含法宝、丹药、功法等物品类和背包管理
"""
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ItemType(str, Enum):
    """物品类型枚举"""
    ARTIFACT = "法宝"      # 法宝：攻击力、防御力
    PILL = "丹药"          # 丹药：属性恢复
    TECHNIQUE = "功法"     # 功法：灵力加成、特殊效果


@dataclass
class Item:
    """物品基类"""
    id: str
    name: str
    item_type: ItemType
    description: str = ""

    # 物品属性
    attack_bonus: int = 0
    defense_bonus: int = 0
    spirit_power_bonus: int = 0
    health_restore: int = 0
    spirit_power_restore: int = 0

    # 特殊效果标识
    is_equipped: bool = False

    @property
    def display_info(self) -> str:
        """获取物品显示信息"""
        info = f"[{self.name}] {self.item_type.value}"
        if self.attack_bonus > 0:
            info += f" 攻+{self.attack_bonus}"
        if self.defense_bonus > 0:
            info += f" 防+{self.defense_bonus}"
        if self.health_restore > 0:
            info += f" 回血{self.health_restore}"
        if self.spirit_power_restore > 0:
            info += f" 回灵{self.spirit_power_restore}"
        return info

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.item_type.value,
            "description": self.description,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "spirit_power_bonus": self.spirit_power_bonus,
            "health_restore": self.health_restore,
            "spirit_power_restore": self.spirit_power_restore,
            "is_equipped": self.is_equipped,
        }


# 预定义物品库
ITEM_LIBRARY = {
    "基础飞剑": Item(
        id="artifact_001",
        name="基础飞剑",
        item_type=ItemType.ARTIFACT,
        description="一把入门级的飞剑",
        attack_bonus=10,
    ),
    "青钢剑": Item(
        id="artifact_002",
        name="青钢剑",
        item_type=ItemType.ARTIFACT,
        description="材质坚固的青钢剑",
        attack_bonus=20,
    ),
    "玄铁盾": Item(
        id="artifact_003",
        name="玄铁盾",
        item_type=ItemType.ARTIFACT,
        description="厚重的玄铁盾牌",
        defense_bonus=15,
    ),
    "回灵丹": Item(
        id="pill_001",
        name="回灵丹",
        item_type=ItemType.PILL,
        description="恢复灵力的丹药",
        spirit_power_restore=30,
    ),
    "回血丹": Item(
        id="pill_002",
        name="回血丹",
        item_type=ItemType.PILL,
        description="恢复伤势的丹药",
        health_restore=50,
    ),
    "炼气决": Item(
        id="technique_001",
        name="炼气决",
        item_type=ItemType.TECHNIQUE,
        description="基础的炼气功法",
        spirit_power_bonus=10,
    ),
    "长春功": Item(
        id="technique_002",
        name="长春功",
        item_type=ItemType.TECHNIQUE,
        description="以长春之意滋养身体",
        spirit_power_bonus=15,
    ),
}


@dataclass
class Inventory:
    """背包类

    管理角色的物品
    """
    # 背包中的物品列表
    items: List[Item] = None

    # 装备的法宝
    equipped_artifact: Optional[Item] = None

    # 装备的功法
    equipped_technique: Optional[Item] = None

    def __post_init__(self) -> None:
        if self.items is None:
            self.items = []

    def add_item(self, item: Item) -> bool:
        """添加物品到背包

        Args:
            item: 要添加的物品

        Returns:
            是否添加成功
        """
        self.items.append(item)
        return True

    def add_item_by_name(self, item_name: str) -> bool:
        """通过物品名称添加物品

        Args:
            item_name: 物品名称

        Returns:
            是否添加成功
        """
        if item_name in ITEM_LIBRARY:
            item = ITEM_LIBRARY[item_name]
            return self.add_item(item)
        return False

    def remove_item(self, item_id: str) -> bool:
        """从背包移除物品

        Args:
            item_id: 物品ID

        Returns:
            是否移除成功
        """
        # 先检查是否装备了该物品
        if self.equipped_artifact and self.equipped_artifact.id == item_id:
            self.equipped_artifact = None
        if self.equipped_technique and self.equipped_technique.id == item_id:
            self.equipped_technique = None

        # 从背包移除
        for i, item in enumerate(self.items):
            if item.id == item_id:
                self.items.pop(i)
                return True
        return False

    def equip_item(self, item_id: str) -> bool:
        """装备物品

        Args:
            item_id: 物品ID

        Returns:
            是否装备成功
        """
        for item in self.items:
            if item.id == item_id:
                if item.item_type == ItemType.ARTIFACT:
                    self.equipped_artifact = item
                    return True
                elif item.item_type == ItemType.TECHNIQUE:
                    self.equipped_technique = item
                    return True
        return False

    def get_equipped_bonus(self) -> Dict[str, int]:
        """获取装备的属性加成

        Returns:
            属性加成字典
        """
        bonus = {
            "attack_power": 0,
            "defense_power": 0,
            "spirit_power": 0,
        }

        if self.equipped_artifact:
            bonus["attack_power"] += self.equipped_artifact.attack_bonus
            bonus["defense_power"] += self.equipped_artifact.defense_bonus

        if self.equipped_technique:
            bonus["spirit_power"] += self.equipped_technique.spirit_power_bonus

        return bonus

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "items": [item.to_dict() for item in self.items],
            "equipped_artifact": self.equipped_artifact.to_dict() if self.equipped_artifact else None,
            "equipped_technique": self.equipped_technique.to_dict() if self.equipped_technique else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Inventory":
        """从字典创建背包对象"""
        items = []
        for item_data in data.get("items", []):
            items.append(Item(
                id=item_data["id"],
                name=item_data["name"],
                item_type=ItemType(item_data["type"]),
                description=item_data.get("description", ""),
                attack_bonus=item_data.get("attack_bonus", 0),
                defense_bonus=item_data.get("defense_bonus", 0),
                spirit_power_bonus=item_data.get("spirit_power_bonus", 0),
                health_restore=item_data.get("health_restore", 0),
                spirit_power_restore=item_data.get("spirit_power_restore", 0),
                is_equipped=item_data.get("is_equipped", False),
            ))

        inventory = cls(items=items)

        # 恢复装备状态
        artifact_data = data.get("equipped_artifact")
        if artifact_data:
            for item in items:
                if item.id == artifact_data["id"]:
                    inventory.equipped_artifact = item
                    break

        technique_data = data.get("equipped_technique")
        if technique_data:
            for item in items:
                if item.id == technique_data["id"]:
                    inventory.equipped_technique = item
                    break

        return inventory
