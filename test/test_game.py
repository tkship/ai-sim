"""简单的游戏测试脚本（不启动 pygame 窗口）。"""

import asyncio
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from src.ai import AIInterface, AuditValidator, ChangeApplier, PromptBuilder, ResponseParser
from src.character import Character, Element, MajorRealm, MinorRealm, Realm, SpiritRoot
from src.game import GameLoop, World
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
    """校验基础配置数据是否可用。"""
    treasure_repo = TreasureRepository(db)
    technique_repo = TechniqueRepository(db)

    treasures = treasure_repo.get_all()
    techniques = technique_repo.get_all()

    if not treasures:
        raise RuntimeError("未找到法宝配置，请检查 config/content/treasures.yaml")
    if not techniques:
        raise RuntimeError("未找到功法配置，请检查 config/content/techniques.yaml")

    print(f"Loaded {len(treasures)} treasures from config")
    print(f"Loaded {len(techniques)} techniques from config")


def print_section(title: str) -> None:
    """打印测试分隔标题。"""
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def make_character(
    char_id: str,
    name: str,
    *,
    hp: int = 100,
    mp: int = 60,
    spirit: int = 20,
    position: tuple[float, float] = (0, 0),
) -> Character:
    character = Character.create(char_id, name, base_hp=hp, base_mp=mp, base_spirit=spirit)
    return character.with_position(*position)


def initialize_repositories() -> tuple[dict[str, dict], dict[str, dict]]:
    db = Database()
    initialize_sample_data(db)
    treasures = {item["name"]: item for item in TreasureRepository(db).get_all()}
    techniques = {item["name"]: item for item in TechniqueRepository(db).get_all()}
    return treasures, techniques


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
            "participants": ["char_003"],
            "scene_summary": "角色试剑",
            "scene_description": "剑气纵横",
            "events": [],
            "character_updates": {
                "char_003": {
                    "intent": {"summary": "试探法宝状态", "target_ids": []},
                    "action": {"action_type": "attack", "target_ids": []},
                    "basis": {
                        "resource_basis": {},
                        "effect_basis": {"primary_effect": "法宝损耗"},
                    },
                    "attribute_changes": {},
                    "item_changes": {"gained": {}, "lost": {}},
                    "treasure_changes": [
                        {
                            "treasure_name": "玄金剑",
                            "wear_delta": -10,
                            "durability_delta": -8,
                            "injected_spirit": 12,
                        }
                    ],
                }
            },
        },
        ensure_ascii=False,
    )

    response = ResponseParser.parse(response_json)
    assert response is not None
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


def test_position_change_application() -> None:
    """测试 AI 位置变化应用。"""
    print_section("Testing Position Change Application")

    character = Character.create("char_007", "临渊").with_position(1, 2)
    response_json = json.dumps(
        {
            "participants": ["char_007"],
            "scene_summary": "角色移动",
            "scene_description": "角色向东南方向移动",
            "events": [],
            "character_updates": {
                "char_007": {
                    "intent": {"summary": "移动到更安全的位置", "target_ids": []},
                    "action": {"action_type": "move", "target_ids": []},
                    "basis": {
                        "resource_basis": {},
                        "effect_basis": {"primary_effect": "位移"},
                    },
                    "attribute_changes": {},
                    "item_changes": {"gained": {}, "lost": {}},
                    "position": {"dx": 3, "dy": -1},
                }
            },
        },
        ensure_ascii=False,
    )

    response = ResponseParser.parse(response_json)
    assert response is not None
    moved, logs = ChangeApplier.apply_to_character(character, response)
    assert moved.position.x == 4
    assert moved.position.y == 1
    assert any("位置变化" in log for log in logs)
    print("Position change application test passed!")


def test_group_response_parsing() -> None:
    """测试组级响应解析。"""
    print_section("Testing Group Response Parsing")

    single_payload = {
        "participants": ["char_010"],
        "scene_summary": "顾辰独自调息恢复灵力",
        "scene_description": "洞府内灵气回旋，顾辰稳住气机继续修炼。",
        "events": [{"type": "cultivate", "actor_id": "char_010", "description": "顾辰运转功法调息一个周天"}],
        "character_updates": {
            "char_010": {
                "intent": {"summary": "继续修炼并恢复灵力", "target_ids": []},
                "action": {"action_type": "cultivate", "target_ids": [], "technique_name": "太虚纳灵诀"},
                "basis": {
                    "resource_basis": {"mp_cost": -8, "technique_name": "太虚纳灵诀"},
                    "effect_basis": {"primary_effect": "灵力恢复", "factors": ["环境灵气平稳", "修炼状态专注"]},
                },
                "attribute_changes": {"mp_delta": 8, "status": {"add": ["入定"], "remove": []}},
                "item_changes": {"gained": {}, "lost": {}},
            }
        },
    }

    multi_payload = {
        "participants": ["char_011", "char_012"],
        "scene_summary": "两名修士短暂交锋后各自收招",
        "scene_description": "林间剑气与掌风碰撞，短促试探后双方重新拉开距离。",
        "events": [
            {"type": "clash", "actor_id": "char_011", "target_ids": ["char_012"], "description": "剑气与掌风正面碰撞"},
            {"type": "move", "actor_id": "char_012", "target_ids": ["char_011"], "description": "双方各退半步"},
        ],
        "character_updates": [
            {
                "character_id": "char_011",
                "intent": {"summary": "试探对手底细", "target_ids": ["char_012"]},
                "action": {"action_type": "attack", "target_ids": ["char_012"], "treasure_name": "玄金剑"},
                "basis": {
                    "resource_basis": {"mp_cost": 6, "treasure_costs": [{"treasure_name": "玄金剑", "wear_delta": -2}]},
                    "effect_basis": {"primary_effect": "形成试探性剑气", "result_reference": "events[0]"},
                },
                "attribute_changes": {"mp_delta": -6},
                "item_changes": {"gained": {}, "lost": {}},
            },
            {
                "character_id": "char_012",
                "intent": {"summary": "挡下攻击并拉开身位", "target_ids": ["char_011"]},
                "action": {"action_type": "defend", "target_ids": ["char_011"]},
                "basis": {
                    "resource_basis": {"mp_cost": 3},
                    "effect_basis": {"primary_effect": "化解冲击", "factors": ["借力后退"]},
                },
                "attribute_changes": {"mp_delta": -3, "status": {"add": [], "remove": []}},
                "item_changes": {"gained": {}, "lost": {}},
                "position": {"dx": -1, "dy": 0},
            },
        ],
    }

    invalid_payload = {
        "participants": ["char_013"],
        "scene_description": "角色试图突破但依据不完整。",
        "character_updates": {
            "char_013": {
                "intent": {"target_ids": []},
                "action": {"target_ids": []},
                "basis": {"effect_basis": {"primary_effect": "尝试冲击瓶颈"}},
            }
        },
    }

    single = ResponseParser.parse(json.dumps(single_payload, ensure_ascii=False))
    assert single is not None
    valid, errors = ResponseParser.validate(single)
    assert valid, errors
    assert single.participants == ["char_010"]
    assert single.character_updates["char_010"].basis.resource_basis.mp_cost == -8

    multi = ResponseParser.parse(json.dumps(multi_payload, ensure_ascii=False))
    assert multi is not None
    valid, errors = ResponseParser.validate(multi)
    assert valid, errors
    assert set(multi.character_updates.keys()) == {"char_011", "char_012"}
    assert multi.character_updates["char_011"].treasure_changes[0].treasure_name == "玄金剑"
    assert multi.character_updates["char_012"].position.dx == -1

    invalid = ResponseParser.parse(json.dumps(invalid_payload, ensure_ascii=False))
    assert invalid is not None
    valid, errors = ResponseParser.validate(invalid)
    assert not valid
    assert "缺少组级字段: scene_summary" in errors
    assert "character_updates[char_013] 缺少字段: intent.summary" in errors
    assert "character_updates[char_013] 缺少字段: action.action_type" in errors
    assert "character_updates[char_013] 缺少字段: basis.resource_basis" in errors
    print("Group response parsing test passed!")


def test_prompt_builder_protocol() -> None:
    """测试提示词声明了组协议和白名单。"""
    print_section("Testing Prompt Builder Protocol")

    treasures, techniques = initialize_repositories()
    character = make_character("char_020", "顾辰")
    character = character.equip_item("weapon", "玄金剑", treasures["玄金剑"])
    prompt = PromptBuilder.build_group_prompt(
        [character],
        {
            "location": "黑风岭",
            "time": "修真历 3842 年 3 月 7 日",
            "cycle": 1,
            "map": {"name": "黑风岭"},
            "character_positions": [],
        },
        treasures,
        techniques,
    )

    assert '"allowed_action_types"' in prompt
    assert '"allowed_event_types"' in prompt
    assert '"basis_required_fields"' in prompt
    assert '"participants"' in prompt
    print("Prompt builder protocol test passed!")


def test_audit_hard_failures() -> None:
    """测试强审计硬失败场景。"""
    print_section("Testing Audit Hard Failures")

    treasures, techniques = initialize_repositories()
    attacker = make_character("char_101", "林川", mp=20)
    defender = make_character("char_102", "苏禾", mp=20)
    attacker = attacker.add_item("回灵丹", 1).equip_item("weapon", "玄金剑", treasures["玄金剑"])

    payload = {
        "participants": ["char_101", "char_999"],
        "scene_summary": "一场混乱的交锋",
        "scene_description": "AI 返回了不可信的共享事实和资源账本。",
        "events": [
            {"type": "unknown_event", "actor_id": "char_101", "target_ids": ["char_102"], "description": "异常事件"},
            {"type": "attack", "actor_id": "char_101", "target_ids": ["char_102"], "description": "剑光掠过"},
            {"type": "attack", "actor_id": "char_101", "target_ids": ["char_102"], "description": "却又说是掌风掠过"},
        ],
        "character_updates": {
            "char_101": {
                "intent": {"summary": "猛攻", "target_ids": ["char_102"]},
                "action": {"action_type": "illegal_action", "target_ids": ["char_102"], "treasure_name": "玄金剑"},
                "basis": {
                    "resource_basis": {"mp_cost": 30},
                    "effect_basis": {"primary_effect": "造成伤害"},
                },
                "attribute_changes": {"mp_delta": -30},
                "item_changes": {"gained": {}, "lost": {"回灵丹": 2}},
            },
            "char_102": {
                "intent": {"summary": "防御", "target_ids": ["char_101"]},
                "action": {"action_type": "defend", "target_ids": ["char_101"]},
                "basis": {
                    "resource_basis": {"mp_cost": 1},
                    "effect_basis": {"primary_effect": "招架"},
                },
                "attribute_changes": {"mp_delta": -1},
                "item_changes": {"gained": {}, "lost": {}},
            },
        },
    }

    update = ResponseParser.parse(json.dumps(payload, ensure_ascii=False))
    assert update is not None
    result = AuditValidator.audit_group_update(update, [attacker, defender], treasures, techniques)

    assert not result.ok
    messages = "\n".join(result.error_messages())
    assert "组成员不一致" in messages
    assert "非法事件类型" in messages
    assert "共享事实冲突" in messages
    assert "非法行为类型" in messages
    assert "物品不足" in messages
    assert "超界过大" in messages
    print("Audit hard failures test passed!")


def test_audit_safe_clipping() -> None:
    """测试安全裁剪场景。"""
    print_section("Testing Audit Safe Clipping")

    treasures, techniques = initialize_repositories()
    character = make_character("char_201", "季衡", hp=50, mp=30, spirit=20)
    character = character.equip_item("weapon", "玄金剑", treasures["玄金剑"])
    character = character.with_attributes(
        character.attributes.with_hp_delta(-10).with_mp_delta(-5).with_spirit_delta(-3)
    )

    payload = {
        "participants": ["char_201"],
        "scene_summary": "灵力调动稍有偏差",
        "scene_description": "角色尝试催动法宝，数值略微超界后被代码安全裁剪。",
        "events": [{"type": "attack", "actor_id": "char_201", "target_ids": [], "description": "法宝鸣动"}],
        "character_updates": {
            "char_201": {
                "intent": {"summary": "催动法宝试探边界", "target_ids": []},
                "action": {"action_type": "attack", "target_ids": [], "treasure_name": "玄金剑"},
                "basis": {
                    "resource_basis": {"mp_cost": 2, "treasure_costs": [{"treasure_name": "玄金剑", "wear_delta": 5, "durability_delta": -3}]},
                    "effect_basis": {"primary_effect": "释放试探性剑气"},
                },
                "attribute_changes": {"hp_delta": 15, "mp_delta": 7, "spirit_delta": 4},
                "item_changes": {"gained": {}, "lost": {}},
                "treasure_changes": [{"treasure_name": "玄金剑", "wear_delta": 5, "durability_delta": -3, "injected_spirit": 14}],
            }
        },
    }

    update = ResponseParser.parse(json.dumps(payload, ensure_ascii=False))
    assert update is not None
    result = AuditValidator.audit_group_update(update, [character], treasures, techniques)

    assert result.ok
    clipped = {entry.path: (entry.original, entry.clipped) for entry in result.clipped_values}
    assert clipped["character_updates[char_201].attribute_changes.hp_delta"] == (15, 10)
    assert clipped["character_updates[char_201].attribute_changes.mp_delta"] == (7, 5)
    assert clipped["character_updates[char_201].attribute_changes.spirit_delta"] == (4, 3)
    assert clipped["character_updates[char_201].treasure_changes[0].wear_delta"] == (5, 0)
    assert clipped["character_updates[char_201].treasure_changes[0].injected_spirit"] == (14, 10)
    print("Audit safe clipping test passed!")


async def test_group_apply_flow() -> None:
    """测试通过审计后的组级应用与失败不落地。"""
    print_section("Testing Group Apply Flow")

    config = Config()
    game = GameLoop(config)

    attacker = make_character("char_301", "顾辰", position=(0, 0))
    defender = make_character("char_302", "白芷", position=(2, 0))
    attacker = attacker.with_attributes(attacker.attributes.with_mp_delta(-5))
    attacker = attacker.add_item("回灵丹", 1)

    game.add_character(attacker)
    game.add_character(defender)

    success_payload = {
        "participants": ["char_301", "char_302"],
        "scene_summary": "顾辰与白芷短暂切磋",
        "scene_description": "两人点到为止，顾辰消耗一枚回灵丹后气息稍稳。",
        "events": [{"type": "interact", "actor_id": "char_301", "target_ids": ["char_302"], "description": "短暂切磋后停手"}],
        "character_updates": {
            "char_301": {
                "intent": {"summary": "切磋并恢复状态", "target_ids": ["char_302"]},
                "action": {"action_type": "consume_item", "target_ids": ["char_302"], "item_name": "回灵丹"},
                "basis": {
                    "resource_basis": {"item_costs": {"回灵丹": 1}},
                    "effect_basis": {"primary_effect": "恢复部分灵力"},
                },
                "attribute_changes": {"mp_delta": 5},
                "item_changes": {"gained": {}, "lost": {"回灵丹": 1}},
            },
            "char_302": {
                "intent": {"summary": "试探后收手", "target_ids": ["char_301"]},
                "action": {"action_type": "defend", "target_ids": ["char_301"]},
                "basis": {
                    "resource_basis": {"mp_cost": 0},
                    "effect_basis": {"primary_effect": "稳住身形"},
                },
                "attribute_changes": {},
                "item_changes": {"gained": {}, "lost": {}},
            },
        },
    }

    game.ai_interface.responder = lambda prompt: json.dumps(success_payload, ensure_ascii=False)
    await game._process_ai_group(game.world.get_all_characters(), game.world.get_environment_dict(), {}, {})

    updated_attacker = game.world.get_character("char_301")
    assert updated_attacker.inventory.get("回灵丹", 0) == 0
    assert updated_attacker.attributes.mp.current == attacker.attributes.mp.current + 5
    assert any("顾辰与白芷短暂切磋" in log for log in game.world.scene_logs)
    assert any("两人点到为止" in log for log in game.world.scene_logs)

    before_logs = len(game.world.scene_logs)
    failed_payload = {
        "participants": ["char_301", "char_302"],
        "scene_summary": "异常返回",
        "scene_description": "这组结果应当被整组拒绝。",
        "events": [{"type": "interact", "actor_id": "char_301", "target_ids": ["char_302"], "description": "再次交手"}],
        "character_updates": {
            "char_301": {
                "intent": {"summary": "继续强攻", "target_ids": ["char_302"]},
                "action": {"action_type": "attack", "target_ids": ["char_302"]},
                "basis": {
                    "resource_basis": {"mp_cost": 999},
                    "effect_basis": {"primary_effect": "虚假输出"},
                },
                "attribute_changes": {"mp_delta": -999},
                "item_changes": {"gained": {}, "lost": {}},
            },
            "char_302": {
                "intent": {"summary": "防守", "target_ids": ["char_301"]},
                "action": {"action_type": "defend", "target_ids": ["char_301"]},
                "basis": {
                    "resource_basis": {"mp_cost": 0},
                    "effect_basis": {"primary_effect": "尝试防守"},
                },
                "attribute_changes": {},
                "item_changes": {"gained": {}, "lost": {}},
            },
        },
    }

    game.ai_interface.responder = lambda prompt: json.dumps(failed_payload, ensure_ascii=False)
    await game._process_ai_group(game.world.get_all_characters(), game.world.get_environment_dict(), {}, {})

    failed_attacker = game.world.get_character("char_301")
    assert failed_attacker.attributes.mp.current == updated_attacker.attributes.mp.current
    assert len(game.world.scene_logs) > before_logs
    assert any("AI审计失败" in log for log in game.world.scene_logs[before_logs:])
    print("Group apply flow test passed!")


def test_world_map_clamp() -> None:
    """测试地图边界裁剪。"""
    print_section("Testing World Map Clamp")

    config = Config()
    world = World(config)
    character = Character.create("char_008", "玄舟").with_position(9999, -9999)

    world.add_character(character)
    clamped = world.get_character("char_008")

    assert clamped.position.x == world.map.max_x
    assert clamped.position.y == world.map.min_y
    print("World map clamp test passed!")


def test_save_load_roundtrip() -> None:
    """测试存档读档回环。"""
    print_section("Testing Save/Load Roundtrip")

    config = Config()
    db = Database()
    manager = SaveManager(db, config)

    character = Character.create("char_006", "顾辰")
    character = character.with_position(42, -18)
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
    assert restored.position.x == 42
    assert restored.position.y == -18
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
        test_position_change_application()
        test_group_response_parsing()
        test_prompt_builder_protocol()
        test_audit_hard_failures()
        test_audit_safe_clipping()
        await test_group_apply_flow()
        test_world_map_clamp()
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
        raise


if __name__ == "__main__":
    asyncio.run(main())


