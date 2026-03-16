"""
记忆系统模块
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum


class MemoryImportance(Enum):
    """记忆重要度"""
    TRIVIAL = 0
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass(frozen=True)
class Memory:
    """单条记忆"""
    id: str
    content: str
    importance: MemoryImportance = MemoryImportance.NORMAL
    timestamp: datetime = field(default_factory=datetime.now)
    tags: tuple[str, ...] = ()

    def is_recent(self, hours: int = 24) -> bool:
        """是否是近期记忆"""
        delta = datetime.now() - self.timestamp
        return delta.total_seconds() < hours * 3600

    def has_tag(self, tag: str) -> bool:
        """是否包含某标签"""
        return tag in self.tags

    def matches_keywords(self, keywords: list[str]) -> bool:
        """是否匹配关键词"""
        content_lower = self.content.lower()
        for keyword in keywords:
            if keyword.lower() in content_lower:
                return True
        return False


@dataclass(frozen=True)
class LongTermGoal:
    """长期目标"""
    id: str
    description: str
    priority: int = 5  # 1-10，越高越重要
    created_at: datetime = field(default_factory=datetime.now)
    progress: float = 0.0  # 0.0 - 1.0

    def with_progress(self, progress: float) -> "LongTermGoal":
        """更新进度"""
        new_progress = max(0.0, min(1.0, progress))
        return LongTermGoal(
            self.id,
            self.description,
            self.priority,
            self.created_at,
            new_progress
        )


class MemoryBank:
    """记忆库"""

    def __init__(self, character_id: str):
        self.character_id = character_id
        self._memories: dict[str, Memory] = {}
        self._goals: dict[str, LongTermGoal] = {}

    def add_memory(
        self,
        content: str,
        importance: MemoryImportance | int = MemoryImportance.NORMAL,
        tags: Optional[list[str]] = None,
        memory_id: Optional[str] = None
    ) -> str:
        """
        添加记忆

        Args:
            content: 记忆内容
            importance: 重要度（MemoryImportance 枚举或整数 0-4）
            tags: 标签列表
            memory_id: 记忆ID（自动生成如果未提供）

        Returns:
            记忆ID
        """
        if memory_id is None:
            memory_id = f"mem_{len(self._memories) + 1}"

        # 如果传入的是整数，转换为枚举
        if isinstance(importance, int):
            importance = MemoryImportance(importance)

        memory = Memory(
            id=memory_id,
            content=content,
            importance=importance,
            tags=tuple(tags) if tags else ()
        )
        self._memories[memory_id] = memory
        return memory_id

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        """获取记忆"""
        return self._memories.get(memory_id)

    def get_recent_memories(self, limit: int = 10, hours: int = 24) -> list[Memory]:
        """
        获取近期记忆

        Args:
            limit: 返回数量限制
            hours: 时间范围（小时）

        Returns:
            记忆列表
        """
        memories = [
            m for m in self._memories.values()
            if m.is_recent(hours)
        ]
        # 按时间倒序排列
        memories.sort(key=lambda m: m.timestamp, reverse=True)
        return memories[:limit]

    def get_important_memories(self, limit: int = 10) -> list[Memory]:
        """
        获取重要记忆

        Args:
            limit: 返回数量限制

        Returns:
            记忆列表
        """
        memories = list(self._memories.values())
        # 按重要度和时间排序
        memories.sort(
            key=lambda m: (-m.importance.value, -m.timestamp.timestamp())
        )
        return memories[:limit]

    def search_memories(self, keywords: list[str], limit: int = 10) -> list[Memory]:
        """
        搜索记忆

        Args:
            keywords: 关键词列表
            limit: 返回数量限制

        Returns:
            匹配的记忆列表
        """
        memories = [
            m for m in self._memories.values()
            if m.matches_keywords(keywords)
        ]
        memories.sort(
            key=lambda m: (-m.importance.value, -m.timestamp.timestamp())
        )
        return memories[:limit]

    def get_all_memories(self) -> list[Memory]:
        """获取所有记忆"""
        return list(self._memories.values())

    def add_goal(
        self,
        description: str,
        priority: int = 5,
        goal_id: Optional[str] = None
    ) -> str:
        """
        添加长期目标

        Args:
            description: 目标描述
            priority: 优先级 (1-10)
            goal_id: 目标ID

        Returns:
            目标ID
        """
        if goal_id is None:
            goal_id = f"goal_{len(self._goals) + 1}"

        goal = LongTermGoal(
            id=goal_id,
            description=description,
            priority=priority
        )
        self._goals[goal_id] = goal
        return goal_id

    def update_goal_progress(self, goal_id: str, progress: float) -> bool:
        """更新目标进度"""
        goal = self._goals.get(goal_id)
        if goal:
            self._goals[goal_id] = goal.with_progress(progress)
            return True
        return False

    def get_goal(self, goal_id: str) -> Optional[LongTermGoal]:
        """获取目标"""
        return self._goals.get(goal_id)

    def get_top_goals(self, limit: int = 5) -> list[LongTermGoal]:
        """
        获取优先级最高的目标

        Args:
            limit: 返回数量限制

        Returns:
            目标列表
        """
        goals = list(self._goals.values())
        goals.sort(key=lambda g: (-g.priority, -g.progress))
        return goals[:limit]

    def get_all_goals(self) -> list[LongTermGoal]:
        """获取所有目标"""
        return list(self._goals.values())
