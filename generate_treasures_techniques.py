#!/usr/bin/env python3
"""
生成新的法宝和功法数据并添加到数据库
"""

import json
from src.world.database import Database
from src.world.repository import TreasureRepository, TechniqueRepository


def generate_new_treasures():
    """生成10个新的法宝"""
    return [
        {
            "name": "金虹剑",
            "element": "metal",
            "type": "attack",
            "spirit_power_cost": 25,
            "realm_required": "foundation",
            "attack_min": 80,
            "attack_max": 120,
            "defense_min": 10,
            "defense_max": 20,
            "spirit_bonus": 5,
            "special_effects": ["金灵剑气：攻击时有30%概率额外造成20%金属性伤害", "破甲：无视目标10%防御"],
            "description": "由千年玄金精炼而成的飞剑，剑身上流转着金色虹光，锋利无比，擅长破甲攻击。"
        },
        {
            "name": "青木盾",
            "element": "wood",
            "type": "defense",
            "spirit_power_cost": 20,
            "realm_required": "foundation",
            "attack_min": 5,
            "attack_max": 15,
            "defense_min": 60,
            "defense_max": 90,
            "hp_bonus": 100,
            "special_effects": ["木灵守护：每回合恢复5点生命值", "生生不息：受到攻击时有20%概率触发木灵盾吸收伤害"],
            "description": "以万年青木之心打造的盾牌，蕴含浓郁的木灵之气，不仅防御力强，还能自动恢复生命值。"
        },
        {
            "name": "碧水葫芦",
            "element": "water",
            "type": "support",
            "spirit_power_cost": 15,
            "realm_required": "qi_refining",
            "hp_bonus": 80,
            "mp_bonus": 50,
            "speed_bonus": 0.1,
            "special_effects": ["碧水精华：每回合恢复10点灵力", "净化：解除自身1个负面状态"],
            "description": "可储存无尽碧水的神奇葫芦，能持续提供灵力支持，并能净化体内的负面效果。"
        },
        {
            "name": "烈火幡",
            "element": "fire",
            "type": "attack",
            "spirit_power_cost": 30,
            "realm_required": "foundation",
            "attack_min": 90,
            "attack_max": 130,
            "defense_min": 5,
            "defense_max": 15,
            "special_effects": ["烈火燎原：攻击时有25%概率造成持续烧伤效果", "火灵爆发：消耗50点灵力，攻击力翻倍"],
            "description": "由火焰精金编织而成的幡旗，挥动时烈火焚天，具有极强的火焰攻击力和燃烧效果。"
        },
        {
            "name": "厚土印",
            "element": "earth",
            "type": "defense",
            "spirit_power_cost": 28,
            "realm_required": "foundation",
            "attack_min": 10,
            "attack_max": 25,
            "defense_min": 80,
            "defense_max": 120,
            "hp_bonus": 150,
            "special_effects": ["厚土守护：受到攻击时减少20%伤害", "地脉之力：每回合恢复10点防御力"],
            "description": "蕴含大地厚重之力的印章，防御如山，能大幅提升自身的生存能力。"
        },
        {
            "name": "雷光镜",
            "element": "metal",
            "type": "attack",
            "spirit_power_cost": 35,
            "realm_required": "golden_core",
            "attack_min": 120,
            "attack_max": 160,
            "defense_min": 20,
            "defense_max": 35,
            "special_effects": ["雷光斩：攻击时有35%概率触发雷电伤害", "电光火石：攻击速度提升20%"],
            "description": "上古雷属性法宝，镜面上雷光闪烁，能释放毁灭性的雷电攻击，速度极快。"
        },
        {
            "name": "生命之树",
            "element": "wood",
            "type": "support",
            "spirit_power_cost": 25,
            "realm_required": "golden_core",
            "hp_bonus": 200,
            "mp_bonus": 80,
            "spirit_bonus": 10,
            "special_effects": ["生命源泉：每回合恢复15点生命值", "木灵祝福：提升队友20%防御力"],
            "description": "蕴含生命精华的迷你神树，能为整个队伍提供强大的生命支持和防御加成。"
        },
        {
            "name": "玄冰玉佩",
            "element": "water",
            "type": "defense",
            "spirit_power_cost": 22,
            "realm_required": "foundation",
            "attack_min": 15,
            "attack_max": 30,
            "defense_min": 70,
            "defense_max": 100,
            "speed_bonus": 0.08,
            "special_effects": ["玄冰护盾：受到攻击时有25%概率冻结攻击者", "冰寒气息：降低周围敌人15%攻击速度"],
            "description": "由极寒玄冰雕琢而成的玉佩，佩戴后周身环绕冰寒气息，既能防御又能控制敌人。"
        },
        {
            "name": "神火珠",
            "element": "fire",
            "type": "attack",
            "spirit_power_cost": 40,
            "realm_required": "golden_core",
            "attack_min": 140,
            "attack_max": 180,
            "defense_min": 15,
            "defense_max": 25,
            "special_effects": ["神火焚天：攻击时有30%概率造成范围伤害", "火焰净化：燃烧敌人的灵力，每回合消耗5点"],
            "description": "蕴含太阳真火的宝珠，释放时神火漫天，具有极强的范围攻击和灵力消耗效果。"
        },
        {
            "name": "戊土战甲",
            "element": "earth",
            "type": "defense",
            "spirit_power_cost": 32,
            "realm_required": "golden_core",
            "attack_min": 20,
            "attack_max": 40,
            "defense_min": 100,
            "defense_max": 150,
            "hp_bonus": 250,
            "special_effects": ["戊土之躯：免疫所有控制效果", "大地之力：每3回合恢复30点生命值"],
            "description": "由戊土精华凝聚而成的战甲，如同大地般稳固，提供极强的防御力和生存能力。"
        }
    ]


def generate_new_techniques():
    """生成10个新的功法"""
    return [
        {
            "name": "金罡剑诀",
            "element": "metal",
            "realm_required": "qi_refining",
            "max_level": 15,
            "attack_bonus": 0.25,
            "defense_bonus": 0.05,
            "cultivation_speed_bonus": 0.08,
            "breakthrough_bonus": 0.1,
            "skills": ["金灵剑气", "破甲一击", "金罡护体"],
            "description": "金属性基础剑诀，注重攻击力和破甲效果，修炼到高层能以剑气护体。"
        },
        {
            "name": "青木长生诀",
            "element": "wood",
            "realm_required": "qi_refining",
            "max_level": 15,
            "attack_bonus": 0.05,
            "defense_bonus": 0.15,
            "cultivation_speed_bonus": 0.12,
            "breakthrough_bonus": 0.15,
            "skills": ["木灵恢复", "长生真气", "神木壁垒"],
            "description": "木属性养生功法，修炼后能大幅提升生命力和恢复能力，适合持久战。"
        },
        {
            "name": "碧水神功",
            "element": "water",
            "realm_required": "foundation",
            "max_level": 20,
            "attack_bonus": 0.15,
            "defense_bonus": 0.1,
            "cultivation_speed_bonus": 0.1,
            "breakthrough_bonus": 0.12,
            "skills": ["碧水潮生", "水柔剑法", "冰寒真气"],
            "description": "水属性高级功法，招式柔中带刚，能灵活变化，擅长控制和反击。"
        },
        {
            "name": "烈火焚天诀",
            "element": "fire",
            "realm_required": "foundation",
            "max_level": 20,
            "attack_bonus": 0.3,
            "defense_bonus": 0.08,
            "cultivation_speed_bonus": 0.09,
            "breakthrough_bonus": 0.1,
            "skills": ["烈火烧身", "火焰刀", "焚天烈焰"],
            "description": "火属性攻击功法，招式霸道凌厉，能释放熊熊烈焰，造成毁灭性的伤害。"
        },
        {
            "name": "厚土心法",
            "element": "earth",
            "realm_required": "qi_refining",
            "max_level": 15,
            "attack_bonus": 0.08,
            "defense_bonus": 0.25,
            "cultivation_speed_bonus": 0.07,
            "breakthrough_bonus": 0.18,
            "skills": ["厚土壁", "大地之力", "泰山压顶"],
            "description": "土属性防御功法，修炼后身躯如同大地般稳固，能承受极强的攻击。"
        },
        {
            "name": "雷动九天诀",
            "element": "metal",
            "realm_required": "golden_core",
            "max_level": 25,
            "attack_bonus": 0.4,
            "defense_bonus": 0.15,
            "cultivation_speed_bonus": 0.1,
            "breakthrough_bonus": 0.12,
            "skills": ["雷光斩", "雷电护盾", "雷动九天"],
            "description": "高级雷属性功法，能引九天雷电之力，攻击力极强，速度极快。"
        },
        {
            "name": "枯木逢春功",
            "element": "wood",
            "realm_required": "golden_core",
            "max_level": 25,
            "attack_bonus": 0.15,
            "defense_bonus": 0.25,
            "cultivation_speed_bonus": 0.18,
            "breakthrough_bonus": 0.2,
            "skills": ["枯木禅", "生机焕发", "春回大地"],
            "description": "木属性顶级功法，不仅能大幅提升生命力，还能在绝境中恢复生机。"
        },
        {
            "name": "玄冥真水诀",
            "element": "water",
            "realm_required": "golden_core",
            "max_level": 25,
            "attack_bonus": 0.25,
            "defense_bonus": 0.2,
            "cultivation_speed_bonus": 0.15,
            "breakthrough_bonus": 0.18,
            "skills": ["玄冥寒气", "真水剑法", "冰封万里"],
            "description": "水属性顶级功法，能操纵玄冥真水，冰封一切，既有强大的攻击力又有控制能力。"
        },
        {
            "name": "太阳真火功",
            "element": "fire",
            "realm_required": "golden_core",
            "max_level": 25,
            "attack_bonus": 0.45,
            "defense_bonus": 0.12,
            "cultivation_speed_bonus": 0.1,
            "breakthrough_bonus": 0.1,
            "skills": ["真火护体", "太阳剑气", "天火燎原"],
            "description": "火属性顶级功法，修炼到极致能掌控太阳真火，焚天灭地，无人能敌。"
        },
        {
            "name": "大地乾坤诀",
            "element": "earth",
            "realm_required": "golden_core",
            "max_level": 25,
            "attack_bonus": 0.2,
            "defense_bonus": 0.4,
            "cultivation_speed_bonus": 0.1,
            "breakthrough_bonus": 0.25,
            "skills": ["乾坤挪移", "大地守护", "泰山镇岳"],
            "description": "土属性顶级功法，能掌控大地之力，防御力极强，还能改变地形。"
        }
    ]


def main():
    """主函数"""
    # 初始化数据库和仓库
    db = Database("/home/aiuser/ai-sim/game.db")
    treasure_repo = TreasureRepository(db)
    technique_repo = TechniqueRepository(db)

    # 生成新的法宝
    treasures = generate_new_treasures()
    print("正在添加新法宝...")
    for treasure in treasures:
        # 检查是否已存在
        existing = treasure_repo.get_by_name(treasure["name"])
        if existing:
            print(f"法宝 '{treasure['name']}' 已存在，跳过...")
            continue
        try:
            treasure_repo.create(treasure)
            print(f"成功添加法宝: {treasure['name']}")
        except Exception as e:
            print(f"添加法宝 '{treasure['name']}' 失败: {e}")

    # 生成新的功法
    techniques = generate_new_techniques()
    print("\n正在添加新功法...")
    for technique in techniques:
        # 检查是否已存在
        existing = technique_repo.get_by_name(technique["name"])
        if existing:
            print(f"功法 '{technique['name']}' 已存在，跳过...")
            continue
        try:
            technique_repo.create(technique)
            print(f"成功添加功法: {technique['name']}")
        except Exception as e:
            print(f"添加功法 '{technique['name']}' 失败: {e}")

    print("\n所有法宝和功法已成功添加！")

    # 验证添加结果
    print(f"\n法宝总数: {len(treasure_repo.get_all())}")
    print(f"功法总数: {len(technique_repo.get_all())}")


if __name__ == "__main__":
    main()
