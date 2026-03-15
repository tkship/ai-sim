"""
角色类模块 - 整合所有角色功能
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from .attributes import CharacterAttributes, Attribute
from .realm import Realm, MajorRealm, MinorRealm
from .spirit_root import SpiritRoot, Element
from .memory import MemoryBank


@dataclass(frozen=True)
class Position:
    """位置"""
    x: float = 0.0
    y: float = 0.0

    def distance_to(self, other: "Position") -> float:
        """计算到另一个位置的距离"""
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

    def with_position(self, x: float, y: float) -> "Position":
        """返回新的位置"""
        return Position(x, y)


@dataclass
class Character:
    """角色类（整合所有功能）"""
    id: str
    name: str

    # 核心属性
    attributes: CharacterAttributes
    realm: Realm
    spirit_root: SpiritRoot

    # 记忆和目标
    memory_bank: MemoryBank

    # 位置
    position: Position = field(default_factory=Position)

    # 修炼的功法（名称 -> 当前等级）
    techniques: dict[str, int] = field(default_factory=dict)

    # 物品栏（名称 -> 数量）
    inventory: dict[str, int] = field(default_factory=dict)

    # 装备的法宝（槽位 -> 法宝名称）
    equipment: dict[str, str] = field(default_factory=dict)

    # 战斗相关
    combat_insight: float = 0.0  # 战斗感悟加成
    breakthrough_bonus: float = 0.0  # 突破临时加成

    def __post_init__(self):
        if not hasattr(self, "memory_bank") or self.memory_bank is None:
            object.__setattr__(self, "memory_bank", MemoryBank(self.id))

    @property
    def is_alive(self) -> bool:
        """是否存活"""
        return self.attributes.is_alive

    @property
    def detection_range(self) -> float:
        """探测范围（基于神识）"""
        base_range = 10.0
        spirit_bonus = self.attributes.spirit.current * 0.5
        return base_range + spirit_bonus

    def can_detect(self, other: "Character") -> bool:
        """是否能探测到另一个角色"""
        distance = self.position.distance_to(other.position)
        return distance <= self.detection_range

    def with_attributes(self, attributes: CharacterAttributes) -> "Character":
        """返回新角色，更新属性"""
        return Character(
            id=self.id,
            name=self.name,
            attributes=attributes,
            realm=self.realm,
            spirit_root=self.spirit_root,
            memory_bank=self.memory_bank,
            position=self.position,
            techniques=self.techniques.copy(),
            inventory=self.inventory.copy(),
            equipment=self.equipment.copy(),
            combat_insight=self.combat_insight,
            breakthrough_bonus=self.breakthrough_bonus
        )

    def with_position(self, x: float, y: float) -> "Character":
        """返回新角色，更新位置"""
        return Character(
            id=self.id,
            name=self.name,
            attributes=self.attributes,
            realm=self.realm,
            spirit_root=self.spirit_root,
            memory_bank=self.memory_bank,
            position=Position(x, y),
            techniques=self.techniques.copy(),
            inventory=self.inventory.copy(),
            equipment=self.equipment.copy(),
            combat_insight=self.combat_insight,
            breakthrough_bonus=self.breakthrough_bonus
        )

    def with_realm(self, realm: Realm) -> "Character":
        """返回新角色，更新境界"""
        # 计算新的属性倍率
        new_attributes = self.attributes.with_max_multiplier(realm.hp_multiplier / self.realm.hp_multiplier)

        return Character(
            id=self.id,
            name=self.name,
            attributes=new_attributes,
            realm=realm,
            spirit_root=self.spirit_root,
            memory_bank=self.memory_bank,
            position=self.position,
            techniques=self.techniques.copy(),
            inventory=self.inventory.copy(),
            equipment=self.equipment.copy(),
            combat_insight=self.combat_insight,
            breakthrough_bonus=self.breakthrough_bonus
        )

    def add_item(self, item_name: str, count: int = 1) -> "Character":
        """添加物品"""
        new_inventory = self.inventory.copy()
        new_inventory[item_name] = new_inventory.get(item_name, 0) + count
        return Character(
            id=self.id,
            name=self.name,
            attributes=self.attributes,
            realm=self.realm,
            spirit_root=self.spirit_root,
            memory_bank=self.memory_bank,
            position=self.position,
            techniques=self.techniques.copy(),
            inventory=new_inventory,
            equipment=self.equipment.copy(),
            combat_insight=self.combat_insight,
            breakthrough_bonus=self.breakthrough_bonus
        )

    def remove_item(self, item_name: str, count: int = 1) -> "Character":
        """移除物品"""
        new_inventory = self.inventory.copy()
        current = new_inventory.get(item_name, 0)
        if current <= count:
            new_inventory.pop(item_name, None)
        else:
            new_inventory[item_name] = current - count
        return Character(
            id=self.id,
            name=self.name,
            attributes=self.attributes,
            realm=self.realm,
            spirit_root=self.spirit_root,
            memory_bank=self.memory_bank,
            position=self.position,
            techniques=self.techniques.copy(),
            inventory=new_inventory,
            equipment=self.equipment.copy(),
            combat_insight=self.combat_insight,
            breakthrough_bonus=self.breakthrough_bonus
        )

    def equip_item(self, slot: str, item_name: str) -> "Character":
        """装备物品"""
        new_equipment = self.equipment.copy()
        new_equipment[slot] = item_name
        return Character(
            id=self.id,
            name=self.name,
            attributes=self.attributes,
            realm=self.realm,
            spirit_root=self.spirit_root,
            memory_bank=self.memory_bank,
            position=self.position,
            techniques=self.techniques.copy(),
            inventory=self.inventory.copy(),
            equipment=new_equipment,
            combat_insight=self.combat_insight,
            breakthrough_bonus=self.breakthrough_bonus
        )

    def add_combat_insight(self, bonus: float) -> "Character":
        """添加战斗感悟"""
        return Character(
            id=self.id,
            name=self.name,
            attributes=self.attributes,
            realm=self.realm,
            spirit_root=self.spirit_root,
            memory_bank=self.memory_bank,
            position=self.position,
            techniques=self.techniques.copy(),
            inventory=self.inventory.copy(),
            equipment=self.equipment.copy(),
            combat_insight=self.combat_insight + bonus,
            breakthrough_bonus=self.breakthrough_bonus
        )

    def add_breakthrough_bonus(self, bonus: float) -> "Character":
        """添加临时突破加成"""
        return Character(
            id=self.id,
            name=self.name,
            attributes=self.attributes,
            realm=self.realm,
            spirit_root=self.spirit_root,
            memory_bank=self.memory_bank,
            position=self.position,
            techniques=self.techniques.copy(),
            inventory=self.inventory.copy(),
            equipment=self.equipment.copy(),
            combat_insight=self.combat_insight,
            breakthrough_bonus=self.breakthrough_bonus + bonus
        )

    def clear_breakthrough_bonus(self) -> "Character":
        """清除临时突破加成"""
        return Character(
            id=self.id,
            name=self.name,
            attributes=self.attributes,
            realm=self.realm,
            spirit_root=self.spirit_root,
            memory_bank=self.memory_bank,
            position=self.position,
            techniques=self.techniques.copy(),
            inventory=self.inventory.copy(),
            equipment=self.equipment.copy(),
            combat_insight=self.combat_insight,
            breakthrough_bonus=0.0
        )

    def to_prompt_dict(self) -> dict[str, Any]:
        """转换为提示词字典"""
        return {
            "id": self.id,
            "name": self.name,
            "realm": self.realm.full_name,
            "spirit_root": self.spirit_root.display_name,
            "hp": str(self.attributes.hp),
            "mp": str(self.attributes.mp),
            "spirit": str(self.attributes.spirit),
            "statuses": list(self.attributes.statuses),
            "position": {"x": self.position.x, "y": self.position.y},
            "techniques": self.techniques,
            "inventory": self.inventory,
            "equipment": self.equipment,
        }

    @staticmethod
    def create(
        char_id: str,
        name: str,
        base_hp: int = 50,
        base_mp: int = 30,
        base_spirit: int = 20,
        realm: Optional[Realm] = None,
        spirit_root: Optional[SpiritRoot] = None
    ) -> "Character":
        """
        创建新角色

        Args:
            char_id: 角色ID
            name: 角色名称
            base_hp: 基础血量
            base_mp: 基础灵力
            base_spirit: 基础神识
            realm: 境界（默认为炼气初期）
            spirit_root: 灵根（默认为金单灵根）

        Returns:
            角色对象
        """
        if realm is None:
            realm = Realm(MajorRealm.QI_REFINING, MinorRealm.EARLY)
        if spirit_root is None:
            spirit_root = SpiritRoot.create_single(Element.METAL)

        # 应用境界倍率
        hp_max = int(base_hp * realm.hp_multiplier)
        mp_max = int(base_mp * realm.mp_multiplier)
        spirit_max = int(base_spirit * 1.0)

        attributes = CharacterAttributes(
            hp=Attribute(hp_max, hp_max),
            mp=Attribute(mp_max, mp_max),
            spirit=Attribute(spirit_max, spirit_max)
        )

        return Character(
            id=char_id,
            name=name,
            attributes=attributes,
            realm=realm,
            spirit_root=spirit_root,
            memory_bank=MemoryBank(char_id)
        )
