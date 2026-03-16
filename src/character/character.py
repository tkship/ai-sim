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

    # 法宝动态状态（法宝名 -> 状态）
    treasure_states: dict[str, dict[str, Any]] = field(default_factory=dict)
    # 功法动态修正（功法名 -> 加成）
    technique_modifiers: dict[str, dict[str, float]] = field(default_factory=dict)

    # 战斗相关
    combat_insight: float = 0.0  # 战斗感悟加成
    breakthrough_bonus: float = 0.0  # 突破临时加成

    def __post_init__(self):
        if not hasattr(self, "memory_bank") or self.memory_bank is None:
            object.__setattr__(self, "memory_bank", MemoryBank(self.id))

    def _copy_with(self, **updates: Any) -> "Character":
        """内部复制工具，避免遗漏字段"""
        return Character(
            id=updates.get("id", self.id),
            name=updates.get("name", self.name),
            attributes=updates.get("attributes", self.attributes),
            realm=updates.get("realm", self.realm),
            spirit_root=updates.get("spirit_root", self.spirit_root),
            memory_bank=updates.get("memory_bank", self.memory_bank),
            position=updates.get("position", self.position),
            techniques=updates.get("techniques", self.techniques.copy()),
            inventory=updates.get("inventory", self.inventory.copy()),
            equipment=updates.get("equipment", self.equipment.copy()),
            treasure_states=updates.get("treasure_states", {k: v.copy() for k, v in self.treasure_states.items()}),
            technique_modifiers=updates.get(
                "technique_modifiers",
                {k: v.copy() for k, v in self.technique_modifiers.items()},
            ),
            combat_insight=updates.get("combat_insight", self.combat_insight),
            breakthrough_bonus=updates.get("breakthrough_bonus", self.breakthrough_bonus),
        )

    @property
    def is_alive(self) -> bool:
        """是否存活"""
        return self.attributes.is_alive

    @property
    def detection_range(self) -> float:
        """探测范围（基于神识）"""
        base_range = 10.0
        spirit_bonus = self.attributes.spirit.current * 0.5
        return base_range + spirit_bonus + self.equipment_detection_bonus + self.technique_detection_bonus

    @property
    def equipment_detection_bonus(self) -> float:
        """装备提供的探测加成"""
        total = 0.0
        for treasure_name in self.equipment.values():
            state = self.treasure_states.get(treasure_name, {})
            total += float(state.get("detection_bonus", 0.0))
        return total

    def can_detect(self, other: "Character") -> bool:
        """是否能探测到另一个角色"""
        distance = self.position.distance_to(other.position)
        return distance <= self.detection_range

    @property
    def technique_detection_bonus(self) -> float:
        """功法提供的探测加成"""
        total = 0.0
        for tech_name, level in self.techniques.items():
            mods = self.technique_modifiers.get(tech_name, {})
            total += float(mods.get("detection_bonus", 0.0)) * max(1, level)
        return total

    def with_attributes(self, attributes: CharacterAttributes) -> "Character":
        """返回新角色，更新属性"""
        return self._copy_with(attributes=attributes)

    def with_position(self, x: float, y: float) -> "Character":
        """返回新角色，更新位置"""
        return self._copy_with(position=Position(x, y))

    def with_realm(self, realm: Realm) -> "Character":
        """返回新角色，更新境界"""
        new_attributes = self.attributes.with_max_multiplier(realm.hp_multiplier / self.realm.hp_multiplier)
        return self._copy_with(attributes=new_attributes, realm=realm)

    def add_item(self, item_name: str, count: int = 1) -> "Character":
        """添加物品"""
        new_inventory = self.inventory.copy()
        new_inventory[item_name] = new_inventory.get(item_name, 0) + count
        return self._copy_with(inventory=new_inventory)

    def remove_item(self, item_name: str, count: int = 1) -> "Character":
        """移除物品"""
        new_inventory = self.inventory.copy()
        current = new_inventory.get(item_name, 0)
        if current <= count:
            new_inventory.pop(item_name, None)
        else:
            new_inventory[item_name] = current - count
        return self._copy_with(inventory=new_inventory)

    def equip_item(self, slot: str, item_name: str, treasure_data: Optional[dict[str, Any]] = None) -> "Character":
        """装备物品"""
        new_equipment = self.equipment.copy()
        new_equipment[slot] = item_name
        new_states = {k: v.copy() for k, v in self.treasure_states.items()}
        if item_name not in new_states:
            new_states[item_name] = self._build_treasure_state(item_name, treasure_data)
        return self._copy_with(equipment=new_equipment, treasure_states=new_states)

    def _build_treasure_state(self, item_name: str, treasure_data: Optional[dict[str, Any]]) -> dict[str, Any]:
        """构建法宝动态状态"""
        data = treasure_data or {}
        max_durability = int(data.get("max_durability", data.get("durability", 100)))
        durability = int(data.get("durability", max_durability))
        wear = int(data.get("wear", 100))
        return {
            "name": item_name,
            "durability": max(0, min(max_durability, durability)),
            "max_durability": max(1, max_durability),
            "wear": max(0, min(100, wear)),
            "injected_spirit": int(data.get("injected_spirit", 0)),
            "max_injected_spirit": int(data.get("max_injected_spirit", data.get("spirit_power_cost", 20) + 5)),
            "detection_bonus": float(data.get("detection_bonus", 0.0)),
        }

    def sync_treasure_templates(self, treasures_data: dict[str, Any]) -> "Character":
        """同步装备法宝的模板数据到动态状态"""
        new_states = {k: v.copy() for k, v in self.treasure_states.items()}

        for treasure_name in self.equipment.values():
            template = treasures_data.get(treasure_name, {})
            if treasure_name not in new_states:
                new_states[treasure_name] = self._build_treasure_state(treasure_name, template)
                continue

            state = new_states[treasure_name]
            state["max_durability"] = int(template.get("max_durability", state.get("max_durability", 100)))
            state["max_injected_spirit"] = int(
                template.get("max_injected_spirit", template.get("spirit_power_cost", state.get("max_injected_spirit", 20)))
            )
            state["detection_bonus"] = float(template.get("detection_bonus", state.get("detection_bonus", 0.0)))
            state["durability"] = max(0, min(int(state["durability"]), int(state["max_durability"])))
            state["injected_spirit"] = max(0, min(int(state["injected_spirit"]), int(state["max_injected_spirit"])))
            state["wear"] = max(0, min(100, int(state.get("wear", 100))))

        return self._copy_with(treasure_states=new_states)

    def sync_technique_templates(self, techniques_data: dict[str, Any]) -> "Character":
        """同步功法模板信息到角色功法修正"""
        new_mods = {k: v.copy() for k, v in self.technique_modifiers.items()}
        for tech_name in self.techniques.keys():
            template = techniques_data.get(tech_name, {})
            if tech_name not in new_mods:
                new_mods[tech_name] = {}
            new_mods[tech_name]["detection_bonus"] = float(template.get("detection_bonus", 0.0))
        return self._copy_with(technique_modifiers=new_mods)

    def apply_treasure_change(
        self,
        treasure_name: str,
        wear_delta: int = 0,
        durability_delta: int = 0,
        injected_spirit: Optional[int] = None,
    ) -> "Character":
        """应用法宝动态变化"""
        new_states = {k: v.copy() for k, v in self.treasure_states.items()}
        if treasure_name not in new_states:
            new_states[treasure_name] = self._build_treasure_state(treasure_name, None)

        state = new_states[treasure_name]
        state["wear"] = max(0, min(100, int(state.get("wear", 100)) + wear_delta))
        max_durability = int(state.get("max_durability", 100))
        state["durability"] = max(0, min(max_durability, int(state.get("durability", max_durability)) + durability_delta))
        if injected_spirit is not None:
            max_injected = int(state.get("max_injected_spirit", 20))
            state["injected_spirit"] = max(0, min(max_injected, int(injected_spirit)))

        return self._copy_with(treasure_states=new_states)

    def add_combat_insight(self, bonus: float) -> "Character":
        """添加战斗感悟"""
        return self._copy_with(combat_insight=self.combat_insight + bonus)

    def add_breakthrough_bonus(self, bonus: float) -> "Character":
        """添加临时突破加成"""
        return self._copy_with(breakthrough_bonus=self.breakthrough_bonus + bonus)

    def clear_breakthrough_bonus(self) -> "Character":
        """清除临时突破加成"""
        return self._copy_with(breakthrough_bonus=0.0)

    def can_cultivate_technique(self, technique_elements: list[str]) -> bool:
        """检查灵根是否满足功法元素约束"""
        if not technique_elements:
            return True
        name_map = {
            "metal": Element.METAL, "金": Element.METAL,
            "wood": Element.WOOD, "木": Element.WOOD,
            "water": Element.WATER, "水": Element.WATER,
            "fire": Element.FIRE, "火": Element.FIRE,
            "earth": Element.EARTH, "土": Element.EARTH,
            "chaos": Element.CHAOS, "混沌": Element.CHAOS,
        }
        elements = []
        for name in technique_elements:
            key = str(name).lower()
            if key in name_map:
                elements.append(name_map[key])
        if not elements:
            return True
        element_set = frozenset(elements)
        return self.spirit_root.can_cultivate(element_set)

    def learn_technique(
        self,
        technique_name: str,
        level: int = 1,
        technique_elements: Optional[list[str]] = None,
    ) -> tuple["Character", bool, str]:
        """学习功法（会校验灵根约束）"""
        elements = technique_elements or []
        if not self.can_cultivate_technique(elements):
            return self, False, f"灵根不兼容功法 {technique_name}"

        new_techniques = self.techniques.copy()
        new_techniques[technique_name] = max(1, level)
        return self._copy_with(techniques=new_techniques), True, ""

    def consume_pill(self, item_name: str, pill: Any) -> tuple["Character", list[str]]:
        """服用丹药，应用效果并扣减库存"""
        logs: list[str] = []
        if not self.inventory.get(item_name):
            return self, logs

        new_char = self.remove_item(item_name, 1)
        effect = getattr(pill, "effect", None)
        if not effect:
            logs.append(f"服用了 {item_name}")
            return new_char, logs

        if effect.hp_change:
            new_char = new_char.with_attributes(new_char.attributes.with_hp_delta(effect.hp_change))
            logs.append(f"血量变化: {effect.hp_change:+d}")
        if effect.mp_change:
            new_char = new_char.with_attributes(new_char.attributes.with_mp_delta(effect.mp_change))
            logs.append(f"灵力变化: {effect.mp_change:+d}")
        if effect.spirit_change:
            new_char = new_char.with_attributes(new_char.attributes.with_spirit_delta(effect.spirit_change))
            logs.append(f"神识变化: {effect.spirit_change:+d}")

        if getattr(effect, "breakthrough_bonus", 0.0):
            new_char = new_char.add_breakthrough_bonus(effect.breakthrough_bonus)
            logs.append(f"突破加成: +{effect.breakthrough_bonus * 100:.1f}%")

        for status in getattr(effect, "status_add", ()):
            new_char = new_char.with_attributes(new_char.attributes.add_status(status))
        for status in getattr(effect, "status_remove", ()):
            new_char = new_char.with_attributes(new_char.attributes.remove_status(status))

        logs.append(f"服用了 {item_name}")
        return new_char, logs

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
            "treasure_states": self.treasure_states,
            "technique_modifiers": self.technique_modifiers,
        }

    def to_save_dict(self) -> dict[str, Any]:
        """转换为存档字典"""
        return {
            "id": self.id,
            "name": self.name,
            "attributes": {
                "hp": {"current": self.attributes.hp.current, "max": self.attributes.hp.max},
                "mp": {"current": self.attributes.mp.current, "max": self.attributes.mp.max},
                "spirit": {"current": self.attributes.spirit.current, "max": self.attributes.spirit.max},
                "statuses": list(self.attributes.statuses),
            },
            "realm": {
                "major": self.realm.major.value,
                "minor": self.realm.minor.value,
            },
            "spirit_root": {
                "is_chaos": self.spirit_root.is_chaos,
                "elements": [e.value for e in self.spirit_root.elements],
            },
            "position": {"x": self.position.x, "y": self.position.y},
            "techniques": self.techniques,
            "inventory": self.inventory,
            "equipment": self.equipment,
            "treasure_states": self.treasure_states,
            "technique_modifiers": self.technique_modifiers,
            "combat_insight": self.combat_insight,
            "breakthrough_bonus": self.breakthrough_bonus,
            "memory_bank": self.memory_bank.to_dict(),
        }

    @staticmethod
    def from_save_dict(data: dict[str, Any]) -> "Character":
        """从存档字典恢复角色"""
        realm_data = data.get("realm", {})
        realm = Realm(
            MajorRealm(realm_data.get("major", MajorRealm.QI_REFINING.value)),
            MinorRealm(realm_data.get("minor", MinorRealm.EARLY.value)),
        )

        root_data = data.get("spirit_root", {})
        if root_data.get("is_chaos"):
            spirit_root = SpiritRoot.create_chaos()
        else:
            elements = [Element(name) for name in root_data.get("elements", [])]
            spirit_root = SpiritRoot(frozenset(elements))

        attr_data = data.get("attributes", {})
        attributes = CharacterAttributes(
            hp=Attribute(attr_data.get("hp", {}).get("current", 0), attr_data.get("hp", {}).get("max", 1)),
            mp=Attribute(attr_data.get("mp", {}).get("current", 0), attr_data.get("mp", {}).get("max", 1)),
            spirit=Attribute(attr_data.get("spirit", {}).get("current", 0), attr_data.get("spirit", {}).get("max", 1)),
            statuses=tuple(attr_data.get("statuses", [])),
        )

        pos_data = data.get("position", {})
        memory_bank = MemoryBank.from_dict(data.get("id", ""), data.get("memory_bank"))

        return Character(
            id=data.get("id", ""),
            name=data.get("name", ""),
            attributes=attributes,
            realm=realm,
            spirit_root=spirit_root,
            memory_bank=memory_bank,
            position=Position(pos_data.get("x", 0.0), pos_data.get("y", 0.0)),
            techniques=data.get("techniques", {}),
            inventory=data.get("inventory", {}),
            equipment=data.get("equipment", {}),
            treasure_states=data.get("treasure_states", {}),
            technique_modifiers=data.get("technique_modifiers", {}),
            combat_insight=float(data.get("combat_insight", 0.0)),
            breakthrough_bonus=float(data.get("breakthrough_bonus", 0.0)),
        )

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
        """
        if realm is None:
            realm = Realm(MajorRealm.QI_REFINING, MinorRealm.EARLY)
        if spirit_root is None:
            spirit_root = SpiritRoot.create_single(Element.METAL)

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
