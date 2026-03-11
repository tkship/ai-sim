"""属性系统模块

包含核心属性和派生属性的计算
"""


from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Attributes:
    """角色属性类

    包含核心属性、派生属性和相关计算方法
    """
    # 核心属性
    health: int = 100           # 血量
    max_health: int = 100       # 最大血量
    spirit_power: int = 50      # 灵力
    max_spirit_power: int = 50  # 最大灵力
    consciousness: int = 20     # 神识
    luck: int = 10              # 运气

    # 派生属性（计算得出）
    attack_power: int = field(init=False)
    defense_power: int = field(init=False)
    recovery_rate: int = field(init=False)

    def __post_init__(self) -> None:
        """初始化后计算派生属性"""
        self._update_derived_attributes()

    def _update_derived_attributes(self) -> None:
        """更新派生属性"""
        # 攻击力 = 灵力 * 0.8 + 神识 * 0.2
        self.attack_power = int(self.spirit_power * 0.8 + self.consciousness * 0.2)
        # 防御力 = 灵力 * 0.5 + 神识 * 0.5
        self.defense_power = int(self.spirit_power * 0.5 + self.consciousness * 0.5)
        # 恢复速率 = 神识 * 0.3 + 运气 * 0.1
        self.recovery_rate = int(self.consciousness * 0.3 + self.luck * 0.1)

    def apply_delta(self, delta: Dict[str, int]) -> Dict[str, Any]:
        """应用属性增量变化

        Args:
            delta: 属性增量字典，例如 {"health": -10, "spirit_power": 5}

        Returns:
            实际变化的结果字典，包含受限的属性变化
        """
        result = {}

        for attr_name, delta_value in delta.items():
            if not hasattr(self, attr_name):
                continue

            current_value = getattr(self, attr_name)
            new_value = current_value + delta_value

            # 处理最大值限制
            max_attr = f"max_{attr_name}"
            if hasattr(self, max_attr):
                max_value = getattr(self, max_attr)
                new_value = min(max_value, new_value)

            # 确保不小于0
            new_value = max(0, new_value)

            actual_delta = new_value - current_value
            setattr(self, attr_name, new_value)
            result[attr_name] = actual_delta

        # 更新派生属性
        self._update_derived_attributes()

        return result

    def to_dict(self) -> Dict[str, int]:
        """转换为字典格式

        Returns:
            属性字典
        """
        return {
            "health": self.health,
            "max_health": self.max_health,
            "spirit_power": self.spirit_power,
            "max_spirit_power": self.max_spirit_power,
            "consciousness": self.consciousness,
            "luck": self.luck,
            "attack_power": self.attack_power,
            "defense_power": self.defense_power,
            "recovery_rate": self.recovery_rate,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, int]) -> "Attributes":
        """从字典创建属性对象

        Args:
            data: 属性字典

        Returns:
            Attributes 对象
        """
        return cls(
            health=data.get("health", 100),
            max_health=data.get("max_health", 100),
            spirit_power=data.get("spirit_power", 50),
            max_spirit_power=data.get("max_spirit_power", 50),
            consciousness=data.get("consciousness", 20),
            luck=data.get("luck", 10),
        )
