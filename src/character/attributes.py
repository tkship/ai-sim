"""
角色属性模块
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Attribute:
    """不可变属性类"""
    current: int
    max: int

    def with_current(self, value: int) -> "Attribute":
        """返回新的属性对象，设置当前值（在有效范围内）"""
        new_current = max(0, min(value, self.max))
        return Attribute(new_current, self.max)

    def with_delta(self, delta: int) -> "Attribute":
        """返回新的属性对象，应用增量变化"""
        return self.with_current(self.current + delta)

    def with_max(self, value: int) -> "Attribute":
        """返回新的属性对象，设置最大值"""
        new_max = max(1, value)
        new_current = min(self.current, new_max)
        return Attribute(new_current, new_max)

    @property
    def ratio(self) -> float:
        """当前值占最大值的比例"""
        if self.max <= 0:
            return 0.0
        return self.current / self.max

    def __str__(self) -> str:
        return f"{self.current}/{self.max}"


@dataclass(frozen=True)
class CharacterAttributes:
    """角色核心属性（不可变）"""
    hp: Attribute  # 血量
    mp: Attribute  # 灵力
    spirit: Attribute  # 神识
    statuses: tuple[str, ...] = ()  # 状态效果

    def with_hp_delta(self, delta: int) -> "CharacterAttributes":
        """应用血量变化"""
        return CharacterAttributes(
            hp=self.hp.with_delta(delta),
            mp=self.mp,
            spirit=self.spirit,
            statuses=self.statuses
        )

    def with_mp_delta(self, delta: int) -> "CharacterAttributes":
        """应用灵力变化"""
        return CharacterAttributes(
            hp=self.hp,
            mp=self.mp.with_delta(delta),
            spirit=self.spirit,
            statuses=self.statuses
        )

    def with_spirit_delta(self, delta: int) -> "CharacterAttributes":
        """应用神识变化"""
        return CharacterAttributes(
            hp=self.hp,
            mp=self.mp,
            spirit=self.spirit.with_delta(delta),
            statuses=self.statuses
        )

    def with_max_multiplier(self, multiplier: float) -> "CharacterAttributes":
        """应用最大值倍率（用于境界突破）"""
        new_hp_max = int(self.hp.max * multiplier)
        new_mp_max = int(self.mp.max * multiplier)
        new_spirit_max = int(self.spirit.max * multiplier)

        # 按比例恢复当前值
        hp_ratio = self.hp.ratio
        mp_ratio = self.mp.ratio
        spirit_ratio = self.spirit.ratio

        return CharacterAttributes(
            hp=Attribute(int(new_hp_max * hp_ratio), new_hp_max),
            mp=Attribute(int(new_mp_max * mp_ratio), new_mp_max),
            spirit=Attribute(int(new_spirit_max * spirit_ratio), new_spirit_max),
            statuses=self.statuses
        )

    def add_status(self, status: str) -> "CharacterAttributes":
        """添加状态效果"""
        if status not in self.statuses:
            return CharacterAttributes(
                hp=self.hp,
                mp=self.mp,
                spirit=self.spirit,
                statuses=self.statuses + (status,)
            )
        return self

    def remove_status(self, status: str) -> "CharacterAttributes":
        """移除状态效果"""
        if status in self.statuses:
            new_statuses = tuple(s for s in self.statuses if s != status)
            return CharacterAttributes(
                hp=self.hp,
                mp=self.mp,
                spirit=self.spirit,
                statuses=new_statuses
            )
        return self

    @property
    def is_alive(self) -> bool:
        """是否存活"""
        return self.hp.current > 0

    @property
    def has_mp(self, amount: int) -> bool:
        """是否有足够的灵力"""
        return self.mp.current >= amount
