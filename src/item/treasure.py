"""
法宝模块
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum


class TreasureType(Enum):
    """法宝类型"""
    ATTACK = "attack"
    DEFENSE = "defense"
    SUPPORT = "support"

    @property
    def display_name(self) -> str:
        """显示名称"""
        names = {
            self.ATTACK: "攻击",
            self.DEFENSE: "防御",
            self.SUPPORT: "辅助",
        }
        return names[self]


@dataclass(frozen=True)
class Treasure:
    """法宝（不可变）"""
    id: Optional[int] = None
    name: str = ""
    element: Optional[str] = None
    type: TreasureType = TreasureType.ATTACK
    spirit_power_cost: int = 0
    realm_required: Optional[str] = None

    # 耐久度
    durability: int = 100
    max_durability: int = 100
    wear: int = 100  # 损耗度 0-100

    # 数值加成
    attack_min: int = 0
    attack_max: int = 0
    defense_min: int = 0
    defense_max: int = 0
    hp_bonus: int = 0
    mp_bonus: int = 0
    spirit_bonus: int = 0
    speed_bonus: float = 0.0
    detection_bonus: float = 0.0
    breakthrough_bonus: float = 0.0

    # 当前注入灵力
    injected_spirit: int = 0
    max_injected_spirit: int = 20

    # 特殊效果
    special_effects: tuple[str, ...] = field(default_factory=tuple)
    description: str = ""

    @property
    def is_broken(self) -> bool:
        """是否已损坏"""
        return self.durability <= 0

    @property
    def efficiency(self) -> float:
        """效率（基于损耗度）"""
        if self.wear >= 80:
            return 1.0
        return self.wear / 100.0

    @property
    def current_attack(self) -> tuple[int, int]:
        """当前攻击力（考虑损耗和注入灵力）"""
        bonus = self.injected_spirit * 0.5
        eff = self.efficiency
        return (
            int((self.attack_min + bonus) * eff),
            int((self.attack_max + bonus) * eff)
        )

    @property
    def current_defense(self) -> tuple[int, int]:
        """当前防御力（考虑损耗和注入灵力）"""
        bonus = self.injected_spirit * 0.5
        eff = self.efficiency
        return (
            int((self.defense_min + bonus) * eff),
            int((self.defense_max + bonus) * eff)
        )

    def with_wear(self, delta: int) -> "Treasure":
        """更新损耗度"""
        new_wear = max(0, min(100, self.wear + delta))
        return Treasure(
            id=self.id,
            name=self.name,
            element=self.element,
            type=self.type,
            spirit_power_cost=self.spirit_power_cost,
            realm_required=self.realm_required,
            durability=self.durability,
            max_durability=self.max_durability,
            wear=new_wear,
            attack_min=self.attack_min,
            attack_max=self.attack_max,
            defense_min=self.defense_min,
            defense_max=self.defense_max,
            hp_bonus=self.hp_bonus,
            mp_bonus=self.mp_bonus,
            spirit_bonus=self.spirit_bonus,
            speed_bonus=self.speed_bonus,
            detection_bonus=self.detection_bonus,
            breakthrough_bonus=self.breakthrough_bonus,
            injected_spirit=self.injected_spirit,
            max_injected_spirit=self.max_injected_spirit,
            special_effects=self.special_effects,
            description=self.description
        )

    def with_durability(self, delta: int) -> "Treasure":
        """更新耐久度"""
        new_durability = max(0, min(self.max_durability, self.durability + delta))
        return Treasure(
            id=self.id,
            name=self.name,
            element=self.element,
            type=self.type,
            spirit_power_cost=self.spirit_power_cost,
            realm_required=self.realm_required,
            durability=new_durability,
            max_durability=self.max_durability,
            wear=self.wear,
            attack_min=self.attack_min,
            attack_max=self.attack_max,
            defense_min=self.defense_min,
            defense_max=self.defense_max,
            hp_bonus=self.hp_bonus,
            mp_bonus=self.mp_bonus,
            spirit_bonus=self.spirit_bonus,
            speed_bonus=self.speed_bonus,
            detection_bonus=self.detection_bonus,
            breakthrough_bonus=self.breakthrough_bonus,
            injected_spirit=self.injected_spirit,
            max_injected_spirit=self.max_injected_spirit,
            special_effects=self.special_effects,
            description=self.description
        )

    def with_injected_spirit(self, amount: int) -> "Treasure":
        """设置注入灵力"""
        new_injected = max(0, min(self.max_injected_spirit, amount))
        return Treasure(
            id=self.id,
            name=self.name,
            element=self.element,
            type=self.type,
            spirit_power_cost=self.spirit_power_cost,
            realm_required=self.realm_required,
            durability=self.durability,
            max_durability=self.max_durability,
            wear=self.wear,
            attack_min=self.attack_min,
            attack_max=self.attack_max,
            defense_min=self.defense_min,
            defense_max=self.defense_max,
            hp_bonus=self.hp_bonus,
            mp_bonus=self.mp_bonus,
            spirit_bonus=self.spirit_bonus,
            speed_bonus=self.speed_bonus,
            detection_bonus=self.detection_bonus,
            breakthrough_bonus=self.breakthrough_bonus,
            injected_spirit=new_injected,
            max_injected_spirit=self.max_injected_spirit,
            special_effects=self.special_effects,
            description=self.description
        )

    def to_prompt_dict(self) -> dict[str, Any]:
        """转换为提示词字典"""
        return {
            "name": self.name,
            "type": self.type.display_name,
            "element": self.element,
            "durability": f"{self.durability}/{self.max_durability}",
            "wear": f"{self.wear}/100",
            "attack": f"{self.current_attack[0]}-{self.current_attack[1]}" if self.attack_max > 0 else None,
            "defense": f"{self.current_defense[0]}-{self.current_defense[1]}" if self.defense_max > 0 else None,
            "hp_bonus": self.hp_bonus if self.hp_bonus != 0 else None,
            "mp_bonus": self.mp_bonus if self.mp_bonus != 0 else None,
            "injected_spirit": f"{self.injected_spirit}/{self.max_injected_spirit}",
            "special_effects": list(self.special_effects),
            "description": self.description
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> "Treasure":
        """从字典创建法宝"""
        treasure_type = TreasureType(data.get("type", "attack"))
        effects = data.get("special_effects", [])
        if isinstance(effects, str):
            import json
            effects = json.loads(effects)

        return Treasure(
            id=data.get("id"),
            name=data.get("name", ""),
            element=data.get("element"),
            type=treasure_type,
            spirit_power_cost=data.get("spirit_power_cost", 0),
            realm_required=data.get("realm_required"),
            durability=data.get("durability", 100),
            max_durability=data.get("max_durability", 100),
            wear=data.get("durability", 100),
            attack_min=data.get("attack_min", 0),
            attack_max=data.get("attack_max", 0),
            defense_min=data.get("defense_min", 0),
            defense_max=data.get("defense_max", 0),
            hp_bonus=data.get("hp_bonus", 0),
            mp_bonus=data.get("mp_bonus", 0),
            spirit_bonus=data.get("spirit_bonus", 0),
            speed_bonus=data.get("speed_bonus", 0.0),
            detection_bonus=data.get("detection_bonus", 0.0),
            breakthrough_bonus=data.get("breakthrough_bonus", 0.0),
            max_injected_spirit=data.get("spirit_power_cost", 20) + 5,
            special_effects=tuple(effects),
            description=data.get("description", "")
        )
