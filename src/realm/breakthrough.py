"""
境界突破系统模块
"""
import random
from typing import Optional
from dataclasses import dataclass
from ..character import Character, Realm, MajorRealm, MinorRealm
from ..world import Config


@dataclass
class BreakthroughResult:
    """突破结果"""
    success: bool
    new_realm: Optional[Realm] = None
    penalties: list[str] = None

    def __post_init__(self):
        if self.penalties is None:
            self.penalties = []


class BreakthroughSystem:
    """境界突破系统"""

    def __init__(self, config: Config):
        self.config = config

    def calculate_minor_success_rate(self, character: Character) -> float:
        """
        计算小境界突破成功率

        Args:
            character: 角色

        Returns:
            成功率 (0.0 - 1.0)
        """
        if not character.realm.can_progress_minor():
            return 0.0

        # 基础成功率
        realm_config = self.config.realms
        minor_rates = realm_config.get("minor_breakthrough_rates", {})
        major_key = character.realm.major.value

        minor_key_map = {
            (MinorRealm.EARLY, MinorRealm.MID): "early_to_mid",
            (MinorRealm.MID, MinorRealm.LATE): "mid_to_late",
        }
        minor_transition = (character.realm.minor, character.realm.minor.next())
        minor_key = minor_key_map.get(minor_transition)

        base_rate = 0.1
        if major_key in minor_rates and minor_key:
            base_rate = minor_rates[major_key].get(minor_key, 10) / 100.0

        # 加成因素
        total_rate = base_rate

        # 战斗感悟加成
        total_rate += character.combat_insight / 100.0

        # 临时突破加成（如丹药）
        total_rate += character.breakthrough_bonus

        # 灵根加成
        total_rate *= character.spirit_root.cultivation_speed_bonus

        # 确保不超过 100%
        return min(1.0, max(0.0, total_rate))

    def calculate_major_success_rate(self, character: Character) -> float:
        """
        计算大境界突破成功率

        Args:
            character: 角色

        Returns:
            成功率 (0.0 - 1.0)
        """
        if not character.realm.can_progress_major():
            return 0.0

        # 基础成功率
        realm_config = self.config.realms
        major_rates = realm_config.get("major_breakthrough_rates", {})

        transition_map = {
            (MajorRealm.QI_REFINING, MajorRealm.FOUNDATION): "qi_to_foundation",
            (MajorRealm.FOUNDATION, MajorRealm.GOLDEN_CORE): "foundation_to_golden",
            (MajorRealm.GOLDEN_CORE, MajorRealm.NASCENT_SOUL): "golden_to_nascent",
            (MajorRealm.NASCENT_SOUL, MajorRealm.SPIRIT_SEVERANCE): "nascent_to_spirit",
        }
        next_major = character.realm.major.next()
        transition = (character.realm.major, next_major)
        transition_key = transition_map.get(transition)

        base_rate = 0.01
        if transition_key and transition_key in major_rates:
            base_rate = major_rates[transition_key] / 100.0

        # 加成因素（同小境界）
        total_rate = base_rate
        total_rate += character.combat_insight / 100.0
        total_rate += character.breakthrough_bonus
        total_rate *= character.spirit_root.cultivation_speed_bonus

        return min(1.0, max(0.0, total_rate))

    def try_minor_breakthrough(self, character: Character) -> tuple[Character, BreakthroughResult]:
        """
        尝试小境界突破

        Args:
            character: 角色

        Returns:
            (新角色, 突破结果)
        """
        success_rate = self.calculate_minor_success_rate(character)
        success = random.random() < success_rate

        result = BreakthroughResult(success=success)

        if success:
            new_realm = character.realm.with_minor_progress()
            result.new_realm = new_realm
            return character.with_realm(new_realm), result

        # 小境界突破失败无惩罚
        return character, result

    def try_major_breakthrough(self, character: Character) -> tuple[Character, BreakthroughResult]:
        """
        尝试大境界突破

        Args:
            character: 角色

        Returns:
            (新角色, 突破结果)
        """
        success_rate = self.calculate_major_success_rate(character)
        success = random.random() < success_rate

        result = BreakthroughResult(success=success)
        new_char = character.clear_breakthrough_bonus()

        if success:
            new_realm = character.realm.with_major_progress()
            result.new_realm = new_realm
            return new_char.with_realm(new_realm), result

        # 大境界突破失败惩罚
        penalties = []
        if character.realm.major == MajorRealm.GOLDEN_CORE:
            # 结丹→元婴失败：产生心魔
            new_attr = new_char.attributes.add_status("心魔")
            new_char = new_char.with_attributes(new_attr)
            penalties.append("产生心魔，后续突破概率降低")
            result.penalties = penalties

        return new_char, result

    def should_attempt_breakthrough(self, cycle_count: int) -> bool:
        """
        判断是否应该尝试突破

        Args:
            cycle_count: 当前循环次数

        Returns:
            是否应该尝试
        """
        breakthrough_cycles = self.config.realms.get("breakthrough_cycles", 10)
        return cycle_count % breakthrough_cycles == 0
