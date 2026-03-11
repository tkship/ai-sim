"""角色类模块

整合属性、物品、记忆等模块，管理角色的完整状态
"""
from dataclasses import dataclass, field
from typing import Dict, Optional, List
import uuid
from datetime import datetime

from .attributes import Attributes
from .realm import Realm
from .inventory import Inventory
from .memory import Memory, MemoryType


class CharacterState(str):
    """角色状态枚举"""
    IDLE = "idle"          # 闲置
    MEDITATING = "meditating"  # 打坐修炼
    COMBAT = "combat"      # 战斗中
    MOVING = "moving"      # 移动中
    EXPLORING = "exploring"    # 探索中
    DEAD = "dead"          # 已死亡


@dataclass
class Character:
    """角色类

    修仙者的完整表示
    """
    # 基本信息
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = "无名修仙者"

    # 系统组件
    attributes: Attributes = field(default_factory=Attributes)
    realm: Realm = field(default_factory=Realm)
    inventory: Inventory = field(default_factory=Inventory)
    memory: Memory = field(default_factory=Memory)

    # 位置信息
    position: tuple = (0, 0)
    detection_range: int = 100  # 探测范围

    # 状态
    state: str = CharacterState.IDLE
    is_alive: bool = True
    death_time: Optional[datetime] = None

    # 创建时间
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """初始化后更新探测范围"""
        self._update_detection_range()

    def _update_detection_range(self) -> None:
        """根据神识更新探测范围"""
        self.detection_range = self.attributes.consciousness * 10

    @property
    def total_attack_power(self) -> int:
        """获取总攻击力（包含装备加成、境界加成）"""
        base = self.attributes.attack_power
        bonus = self.inventory.get_equipped_bonus()
        return int((base + bonus["attack_power"]) * self.realm.power_bonus)

    @property
    def total_defense_power(self) -> int:
        """获取总防御力（包含装备加成、境界加成）"""
        base = self.attributes.defense_power
        bonus = self.inventory.get_equipped_bonus()
        return int((base + bonus["defense_power"]) * self.realm.power_bonus)

    @property
    def total_spirit_power(self) -> int:
        """获取总灵力（包含装备加成）"""
        base = self.attributes.spirit_power
        bonus = self.inventory.get_equipped_bonus()
        return base + bonus["spirit_power"]

    def apply_attribute_delta(self, delta: Dict[str, int]) -> Dict[str, int]:
        """应用属性增量

        Args:
            delta: 属性增量字典

        Returns:
            实际变化结果
        """
        result = self.attributes.apply_delta(delta)

        # 更新探测范围
        self._update_detection_range()

        return result

    def add_memory(self, memory_type: str, description: str,
                   related_character_ids: List[str] = None,
                   data: Dict = None) -> None:
        """添加记忆

        Args:
            memory_type: 记忆类型
            description: 描述
            related_character_ids: 相关角色ID列表
            data: 附加数据
        """
        self.memory.add_entry(
            memory_type=memory_type,
            description=description,
            related_character_ids=related_character_ids,
            data=data,
        )

    def take_damage(self, damage: int) -> int:
        """承受伤害

        Args:
            damage: 伤害值

        Returns:
            实际受到的伤害
        """
        # 考虑防御力
        actual_damage = max(0, damage - self.total_defense_power)

        # 应用伤害
        result = self.apply_attribute_delta({"health": -actual_damage})

        # 检查死亡
        if self.attributes.health <= 0:
            self.die()

        return actual_damage

    def heal(self, amount: int) -> int:
        """治疗

        Args:
            amount: 治疗量

        Returns:
            实际恢复的数值
        """
        result = self.apply_attribute_delta({"health": amount})
        return result.get("health", 0)

    def restore_spirit_power(self, amount: int) -> int:
        """恢复灵力

        Args:
            amount: 恢复量

        Returns:
            实际恢复的数值
        """
        result = self.apply_attribute_delta({"spirit_power": amount})
        return result.get("spirit_power", 0)

    def try_realm_advance(self) -> bool:
        """尝试境界提升

        Returns:
            是否成功
        """
        success = self.realm.try_advance()
        if success:
            self.add_memory(
                memory_type=MemoryType.REALM_ADVANCE,
                description=f"境界提升至{self.realm.name}",
                data={"new_realm": self.realm.to_dict()},
            )
        return success

    def die(self) -> None:
        """死亡"""
        self.is_alive = False
        self.state = CharacterState.DEAD
        self.death_time = datetime.now()

        self.add_memory(
            memory_type=MemoryType.DEATH,
            description=f"{self.name} 在 {self.death_time.strftime('%Y-%m-%d %H:%M:%S')} 身陨",
        )

    def revive(self) -> None:
        """复活（测试用）"""
        self.is_alive = True
        self.state = CharacterState.IDLE
        self.death_time = None
        self.attributes.health = self.attributes.max_health // 2  # 复活时恢复50%血量

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "attributes": self.attributes.to_dict(),
            "realm": self.realm.to_dict(),
            "inventory": self.inventory.to_dict(),
            "memory": self.memory.to_dict(),
            "position": self.position,
            "detection_range": self.detection_range,
            "state": self.state,
            "is_alive": self.is_alive,
            "death_time": self.death_time.isoformat() if self.death_time else None,
            "created_at": self.created_at.isoformat(),
            "total_attack_power": self.total_attack_power,
            "total_defense_power": self.total_defense_power,
            "total_spirit_power": self.total_spirit_power,
        }

    def get_info_for_ai(self) -> dict:
        """获取AI所需的角色信息

        Returns:
            结构化的角色信息
        """
        return {
            "id": self.id,
            "name": self.name,
            "state": self.state,
            "realm": self.realm.name,
            "health": self.attributes.health,
            "max_health": self.attributes.max_health,
            "health_percent": self.attributes.health / self.attributes.max_health,
            "spirit_power": self.attributes.spirit_power,
            "max_spirit_power": self.attributes.max_spirit_power,
            "spirit_power_percent": self.attributes.spirit_power / self.attributes.max_spirit_power,
            "consciousness": self.attributes.consciousness,
            "attack_power": self.total_attack_power,
            "defense_power": self.total_defense_power,
            "detection_range": self.detection_range,
            "items": [item.display_info for item in self.inventory.items],
            "equipped_artifact": self.inventory.equipped_artifact.name if self.inventory.equipped_artifact else None,
            "equipped_technique": self.inventory.equipped_technique.name if self.inventory.equipped_technique else None,
            "recent_memories": [entry.description for entry in self.memory.get_recent_memories(5)],
        }


def create_character(
    name: str,
    health: int = 100,
    spirit_power: int = 50,
    consciousness: int = 20,
    position: tuple = (0, 0),
    start_items: List[str] = None,
) -> Character:
    """创建角色辅助函数

    Args:
        name: 角色名称
        health: 初始血量
        spirit_power: 初始灵力
        consciousness: 初始神识
        position: 位置
        start_items: 初始物品列表

    Returns:
        角色对象
    """
    if start_items is None:
        start_items = []

    character = Character(
        name=name,
        attributes=Attributes(
            health=health,
            max_health=health,
            spirit_power=spirit_power,
            max_spirit_power=spirit_power,
            consciousness=consciousness,
        ),
        position=position,
    )

    # 添加初始物品
    for item_name in start_items:
        character.inventory.add_item_by_name(item_name)

    # 自动装备第一个法宝和功法
    for item in character.inventory.items:
        if item.item_type.value == "法宝" and character.inventory.equipped_artifact is None:
            character.inventory.equip_item(item.id)
        elif item.item_type.value == "功法" and character.inventory.equipped_technique is None:
            character.inventory.equip_item(item.id)

    return character
