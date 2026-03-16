"""
修仙 AI 模拟器 - 主程序入口
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.world import Config, Database, TreasureRepository, TechniqueRepository
from src.character import (
    Character, CharacterAttributes, Attribute,
    Realm, MajorRealm, MinorRealm,
    SpiritRoot, Element,
    Position
)
from src.game import GameLoop


def initialize_sample_data(db: Database, config: Optional[Config] = None) -> None:
    """初始化示例数据"""
    treasure_repo = TreasureRepository(db)
    technique_repo = TechniqueRepository(db)

    # 检查是否已有数据
    existing_treasures = treasure_repo.get_all()
    if existing_treasures:
        return

    template_treasures = []
    template_techniques = []
    if config:
        template_treasures = config.get("templates.treasures", []) or []
        template_techniques = config.get("templates.techniques", []) or []

    if not template_treasures:
        template_treasures = [
            {
                "name": "玄金剑",
                "element": "metal",
                "type": "attack",
                "spirit_power_cost": 5,
                "attack_min": 15,
                "attack_max": 25,
                "special_effects": ["对木系敌人伤害+30%"],
                "description": "精金打造的长剑"
            },
            {
                "name": "玄铁盾",
                "element": "earth",
                "type": "defense",
                "spirit_power_cost": 3,
                "defense_min": 10,
                "defense_max": 15,
                "special_effects": [],
                "description": "厚重的铁盾"
            },
            {
                "name": "聚灵佩",
                "element": None,
                "type": "support",
                "mp_bonus": 20,
                "special_effects": ["灵力恢复速度+10%"],
                "description": "辅助修炼的玉佩"
            },
        ]

    if not template_techniques:
        template_techniques = [
            {
                "name": "烈阳诀",
                "element": "fire",
                "max_level": 10,
                "cultivation_speed_bonus": 0.15,
                "attack_bonus": 0.1,
                "skills": ["烈阳一击"],
                "description": "火系功法，修炼速度+15%"
            },
            {
                "name": "金锋剑诀",
                "element": "metal",
                "max_level": 10,
                "attack_bonus": 0.2,
                "skills": ["金锋斩"],
                "description": "金系剑法，剑类法宝伤害+20%"
            },
        ]

    for treasure in template_treasures:
        treasure_repo.create(treasure)
    for technique in template_techniques:
        technique_repo.create(technique)


def create_sample_characters(game: GameLoop) -> None:
    """创建示例角色"""
    # 角色 1: 墨云
    char1 = Character.create(
        "char_001",
        "墨云",
        realm=Realm(MajorRealm.FOUNDATION, MinorRealm.MID),
        spirit_root=SpiritRoot.create_dual(Element.METAL, Element.FIRE)
    )

    # 添加记忆
    char1.memory_bank.add_memory("初入黑风岭，四周一片寂静", importance=1)
    char1.memory_bank.add_memory("似乎感受到远处有灵力波动", importance=2)

    # 添加目标
    char1.memory_bank.add_goal("寻找修炼资源", priority=8)
    char1.memory_bank.add_goal("突破到筑基后期", priority=10)

    # 添加物品
    char1 = char1.add_item("玄金剑", 1)
    char1 = char1.add_item("玄铁盾", 1)
    char1 = char1.add_item("聚灵佩", 1)
    char1 = char1.add_item("回灵丹", 3)
    char1 = char1.add_item("金疮药", 2)
    char1 = char1.add_item("下品灵石", 45)

    # 装备
    char1 = char1.equip_item("weapon", "玄金剑")
    char1 = char1.equip_item("armor", "玄铁盾")
    char1 = char1.equip_item("accessory1", "聚灵佩")

    # 功法（通过灵根兼容性校验）
    char1, _, _ = char1.learn_technique("烈阳诀", level=3, technique_elements=["fire"])
    char1, _, _ = char1.learn_technique("金锋剑诀", level=2, technique_elements=["metal"])

    # 设置位置
    char1 = char1.with_position(0, 0)

    game.add_character(char1)

    # 角色 2: 张烈
    char2 = Character.create(
        "char_002",
        "张烈",
        realm=Realm(MajorRealm.FOUNDATION, MinorRealm.EARLY),
        spirit_root=SpiritRoot.create_dual(Element.WATER, Element.EARTH)
    )

    char2.memory_bank.add_memory("刚经历一场战斗，灵力消耗不少", importance=3)
    char2.memory_bank.add_memory("需要找个地方疗伤", importance=4)

    char2.memory_bank.add_goal("找到安全的地方疗伤", priority=10)

    char2 = char2.add_item("血煞刀", 1)
    char2 = char2.add_item("疗伤丹", 1)
    char2 = char2.add_item("爆灵丹", 1)
    char2 = char2.add_item("下品灵石", 23)

    char2 = char2.equip_item("weapon", "血煞刀")

    # 设置位置（在墨云附近）
    char2 = char2.with_position(30, 10)

    game.add_character(char2)


async def main():
    """主函数"""
    print("=" * 60)
    print("修仙 AI 模拟器")
    print("=" * 60)
    print()

    # 加载配置
    print("加载配置...")
    config = Config()

    # 初始化数据库
    print("初始化数据库...")
    db = Database()

    # 初始化示例数据
    print("加载游戏数据...")
    initialize_sample_data(db, config)

    # 创建游戏循环
    print("初始化游戏...")
    game = GameLoop(config)

    # 创建示例角色
    create_sample_characters(game)

    # 初始化 UI
    print("初始化 UI...")
    game.init_ui()

    # 添加启动日志
    game.world.add_scene_log("欢迎来到修仙世界！")
    game.world.add_scene_log("按 ESC 或关闭窗口退出游戏。")

    print("游戏开始！")
    print()

    # 运行游戏
    await game.run()

    print()
    print("游戏已退出。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n游戏已中断。")
    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()
