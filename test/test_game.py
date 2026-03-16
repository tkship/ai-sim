"""简单的游戏测试脚本（不启动 pygame 窗口）。"""

import asyncio
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.ai import ChangeApplier, ResponseParser
from src.character import Character, Element, MajorRealm, MinorRealm, Realm, SpiritRoot
from src.item import Pill
from src.world import (
    Config,
    Database,
    GameState,
    SaveManager,
    TechniqueRepository,
    TreasureRepository,
)


def initialize_sample_data(db: Database) -> None:
    """初始化示例数据。"""
    treasure_repo = TreasureRepository(db)
    technique_repo = TechniqueRepository(db)

    if treasure_repo.get_all():
        print("Sample data already exists")
        return

    print("Creating sample data...")

    treasure_repo.create(
        {
            "name": "玄金剑",
            "element": "metal",
            "type": "attack",
            "spirit_power_cost": 5,
            "attack_min": 15,
            "attack_max": 25,
            "special_effects": ["对木系敌人伤害+30%"],
            "description": "精金打造的长剑",
        }
    )

    treasure_repo.create(
        {
            "name": "玄铁盾",
            "element": "earth",
            "type": "defense",
            "spirit_power_cost": 3,
            "defense_min": 10,
            "defense_max": 15,
            "special_effects": [],
            "description": "厚重的铁盾",
        }
    )

    technique_repo.create(
        {
            "name": "烈阳诀",
            "element": "fire",
            "max_level": 10,
            "cultivation_speed_bonus": 0.15,
            "attack_bonus": 0.1,
            "skills": ["烈阳一击"],
            "description": "火系功法，修炼速度+15%",
        }
    )

    print("Sample data created!")


def print_section(title: str) -> None:
    """打印测试分隔标题。"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def test_character_system() -> Character:
    """测试角色系统。"""
    print_section("Testing Character System")

    print("\nCreating character...")
    character = Character.create(
        "char_001",
        "墨云",
        realm=Realm(MajorRealm.FOUNDATION, MinorRealm.MID),
        spirit_root=SpiritRoot.create_dual(Element.METAL, Element.FIRE),
    )

    print(f"  Name: {character.name}")
    print(f"  Realm: {character.realm.full_name}")
    print(f"  Spirit Root: {character.spirit_root.display_name}")
    print(f"  HP: {character.attributes.hp}")
    print(f"  MP: {character.attributes.mp}")
    print(f"  Spirit: {character.attributes.spirit}")

    print("\nTesting memory system...")
    character.memory_bank.add_memory("初入黑风岭，四周一片寂静", importance=1)
    character.memory_bank.add_memory("似乎感受到远处有灵力波动", importance=2)
    memories = character.memory_bank.get_all_memories()
    print(f"  Added {len(memories)} memories")

    print("\nTesting inventory...")
    character = character.add_item("玄金剑", 1)
    character = character.add_item("回灵丹", 3)
    print(f"  Inventory: {character.inventory}")

    print("\nCharacter system test passed!")
    return character


def test_world_config() -> None:
    """测试世界配置。"""
    print_section("Testing World Config")

    config = Config()
    print(f"\nWorld name: {config.world.get('name')}")
    print(f"Start year: {config.world.get('start_year')}")
    print("\nMajor realms config loaded")
    print("\nWorld config test passed!")


def test_database() -> None:
    """测试数据库。"""
    print_section("Testing Database")

    db = Database()
    initialize_sample_data(db)

    treasure_repo = TreasureRepository(db)
    treasures = treasure_repo.get_all()
    print(f"\nFound {len(treasures)} treasures")
    for treasure in treasures:
        print(f"  - {treasure['name']}")

    technique_repo = TechniqueRepository(db)
    techniques = technique_repo.get_all()
    print(f"\nFound {len(techniques)} techniques")
    for technique in techniques:
        print(f"  - {technique['name']}")

    print("\nDatabase test passed!")


def test_ai_treasure_change_application() -> None:
    """测试 AI 法宝变化应用。"""
    print_section("Testing AI Treasure Change Application")

    character = Character.create(
        "char_003",
        "凌川",
        realm=Realm(MajorRealm.FOUNDATION, MinorRealm.EARLY),
        spirit_root=SpiritRoot.create_single(Element.METAL),
    )
    character = character.equip_item(
        "weapon",
        "玄金剑",
        {
            "durability": 100,
            "max_durability": 100,
            "max_injected_spirit": 20,
        },
    )

    response_json = json.dumps(
        {
            "交互概述": "角色试剑",
            "场景描述": "剑气纵横",
            "属性变化": {
                "char_003": {
                    "法宝变化": [
                        {
                            "法宝名称": "玄金剑",
                            "损耗度变化": -10,
                            "耐久度变化": -8,
                            "当前注入灵力": 12,
                        }
                    ]
                }
            },
        },
        ensure_ascii=False,
    )

    response = ResponseParser.parse(response_json)
    new_character, logs = ChangeApplier.apply_to_character(character, response)
    state = new_character.treasure_states.get("玄金剑", {})

    assert state.get("wear") == 90
    assert state.get("durability") == 92
    assert state.get("injected_spirit") == 12
    assert logs, "Treasure change logs should exist"
    print("AI treasure change application test passed!")


def test_spirit_root_technique_constraint() -> None:
    """测试灵根功法约束。"""
    print_section("Testing Spirit Root Technique Constraint")

    metal_character = Character.create(
        "char_004",
        "青岳",
        spirit_root=SpiritRoot.create_single(Element.METAL),
    )

    _, ok_fire, _ = metal_character.learn_technique(
        "烈阳诀", technique_elements=["fire"]
    )
    assert not ok_fire, "Metal-only spirit root should not learn fire technique"

    _, ok_metal, _ = metal_character.learn_technique(
        "金锋剑诀", technique_elements=["metal"]
    )
    assert ok_metal, "Metal-only spirit root should learn metal technique"
    print("Spirit root constraint test passed!")


def test_pill_consumption() -> None:
    """测试丹药服用效果。"""
    print_section("Testing Pill Consumption")

    character = Character.create("char_005", "白芷")
    character = character.add_item("破境丹", 1)
    pill = Pill.create_breakthrough("破境丹", 0.25)

    new_character, logs = character.consume_pill("破境丹", pill)

    assert "破境丹" not in new_character.inventory
    assert new_character.breakthrough_bonus > character.breakthrough_bonus
    assert logs
    print("Pill consumption test passed!")


def test_save_load_roundtrip() -> None:
    """测试存档读档回环。"""
    print_section("Testing Save/Load Roundtrip")

    config = Config()
    db = Database()
    manager = SaveManager(db, config)

    character = Character.create("char_006", "顾辰")
    character = character.add_item("下品灵石", 20)

    state = GameState()
    state.current_year = 4000
    state.current_month = 1
    state.current_day = 2
    state.cycle_count = 99
    state.characters = {character.id: character.to_save_dict()}

    assert manager.save_game(state, slot=99)
    loaded = manager.load_game(slot=99)
    assert loaded is not None
    assert loaded.current_year == 4000
    assert "char_006" in loaded.characters

    restored = Character.from_save_dict(loaded.characters["char_006"])
    assert restored.inventory.get("下品灵石") == 20
    print("Save/load roundtrip test passed!")


async def main() -> None:
    """主测试函数。"""
    print("=" * 60)
    print("Xianxia AI Simulator - Test Suite")
    print("=" * 60)

    try:
        test_world_config()
        test_database()
        test_character_system()
        test_ai_treasure_change_application()
        test_spirit_root_technique_constraint()
        test_pill_consumption()
        test_save_load_roundtrip()

        print("\n" + "=" * 60)
        print("All tests passed!")
        print("=" * 60)
        print("\nTo run the full game with UI:")
        print("  uv run python src/main.py")

    except Exception as exc:
        print(f"\nError: {exc}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
