"""主入口模块

游戏的启动入口
"""
import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.config import load_config
from game.world import World
from game.loop import GameLoop
from ui.display import Display


def main():
    """主函数"""
    print("=" * 50)
    print("修仙 AI 模拟游戏")
    print("=" * 50)
    print()

    try:
        # 加载配置
        print("正在加载配置...")
        config = load_config("config.yaml")
        print(f"  世界名称: {config.world.name}")
        print(f"  AI 接口: {config.ai.url}")
        print(f"  使用 Mock AI: 是（测试模式）")
        print()

        # 初始化游戏世界
        print("正在初始化游戏世界...")
        world = World(config)
        print()

        # 创建初始角色
        print("正在创建角色...")
        _create_initial_characters(world)
        print()

        # 初始化游戏循环
        print("正在初始化游戏循环...")
        game_loop = GameLoop(
            world=world,
            config=config,
            use_mock_ai=True,  # 使用 Mock AI 进行测试
        )
        print()

        # 初始化界面
        print("正在初始化界面...")
        display = Display(config)

        # 设置游戏循环引用
        display.set_game_loop(game_loop)

        print()
        print("=" * 50)
        print("游戏初始化完成！")
        print("=" * 50)
        print()
        print("操作提示：")
        print("  空格键: 暂停/继续")
        print("  S 键: 单步执行")
        print("  ESC 键: 退出游戏")
        print()

        # 启动游戏
        print("正在启动游戏...")
        game_loop.start()
        display.run()

    except KeyboardInterrupt:
        print()
        print("游戏被中断")
        sys.exit(0)

    except Exception as e:
        print()
        print(f"游戏启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def _create_initial_characters(world: World):
    """创建初始角色

    Args:
        world: 游戏世界
    """
    # 角色 A: 独立，高神识（在左上角）
    char_a = world.create_random_character(
        name="李青云",
        position=(100, 100),
    )
    char_a.attributes.consciousness = 50  # 高神识，探测范围大
    char_a._update_detection_range()
    world.add_character(char_a)

    print(f"  创建角色: {char_a.name}, 境界{char_a.realm.name}")
    print(f"    位置: {char_a.position}")
    print(f"    神识: {char_a.attributes.consciousness} (探测范围: {char_a.detection_range})")

    # 角色 B: 中等属性（在中间区域）
    char_b = world.create_random_character(
        name="王清风",
        position=(300, 300),
    )
    char_b.attributes.consciousness = 30
    char_b._update_detection_range()
    world.add_character(char_b)

    print(f"  创建角色: {char_b.name}, 境界{char_b.realm.name}")
    print(f"    位置: {char_b.position}")
    print(f"    神识: {char_b.attributes.consciousness} (探测范围: {char_b.detection_range})")

    # 角色 C: 中等属性（能与角色 B 交互）
    char_c = world.create_random_character(
        name="张明月",
        position=(350, 320),
    )
    char_c.attributes.consciousness = 30
    char_c._update_detection_range()
    world.add_character(char_c)

    print(f"  创建角色: {char_c.name}, 境界{char_c.realm.name}")
    print(f"    位置: {char_c.position}")
    print(f"    神识: {char_c.attributes.consciousness} (探测范围: {char_c.detection_range})")

    # 角色 D: 中等属性（能与角色 B、C 交互）
    char_d = world.create_random_character(
        name="刘长风",
        position=(320, 280),
    )
    char_d.attributes.consciousness = 30
    char_d._update_detection_range()
    world.add_character(char_d)

    print(f"  创建角色: {char_d.name}, 境界{char_d.realm.name}")
    print(f"    位置: {char_d.position}")
    print(f"    神识: {char_d.attributes.consciousness} (探测范围: {char_d.detection_range})")


if __name__ == "__main__":
    main()
