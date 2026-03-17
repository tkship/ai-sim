"""
AI 提示词构建模块
"""
from typing import Any
from ..character import Character


class PromptBuilder:
    """提示词构建器"""

    @staticmethod
    def build_single_character_prompt(
        character: Character,
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any]
    ) -> str:
        """
        构建单角色场景的提示词

        Args:
            character: 角色对象
            environment: 环境信息
            treasures_data: 法宝详细数据
            techniques_data: 功法详细数据

        Returns:
            完整提示词
        """
        lines = []
        lines.append(f"{'=' * 40} {character.name} 信息 {'=' * 40}")
        lines.append("")

        # 角色基础信息
        lines.append("【角色信息】")
        lines.append(f"姓名：{character.name}")
        lines.append(f"境界：{character.realm.full_name}")
        lines.append(f"灵根：{character.spirit_root.display_name}")
        lines.append("")
        lines.append("当前状态：")
        lines.append(f"- 血量：{character.attributes.hp}")
        lines.append(f"- 灵力：{character.attributes.mp}")
        lines.append(f"- 神识：{character.attributes.spirit}")
        lines.append(f"- 坐标：({character.position.x:.1f}, {character.position.y:.1f})")
        if character.attributes.statuses:
            lines.append(f"- 状态：{', '.join(character.attributes.statuses)}")
        else:
            lines.append("- 状态：正常")
        lines.append("")

        # 功法
        if character.techniques:
            lines.append("【功法】")
            for tech_name, level in character.techniques.items():
                tech_data = techniques_data.get(tech_name, {})
                tech_desc = tech_data.get("description", "")
                lines.append(f"- {tech_name}（第 {level} 层）{tech_desc}")
            lines.append("")

        # 装备法宝
        if character.equipment:
            lines.append("【法宝装备】")
            for slot, treasure_name in character.equipment.items():
                treasure_data = treasures_data.get(treasure_name)
                if treasure_data:
                    treasure_state = character.treasure_states.get(treasure_name, {})
                    lines.append(f"{slot}: {treasure_name}")
                    lines.append(f"   - 基础攻击：{treasure_data.get('attack_min', 0)}-{treasure_data.get('attack_max', 0)}")
                    lines.append(f"   - 当前损耗度：{treasure_state.get('wear', treasure_data.get('wear', 100))}/100")
                    lines.append(
                        "   - 当前注入灵力："
                        f"{treasure_state.get('injected_spirit', treasure_data.get('injected_spirit', 0))}/"
                        f"{treasure_state.get('max_injected_spirit', treasure_data.get('max_injected_spirit', 20))}"
                    )
            lines.append("")

        # 物品栏
        if character.inventory:
            lines.append("【物品栏】")
            for item_name, count in character.inventory.items():
                lines.append(f"- {item_name} × {count}")
            lines.append("")

        # 记忆
        recent_memories = character.memory_bank.get_recent_memories(limit=5)
        important_memories = character.memory_bank.get_important_memories(limit=5)
        all_memories = {m.id: m for m in recent_memories + important_memories}.values()

        if all_memories:
            lines.append("【记忆/经历】")
            for mem in sorted(all_memories, key=lambda m: m.timestamp, reverse=True):
                lines.append(f"- {mem.content}")
            lines.append("")

        # 目标
        top_goals = character.memory_bank.get_top_goals(limit=3)
        if top_goals:
            lines.append("【长期目标】")
            for goal in top_goals:
                progress_pct = int(goal.progress * 100)
                lines.append(f"- {goal.description}（进度：{progress_pct}%，优先级：{goal.priority}）")
            lines.append("")

        # 环境信息
        lines.append("【当前环境】")
        if "location" in environment:
            lines.append(f"【地点】{environment['location']}")
        if "time" in environment:
            lines.append(f"【时间】{environment['time']}")
        if "map" in environment:
            map_data = environment["map"]
            lines.append(
                f"【地图】{map_data.get('name', '')} "
                f"范围 x:[{map_data.get('min_x')}, {map_data.get('max_x')}] "
                f"y:[{map_data.get('min_y')}, {map_data.get('max_y')}]"
            )
        if "scene_type" in environment:
            lines.append(f"【场景类型】{environment['scene_type']}")
        for key, value in environment.items():
            if key not in ["location", "time", "scene_type", "map", "character_positions"]:
                lines.append(f"- {key}：{value}")

        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        lines.append("请基于以上信息，决定角色接下来的行动。")
        lines.append("")

        return "\n".join(lines)

    @staticmethod
    def build_multi_character_prompt(
        characters: list[Character],
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any]
    ) -> str:
        """
        构建多角色交互场景的提示词

        Args:
            characters: 角色列表
            environment: 环境信息
            treasures_data: 法宝详细数据
            techniques_data: 功法详细数据

        Returns:
            完整提示词
        """
        lines = []

        for i, character in enumerate(characters):
            lines.append(f"{'=' * 40} {character.name} 信息 {'=' * 40}")
            lines.append("")
            lines.append("【基础信息】")
            lines.append(f"姓名：{character.name}")
            lines.append(f"境界：{character.realm.full_name}")
            lines.append(f"灵根：{character.spirit_root.display_name}")
            lines.append("")
            lines.append("【当前状态】")
            lines.append(f"- 血量：{character.attributes.hp}")
            lines.append(f"- 灵力：{character.attributes.mp}")
            lines.append(f"- 神识：{character.attributes.spirit}")
            lines.append(f"- 坐标：({character.position.x:.1f}, {character.position.y:.1f})")
            if character.attributes.statuses:
                lines.append(f"- 状态：{', '.join(character.attributes.statuses)}")
            lines.append("")

            if i == 0:
                # 只对第一个角色显示完整信息
                if character.inventory:
                    lines.append("【物品栏】")
                    for item_name, count in character.inventory.items():
                        lines.append(f"- {item_name} × {count}")
                    lines.append("")

                recent_memories = character.memory_bank.get_recent_memories(limit=5)
                if recent_memories:
                    lines.append("【记忆/战斗认知】")
                    for mem in recent_memories:
                        lines.append(f"- {mem.content}")
                    lines.append("")

        lines.append("=" * 90)
        lines.append("")
        lines.append("【当前环境】")
        if "location" in environment:
            lines.append(f"【地点】{environment['location']}")
        if "time" in environment:
            lines.append(f"【时间】{environment['time']}")
        if "map" in environment:
            map_data = environment["map"]
            lines.append(
                f"【地图】{map_data.get('name', '')} "
                f"范围 x:[{map_data.get('min_x')}, {map_data.get('max_x')}] "
                f"y:[{map_data.get('min_y')}, {map_data.get('max_y')}]"
            )
        for key, value in environment.items():
            if key not in ["location", "time", "map", "character_positions"]:
                lines.append(f"- {key}：{value}")
        lines.append("")
        lines.append("=" * 90)
        lines.append("")
        lines.append("请基于以上角色的状态，输出他们接下来的行动和结果。")
        lines.append("")

        return "\n".join(lines)
