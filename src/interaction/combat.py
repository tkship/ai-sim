"""
战斗系统模块
"""
import random
from typing import Optional, Tuple
from dataclasses import dataclass
from ..character import Character
from ..item import Treasure
from ..world import Config


@dataclass
class AttackResult:
    """攻击结果"""
    damage: int
    attacker_mp_cost: int
    defender_mp_cost: int
    attacker_treasure_wear: int
    defender_treasure_wear: int
    dodged: bool = False
    special_effects: list[str] = None

    def __post_init__(self):
        if self.special_effects is None:
            self.special_effects = []


@dataclass
class CombatState:
    """战斗状态"""
    round_count: int = 0
    in_combat: bool = False
    combatants: list[str] = None
    status_effects: dict[str, list[tuple[str, int]]] = None

    def __post_init__(self):
        if self.combatants is None:
            self.combatants = []
        if self.status_effects is None:
            self.status_effects = {}


class CombatSystem:
    """战斗系统"""

    def __init__(self, config: Config):
        self.config = config

    def calculate_attack(
        self,
        attacker: Character,
        defender: Character,
        attacker_treasure: Optional[Treasure],
        defender_treasure: Optional[Treasure],
        attacker_inject: int,
        defender_inject: int,
        environment_element: Optional[str] = None
    ) -> AttackResult:
        """
        计算攻击伤害

        Args:
            attacker: 攻击者
            defender: 防御者
            attacker_treasure: 攻击方法宝
            defender_treasure: 防御法宝
            attacker_inject: 攻击者注入灵力
            defender_inject: 防御者注入灵力
            environment_element: 环境元素

        Returns:
            攻击结果
        """
        result = AttackResult(
            damage=0,
            attacker_mp_cost=0,
            defender_mp_cost=0,
            attacker_treasure_wear=0,
            defender_treasure_wear=0
        )

        # 检查闪避
        if self._check_dodge(defender):
            result.dodged = True
            return result

        # 计算基础攻击
        attack_min, attack_max = 0, 0
        if attacker_treasure:
            attack_min, attack_max = attacker_treasure.current_attack
            result.attacker_treasure_wear = -3

        # 注入灵力加成
        inject_bonus = attacker_inject * 0.5
        attack_min += int(inject_bonus)
        attack_max += int(inject_bonus)
        result.attacker_mp_cost = attacker_inject

        # 环境加成/减成
        if attacker_treasure and attacker_treasure.element:
            combat_config = self.config.combat
            bonus_ratio = combat_config.get("environment_bonus_ratio", 0.2)
            penalty_ratio = combat_config.get("environment_penalty_ratio", 0.2)

            if environment_element == attacker_treasure.element:
                attack_min = int(attack_min * (1 + bonus_ratio))
                attack_max = int(attack_max * (1 + bonus_ratio))
            elif environment_element and self._elements_counter(attacker_treasure.element, environment_element):
                attack_min = int(attack_min * (1 - penalty_ratio))
                attack_max = int(attack_max * (1 - penalty_ratio))

        # 基础伤害
        damage = random.randint(attack_min, attack_max) if attack_max > 0 else 0

        # 计算防御
        defense_min, defense_max = 0, 0
        if defender_treasure:
            defense_min, defense_max = defender_treasure.current_defense
            result.defender_treasure_wear = -2

        # 防御注入灵力
        def_inject_bonus = defender_inject * 0.5
        defense_min += int(def_inject_bonus)
        defense_max += int(def_inject_bonus)
        result.defender_mp_cost = defender_inject

        # 环境防御加成
        if defender_treasure and defender_treasure.element:
            combat_config = self.config.combat
            bonus_ratio = combat_config.get("environment_bonus_ratio", 0.2)
            penalty_ratio = combat_config.get("environment_penalty_ratio", 0.2)

            if environment_element == defender_treasure.element:
                defense_min = int(defense_min * (1 + bonus_ratio))
                defense_max = int(defense_max * (1 + bonus_ratio))
            elif environment_element and self._elements_counter(defender_treasure.element, environment_element):
                defense_min = int(defense_min * (1 - penalty_ratio))
                defense_max = int(defense_max * (1 - penalty_ratio))

        defense = random.randint(defense_min, defense_max) if defense_max > 0 else 0

        # 最终伤害
        result.damage = max(0, damage - defense)
        return result

    def _check_dodge(self, defender: Character) -> bool:
        """检查是否闪避成功"""
        # 简化版闪避检查
        return False

    def _elements_counter(self, elem1: str, elem2: str) -> bool:
        """检查元素是否相克"""
        # 简化版相克检查
        counter_pairs = [
            ("metal", "wood"),
            ("wood", "earth"),
            ("earth", "water"),
            ("water", "fire"),
            ("fire", "metal"),
        ]
        return (elem1, elem2) in counter_pairs

    def apply_attack_result(
        self,
        attacker: Character,
        defender: Character,
        result: AttackResult
    ) -> tuple[Character, Character]:
        """
        应用攻击结果

        Args:
            attacker: 攻击者
            defender: 防御者
            result: 攻击结果

        Returns:
            (新攻击者, 新防御者)
        """
        # 应用灵力消耗
        new_attacker = attacker
        new_defender = defender

        if result.attacker_mp_cost > 0:
            new_attr = new_attacker.attributes.with_mp_delta(-result.attacker_mp_cost)
            new_attacker = new_attacker.with_attributes(new_attr)

        if result.defender_mp_cost > 0:
            new_attr = new_defender.attributes.with_mp_delta(-result.defender_mp_cost)
            new_defender = new_defender.with_attributes(new_attr)

        # 应用伤害
        if not result.dodged and result.damage > 0:
            new_attr = new_defender.attributes.with_hp_delta(-result.damage)
            new_defender = new_defender.with_attributes(new_attr)

        # 添加战斗感悟
        new_attacker = new_attacker.add_combat_insight(2.0)
        new_defender = new_defender.add_combat_insight(2.0)

        return new_attacker, new_defender


class CombatRoundTracker:
    """战斗回合追踪器"""

    def __init__(self):
        self.state = CombatState()

    def start_combat(self, combatant_ids: list[str]) -> None:
        """开始战斗"""
        self.state.in_combat = True
        self.state.round_count = 0
        self.state.combatants = combatant_ids.copy()

    def end_combat(self) -> None:
        """结束战斗"""
        self.state.in_combat = False

    def next_round(self) -> int:
        """下一回合"""
        self.state.round_count += 1
        self._update_status_effects()
        return self.state.round_count

    def add_status_effect(self, character_id: str, effect: str, duration: int) -> None:
        """添加状态效果"""
        if character_id not in self.state.status_effects:
            self.state.status_effects[character_id] = []
        self.state.status_effects[character_id].append((effect, duration))

    def _update_status_effects(self) -> None:
        """更新状态效果持续时间"""
        for char_id in list(self.state.status_effects.keys()):
            effects = self.state.status_effects[char_id]
            new_effects = []
            for effect, dur in effects:
                if dur > 1:
                    new_effects.append((effect, dur - 1))
            self.state.status_effects[char_id] = new_effects

    def get_active_effects(self, character_id: str) -> list[str]:
        """获取活跃状态效果"""
        if character_id not in self.state.status_effects:
            return []
        return [effect for effect, _ in self.state.status_effects[character_id]]
