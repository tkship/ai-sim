"""
丹药模块
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class PillType(Enum):
    """丹药类型"""
    HEALING = "healing"
    SPIRIT = "spirit"
    BREAKTHROUGH = "breakthrough"
    POISON = "poison"
    SPECIAL = "special"

    @property
    def display_name(self) -> str:
        """显示名称"""
        names = {
            self.HEALING: "疗伤",
            self.SPIRIT: "灵气",
            self.BREAKTHROUGH: "破境",
            self.POISON: "毒药",
            self.SPECIAL: "特殊",
        }
        return names[self]


@dataclass(frozen=True)
class PillEffect:
    """丹药效果"""
    hp_change: int = 0
    mp_change: int = 0
    spirit_change: int = 0
    breakthrough_bonus: float = 0.0
    temporary_bonus: dict[str, float] = None
    status_add: tuple[str, ...] = ()
    status_remove: tuple[str, ...] = ()
    description: str = ""

    def __post_init__(self):
        if self.temporary_bonus is None:
            object.__setattr__(self, "temporary_bonus", {})


@dataclass(frozen=True)
class Pill:
    """丹药（不可变）"""
    id: Optional[int] = None
    name: str = ""
    type: PillType = PillType.HEALING
    element: Optional[str] = None
    effect: PillEffect = None
    realm_required: Optional[str] = None
    description: str = ""

    def __post_init__(self):
        if self.effect is None:
            object.__setattr__(self, "effect", PillEffect())

    @property
    def is_instant(self) -> bool:
        """是否是即时效果丹药"""
        return self.type in (PillType.HEALING, PillType.SPIRIT)

    @property
    def has_side_effect(self) -> bool:
        """是否有副作用"""
        return self.type == PillType.POISON or bool(self.effect.temporary_bonus)

    def to_prompt_dict(self) -> dict:
        """转换为提示词字典"""
        return {
            "name": self.name,
            "type": self.type.display_name,
            "effect": self.effect.description,
            "description": self.description
        }

    @staticmethod
    def create_healing(name: str, hp_restore: int, description: str = "") -> "Pill":
        """创建疗伤丹药"""
        return Pill(
            name=name,
            type=PillType.HEALING,
            effect=PillEffect(
                hp_change=hp_restore,
                description=f"恢复 {hp_restore} 点血量"
            ),
            description=description
        )

    @staticmethod
    def create_spirit(name: str, mp_restore: int, description: str = "") -> "Pill":
        """创建灵力丹药"""
        return Pill(
            name=name,
            type=PillType.SPIRIT,
            effect=PillEffect(
                mp_change=mp_restore,
                description=f"恢复 {mp_restore} 点灵力"
            ),
            description=description
        )

    @staticmethod
    def create_breakthrough(name: str, bonus: float, description: str = "") -> "Pill":
        """创建破境丹药"""
        return Pill(
            name=name,
            type=PillType.BREAKTHROUGH,
            effect=PillEffect(
                breakthrough_bonus=bonus,
                description=f"突破成功率 +{bonus * 100}%"
            ),
            description=description
        )
