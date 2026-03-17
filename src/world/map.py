"""世界地图模型。"""
from dataclasses import dataclass
from typing import Any
from ..character import Position


@dataclass(frozen=True)
class WorldMap:
    """二维地图基础信息与坐标工具。"""

    name: str = "黑风岭"
    width: float = 120.0
    height: float = 80.0
    min_x: float = -60.0
    min_y: float = -40.0

    @staticmethod
    def from_config(data: dict[str, Any]) -> "WorldMap":
        """从配置读取地图参数。"""
        width = float(data.get("width", 120.0))
        height = float(data.get("height", 80.0))
        min_x = float(data.get("min_x", -width / 2.0))
        min_y = float(data.get("min_y", -height / 2.0))
        return WorldMap(
            name=str(data.get("name", "黑风岭")),
            width=max(1.0, width),
            height=max(1.0, height),
            min_x=min_x,
            min_y=min_y,
        )

    @property
    def max_x(self) -> float:
        return self.min_x + self.width

    @property
    def max_y(self) -> float:
        return self.min_y + self.height

    def clamp_position(self, position: Position) -> Position:
        """限制坐标在地图边界内。"""
        clamped_x = min(self.max_x, max(self.min_x, position.x))
        clamped_y = min(self.max_y, max(self.min_y, position.y))
        return Position(clamped_x, clamped_y)

    def normalize(self, position: Position) -> tuple[float, float]:
        """将地图坐标映射到 [0, 1] 范围。"""
        x_ratio = (position.x - self.min_x) / self.width
        y_ratio = (position.y - self.min_y) / self.height
        return (
            min(1.0, max(0.0, x_ratio)),
            min(1.0, max(0.0, y_ratio)),
        )

    def to_dict(self) -> dict[str, Any]:
        """转换为字典。"""
        return {
            "name": self.name,
            "width": self.width,
            "height": self.height,
            "min_x": self.min_x,
            "min_y": self.min_y,
            "max_x": self.max_x,
            "max_y": self.max_y,
        }
