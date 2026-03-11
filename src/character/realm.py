"""境界系统模块

定义修仙者的境界等级和提升规则
"""
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List
import random


class MajorRealm(str, Enum):
    """大境界枚举"""
    LIANQI = "炼气"
    ZHUJI = "筑基"
    JINDAN = "金丹"
    YUANYING = "元婴"
    HUASHEN = "化神"


class MinorRealm(str, Enum):
    """小境界枚举"""
    EARLY = "初期"
    MIDDLE = "中期"
    LATE = "后期"
    PEAK = "圆满"


# 境界提升概率配置（随机数 0-100）
REALM_ADVANCE_CHANCE = {
    (MajorRealm.LIANQI, MinorRealm.EARLY): 30,
    (MajorRealm.LIANQI, MinorRealm.MIDDLE): 25,
    (MajorRealm.LIANQI, MinorRealm.LATE): 20,
    (MajorRealm.LIANQI, MinorRealm.PEAK): 15,  # 飞升到筑基

    (MajorRealm.ZHUJI, MinorRealm.EARLY): 20,
    (MajorRealm.ZHUJI, MinorRealm.MIDDLE): 15,
    (MajorRealm.ZHUJI, MinorRealm.LATE): 10,
    (MajorRealm.ZHUJI, MinorRealm.PEAK): 8,  # 飞升到金丹

    (MajorRealm.JINDAN, MinorRealm.EARLY): 15,
    (MajorRealm.JINDAN, MinorRealm.MIDDLE): 12,
    (MajorRealm.JINDAN, MinorRealm.LATE): 8,
    (MajorRealm.JINDAN, MinorRealm.PEAK): 5,  # 飞升到元婴

    (MajorRealm.YUANYING, MinorRealm.EARLY): 10,
    (MajorRealm.YUANYING, MinorRealm.MIDDLE): 8,
    (MajorRealm.YUANYING, MinorRealm.LATE): 5,
    (MajorRealm.YUANYING, MinorRealm.PEAK): 3,  # 飞升到化神

    (MajorRealm.HUASHEN, MinorRealm.EARLY): 5,
    (MajorRealm.HUASHEN, MinorRealm.MIDDLE): 3,
    (MajorRealm.HUASHEN, MinorRealm.LATE): 2,
    (MajorRealm.HUASHEN, MinorRealm.PEAK): 0,  # 已达最高
}


# 境界战斗力加成
REALM_POWER_BONUS = {
    (MajorRealm.LIANQI, MinorRealm.EARLY): 1.0,
    (MajorRealm.LIANQI, MinorRealm.MIDDLE): 1.2,
    (MajorRealm.LIANQI, MinorRealm.LATE): 1.5,
    (MajorRealm.LIANQI, MinorRealm.PEAK): 1.8,

    (MajorRealm.ZHUJI, MinorRealm.EARLY): 2.0,
    (MajorRealm.ZHUJI, MinorRealm.MIDDLE): 2.5,
    (MajorRealm.ZHUJI, MinorRealm.LATE): 3.0,
    (MajorRealm.ZHUJI, MinorRealm.PEAK): 3.5,

    (MajorRealm.JINDAN, MinorRealm.EARLY): 4.0,
    (MajorRealm.JINDAN, MinorRealm.MIDDLE): 5.0,
    (MajorRealm.JINDAN, MinorRealm.LATE): 6.0,
    (MajorRealm.JINDAN, MinorRealm.PEAK): 7.0,

    (MajorRealm.YUANYING, MinorRealm.EARLY): 8.0,
    (MajorRealm.YUANYING, MinorRealm.MIDDLE): 10.0,
    (MajorRealm.YUANYING, MinorRealm.LATE): 12.0,
    (MajorRealm.YUANYING, MinorRealm.PEAK): 14.0,

    (MajorRealm.HUASHEN, MinorRealm.EARLY): 16.0,
    (MajorRealm.HUASHEN, MinorRealm.MIDDLE): 20.0,
    (MajorRealm.HUASHEN, MinorRealm.LATE): 25.0,
    (MajorRealm.HUASHEN, MinorRealm.PEAK): 30.0,
}


@dataclass
class Realm:
    """境界类

    管理角色的修仙境界
    """
    major: MajorRealm = MajorRealm.LIANQI
    minor: MinorRealm = MinorRealm.EARLY

    @property
    def name(self) -> str:
        """获取完整境界名称"""
        return f"{self.major.value}{self.minor.value}"

    @property
    def level(self) -> int:
        """获取等级数值（用于比较）"""
        major_levels = {
            MajorRealm.LIANQI: 0,
            MajorRealm.ZHUJI: 10,
            MajorRealm.JINDAN: 20,
            MajorRealm.YUANYING: 30,
            MajorRealm.HUASHEN: 40,
        }
        minor_levels = {
            MinorRealm.EARLY: 1,
            MinorRealm.MIDDLE: 2,
            MinorRealm.LATE: 3,
            MinorRealm.PEAK: 4,
        }
        return major_levels[self.major] + minor_levels[self.minor]

    @property
    def power_bonus(self) -> float:
        """获取境界战斗力加成"""
        return REALM_POWER_BONUS.get((self.major, self.minor), 1.0)

    def try_advance(self) -> bool:
        """尝试境界提升

        Returns:
            是否提升成功
        """
        chance = REALM_ADVANCE_CHANCE.get((self.major, self.minor), 0)
        if random.randint(1, 100) <= chance:
            self._advance()
            return True
        return False

    def _advance(self) -> None:
        """执行境界提升"""
        minor_order = [MinorRealm.EARLY, MinorRealm.MIDDLE, MinorRealm.LATE, MinorRealm.PEAK]
        major_order = [MajorRealm.LIANQI, MajorRealm.ZHUJI, MajorRealm.JINDAN, MajorRealm.YUANYING, MajorRealm.HUASHEN]

        # 先尝试小境界提升
        current_minor_index = minor_order.index(self.minor)
        if current_minor_index < len(minor_order) - 1:
            self.minor = minor_order[current_minor_index + 1]
        else:
            # 小境界圆满，尝试大境界提升
            current_major_index = major_order.index(self.major)
            if current_major_index < len(major_order) - 1:
                self.major = major_order[current_major_index + 1]
                self.minor = MinorRealm.EARLY

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "major": self.major.value,
            "minor": self.minor.value,
            "name": self.name,
            "level": self.level,
            "power_bonus": self.power_bonus,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Realm":
        """从字典创建境界对象"""
        major = MajorRealm(data.get("major", "炼气"))
        minor = MinorRealm(data.get("minor", "初期"))
        return cls(major=major, minor=minor)
