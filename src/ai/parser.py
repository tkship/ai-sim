"""AI response parsing and group-update data models."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any


def _first_present(data: dict[str, Any], *keys: str, default: Any = None) -> Any:
    """Return the first matching key from a mapping."""
    for key in keys:
        if key in data:
            return data[key]
    return default


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _as_dict(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {}


def _to_int(value: Any, default: int = 0) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _to_float(value: Any, default: float = 0.0) -> float:
    if value is None:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


@dataclass
class AttributeChange:
    hp_delta: int = 0
    mp_delta: int = 0
    spirit_delta: int = 0
    status_add: list[str] = field(default_factory=list)
    status_remove: list[str] = field(default_factory=list)


@dataclass
class TreasureChange:
    treasure_name: str
    wear_delta: int = 0
    durability_delta: int = 0
    injected_spirit: int | None = None
    description: str = ""


@dataclass
class ItemChange:
    items_gained: dict[str, int] = field(default_factory=dict)
    items_lost: dict[str, int] = field(default_factory=dict)


@dataclass
class PositionChange:
    x: float | None = None
    y: float | None = None
    dx: float = 0.0
    dy: float = 0.0


@dataclass
class Intent:
    summary: str = ""
    target_ids: list[str] = field(default_factory=list)
    priority: str = ""
    notes: str = ""


@dataclass
class Action:
    action_type: str = ""
    target_ids: list[str] = field(default_factory=list)
    technique_name: str = ""
    item_name: str = ""
    treasure_name: str = ""
    description: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceBasis:
    mp_cost: int = 0
    spirit_cost: int = 0
    item_costs: dict[str, int] = field(default_factory=dict)
    treasure_costs: list[TreasureChange] = field(default_factory=list)
    technique_name: str = ""
    notes: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class EffectBasis:
    primary_effect: str = ""
    factors: list[str] = field(default_factory=list)
    result_reference: str = ""
    notes: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Basis:
    resource_basis: ResourceBasis = field(default_factory=ResourceBasis)
    effect_basis: EffectBasis = field(default_factory=EffectBasis)


@dataclass
class GroupEvent:
    event_type: str = ""
    actor_id: str = ""
    target_ids: list[str] = field(default_factory=list)
    description: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterUpdate:
    character_id: str
    intent: Intent = field(default_factory=Intent)
    action: Action = field(default_factory=Action)
    basis: Basis = field(default_factory=Basis)
    attributes: AttributeChange = field(default_factory=AttributeChange)
    treasure_changes: list[TreasureChange] = field(default_factory=list)
    item_changes: ItemChange = field(default_factory=ItemChange)
    position: PositionChange = field(default_factory=PositionChange)
    raw_data: dict[str, Any] = field(default_factory=dict)


CharacterChange = CharacterUpdate


@dataclass
class GroupUpdate:
    participants: list[str] = field(default_factory=list)
    scene_summary: str = ""
    scene_description: str = ""
    events: list[GroupEvent] = field(default_factory=list)
    character_updates: dict[str, CharacterUpdate] = field(default_factory=dict)
    raw_json: dict[str, Any] | None = None

    @property
    def interaction_summary(self) -> str:
        return self.scene_summary

    @property
    def character_changes(self) -> dict[str, CharacterUpdate]:
        return self.character_updates

    @property
    def environment_changes(self) -> dict[str, Any]:
        return {}


AIResponse = GroupUpdate


class ResponseParser:
    """Parse AI JSON responses into normalized group updates."""

    @staticmethod
    def parse(json_str: str) -> AIResponse | None:
        try:
            data = json.loads(json_str)
        except json.JSONDecodeError:
            return None

        if not isinstance(data, dict):
            return None

        return ResponseParser._parse_dict(data)

    @staticmethod
    def _parse_dict(data: dict[str, Any]) -> AIResponse:
        normalized = ResponseParser._normalize_group_payload(data)
        response = GroupUpdate(
            participants=[
                str(participant)
                for participant in _as_list(normalized.get("participants"))
                if str(participant).strip()
            ],
            scene_summary=str(normalized.get("scene_summary", "")),
            scene_description=str(normalized.get("scene_description", "")),
            raw_json=data,
        )

        for event_data in _as_list(normalized.get("events")):
            if not isinstance(event_data, dict):
                continue
            response.events.append(ResponseParser._parse_event(event_data))

        for character_id, char_data in ResponseParser._iter_character_updates(
            normalized.get("character_updates")
        ):
            response.character_updates[character_id] = ResponseParser._parse_character_update(
                character_id,
                char_data,
            )

        return response

    @staticmethod
    def _normalize_group_payload(data: dict[str, Any]) -> dict[str, Any]:
        participants = _first_present(data, "participants", "参与者")
        scene_summary = _first_present(
            data,
            "scene_summary",
            "场景摘要",
            "interaction_summary",
            "交互概述",
            "summary",
        )
        scene_description = _first_present(
            data,
            "scene_description",
            "场景描述",
            "scene",
        )
        events = _first_present(data, "events", "事件", default=[])
        character_updates = _first_present(
            data,
            "character_updates",
            "角色更新",
            "attribute_changes",
            "属性变化",
            default={},
        )

        if participants is None and isinstance(character_updates, dict):
            participants = list(character_updates.keys())

        return {
            "participants": _as_list(participants),
            "scene_summary": scene_summary or "",
            "scene_description": scene_description or "",
            "events": _as_list(events),
            "character_updates": character_updates,
        }

    @staticmethod
    def _iter_character_updates(value: Any) -> list[tuple[str, dict[str, Any]]]:
        if isinstance(value, dict):
            return [
                (str(character_id), _as_dict(char_data))
                for character_id, char_data in value.items()
            ]

        result: list[tuple[str, dict[str, Any]]] = []
        for char_data in _as_list(value):
            if not isinstance(char_data, dict):
                continue
            character_id = str(
                _first_present(
                    char_data,
                    "character_id",
                    "character",
                    "id",
                    "角色ID",
                    "角色",
                    default="",
                )
            )
            if character_id:
                result.append((character_id, char_data))
        return result

    @staticmethod
    def _parse_event(event_data: dict[str, Any]) -> GroupEvent:
        return GroupEvent(
            event_type=str(
                _first_present(event_data, "type", "event_type", "事件类型", default="")
            ),
            actor_id=str(
                _first_present(event_data, "actor_id", "actor", "发起者", default="")
            ),
            target_ids=[
                str(target_id)
                for target_id in _as_list(
                    _first_present(event_data, "target_ids", "targets", "目标", default=[])
                )
                if str(target_id).strip()
            ],
            description=str(
                _first_present(event_data, "description", "描述", default="")
            ),
            raw_data=event_data,
        )

    @staticmethod
    def _parse_character_update(
        character_id: str,
        char_data: dict[str, Any],
    ) -> CharacterUpdate:
        update = CharacterUpdate(character_id=character_id, raw_data=char_data)
        update.intent = ResponseParser._parse_intent(
            _as_dict(_first_present(char_data, "intent", "意图", default={}))
        )
        update.action = ResponseParser._parse_action(
            _as_dict(_first_present(char_data, "action", "行为", default={}))
        )
        update.basis = ResponseParser._parse_basis(
            _as_dict(_first_present(char_data, "basis", "依据", default={}))
        )
        update.attributes = ResponseParser._parse_attribute_change(
            _as_dict(
                _first_present(
                    char_data,
                    "attribute_changes",
                    "属性变化",
                    default=char_data,
                )
            )
        )
        update.item_changes = ResponseParser._parse_item_change(
            _as_dict(_first_present(char_data, "item_changes", "物品变化", default={}))
        )
        update.position = ResponseParser._parse_position_change(
            _as_dict(_first_present(char_data, "position", "位置", default={}))
        )

        treasure_payload = _first_present(
            char_data,
            "treasure_changes",
            "法宝变化",
            default=[],
        )
        update.treasure_changes = [
            ResponseParser._parse_treasure_change(_as_dict(treasure_data))
            for treasure_data in _as_list(treasure_payload)
            if isinstance(treasure_data, dict)
        ]

        if not update.treasure_changes and update.basis.resource_basis.treasure_costs:
            update.treasure_changes = list(update.basis.resource_basis.treasure_costs)

        return update

    @staticmethod
    def _parse_intent(intent_data: dict[str, Any]) -> Intent:
        return Intent(
            summary=str(_first_present(intent_data, "summary", "内容", "description", "描述", default="")),
            target_ids=[
                str(target_id)
                for target_id in _as_list(
                    _first_present(intent_data, "target_ids", "targets", "目标", default=[])
                )
                if str(target_id).strip()
            ],
            priority=str(_first_present(intent_data, "priority", "优先级", default="")),
            notes=str(_first_present(intent_data, "notes", "备注", default="")),
        )

    @staticmethod
    def _parse_action(action_data: dict[str, Any]) -> Action:
        return Action(
            action_type=str(_first_present(action_data, "action_type", "type", "行为类型", default="")),
            target_ids=[
                str(target_id)
                for target_id in _as_list(
                    _first_present(action_data, "target_ids", "targets", "目标", default=[])
                )
                if str(target_id).strip()
            ],
            technique_name=str(
                _first_present(action_data, "technique_name", "功法", default="")
            ),
            item_name=str(_first_present(action_data, "item_name", "物品", default="")),
            treasure_name=str(
                _first_present(action_data, "treasure_name", "法宝", default="")
            ),
            description=str(_first_present(action_data, "description", "描述", default="")),
            raw_data=action_data,
        )

    @staticmethod
    def _parse_basis(basis_data: dict[str, Any]) -> Basis:
        return Basis(
            resource_basis=ResponseParser._parse_resource_basis(
                _as_dict(
                    _first_present(basis_data, "resource_basis", "资源依据", default={})
                )
            ),
            effect_basis=ResponseParser._parse_effect_basis(
                _as_dict(
                    _first_present(basis_data, "effect_basis", "效果依据", default={})
                )
            ),
        )

    @staticmethod
    def _parse_resource_basis(resource_data: dict[str, Any]) -> ResourceBasis:
        treasure_costs_payload = _first_present(
            resource_data,
            "treasure_costs",
            "法宝代价",
            default=[],
        )
        return ResourceBasis(
            mp_cost=_to_int(_first_present(resource_data, "mp_cost", "灵力消耗", default=0)),
            spirit_cost=_to_int(
                _first_present(resource_data, "spirit_cost", "神识消耗", default=0)
            ),
            item_costs={
                str(name): _to_int(count)
                for name, count in _as_dict(
                    _first_present(resource_data, "item_costs", "物品消耗", default={})
                ).items()
            },
            treasure_costs=[
                ResponseParser._parse_treasure_change(_as_dict(treasure_data))
                for treasure_data in _as_list(treasure_costs_payload)
                if isinstance(treasure_data, dict)
            ],
            technique_name=str(
                _first_present(resource_data, "technique_name", "功法", default="")
            ),
            notes=str(_first_present(resource_data, "notes", "备注", default="")),
            raw_data=resource_data,
        )

    @staticmethod
    def _parse_effect_basis(effect_data: dict[str, Any]) -> EffectBasis:
        return EffectBasis(
            primary_effect=str(
                _first_present(effect_data, "primary_effect", "主要效果", default="")
            ),
            factors=[
                str(factor)
                for factor in _as_list(
                    _first_present(effect_data, "factors", "作用因子", default=[])
                )
                if str(factor).strip()
            ],
            result_reference=str(
                _first_present(effect_data, "result_reference", "结果关联", default="")
            ),
            notes=str(_first_present(effect_data, "notes", "备注", default="")),
            raw_data=effect_data,
        )

    @staticmethod
    def _parse_attribute_change(attr_data: dict[str, Any]) -> AttributeChange:
        status_data = _as_dict(_first_present(attr_data, "status", "状态", default={}))
        return AttributeChange(
            hp_delta=_to_int(_first_present(attr_data, "hp_delta", "hp", "血量", default=0)),
            mp_delta=_to_int(_first_present(attr_data, "mp_delta", "mp", "灵力", default=0)),
            spirit_delta=_to_int(
                _first_present(attr_data, "spirit_delta", "spirit", "神识", default=0)
            ),
            status_add=[
                str(status)
                for status in _as_list(
                    _first_present(status_data, "add", "新增", default=[])
                )
                if str(status).strip()
            ],
            status_remove=[
                str(status)
                for status in _as_list(
                    _first_present(status_data, "remove", "移除", default=[])
                )
                if str(status).strip()
            ],
        )

    @staticmethod
    def _parse_item_change(item_data: dict[str, Any]) -> ItemChange:
        return ItemChange(
            items_gained={
                str(name): _to_int(count)
                for name, count in _as_dict(
                    _first_present(item_data, "gained", "获得", default={})
                ).items()
            },
            items_lost={
                str(name): _to_int(count)
                for name, count in _as_dict(
                    _first_present(item_data, "lost", "失去", default={})
                ).items()
            },
        )

    @staticmethod
    def _parse_position_change(position_data: dict[str, Any]) -> PositionChange:
        return PositionChange(
            x=_to_float(position_data["x"]) if "x" in position_data else None,
            y=_to_float(position_data["y"]) if "y" in position_data else None,
            dx=_to_float(_first_present(position_data, "dx", default=0.0)),
            dy=_to_float(_first_present(position_data, "dy", default=0.0)),
        )

    @staticmethod
    def _parse_treasure_change(treasure_data: dict[str, Any]) -> TreasureChange:
        injected_spirit = _first_present(
            treasure_data,
            "injected_spirit",
            "当前注入灵力",
        )
        return TreasureChange(
            treasure_name=str(
                _first_present(treasure_data, "treasure_name", "name", "法宝名称", default="")
            ),
            wear_delta=_to_int(
                _first_present(treasure_data, "wear_delta", "损耗度变化", default=0)
            ),
            durability_delta=_to_int(
                _first_present(
                    treasure_data,
                    "durability_delta",
                    "耐久度变化",
                    default=0,
                )
            ),
            injected_spirit=_to_int(injected_spirit) if injected_spirit is not None else None,
            description=str(_first_present(treasure_data, "description", "说明", default="")),
        )

    @staticmethod
    def validate(response: AIResponse) -> tuple[bool, list[str]]:
        errors: list[str] = []

        if not response.participants:
            errors.append("缺少组级字段: participants")
        if not response.scene_summary:
            errors.append("缺少组级字段: scene_summary")
        if not response.scene_description:
            errors.append("缺少组级字段: scene_description")
        if not response.character_updates:
            errors.append("缺少组级字段: character_updates")

        for index, event in enumerate(response.events):
            if not event.event_type:
                errors.append(f"events[{index}] 缺少字段: type")

        for character_id, update in response.character_updates.items():
            if not update.character_id:
                errors.append("character_updates 存在缺少字段: character_id 的条目")
                continue

            if not update.intent.summary:
                errors.append(f"character_updates[{character_id}] 缺少字段: intent.summary")
            if not update.action.action_type:
                errors.append(f"character_updates[{character_id}] 缺少字段: action.action_type")

            if not update.basis.resource_basis.raw_data:
                errors.append(
                    f"character_updates[{character_id}] 缺少字段: basis.resource_basis"
                )
            if not update.basis.effect_basis.raw_data:
                errors.append(
                    f"character_updates[{character_id}] 缺少字段: basis.effect_basis"
                )

        return len(errors) == 0, errors

