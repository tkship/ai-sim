"""
物品栏和装备系统模块
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from .treasure import Treasure
from .pill import Pill


@dataclass(frozen=True)
class InventoryItem:
    """物品栏物品"""
    name: str
    count: int = 1
    item_type: str = "treasure"  # treasure, pill, other
    data: Any = None

    def with_count(self, delta: int) -> "InventoryItem":
        """更新数量"""
        new_count = max(0, self.count + delta)
        return InventoryItem(
            name=self.name,
            count=new_count,
            item_type=self.item_type,
            data=self.data
        )


@dataclass
class Inventory:
    """物品栏"""
    items: dict[str, InventoryItem] = field(default_factory=dict)

    def get_item(self, name: str) -> Optional[InventoryItem]:
        """获取物品"""
        return self.items.get(name)

    def has_item(self, name: str, count: int = 1) -> bool:
        """检查是否有足够的物品"""
        item = self.items.get(name)
        return item is not None and item.count >= count

    def add_item(self, name: str, count: int = 1, item_type: str = "treasure", data: Any = None) -> "Inventory":
        """添加物品"""
        new_items = self.items.copy()
        if name in new_items:
            new_items[name] = new_items[name].with_count(count)
        else:
            new_items[name] = InventoryItem(name, count, item_type, data)
        return Inventory(new_items)

    def remove_item(self, name: str, count: int = 1) -> "Inventory":
        """移除物品"""
        if name not in self.items:
            return self

        new_items = self.items.copy()
        item = new_items[name]
        if item.count <= count:
            new_items.pop(name)
        else:
            new_items[name] = item.with_count(-count)
        return Inventory(new_items)

    def get_all_items(self) -> list[InventoryItem]:
        """获取所有物品"""
        return list(self.items.values())

    def to_prompt_dict(self) -> dict[str, int]:
        """转换为提示词字典"""
        return {name: item.count for name, item in self.items.items()}


@dataclass
class Equipment:
    """装备栏"""
    slots: dict[str, Optional[Treasure]] = field(default_factory=dict)

    # 默认装备槽位
    DEFAULT_SLOTS = ["weapon", "armor", "accessory1", "accessory2"]

    def __init__(self):
        self.slots = {slot: None for slot in self.DEFAULT_SLOTS}

    def get_equipped(self, slot: str) -> Optional[Treasure]:
        """获取已装备的物品"""
        return self.slots.get(slot)

    def equip(self, slot: str, treasure: Treasure) -> "Equipment":
        """装备物品"""
        if slot not in self.slots:
            return self
        new_slots = self.slots.copy()
        new_slots[slot] = treasure
        new_eq = Equipment()
        new_eq.slots = new_slots
        return new_eq

    def unequip(self, slot: str) -> tuple["Equipment", Optional[Treasure]]:
        """卸下物品，返回新装备栏和卸下的物品"""
        if slot not in self.slots:
            return self, None
        treasure = self.slots[slot]
        new_slots = self.slots.copy()
        new_slots[slot] = None
        new_eq = Equipment()
        new_eq.slots = new_slots
        return new_eq, treasure

    def get_all_equipped(self) -> dict[str, Treasure]:
        """获取所有已装备的物品"""
        return {slot: t for slot, t in self.slots.items() if t is not None}

    def get_total_bonuses(self) -> dict[str, Any]:
        """获取所有装备的总加成"""
        bonuses = {
            "hp": 0,
            "mp": 0,
            "spirit": 0,
            "attack_min": 0,
            "attack_max": 0,
            "defense_min": 0,
            "defense_max": 0,
            "speed": 0.0,
            "detection": 0.0,
            "breakthrough": 0.0,
        }

        for treasure in self.slots.values():
            if treasure:
                bonuses["hp"] += treasure.hp_bonus
                bonuses["mp"] += treasure.mp_bonus
                bonuses["spirit"] += treasure.spirit_bonus
                bonuses["attack_min"] += treasure.attack_min
                bonuses["attack_max"] += treasure.attack_max
                bonuses["defense_min"] += treasure.defense_min
                bonuses["defense_max"] += treasure.defense_max
                bonuses["speed"] += treasure.speed_bonus
                bonuses["detection"] += treasure.detection_bonus
                bonuses["breakthrough"] += treasure.breakthrough_bonus

        return bonuses

    def to_prompt_dict(self) -> dict[str, Optional[dict]]:
        """转换为提示词字典"""
        result = {}
        for slot, treasure in self.slots.items():
            if treasure:
                result[slot] = treasure.to_prompt_dict()
            else:
                result[slot] = None
        return result
