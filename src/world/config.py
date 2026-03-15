"""
YAML 配置加载器模块
"""
from pathlib import Path
from typing import Any
import yaml


class Config:
    """游戏配置管理器"""

    def __init__(self, config_path: str | Path = "config.yaml"):
        self.config_path = Path(config_path)
        self._data: dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """加载 YAML 配置文件"""
        if not self.config_path.exists():
            raise FileNotFoundError(f"配置文件不存在: {self.config_path}")

        with open(self.config_path, "r", encoding="utf-8") as f:
            self._data = yaml.safe_load(f)

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值

        Args:
            key: 配置键，支持点号分隔，如 "world.name"
            default: 默认值

        Returns:
            配置值
        """
        keys = key.split(".")
        value = self._data

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_nested(self, *keys: str, default: Any = None) -> Any:
        """
        获取嵌套配置值

        Args:
            *keys: 配置键列表
            default: 默认值

        Returns:
            配置值
        """
        value = self._data
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value

    @property
    def world(self) -> dict[str, Any]:
        """世界配置"""
        return self.get("world", {})

    @property
    def realms(self) -> dict[str, Any]:
        """境界配置"""
        return self.get("realms", {})

    @property
    def character(self) -> dict[str, Any]:
        """角色配置"""
        return self.get("character", {})

    @property
    def combat(self) -> dict[str, Any]:
        """战斗配置"""
        return self.get("combat", {})

    @property
    def ai(self) -> dict[str, Any]:
        """AI 配置"""
        return self.get("ai", {})

    @property
    def detection(self) -> dict[str, Any]:
        """探测配置"""
        return self.get("detection", {})

    def reload(self) -> None:
        """重新加载配置"""
        self._load_config()
