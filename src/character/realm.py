"""
境界系统模块
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class MajorRealm(Enum):
    """大境界"""
    QI_REFINING = "qi_refining"
    FOUNDATION = "foundation"
    GOLDEN_CORE = "golden_core"
    NASCENT_SOUL = "nascent_soul"
    SPIRIT_SEVERANCE = "spirit_severance"

    @property
    def display_name(self) -> str:
        """显示名称"""
        names = {
            self.QI_REFINING: "炼气",
            self.FOUNDATION: "筑基",
            self.GOLDEN_CORE: "结丹",
            self.NASCENT_SOUL: "元婴",
            self.SPIRIT_SEVERANCE: "化神",
        }
        return names[self]

    @property
    def order(self) -> int:
        """境界顺序"""
        orders = {
            self.QI_REFINING: 1,
            self.FOUNDATION: 2,
            self.GOLDEN_CORE: 3,
            self.NASCENT_SOUL: 4,
            self.SPIRIT_SEVERANCE: 5,
        }
        return orders[self]

    @property
    def abilities(self) -> tuple[str, ...]:
        """解锁的特殊能力"""
        abilities_map = {
            self.QI_REFINING: (),
            self.FOUNDATION: ("御剑飞行",),
            self.GOLDEN_CORE: ("御剑飞行", "本命法宝"),
            self.NASCENT_SOUL: ("御剑飞行", "本命法宝", "元婴出窍"),
            self.SPIRIT_SEVERANCE: ("御剑飞行", "本命法宝", "元婴出窍", "神识化形", "空间跃迁"),
        }
        return abilities_map[self]

    @property
    def hp_multiplier(self) -> float:
        """血量倍率"""
        multipliers = {
            self.QI_REFINING: 1.0,
            self.FOUNDATION: 2.0,
            self.GOLDEN_CORE: 6.0,
            self.NASCENT_SOUL: 30.0,
            self.SPIRIT_SEVERANCE: 300.0,
        }
        return multipliers[self]

    @property
    def mp_multiplier(self) -> float:
        """灵力倍率"""
        return self.hp_multiplier

    def next(self) -> Optional["MajorRealm"]:
        """下一个大境界"""
        next_realms = {
            self.QI_REFINING: self.FOUNDATION,
            self.FOUNDATION: self.GOLDEN_CORE,
            self.GOLDEN_CORE: self.NASCENT_SOUL,
            self.NASCENT_SOUL: self.SPIRIT_SEVERANCE,
        }
        return next_realms.get(self)


class MinorRealm(Enum):
    """小境界"""
    EARLY = "early"
    MID = "mid"
    LATE = "late"

    @property
    def display_name(self) -> str:
        """显示名称"""
        names = {
            self.EARLY: "初期",
            self.MID: "中期",
            self.LATE: "后期",
        }
        return names[self]

    @property
    def order(self) -> int:
        """小境界顺序"""
        orders = {
            self.EARLY: 1,
            self.MID: 2,
            self.LATE: 3,
        }
        return orders[self]

    def next(self) -> Optional["MinorRealm"]:
        """下一个小境界"""
        next_realms = {
            self.EARLY: self.MID,
            self.MID: self.LATE,
        }
        return next_realms.get(self)


@dataclass(frozen=True)
class Realm:
    """境界（包含大境界和小境界）"""
    major: MajorRealm
    minor: MinorRealm

    @property
    def full_name(self) -> str:
        """完整境界名称"""
        return f"{self.major.display_name}{self.minor.display_name}"

    @property
    def total_order(self) -> tuple[int, int]:
        """总排序（大境界，小境界）"""
        return (self.major.order, self.minor.order)

    def __lt__(self, other: "Realm") -> bool:
        return self.total_order < other.total_order

    def __le__(self, other: "Realm") -> bool:
        return self.total_order <= other.total_order

    def __gt__(self, other: "Realm") -> bool:
        return self.total_order > other.total_order

    def __ge__(self, other: "Realm") -> bool:
        return self.total_order >= other.total_order

    def can_progress_minor(self) -> bool:
        """是否可以提升小境界"""
        return self.minor.next() is not None

    def can_progress_major(self) -> bool:
        """是否可以提升大境界"""
        return self.minor == MinorRealm.LATE and self.major.next() is not None

    def with_minor_progress(self) -> "Realm":
        """提升小境界"""
        next_minor = self.minor.next()
        if next_minor:
            return Realm(self.major, next_minor)
        return self

    def with_major_progress(self) -> "Realm":
        """提升大境界（重置小境界为初期）"""
        next_major = self.major.next()
        if next_major:
            return Realm(next_major, MinorRealm.EARLY)
        return self

    @property
    def abilities(self) -> tuple[str, ...]:
        """解锁的特殊能力"""
        return self.major.abilities

    @property
    def hp_multiplier(self) -> float:
        """血量倍率"""
        return self.major.hp_multiplier

    @property
    def mp_multiplier(self) -> float:
        """灵力倍率"""
        return self.major.mp_multiplier

    def meets_requirement(self, required: str) -> bool:
        """检查是否满足境界要求"""
        # 简单实现：检查境界名称是否包含要求的境界
        return required in self.full_name

    @staticmethod
    def create(major: str = "qi_refining", minor: str = "early") -> "Realm":
        """创建境界对象"""
        return Realm(
            MajorRealm(major),
            MinorRealm(minor)
        )
