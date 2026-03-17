"""Prompt construction for group-based AI updates."""

from __future__ import annotations

import json
from typing import Any

from .audit import ALLOWED_ACTION_TYPES, ALLOWED_EVENT_TYPES
from ..character import Character


class PromptBuilder:
    """Build prompts for single-character and interaction-group updates."""

    @staticmethod
    def build_group_prompt(
        characters: list[Character],
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any],
    ) -> str:
        payload = {
            "participants": [PromptBuilder._character_payload(character) for character in characters],
            "environment": PromptBuilder._environment_payload(environment),
            "protocol": {
                "top_level_required_fields": [
                    "participants",
                    "scene_summary",
                    "scene_description",
                    "events",
                    "character_updates",
                ],
                "character_required_fields": [
                    "character_id",
                    "intent",
                    "action",
                    "basis",
                    "attribute_changes",
                    "item_changes",
                ],
                "basis_required_fields": [
                    "basis.resource_basis",
                    "basis.effect_basis",
                ],
                "allowed_action_types": sorted(ALLOWED_ACTION_TYPES),
                "allowed_event_types": sorted(ALLOWED_EVENT_TYPES),
            },
            "knowledge": {
                "treasures": PromptBuilder._filter_relevant_treasures(characters, treasures_data),
                "techniques": PromptBuilder._filter_relevant_techniques(characters, techniques_data),
            },
        }

        instructions = [
            "你必须只输出一个 JSON 对象，不要输出解释。",
            "所有角色必须统一按一个 GroupUpdate 返回；单角色也必须返回 participants 和 character_updates。",
            "participants 必须与输入角色 ID 完全一致，character_updates 必须覆盖组内全部角色且不能包含组外角色。",
            "scene_summary 是本组共享摘要，scene_description 是本组共享场景描述。",
            "events 只允许使用白名单事件类型，action.action_type 只允许使用白名单行为类型。",
            "存在显著属性变化、状态变化、物品消耗或法宝变化时，必须提供 basis.resource_basis 和 basis.effect_basis。",
            "attribute_changes 里的数值表示账本增量；item_changes.gained/lost 使用物品名到数量的映射。",
            "treasure_changes 中可以写 wear_delta、durability_delta、injected_spirit。",
        ]

        return (
            "你正在为修仙模拟器生成结构化交互组更新。\n\n"
            "输出要求:\n- " + "\n- ".join(instructions) + "\n\n"
            "输入上下文:\n"
            f"{json.dumps(payload, ensure_ascii=False, indent=2)}"
        )

    @staticmethod
    def build_single_character_prompt(
        character: Character,
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any],
    ) -> str:
        return PromptBuilder.build_group_prompt(
            [character],
            environment,
            treasures_data,
            techniques_data,
        )

    @staticmethod
    def build_multi_character_prompt(
        characters: list[Character],
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any],
    ) -> str:
        return PromptBuilder.build_group_prompt(
            characters,
            environment,
            treasures_data,
            techniques_data,
        )

    @staticmethod
    def _character_payload(character: Character) -> dict[str, Any]:
        recent_memories = [memory.content for memory in character.memory_bank.get_recent_memories(limit=5)]
        goals = [
            {
                "description": goal.description,
                "priority": goal.priority,
                "progress": goal.progress,
            }
            for goal in character.memory_bank.get_top_goals(limit=3)
        ]
        return {
            "id": character.id,
            "name": character.name,
            "realm": character.realm.full_name,
            "spirit_root": character.spirit_root.display_name,
            "attributes": {
                "hp": {
                    "current": character.attributes.hp.current,
                    "max": character.attributes.hp.max,
                },
                "mp": {
                    "current": character.attributes.mp.current,
                    "max": character.attributes.mp.max,
                },
                "spirit": {
                    "current": character.attributes.spirit.current,
                    "max": character.attributes.spirit.max,
                },
                "statuses": list(character.attributes.statuses),
            },
            "position": {
                "x": character.position.x,
                "y": character.position.y,
            },
            "inventory": character.inventory,
            "equipment": character.equipment,
            "treasure_states": character.treasure_states,
            "techniques": character.techniques,
            "recent_memories": recent_memories,
            "goals": goals,
        }

    @staticmethod
    def _environment_payload(environment: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value
            for key, value in environment.items()
            if key in {"location", "time", "cycle", "map", "scene_type", "character_positions"}
        }

    @staticmethod
    def _filter_relevant_treasures(
        characters: list[Character],
        treasures_data: dict[str, Any],
    ) -> dict[str, Any]:
        relevant_names = set()
        for character in characters:
            relevant_names.update(character.equipment.values())
            relevant_names.update(character.treasure_states.keys())
        return {
            name: treasures_data[name]
            for name in sorted(relevant_names)
            if name in treasures_data
        }

    @staticmethod
    def _filter_relevant_techniques(
        characters: list[Character],
        techniques_data: dict[str, Any],
    ) -> dict[str, Any]:
        relevant_names = set()
        for character in characters:
            relevant_names.update(character.techniques.keys())
        return {
            name: techniques_data[name]
            for name in sorted(relevant_names)
            if name in techniques_data
        }
