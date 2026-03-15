"""
简单的游戏测试脚本（不启动 pygame 窗口）
"""
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.world import Config, Database, TreasureRepository, TechniqueRepository
from src.character import (
    Character, CharacterAttributes, Attribute,
    Realm, MajorRealm, MinorRealm,
    SpiritRoot, Element,
    Position
)


def initialize_sample_data(db: Database) -> None:
    """初始化示例数据"""
    treasure_repo = TreasureRepository(db)
    technique_repo = TechniqueRepository(db)

    # 检查是否已有数据
    existing_treasures = treasure_repo.get_all()
    if existing_treasures:
        print("Sample data already exists")
        return

    print("Creating sample data...")

    # 创建示例法宝
    treasure_repo.create({
        "name": "玄金剑",
        "element": "metal",
        "type": "attack",
        "spirit_power_cost": 5,
        "attack_min": 15,
        "attack_max": 25,
        "special_effects": ["对木系敌人伤害+30%"],
        "description": "精金打造的长剑"
    })

    treasure_repo.create({
        "name": "玄铁盾",
        "element": "earth",
        "type": "defense",
        "spirit_power_cost": 3,
        "defense_min": 10,
        "defense_max": 15,
        "special_effects": [],
        "description": "厚重的铁盾"
    })

    # 创建示例功法
    technique_repo.create({
        "name": "烈阳诀",
        "element": "fire",
        "max_level": 10,
        "cultivation_speed_bonus": 0.15,
        "attack_bonus": 0.1,
        "skills": ["烈阳一击"],
        "description": "火系功法，修炼速度+15%"
    })

    print("Sample data created!")


def test_character_system():
    """测试角色系统"""
    print("\n" + "="*60)
    print("Testing Character System")
    print("="*60)

    # 创建角色
    print("\nCreating character...")
    char = Character.create(
        "char_001",
        "墨云",
        realm=Realm(MajorRealm.FOUNDATION, MinorRealm.MID),
        spirit_root=SpiritRoot.create_dual(Element.METAL, Element.FIRE)
    )

    print(f"  Name: {char.name}")
    print(f"  Realm: {char.realm.full_name}")
    print(f"  Spirit Root: {char.spirit_root.display_name}")
    print(f"  HP: {char.attributes.hp}")
    print(f"  MP: {char.attributes.mp}")
    print(f"  Spirit: {char.attributes.spirit}")

    # 测试记忆系统
    print("\nTesting memory system...")
    char.memory_bank.add_memory("初入黑风岭，四周一片寂静", importance=1)
    char.memory_bank.add_memory("似乎感受到远处有灵力波动", importance=2)
    memories = char.memory_bank.get_all_memories()
    print(f"  Added {len(memories)} memories")

    # 测试添加物品
    print("\nTesting inventory...")
    char = char.add_item("玄金剑", 1)
    char = char.add_item("回灵丹", 3)
    print(f"  Inventory: {char.inventory}")

    print("\nCharacter system test passed!")
    return char


def test_world_config():
    """测试世界配置"""
    print("\n" + "="*60)
    print("Testing World Config")
    print("="*60)

    config = Config()
    print(f"\nWorld name: {config.world.get('name')}")
    print(f"Start year: {config.world.get('start_year')}")

    realms = config.realms
    print(f"\nMajor realms config loaded")

    print("\nWorld config test passed!")


def test_database():
    """测试数据库"""
    print("\n" + "="*60)
    print("Testing Database")
    print("="*60)

    db = Database()
    initialize_sample_data(db)

    treasure_repo = TreasureRepository(db)
    treasures = treasure_repo.get_all()
    print(f"\nFound {len(treasures)} treasures")
    for t in treasures:
        print(f"  - {t['name']}")

    technique_repo = TechniqueRepository(db)
    techniques = technique_repo.get_all()
    print(f"\nFound {len(techniques)} techniques")
    for t in techniques:
        print(f"  - {t['name']}")

    print("\nDatabase test passed!")


async def main():
    """主测试函数"""
    print("="*60)
    print("Xianxia AI Simulator - Test Suite")
    print("="*60)

    try:
        test_world_config()
        test_database()
        test_character_system()

        print("\n" + "="*60)
        print("All tests passed!")
        print("="*60)
        print("\nTo run the full game with UI:")
        print("  uv run python src/main.py")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
