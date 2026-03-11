"""战斗计算模块

处理战斗相关的计算逻辑
"""
from typing import Optional, Tuple, List
from character.character import Character
import random


class Combat:
    """战斗计算类

    负责战斗伤害计算和结果判定
    """

    def __init__(self):
        """初始化战斗系统"""
        pass

    def calculate_damage(
        self,
        attacker: Character,
        defender: Character,
        is_critical: bool = False,
    ) -> int:
        """计算伤害

        核心公式：伤害 = 攻击者灵力 + 攻击法宝攻击力 - 防御者灵力 - 防御法宝防御力

        Args:
            attacker: 攻击者
            defender: 防御者
            is_critical: 是否暴击

        Returns:
            伤害值
        """
        # 基础伤害 = 攻击力 - 防御力
        base_damage = attacker.total_attack_power - defender.total_defense_power

        # 装备加成
        attacker_bonus = attacker.inventory.get_equipped_bonus()
        defender_bonus = defender.inventory.get_equipped_bonus()

        # 灵力加成
        spirit_damage = attacker.total_spirit_power - defender.total_spirit_power

        # 总伤害
        total_damage = base_damage + spirit_damage

        # 确保最小伤害
        total_damage = max(1, total_damage)

        # 暴击加成
        if is_critical:
            total_damage = int(total_damage * 1.5)

        # 加上一点随机波动（±10%）
        random_factor = random.uniform(0.9, 1.1)
        total_damage = int(total_damage * random_factor)

        return total_damage

    def check_critical_hit(self, attacker: Character) -> bool:
        """检查是否暴击

        Args:
            attacker: 攻击者

        Returns:
            是否暴击
        """
        # 暴击率 = 运气 * 0.5 + 境界加成
        crit_rate = attacker.attributes.luck * 0.5 + attacker.realm.power_bonus * 0.1
        crit_rate = min(0.3, crit_rate)  # 最高30%暴击率

        return random.random() < crit_rate

    def calculate_hit_chance(
        self,
        attacker: Character,
        defender: Character,
    ) -> float:
        """计算命中率

        Args:
            attacker: 攻击者
            defender: 防御者

        Returns:
            命中概率（0-1）
        """
        # 基础命中率
        base_hit_rate = 0.8

        # 境界差距影响
        realm_diff = attacker.realm.level - defender.realm.level

        # 每级境界差距增加/减少5%命中率
        hit_rate = base_hit_rate + realm_diff * 0.05

        # 运气影响
        luck_diff = attacker.attributes.luck - defender.attributes.luck
        hit_rate += luck_diff * 0.01

        # 限制范围
        hit_rate = max(0.1, min(0.95, hit_rate))

        return hit_rate

    def perform_attack(
        self,
        attacker: Character,
        defender: Character,
    ) -> Tuple[int, bool, bool]:
        """执行一次攻击

        Args:
            attacker: 攻击者
            defender: 防御者

        Returns:
            (伤害值, 是否命中, 是否暴击)
        """
        # 检查是否命中
        hit_rate = self.calculate_hit_chance(attacker, defender)
        is_hit = random.random() < hit_rate

        if not is_hit:
            return (0, False, False)

        # 检查是否暴击
        is_critical = self.check_critical_hit(attacker)

        # 计算伤害
        damage = self.calculate_damage(attacker, defender, is_critical)

        # 应用伤害
        actual_damage = defender.take_damage(damage)

        return (actual_damage, True, is_critical)

    def simulate_combat(
        self,
        attacker: Character,
        defender: Character,
        max_rounds: int = 10,
    ) -> dict:
        """模拟一场战斗

        Args:
            attacker: 攻击者
            defender: 防御者
            max_rounds: 最大回合数

        Returns:
            战斗结果字典
        """
        result = {
            "attacker_id": attacker.id,
            "defender_id": defender.id,
            "rounds": [],
            "winner": None,
            "total_damage_to_defender": 0,
            "total_damage_to_attacker": 0,
        }

        current_round = 0
        attacker_health_before = attacker.attributes.health
        defender_health_before = defender.attributes.health

        while current_round < max_rounds:
            current_round += 1

            # 攻击者攻击
            damage, is_hit, is_critical = self.perform_attack(attacker, defender)
            result["total_damage_to_defender"] += damage

            round_info = {
                "round": current_round,
                "attacker_action": {
                    "damage": damage,
                    "is_hit": is_hit,
                    "is_critical": is_critical,
                    "defender_health_after": defender.attributes.health,
                },
            }

            # 检查防御者是否死亡
            if not defender.is_alive:
                round_info["result"] = "attacker_wins"
                result["rounds"].append(round_info)
                result["winner"] = attacker.id
                break

            # 防御者反击
            counter_damage, is_hit, is_critical = self.perform_attack(defender, attacker)
            result["total_damage_to_attacker"] += counter_damage

            round_info["defender_action"] = {
                "damage": counter_damage,
                "is_hit": is_hit,
                "is_critical": is_critical,
                "attacker_health_after": attacker.attributes.health,
            }

            # 检查攻击者是否死亡
            if not attacker.is_alive:
                round_info["result"] = "defender_wins"
                result["rounds"].append(round_info)
                result["winner"] = defender.id
                break

            result["rounds"].append(round_info)

        # 记录战斗记忆
        attacker.add_memory(
            memory_type="combat",
            description=f"与{defender.name}战斗，造成{result['total_damage_to_defender']}伤害，承受{result['total_damage_to_attacker']}伤害",
            related_character_ids=[defender.id],
            data=result,
        )

        defender.add_memory(
            memory_type="combat",
            description=f"与{attacker.name}战斗，承受{result['total_damage_to_defender']}伤害，造成{result['total_damage_to_attacker']}伤害",
            related_character_ids=[attacker.id],
            data=result,
        )

        return result

    def check_realm_advance_after_combat(
        self,
        character: Character,
        damage_dealt: int,
        damage_taken: int,
    ) -> bool:
        """战斗后检查境界提升

        Args:
            character: 角色
            damage_dealt: 造成的伤害
            damage_taken: 承受的伤害

        Returns:
            是否提升境界
        """
        # 战斗经验值 = 造成的伤害 + 承受的伤害
        combat_exp = damage_dealt + damage_taken

        # 提升概率 = 经验值 / 100 * 0.1
        advance_chance = combat_exp / 100 * 0.1

        # 限制最大概率
        advance_chance = min(0.2, advance_chance)

        if random.random() < advance_chance:
            return character.try_realm_advance()

        return False

    def get_combat_summary(self, combat_result: dict) -> str:
        """获取战斗摘要

        Args:
            combat_result: 战斗结果

        Returns:
            战斗摘要字符串
        """
        rounds = len(combat_result["rounds"])
        attacker_damage = combat_result["total_damage_to_defender"]
        defender_damage = combat_result["total_damage_to_attacker"]

        if combat_result["winner"] is None:
            result_text = "战斗平局"
        elif combat_result["winner"] == combat_result["attacker_id"]:
            result_text = "攻击者获胜"
        else:
            result_text = "防御者获胜"

        return (
            f"战斗持续 {rounds} 回合，"
            f"攻击者造成 {attacker_damage} 伤害、承受 {defender_damage} 伤害，"
            f"{result_text}"
        )
