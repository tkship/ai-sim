"""游戏世界模块

管理所有角色、世界状态和规则
"""
from typing import List, Optional, Dict
from character.character import Character, create_character
from interaction.event import EventManager, EventType
from game.config import Config


class World:
    """游戏世界类

    管理游戏世界的所有实体和规则
    """

    def __init__(self, config: Config):
        """初始化游戏世界

        Args:
            config: 游戏配置
        """
        self.config = config
        self.characters: List[Character] = []
        self.event_manager = EventManager()

        self.current_round = 0
        self.is_running = False
        self.is_paused = False

    def add_character(self, character: Character) -> None:
        """添加角色到世界

        Args:
            character: 角色对象
        """
        self.characters.append(character)

        self.event_manager.emit(
            event_type=EventType.CHARACTER_CREATED,
            description=f"角色 {character.name} 加入世界",
            related_characters=[character.id],
            data=character.to_dict(),
        )

    def remove_character(self, character_id: str) -> bool:
        """从世界移除角色

        Args:
            character_id: 角色ID

        Returns:
            是否移除成功
        """
        for i, char in enumerate(self.characters):
            if char.id == character_id:
                removed = self.characters.pop(i)
                self.event_manager.emit(
                    event_type=EventType.CHARACTER_DIED,
                    description=f"角色 {removed.name} 从世界移除",
                    related_characters=[character_id],
                    data=removed.to_dict(),
                )
                return True
        return False

    def get_character(self, character_id: str) -> Optional[Character]:
        """根据ID获取角色

        Args:
            character_id: 角色ID

        Returns:
            角色对象，如果不存在则返回 None
        """
        for char in self.characters:
            if char.id == character_id:
                return char
        return None

    def get_alive_characters(self) -> List[Character]:
        """获取所有存活的角色

        Returns:
            存活角色列表
        """
        return [c for c in self.characters if c.is_alive]

    def get_dead_characters(self) -> List[Character]:
        """获取所有死亡的角色

        Returns:
            死亡角色列表
        """
        return [c for c in self.characters if not c.is_alive]

    def remove_dead_characters(self) -> List[Character]:
        """移除所有死亡的角色

        Returns:
            被移除的角色列表
        """
        dead_chars = []
        alive_chars = []

        for char in self.characters:
            if not char.is_alive:
                dead_chars.append(char)
            else:
                alive_chars.append(char)

        for char in dead_chars:
            self.remove_character(char.id)

        return dead_chars

    def create_random_character(
        self,
        name: str = None,
        position: tuple = None,
    ) -> Character:
        """创建一个随机角色

        Args:
            name: 角色名称
            position: 位置

        Returns:
            角色对象
        """
        import random

        # 生成随机属性
        health_range = self.config.characters.health_range
        spirit_power_range = self.config.characters.spirit_power_range
        consciousness_range = self.config.characters.consciousness_range

        health = random.randint(health_range[0], health_range[1])
        spirit_power = random.randint(spirit_power_range[0], spirit_power_range[1])
        consciousness = random.randint(consciousness_range[0], consciousness_range[1])

        # 生成随机位置
        if position is None:
            map_width, map_height = self.config.world.map_size
            position = (
                random.randint(0, map_width),
                random.randint(0, map_height),
            )

        # 创建角色
        character = create_character(
            name=name or self._generate_random_name(),
            health=health,
            spirit_power=spirit_power,
            consciousness=consciousness,
            position=position,
            start_items=self.config.characters.start_items.copy(),
        )

        return character

    def _generate_random_name(self) -> str:
        """生成随机角色名称

        Returns:
            随机名称
        """
        import random

        surnames = ["李", "王", "张", "刘", "陈", "杨", "赵", "黄", "周", "吴"]
        names = ["青云", "清风", "明月", "长风", "白云", "灵雨", "天行", "子轩", "文渊", "浩然"]

        surname = random.choice(surnames)
        name = random.choice(names)

        return surname + name

    def get_world_info(self) -> Dict:
        """获取世界信息（用于AI提示词）

        Returns:
            世界信息字典
        """
        return {
            "name": self.config.world.name,
            "description": self.config.world.description,
            "round": self.current_round,
            "alive_count": len(self.get_alive_characters()),
            "dead_count": len(self.get_dead_characters()),
            "total_count": len(self.characters),
        }

    def get_character_positions(self) -> Dict[str, tuple]:
        """获取所有角色位置

        Returns:
            角色ID到位置的映射
        """
        return {char.id: char.position for char in self.characters}

    def check_position_valid(self, position: tuple) -> bool:
        """检查位置是否有效

        Args:
            position: 位置坐标

        Returns:
            位置是否有效
        """
        map_width, map_height = self.config.world.map_size
        x, y = position
        return 0 <= x <= map_width and 0 <= y <= map_height

    def distance_between(self, pos1: tuple, pos2: tuple) -> float:
        """计算两点距离

        Args:
            pos1: 位置1
            pos2: 位置2

        Returns:
            距离
        """
        import math
        return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

    def get_nearby_characters(
        self,
        center_position: tuple,
        radius: float,
    ) -> List[Character]:
        """获取指定半径范围内的角色

        Args:
            center_position: 中心位置
            radius: 半径

        Returns:
            附近的角色列表
        """
        nearby = []
        for char in self.characters:
            if not char.is_alive:
                continue
            if self.distance_between(center_position, char.position) <= radius:
                nearby.append(char)
        return nearby

    def start(self) -> None:
        """开始游戏"""
        self.is_running = True
        self.is_paused = False
        self.current_round = 0

        self.event_manager.emit(
            event_type=EventType.GAME_START,
            description="游戏开始",
            data={"world": self.get_world_info()},
        )

    def pause(self) -> None:
        """暂停游戏"""
        self.is_paused = True

    def resume(self) -> None:
        """继续游戏"""
        self.is_paused = False

    def stop(self) -> None:
        """停止游戏"""
        self.is_running = False

        self.event_manager.emit(
            event_type=EventType.GAME_END,
            description="游戏结束",
            data={"world": self.get_world_info()},
        )

    def next_round(self) -> None:
        """进入下一轮"""
        self.current_round += 1

        self.event_manager.emit(
            event_type=EventType.ROUND_START,
            description=f"第 {self.current_round} 轮开始",
            data={"round": self.current_round},
        )

    def end_round(self) -> None:
        """结束本轮"""
        self.event_manager.emit(
            event_type=EventType.ROUND_END,
            description=f"第 {self.current_round} 轮结束",
            data={"round": self.current_round},
        )

    def to_dict(self) -> Dict:
        """转换为字典（用于保存状态）

        Returns:
            世界状态字典
        """
        return {
            "current_round": self.current_round,
            "is_running": self.is_running,
            "is_paused": self.is_paused,
            "characters": [char.to_dict() for char in self.characters],
            "world_info": self.get_world_info(),
        }
