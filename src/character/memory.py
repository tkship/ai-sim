"""历史记忆模块

存储角色的经历、战斗记录、重要事件等
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime


class MemoryType(str):
    """记忆类型"""
    ENCOUNTER = "encounter"      # 邂遇
    COMBAT = "combat"           # 战斗
    ITEM_OBTAINED = "item"      # 获得物品
    REALM_ADVANCE = "advance"   # 境界提升
    EXCHANGE = "exchange"       # 交流
    DEATH = "death"             # 死亡
    GENERAL = "general"         # 一般事件


@dataclass
class MemoryEntry:
    """记忆条目

    记录角色经历的具体事件
    """
    timestamp: datetime
    memory_type: str
    description: str
    related_character_ids: List[str] = None
    data: Dict = None

    def __post_init__(self) -> None:
        if self.related_character_ids is None:
            self.related_character_ids = []
        if self.data is None:
            self.data = {}

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "memory_type": self.memory_type,
            "description": self.description,
            "related_character_ids": self.related_character_ids,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MemoryEntry":
        """从字典创建记忆条目"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            memory_type=data["memory_type"],
            description=data["description"],
            related_character_ids=data.get("related_character_ids", []),
            data=data.get("data", {}),
        )


@dataclass
class Memory:
    """角色记忆类

    管理角色的所有历史记忆
    """
    # 记忆条目列表
    entries: List[MemoryEntry] = None

    # 最大记忆条数（避免内存溢出）
    max_entries: int = 100

    def __post_init__(self) -> None:
        if self.entries is None:
            self.entries = []

    def add_entry(self, memory_type: str, description: str,
                  related_character_ids: List[str] = None,
                  data: Dict = None) -> None:
        """添加一条记忆

        Args:
            memory_type: 记忆类型
            description: 描述
            related_character_ids: 相关角色ID列表
            data: 附加数据
        """
        entry = MemoryEntry(
            timestamp=datetime.now(),
            memory_type=memory_type,
            description=description,
            related_character_ids=related_character_ids,
            data=data,
        )
        self.entries.append(entry)

        # 限制最大条数
        if len(self.entries) > self.max_entries:
            self.entries.pop(0)

    def get_recent_memories(self, count: int = 10) -> List[MemoryEntry]:
        """获取最近的记忆

        Args:
            count: 获取数量

        Returns:
            最近的记忆条目列表
        """
        return self.entries[-count:]

    def get_memories_by_type(self, memory_type: str) -> List[MemoryEntry]:
        """按类型获取记忆

        Args:
            memory_type: 记忆类型

        Returns:
            该类型的记忆条目列表
        """
        return [e for e in self.entries if e.memory_type == memory_type]

    def get_memories_by_character(self, character_id: str) -> List[MemoryEntry]:
        """按角色获取记忆

        Args:
            character_id: 角色ID

        Returns:
            与该角色相关的记忆条目列表
        """
        return [e for e in self.entries if character_id in e.related_character_ids]

    def get_summary(self) -> str:
        """获取记忆摘要

        Returns:
            记忆的文本摘要
        """
        if not self.entries:
            return "暂无记忆"

        # 统计各类型记忆数量
        type_counts = {}
        for entry in self.entries:
            type_counts[entry.memory_type] = type_counts.get(entry.memory_type, 0) + 1

        summary = f"共 {len(self.entries)} 条记忆\n"
        for memory_type, count in type_counts.items():
            summary += f"  - {memory_type}: {count}\n"

        return summary

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "max_entries": self.max_entries,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Memory":
        """从字典创建记忆对象"""
        entries = [
            MemoryEntry.from_dict(entry_data)
            for entry_data in data.get("entries", [])
        ]
        return cls(
            entries=entries,
            max_entries=data.get("max_entries", 100),
        )
