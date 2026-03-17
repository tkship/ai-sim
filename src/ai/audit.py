"""Audit and validate group AI updates before applying them."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..character import Character
from .parser import AIResponse, CharacterUpdate, GroupEvent, ResponseParser


ALLOWED_ACTION_TYPES = {
    "attack",
    "defend",
    "move",
    "consume_item",
    "cultivate",
    "breakthrough",
    "observe",
    "interact",
}

ALLOWED_EVENT_TYPES = {
    "attack",
    "defense",
    "hit",
    "block",
    "interrupt",
    "consume_item",
    "move",
    "clash",
    "apply_status",
    "remove_status",
    "cultivate",
    "breakthrough_attempt",
    "breakthrough_result",
    "interact",
}

BOUNDARY_TOLERANCE = 5


@dataclass
class AuditIssue:
    code: str
    message: str
    path: str = ""


@dataclass
class ClippedValue:
    path: str
    original: int
    clipped: int


@dataclass
class AuditResult:
    ok: bool
    update: AIResponse | None = None
    errors: list[AuditIssue] = field(default_factory=list)
    warnings: list[AuditIssue] = field(default_factory=list)
    clipped_values: list[ClippedValue] = field(default_factory=list)

    def error_messages(self) -> list[str]:
        return [issue.message for issue in self.errors]

    def warning_messages(self) -> list[str]:
        return [issue.message for issue in self.warnings]


class AuditValidator:
    """Audit parsed group updates against current world state."""

    @staticmethod
    def audit_group_update(
        update: AIResponse,
        characters: list[Character],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any],
    ) -> AuditResult:
        result = AuditResult(ok=True, update=update)
        char_map = {character.id: character for character in characters}
        name_map = {character.name: character for character in characters}
        participant_ids = set(update.participants)
        expected_ids = set(char_map.keys())

        AuditValidator._check_parser_errors(update, result)
        AuditValidator._check_group_boundary(update, expected_ids, result)
        AuditValidator._check_events(update.events, expected_ids, result)

        for character_id, char_update in update.character_updates.items():
            character = char_map.get(character_id) or name_map.get(character_id)
            if character is None:
                result.errors.append(
                    AuditIssue(
                        code="missing_character",
                        path=f"character_updates[{character_id}]",
                        message=f"角色不存在: {character_id}",
                    )
                )
                continue

            AuditValidator._check_action_and_references(
                char_update,
                character,
                expected_ids,
                treasures_data,
                techniques_data,
                result,
            )
            AuditValidator._check_inventory_conservation(char_update, character, result)
            AuditValidator._clip_attribute_bounds(char_update, character, result)
            AuditValidator._clip_treasure_bounds(char_update, character, result)

        if participant_ids != expected_ids:
            result.errors.append(
                AuditIssue(
                    code="participant_mismatch",
                    path="participants",
                    message=(
                        f"组成员不一致: expected={sorted(expected_ids)} "
                        f"actual={sorted(participant_ids)}"
                    ),
                )
            )

        result.ok = len(result.errors) == 0
        if not result.ok:
            result.update = None
        return result

    @staticmethod
    def _check_parser_errors(update: AIResponse, result: AuditResult) -> None:
        valid, errors = ResponseParser.validate(update)
        if valid:
            return
        for index, error in enumerate(errors):
            result.errors.append(
                AuditIssue(
                    code="invalid_structure",
                    path=f"validation[{index}]",
                    message=error,
                )
            )

    @staticmethod
    def _check_group_boundary(
        update: AIResponse,
        expected_ids: set[str],
        result: AuditResult,
    ) -> None:
        actual_update_ids = set(update.character_updates.keys())
        if actual_update_ids != expected_ids:
            result.errors.append(
                AuditIssue(
                    code="character_update_mismatch",
                    path="character_updates",
                    message=(
                        f"角色账本覆盖不一致: expected={sorted(expected_ids)} "
                        f"actual={sorted(actual_update_ids)}"
                    ),
                )
            )

    @staticmethod
    def _check_events(
        events: list[GroupEvent],
        expected_ids: set[str],
        result: AuditResult,
    ) -> None:
        seen_signatures: dict[tuple[str, str, tuple[str, ...]], str] = {}
        for index, event in enumerate(events):
            path = f"events[{index}]"
            if event.event_type not in ALLOWED_EVENT_TYPES:
                result.errors.append(
                    AuditIssue(
                        code="invalid_event_type",
                        path=path,
                        message=f"非法事件类型: {event.event_type}",
                    )
                )
            if event.actor_id and event.actor_id not in expected_ids:
                result.errors.append(
                    AuditIssue(
                        code="event_actor_outside_group",
                        path=f"{path}.actor_id",
                        message=f"事件发起者不在组内: {event.actor_id}",
                    )
                )
            invalid_targets = [target_id for target_id in event.target_ids if target_id not in expected_ids]
            if invalid_targets:
                result.errors.append(
                    AuditIssue(
                        code="event_target_outside_group",
                        path=f"{path}.target_ids",
                        message=f"事件目标不在组内: {invalid_targets}",
                    )
                )
            signature = (
                event.event_type,
                event.actor_id,
                tuple(sorted(event.target_ids)),
            )
            description = event.description.strip()
            if signature in seen_signatures and seen_signatures[signature] != description:
                result.errors.append(
                    AuditIssue(
                        code="shared_fact_conflict",
                        path=path,
                        message=f"共享事实冲突: {signature[0]} / {signature[1]} 的事件描述不一致",
                    )
                )
            else:
                seen_signatures[signature] = description

    @staticmethod
    def _check_action_and_references(
        update: CharacterUpdate,
        character: Character,
        expected_ids: set[str],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any],
        result: AuditResult,
    ) -> None:
        path = f"character_updates[{character.id}]"
        if update.action.action_type not in ALLOWED_ACTION_TYPES:
            result.errors.append(
                AuditIssue(
                    code="invalid_action_type",
                    path=f"{path}.action.action_type",
                    message=f"非法行为类型: {update.action.action_type}",
                )
            )

        invalid_targets = [target_id for target_id in update.action.target_ids if target_id not in expected_ids]
        if invalid_targets:
            result.errors.append(
                AuditIssue(
                    code="action_target_outside_group",
                    path=f"{path}.action.target_ids",
                    message=f"行为目标不在组内: {invalid_targets}",
                )
            )

        technique_name = update.action.technique_name or update.basis.resource_basis.technique_name
        if technique_name and technique_name not in character.techniques and technique_name not in techniques_data:
            result.errors.append(
                AuditIssue(
                    code="unknown_technique",
                    path=f"{path}.action.technique_name",
                    message=f"引用了不存在的功法: {technique_name}",
                )
            )

        if update.action.item_name and update.action.item_name not in character.inventory:
            result.errors.append(
                AuditIssue(
                    code="unknown_item",
                    path=f"{path}.action.item_name",
                    message=f"引用了不存在的物品: {update.action.item_name}",
                )
            )

        referenced_treasures = {
            update.action.treasure_name,
            *(change.treasure_name for change in update.treasure_changes),
            *(change.treasure_name for change in update.basis.resource_basis.treasure_costs),
        }
        for treasure_name in referenced_treasures:
            if not treasure_name:
                continue
            if treasure_name not in character.treasure_states and treasure_name not in character.equipment.values():
                result.errors.append(
                    AuditIssue(
                        code="unknown_treasure",
                        path=f"{path}.treasure",
                        message=f"引用了角色未持有的法宝: {treasure_name}",
                    )
                )
            elif treasure_name not in treasures_data and treasure_name not in character.treasure_states:
                result.errors.append(
                    AuditIssue(
                        code="missing_treasure_template",
                        path=f"{path}.treasure",
                        message=f"引用了不存在的法宝模板: {treasure_name}",
                    )
                )

        if AuditValidator._has_material_changes(update):
            if not update.basis.resource_basis.raw_data:
                result.errors.append(
                    AuditIssue(
                        code="missing_resource_basis",
                        path=f"{path}.basis.resource_basis",
                        message=f"{character.id} 缺少 resource_basis，无法解释资源消耗",
                    )
                )
            if not update.basis.effect_basis.raw_data:
                result.errors.append(
                    AuditIssue(
                        code="missing_effect_basis",
                        path=f"{path}.basis.effect_basis",
                        message=f"{character.id} 缺少 effect_basis，无法解释主要结果",
                    )
                )

    @staticmethod
    def _check_inventory_conservation(
        update: CharacterUpdate,
        character: Character,
        result: AuditResult,
    ) -> None:
        path = f"character_updates[{character.id}].item_changes.lost"
        for item_name, count in update.item_changes.items_lost.items():
            available = character.inventory.get(item_name, 0)
            if available < count:
                result.errors.append(
                    AuditIssue(
                        code="insufficient_inventory",
                        path=path,
                        message=f"{character.id} 物品不足: {item_name} need={count} have={available}",
                    )
                )

    @staticmethod
    def _clip_attribute_bounds(
        update: CharacterUpdate,
        character: Character,
        result: AuditResult,
    ) -> None:
        attributes = update.attributes
        AuditValidator._clip_delta(
            value_name="hp_delta",
            current=character.attributes.hp.current,
            maximum=character.attributes.hp.max,
            current_delta=attributes.hp_delta,
            assign=lambda value: setattr(attributes, "hp_delta", value),
            path=f"character_updates[{character.id}].attribute_changes.hp_delta",
            result=result,
        )
        AuditValidator._clip_delta(
            value_name="mp_delta",
            current=character.attributes.mp.current,
            maximum=character.attributes.mp.max,
            current_delta=attributes.mp_delta,
            assign=lambda value: setattr(attributes, "mp_delta", value),
            path=f"character_updates[{character.id}].attribute_changes.mp_delta",
            result=result,
        )
        AuditValidator._clip_delta(
            value_name="spirit_delta",
            current=character.attributes.spirit.current,
            maximum=character.attributes.spirit.max,
            current_delta=attributes.spirit_delta,
            assign=lambda value: setattr(attributes, "spirit_delta", value),
            path=f"character_updates[{character.id}].attribute_changes.spirit_delta",
            result=result,
        )

    @staticmethod
    def _clip_treasure_bounds(
        update: CharacterUpdate,
        character: Character,
        result: AuditResult,
    ) -> None:
        for index, change in enumerate(update.treasure_changes):
            if not change.treasure_name:
                continue

            state = character.treasure_states.get(change.treasure_name, {})
            wear = int(state.get("wear", 100))
            durability = int(state.get("durability", state.get("max_durability", 100)))
            max_durability = int(state.get("max_durability", 100))
            max_injected = int(state.get("max_injected_spirit", 20))

            AuditValidator._clip_delta(
                value_name="wear_delta",
                current=wear,
                maximum=100,
                current_delta=change.wear_delta,
                assign=lambda value, target=change: setattr(target, "wear_delta", value),
                path=f"character_updates[{character.id}].treasure_changes[{index}].wear_delta",
                result=result,
            )
            AuditValidator._clip_delta(
                value_name="durability_delta",
                current=durability,
                maximum=max_durability,
                current_delta=change.durability_delta,
                assign=lambda value, target=change: setattr(target, "durability_delta", value),
                path=f"character_updates[{character.id}].treasure_changes[{index}].durability_delta",
                result=result,
            )

            if change.injected_spirit is not None:
                original = change.injected_spirit
                if original < 0 or original > max_injected:
                    overflow = max(original - max_injected, -original)
                    if overflow > BOUNDARY_TOLERANCE:
                        result.errors.append(
                            AuditIssue(
                                code="severe_treasure_overflow",
                                path=f"character_updates[{character.id}].treasure_changes[{index}].injected_spirit",
                                message=(
                                    f"{character.id} 法宝注灵超界过大: {change.treasure_name} "
                                    f"value={original} max={max_injected}"
                                ),
                            )
                        )
                    clipped = max(0, min(max_injected, original))
                    change.injected_spirit = clipped
                    result.clipped_values.append(
                        ClippedValue(
                            path=f"character_updates[{character.id}].treasure_changes[{index}].injected_spirit",
                            original=original,
                            clipped=clipped,
                        )
                    )
                    result.warnings.append(
                        AuditIssue(
                            code="clipped_treasure_injected_spirit",
                            path=f"character_updates[{character.id}].treasure_changes[{index}].injected_spirit",
                            message=(
                                f"{character.id} 的法宝注灵已裁剪: "
                                f"{change.treasure_name} {original}->{clipped}"
                            ),
                        )
                    )

    @staticmethod
    def _clip_delta(
        value_name: str,
        current: int,
        maximum: int,
        current_delta: int,
        assign: Any,
        path: str,
        result: AuditResult,
    ) -> None:
        final_value = current + current_delta
        lower_gap = 0 - final_value
        upper_gap = final_value - maximum
        overflow = max(lower_gap, upper_gap, 0)
        if overflow <= 0:
            return

        if overflow > BOUNDARY_TOLERANCE:
            result.errors.append(
                AuditIssue(
                    code="severe_boundary_overflow",
                    path=path,
                    message=(
                        f"{value_name} 超界过大: current={current} delta={current_delta} "
                        f"range=[0,{maximum}]"
                    ),
                )
            )
            return

        clipped_final = max(0, min(maximum, final_value))
        clipped_delta = clipped_final - current
        assign(clipped_delta)
        result.clipped_values.append(
            ClippedValue(path=path, original=current_delta, clipped=clipped_delta)
        )
        result.warnings.append(
            AuditIssue(
                code="clipped_boundary_value",
                path=path,
                message=f"{value_name} 已裁剪: {current_delta}->{clipped_delta}",
            )
        )

    @staticmethod
    def _has_material_changes(update: CharacterUpdate) -> bool:
        attributes = update.attributes
        return any(
            [
                attributes.hp_delta != 0,
                attributes.mp_delta != 0,
                attributes.spirit_delta != 0,
                bool(attributes.status_add),
                bool(attributes.status_remove),
                bool(update.item_changes.items_lost),
                bool(update.item_changes.items_gained),
                bool(update.treasure_changes),
            ]
        )
