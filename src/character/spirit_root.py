"""
灵根系统模块
"""
from dataclasses import dataclass
from typing import Optional, FrozenSet
from enum import Enum


class Element(Enum):
    """五行元素"""
    METAL = "metal"
    WOOD = "wood"
    WATER = "water"
    FIRE = "fire"
    EARTH = "earth"
    CHAOS = "chaos"

    @property
    def display_name(self) -> str:
        """显示名称"""
        names = {
            self.METAL: "金",
            self.WOOD: "木",
            self.WATER: "水",
            self.FIRE: "火",
            self.EARTH: "土",
            self.CHAOS: "混沌",
        }
        return names[self]

    def counters(self, other: "Element") -> bool:
        """是否克制另一个元素"""
        # 五行相克：金克木，木克土，土克水，水克火，火克金
        counter_map = {
            self.METAL: self.WOOD,
            self.WOOD: self.EARTH,
            self.EARTH: self.WATER,
            self.WATER: self.FIRE,
            self.FIRE: self.METAL,
        }
        return counter_map.get(self) == other

    def enhances(self, other: "Element") -> bool:
        """是否相生另一个元素"""
        # 五行相生：金生水，水生木，木生火，火生土，土生金
        enhance_map = {
            self.METAL: self.WATER,
            self.WATER: self.WOOD,
            self.WOOD: self.FIRE,
            self.FIRE: self.EARTH,
            self.EARTH: self.METAL,
        }
        return enhance_map.get(self) == other


@dataclass(frozen=True)
class SpiritRoot:
    """灵根"""
    elements: FrozenSet[Element]
    is_chaos: bool = False

    @property
    def element_count(self) -> int:
        """灵根属性数量"""
        return len(self.elements)

    @property
    def purity(self) -> float:
        """灵根纯净度（1.0 最高）"""
        if self.is_chaos:
            return 2.0
        # 单属性最纯净，五属性最驳杂
        purity_map = {1: 1.5, 2: 1.2, 3: 1.0, 4: 0.8, 5: 0.6}
        return purity_map.get(self.element_count, 1.0)

    @property
    def cultivation_speed_bonus(self) -> float:
        """修炼速度加成"""
        if self.is_chaos:
            return 2.0
        bonuses = {1: 1.5, 2: 1.2, 3: 1.0, 4: 0.8, 5: 0.6}
        return bonuses.get(self.element_count, 1.0)

    @property
    def display_name(self) -> str:
        """灵根显示名称"""
        if self.is_chaos:
            return "混沌灵根"

        element_names = [e.display_name for e in sorted(self.elements, key=lambda x: x.value)]
        type_names = {1: "单", 2: "双", 3: "三", 4: "四", 5: "五"}
        type_name = type_names.get(self.element_count, "")
        return f"{''.join(element_names)}{type_name}灵根"

    def can_cultivate(self, technique_elements: FrozenSet[Element]) -> bool:
        """
        检查是否可以修炼某功法

        Args:
            technique_elements: 功法的元素属性

        Returns:
            是否可以修炼
        """
        # 混沌灵根可以修炼一切功法
        if self.is_chaos:
            return True

        # 无属性功法任何人都可以修炼
        if not technique_elements:
            return True

        # 灵根必须包含功法的所有元素属性
        return technique_elements.issubset(self.elements)

    def has_element(self, element: Element) -> bool:
        """是否包含某元素"""
        if self.is_chaos:
            return True
        return element in self.elements

    @staticmethod
    def create_single(element: Element) -> "SpiritRoot":
        """创建单属性灵根"""
        return SpiritRoot(frozenset([element]))

    @staticmethod
    def create_dual(element1: Element, element2: Element) -> "SpiritRoot":
        """创建双属性灵根"""
        return SpiritRoot(frozenset([element1, element2]))

    @staticmethod
    def create_chaos() -> "SpiritRoot":
        """创建混沌灵根"""
        return SpiritRoot(frozenset(), is_chaos=True)

    @staticmethod
    def create_from_names(*element_names: str) -> "SpiritRoot":
        """从元素名称创建灵根"""
        if "chaos" in element_names or "混沌" in element_names:
            return SpiritRoot.create_chaos()

        elements = []
        name_map = {
            "metal": Element.METAL, "金": Element.METAL,
            "wood": Element.WOOD, "木": Element.WOOD,
            "water": Element.WATER, "水": Element.WATER,
            "fire": Element.FIRE, "火": Element.FIRE,
            "earth": Element.EARTH, "土": Element.EARTH,
        }
        for name in element_names:
            elem = name_map.get(name.lower())
            if elem:
                elements.append(elem)

        return SpiritRoot(frozenset(elements))
