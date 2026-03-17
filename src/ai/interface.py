"""AI orchestration, auditing, and audited change application."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Callable

from ..character import Character
from .audit import AuditResult, AuditValidator
from .parser import AIResponse, ResponseParser
from .prompt import PromptBuilder


@dataclass
class GroupProcessResult:
    response: AIResponse | None
    audit_result: AuditResult | None
    updated_characters: list[Character]
    character_logs: dict[str, list[str]] = field(default_factory=dict)


class AIInterface:
    """Minimal AI client abstraction."""

    def __init__(
        self,
        api_url: str = "",
        api_key: str = "",
        model: str = "",
        responder: Callable[[str], str] | None = None,
    ):
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.responder = responder

    async def request_decision(self, prompt: str) -> AIResponse | None:
        """Request one group update from the AI."""
        if self.responder is not None:
            return ResponseParser.parse(self.responder(prompt))

        mock_response = {
            "participants": ["char_001"],
            "scene_summary": "角色选择继续修炼",
            "scene_description": "角色闭目打坐，运转功法继续调息。",
            "events": [
                {
                    "type": "cultivate",
                    "actor_id": "char_001",
                    "description": "角色平稳运转功法。",
                }
            ],
            "character_updates": {
                "char_001": {
                    "intent": {
                        "summary": "继续修炼并恢复部分灵力",
                        "target_ids": [],
                    },
                    "action": {
                        "action_type": "cultivate",
                        "target_ids": [],
                    },
                    "basis": {
                        "resource_basis": {
                            "mp_cost": -5,
                        },
                        "effect_basis": {
                            "primary_effect": "恢复少量灵力",
                        },
                    },
                    "attribute_changes": {
                        "mp_delta": 5,
                        "status": {
                            "add": [],
                            "remove": [],
                        },
                    },
                    "item_changes": {
                        "gained": {},
                        "lost": {},
                    },
                }
            },
        }
        return ResponseParser.parse(json.dumps(mock_response, ensure_ascii=False))


class ChangeApplier:
    """Apply already-audited group updates to characters."""

    @staticmethod
    def apply_group_update(
        characters: list[Character],
        response: AIResponse,
    ) -> tuple[list[Character], dict[str, list[str]]]:
        new_characters: list[Character] = []
        all_logs: dict[str, list[str]] = {}

        for character in characters:
            new_character, logs = ChangeApplier.apply_to_character(character, response)
            new_characters.append(new_character)
            if logs:
                all_logs[character.id] = logs

        return new_characters, all_logs

    @staticmethod
    def apply_to_character(
        character: Character,
        response: AIResponse,
    ) -> tuple[Character, list[str]]:
        logs: list[str] = []
        char_update = response.character_updates.get(character.id)
        if char_update is None:
            for update in response.character_updates.values():
                if update.character_id == character.name:
                    char_update = update
                    break
        if char_update is None:
            return character, logs

        new_char = character
        attributes = char_update.attributes
        if attributes.hp_delta != 0:
            new_char = new_char.with_attributes(new_char.attributes.with_hp_delta(attributes.hp_delta))
            logs.append(f"血量变化: {attributes.hp_delta:+d}")
        if attributes.mp_delta != 0:
            new_char = new_char.with_attributes(new_char.attributes.with_mp_delta(attributes.mp_delta))
            logs.append(f"灵力变化: {attributes.mp_delta:+d}")
        if attributes.spirit_delta != 0:
            new_char = new_char.with_attributes(new_char.attributes.with_spirit_delta(attributes.spirit_delta))
            logs.append(f"神识变化: {attributes.spirit_delta:+d}")

        for status in attributes.status_add:
            new_char = new_char.with_attributes(new_char.attributes.add_status(status))
            logs.append(f"添加状态: {status}")
        for status in attributes.status_remove:
            new_char = new_char.with_attributes(new_char.attributes.remove_status(status))
            logs.append(f"移除状态: {status}")

        for item_name, count in char_update.item_changes.items_gained.items():
            new_char = new_char.add_item(item_name, count)
            logs.append(f"获得物品: {item_name} x{count}")
        for item_name, count in char_update.item_changes.items_lost.items():
            new_char = new_char.remove_item(item_name, count)
            logs.append(f"失去物品: {item_name} x{count}")

        position = char_update.position
        has_absolute = position.x is not None or position.y is not None
        has_delta = position.dx != 0.0 or position.dy != 0.0
        if has_absolute or has_delta:
            x = float(new_char.position.x + position.dx)
            y = float(new_char.position.y + position.dy)
            if position.x is not None:
                x = position.x
            if position.y is not None:
                y = position.y
            new_char = new_char.with_position(x, y)
            logs.append(f"位置变化: ({new_char.position.x:.1f}, {new_char.position.y:.1f})")

        for treasure_change in char_update.treasure_changes:
            if not treasure_change.treasure_name:
                continue
            new_char = new_char.apply_treasure_change(
                treasure_name=treasure_change.treasure_name,
                wear_delta=treasure_change.wear_delta,
                durability_delta=treasure_change.durability_delta,
                injected_spirit=treasure_change.injected_spirit,
            )
            logs.append(
                f"法宝变化: {treasure_change.treasure_name} "
                f"(损耗{treasure_change.wear_delta:+d}, 耐久{treasure_change.durability_delta:+d})"
            )

        return new_char, logs


class AICoordinator:
    """Coordinate prompt construction, AI request, audit, and audited apply."""

    def __init__(self, ai_interface: AIInterface, prompt_builder: PromptBuilder):
        self.ai_interface = ai_interface
        self.prompt_builder = prompt_builder

    async def process_character_group(
        self,
        characters: list[Character],
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any],
    ) -> GroupProcessResult:
        prompt = self.prompt_builder.build_group_prompt(
            characters,
            environment,
            treasures_data,
            techniques_data,
        )
        response = await self.ai_interface.request_decision(prompt)
        if response is None:
            return GroupProcessResult(
                response=None,
                audit_result=None,
                updated_characters=characters,
            )

        audit_result = AuditValidator.audit_group_update(
            response,
            characters,
            treasures_data,
            techniques_data,
        )
        if not audit_result.ok or audit_result.update is None:
            return GroupProcessResult(
                response=response,
                audit_result=audit_result,
                updated_characters=characters,
            )

        updated_characters, logs = ChangeApplier.apply_group_update(
            characters,
            audit_result.update,
        )
        return GroupProcessResult(
            response=response,
            audit_result=audit_result,
            updated_characters=updated_characters,
            character_logs=logs,
        )

    async def process_single_character(
        self,
        character: Character,
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any],
    ) -> tuple[Character, AIResponse | None, list[str]]:
        result = await self.process_character_group(
            [character],
            environment,
            treasures_data,
            techniques_data,
        )
        logs = result.character_logs.get(character.id, [])
        if result.audit_result and not result.audit_result.ok:
            logs = result.audit_result.error_messages()
        updated = result.updated_characters[0] if result.updated_characters else character
        return updated, result.response, logs

    async def process_interaction_group(
        self,
        characters: list[Character],
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any],
    ) -> tuple[list[Character], AIResponse | None, dict[str, list[str]]]:
        result = await self.process_character_group(
            characters,
            environment,
            treasures_data,
            techniques_data,
        )
        if result.audit_result and not result.audit_result.ok:
            return characters, result.response, {"audit_errors": result.audit_result.error_messages()}
        return result.updated_characters, result.response, result.character_logs
