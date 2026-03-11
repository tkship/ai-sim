"""角色系统测试"""
import pytest
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from character.attributes import Attributes
from character.realm import Realm
from character.inventory import Inventory, ITEM_LIBRARY
from character.memory import Memory
from character.character import Character, create_character


class TestAttributes:
    """属性系统测试"""

    def test_initialization(self):
        """测试属性初始化"""
        attr = Attributes(health=100, spirit_power=50, consciousness=20)

        assert attr.health == 100
        assert attr.max_health == 100
        assert attr.spirit_power == 50
        assert attr.max_spirit_power == 50
        assert attr.consciousness == 20

    def test_derived_attributes(self):
        """测试派生属性计算"""
        attr = Attributes(health=100, spirit_power=50, consciousness=20)

        # 攻击力 = 灵力 * 0.8 + 神识 * 0.2 = 50 * 0.8 + 20 * 0.2 = 44
        assert attr.attack_power == 44

        # 防御力 = 灵力 * 0.5 + 神识 * 0.5 = 50 * 0.5 + 20 * 0.5 = 35
        assert attr.defense_power == 35

    def test_apply_delta(self):
        """测试属性增量应用"""
        attr = Attributes(health=100, spirit_power=50)

        result = attr.apply_delta({"health": -20, "spirit_power": 10})

        assert attr.health == 80
        assert attr.spirit_power == 60
        assert result["health"] == -20
        assert result["spirit_power"] == 10

    def test_delta_limit(self):
        """测试属性变化限制"""
        attr = Attributes(health=100, spirit_power=50)

        # 试图将血量减少超过最大值
        attr.apply_delta({"health": -150})

        # 血量不应小于 0
        assert attr.health == 0

        # 试图将灵力增加超过最大值
        attr.apply_delta({"spirit_power": 100})

        # 灵力不应超过最大值
        assert attr.spirit_power == 50


class TestRealm:
    """境界系统测试"""

    def test_initialization(self):
        """测试境界初始化"""
        realm = Realm()

        assert realm.major == "炼气"
        assert realm.minor == "初期"

    def test_name(self):
        """测试境界名称"""
        realm = Realm()
        assert realm.name == "炼气初期"

    def test_level(self):
        """测试境界等级"""
        realm = Realm()
        assert realm.level == 1  # 炼气(0) + 初期(1) = 1

    def test_power_bonus(self):
        """测试境界战斗力加成"""
        realm = Realm()
        # 炼气初期的战斗力加成是 1.0
        assert realm.power_bonus == 1.0


class TestInventory:
    """物品系统测试"""

    def test_initialization(self):
        """测试背包初始化"""
        inventory = Inventory()
        assert len(inventory.items) == 0

    def test_add_item(self):
        """测试添加物品"""
        inventory = Inventory()

        inventory.add_item(ITEM_LIBRARY["基础飞剑"])

        assert len(inventory.items) == 1
        assert inventory.items[0].name == "基础飞剑"

    def test_remove_item(self):
        """测试移除物品"""
        inventory = Inventory()
        inventory.add_item_by_name("基础飞剑")

        item_id = inventory.items[0].id
        success = inventory.remove_item(item_id)

        assert success is True
        assert len(inventory.items) == 0

    def test_equip_item(self):
        """测试装备物品"""
        inventory = Inventory()
        inventory.add_item_by_name("基础飞剑")

        item_id = inventory.items[0].id
        success = inventory.equip_item(item_id)

        assert success is True
        assert inventory.equipped_artifact is not None
        assert inventory.equipped_artifact.name == "基础飞剑"

    def test_get_equipped_bonus(self):
        """测试获取装备加成"""
        inventory = Inventory()
        inventory.add_item_by_name("基础飞剑")

        item_id = inventory.items[0].id
        inventory.equip_item(item_id)

        bonus = inventory.get_equipped_bonus()

        # 基础飞剑攻击力 +10
        assert bonus["attack_power"] == 10


class TestMemory:
    """记忆系统测试"""

    def test_initialization(self):
        """测试记忆初始化"""
        memory = Memory()
        assert len(memory.entries) == 0

    def test_add_entry(self):
        """测试添加记忆"""
        memory = Memory()
        memory.add_entry("test", "测试记忆")

        assert len(memory.entries) == 1
        assert memory.entries[0].memory_type == "test"
        assert memory.entries[0].description == "测试记忆"

    def test_get_recent_memories(self):
        """测试获取最近记忆"""
        memory = Memory()

        for i in range(10):
            memory.add_entry("test", f"记忆{i}")

        recent = memory.get_recent_memories(5)

        assert len(recent) == 5
        assert recent[-1].description == "记忆9"

    def test_max_entries(self):
        """测试最大记忆条数限制"""
        memory = Memory()
        memory.max_entries = 5

        for i in range(10):
            memory.add_entry("test", f"记忆{i}")

        # 应该只保留最新的 5 条
        assert len(memory.entries) == 5


class TestCharacter:
    """角色类测试"""

    def test_initialization(self):
        """测试角色初始化"""
        character = Character(name="测试角色")

        assert character.name == "测试角色"
        assert character.is_alive is True
        assert character.state == "idle"

    def test_total_attack_power(self):
        """测试总攻击力计算"""
        character = create_character(
            name="测试角色",
            health=100,
            spirit_power=50,
            consciousness=20,
        )

        # 装备基础飞剑（攻击力 +10）
        character.inventory.equip_item(character.inventory.items[0].id)

        total_attack = character.total_attack_power

        # 基础攻击力 44 + 装备 10 = 54
        assert total_attack == 54

    def test_take_damage(self):
        """测试承受伤害"""
        character = create_character(
            name="测试角色",
            health=100,
            spirit_power=50,
            consciousness=20,
        )

        # 无防御情况下
        actual_damage = character.take_damage(30)

        # 承受了 30 伤害
        assert actual_damage == 30
        assert character.attributes.health == 70

    def test_death(self):
        """测试死亡"""
        character = create_character(
            name="测试角色",
            health=100,
            spirit_power=50,
        )

        # 造成超过最大血量的伤害
        character.take_damage(200)

        assert character.is_alive is False
        assert character.state == "dead"

    def test_healing(self):
        """测试治疗"""
        character = create_character(
            name="测试角色",
            health=100,
            spirit_power=50,
        )

        # 先受伤
        character.take_damage(30)

        # 治疗
        healed = character.heal(20)

        assert healed == 20
        assert character.attributes.health == 90

    def test_detection_range(self):
        """测试探测范围"""
        character = create_character(
            name="测试角色",
            health=100,
            spirit_power=50,
            consciousness=50,  # 神识 50
        )

        # 探测范围 = 神识 * 10 = 500
        assert character.detection_range == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
