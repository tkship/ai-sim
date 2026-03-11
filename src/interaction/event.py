"""事件系统模块

记录和管理游戏事件
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class EventType(str, Enum):
    """事件类型枚举"""
    # 角色事件
    CHARACTER_CREATED = "character_created"
    CHARACTER_DIED = "character_died"
    CHARACTER_REVIVED = "character_revived"
    CHARACTER_MOVED = "character_moved"
    REALM_ADVANCED = "realm_advanced"

    # 交互事件
    ENCOUNTER = "encounter"
    COMBAT_START = "combat_start"
    COMBAT_END = "combat_end"
    EXCHANGE = "exchange"
    TRADE = "trade"

    # 物品事件
    ITEM_OBTAINED = "item_obtained"
    ITEM_USED = "item_used"
    ITEM_EQUIPPED = "item_equipped"
    ITEM_LOST = "item_lost"

    # 属性事件
    HEAL = "heal"
    DAMAGE_TAKEN = "damage_taken"
    SPIRIT_POWER_CHANGE = "spirit_power_change"

    # 系统事件
    GAME_START = "game_start"
    GAME_END = "game_end"
    ROUND_START = "round_start"
    ROUND_END = "round_end"

    # AI 事件
    AI_REQUEST = "ai_request"
    AI_RESPONSE = "ai_response"
    AI_ERROR = "ai_error"


@dataclass
class Event:
    """事件类

    表示游戏中的一个事件
    """
    id: str = field(init=False)
    event_type: EventType
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""  # 事件来源
    description: str = ""  # 事件描述

    # 相关角色ID列表
    related_characters: List[str] = field(default_factory=list)

    # 事件数据
    data: Dict = field(default_factory=dict)

    # 优先级（用于排序）
    priority: int = 0

    def __post_init__(self) -> None:
        """生成事件ID"""
        self.id = f"{self.event_type.value}_{self.timestamp.strftime('%Y%m%d%H%M%S%f')}"

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "event_type": self.event_type.value,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "description": self.description,
            "related_characters": self.related_characters,
            "data": self.data,
            "priority": self.priority,
        }


class EventManager:
    """事件管理器

    负责记录、管理和分发游戏事件
    """

    def __init__(self, max_events: int = 1000):
        """初始化事件管理器

        Args:
            max_events: 最大保存事件数量
        """
        self.max_events = max_events
        self.events: List[Event] = []

        # 事件监听器
        self._listeners = {}

    def emit(
        self,
        event_type: EventType,
        description: str = "",
        source: str = "",
        related_characters: List[str] = None,
        data: Dict = None,
        priority: int = 0,
    ) -> Event:
        """触发一个事件

        Args:
            event_type: 事件类型
            description: 事件描述
            source: 事件来源
            related_characters: 相关角色ID列表
            data: 事件数据
            priority: 优先级

        Returns:
            创建的事件对象
        """
        if related_characters is None:
            related_characters = []
        if data is None:
            data = {}

        event = Event(
            event_type=event_type,
            timestamp=datetime.now(),
            source=source,
            description=description,
            related_characters=related_characters,
            data=data,
            priority=priority,
        )

        self.events.append(event)

        # 限制事件数量
        if len(self.events) > self.max_events:
            # 删除最老的事件
            self.events.pop(0)

        # 通知监听器
        self._notify_listeners(event)

        return event

    def on(self, event_type: EventType, callback):
        """注册事件监听器

        Args:
            event_type: 要监听的事件类型
            callback: 回调函数
        """
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def _notify_listeners(self, event: Event) -> None:
        """通知监听器

        Args:
            event: 事件对象
        """
        if event.event_type in self._listeners:
            for callback in self._listeners[event.event_type]:
                try:
                    callback(event)
                except Exception:
                    # 监听器错误不应该影响游戏运行
                    pass

    def get_recent_events(self, count: int = 20) -> List[Event]:
        """获取最近的事件

        Args:
            count: 获取数量

        Returns:
            事件列表
        """
        return self.events[-count:]

    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """按类型获取事件

        Args:
            event_type: 事件类型

        Returns:
            该类型的所有事件
        """
        return [e for e in self.events if e.event_type == event_type]

    def get_events_by_character(self, character_id: str) -> List[Event]:
        """按角色获取事件

        Args:
            character_id: 角色ID

        Returns:
            与该角色相关的所有事件
        """
        return [
            e for e in self.events
            if character_id in e.related_characters
        ]

    def clear_events(self) -> None:
        """清空所有事件"""
        self.events = []

    def get_event_summary(self, count: int = 10) -> str:
        """获取事件摘要

        Args:
            count: 摘要包含的事件数量

        Returns:
            摘要字符串
        """
        recent = self.get_recent_events(count)

        if not recent:
            return "暂无事件"

        lines = [f"最近 {len(recent)} 条事件：", ""]

        for event in reversed(recent):
            timestamp = event.timestamp.strftime("%H:%M:%S")
            lines.append(
                f"[{timestamp}] {event.event_type.value}: {event.description}"
            )

        return "\n".join(lines)


# 便捷的事件创建函数
def create_character_event(
    event_manager: EventManager,
    event_type: EventType,
    character_id: str,
    description: str = "",
    data: Dict = None,
) -> Event:
    """创建角色相关事件

    Args:
        event_manager: 事件管理器
        event_type: 事件类型
        character_id: 角色ID
        description: 描述
        data: 附加数据

    Returns:
        事件对象
    """
    return event_manager.emit(
        event_type=event_type,
        description=description,
        related_characters=[character_id],
        data=data or {},
    )


def create_combat_event(
    event_manager: EventManager,
    event_type: EventType,
    attacker_id: str,
    defender_id: str,
    description: str = "",
    data: Dict = None,
) -> Event:
    """创建战斗相关事件

    Args:
        event_manager: 事件管理器
        event_type: 事件类型
        attacker_id: 攻击者ID
        defender_id: 防御者ID
        description: 描述
        data: 附加数据

    Returns:
        事件对象
    """
    return event_manager.emit(
        event_type=event_type,
        description=description,
        related_characters=[attacker_id, defender_id],
        data=data or {},
    )
