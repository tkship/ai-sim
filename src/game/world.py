"""
世界管理模块
"""
from dataclasses import dataclass
from typing import List, Dict, Any
from ..character import Character
from ..world import WorldMap


@dataclass
class WorldTime:
    """世界时间"""
    year: int = 3842
    month: int = 3
    day: int = 7
    cycle: int = 0
    total_cycles: int = 0

    def advance_cycle(self, cycles_per_day: int = 12) -> bool:
        """
        推进一个循环

        Returns:
            是否进入新的一天
        """
        self.total_cycles += 1
        self.cycle += 1
        if self.cycle >= cycles_per_day:
            self.cycle = 0
            return self.advance_day()
        return False

    def advance_day(self) -> bool:
        """
        推进一天

        Returns:
            是否进入新的一月
        """
        self.day += 1
        if self.day > 30:
            self.day = 1
            return self.advance_month()
        return False

    def advance_month(self) -> bool:
        """
        推进一月

        Returns:
            是否进入新的一年
        """
        self.month += 1
        if self.month > 12:
            self.month = 1
            self.year += 1
            return True
        return False

    @property
    def display(self) -> str:
        """显示时间"""
        return f"修真历第 {self.year} 年 {self.month} 月 {self.day} 日"


class World:
    """世界管理器"""

    def __init__(self, config):
        self.config = config
        self.time = WorldTime()
        self.map = WorldMap.from_config(config.get("map", {}))
        self.characters: Dict[str, Character] = {}
        self.scene_logs: List[str] = []
        self.location = self.map.name

    def add_character(self, character: Character) -> None:
        """添加角色"""
        self.characters[character.id] = self._clamp_character(character)

    def get_character(self, char_id: str) -> Character:
        """获取角色"""
        return self.characters[char_id]

    def update_character(self, character: Character) -> None:
        """更新角色"""
        self.characters[character.id] = self._clamp_character(character)

    def get_all_characters(self) -> List[Character]:
        """获取所有角色"""
        return list(self.characters.values())

    def add_scene_log(self, log: str) -> None:
        """添加场景日志"""
        timestamp = f"[{self.time.display} 第{self.time.cycle}时]"
        self.scene_logs.append(f"{timestamp} {log}")
        # 只保留最近的100条
        if len(self.scene_logs) > 100:
            self.scene_logs = self.scene_logs[-100:]

    def advance_time(self) -> bool:
        """
        推进时间

        Returns:
            是否进入新的一天
        """
        cycles_per_day = self.config.world.get("cycles_per_day", 12)
        return self.time.advance_cycle(cycles_per_day)

    def get_environment_dict(self) -> Dict[str, Any]:
        """获取环境信息字典"""
        return {
            "location": self.location,
            "time": self.time.display,
            "cycle": self.time.cycle,
            "map": self.map.to_dict(),
            "character_positions": [
                {"id": char.id, "name": char.name, "x": char.position.x, "y": char.position.y}
                for char in self.get_all_characters()
            ],
        }

    def _clamp_character(self, character: Character) -> Character:
        """确保角色位置位于地图边界内。"""
        clamped = self.map.clamp_position(character.position)
        if clamped == character.position:
            return character
        return character.with_position(clamped.x, clamped.y)

    def to_save_dict(self) -> Dict[str, Any]:
        """转换为保存字典"""
        return {
            "year": self.time.year,
            "month": self.time.month,
            "day": self.time.day,
            "cycle": self.time.cycle,
            "total_cycles": self.time.total_cycles,
            "location": self.location,
            "scene_logs": self.scene_logs,
        }

    @classmethod
    def from_save_dict(cls, config, data: Dict[str, Any]) -> "World":
        """从保存字典创建"""
        world = cls(config)
        world.time.year = data.get("year", 3842)
        world.time.month = data.get("month", 3)
        world.time.day = data.get("day", 7)
        world.time.cycle = data.get("cycle", 0)
        world.time.total_cycles = data.get("total_cycles", 0)
        world.location = data.get("location", "黑风岭")
        world.scene_logs = data.get("scene_logs", [])
        return world
