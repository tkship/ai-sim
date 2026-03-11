"""配置加载模块

从 YAML 文件加载游戏配置
"""
import yaml
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
import os


@dataclass
class AIConfig:
    """AI 配置类"""
    url: str = "https://api.example.com/v1/chat"
    api_key: str = ""
    format: str = "openai"
    model: str = "gpt-3.5-turbo"
    timeout: int = 30


@dataclass
class WorldConfig:
    """世界配置类"""
    name: str = "灵虚大陆"
    description: str = ""
    map_size: list = None

    def __post_init__(self):
        if self.map_size is None:
            self.map_size = [1000, 1000]


@dataclass
class CharacterConfig:
    """角色配置类"""
    health_range: list = None
    spirit_power_range: list = None
    consciousness_range: list = None
    default_realm: Dict = None
    start_items: list = None

    def __post_init__(self):
        if self.health_range is None:
            self.health_range = [100, 200]
        if self.spirit_power_range is None:
            self.spirit_power_range = [50, 100]
        if self.consciousness_range is None:
            self.consciousness_range = [10, 50]
        if self.default_realm is None:
            self.default_realm = {"major": "炼气", "minor": "初期"}
        if self.start_items is None:
            self.start_items = ["基础飞剑", "回灵丹", "炼气决"]


@dataclass
class GameConfig:
    """游戏循环配置类"""
    round_interval: int = 1000
    auto_start: bool = True


@dataclass
class UIConfig:
    """界面配置类"""
    window_size: list = None
    font_size: int = 16
    colors: Dict = None

    def __post_init__(self):
        if self.window_size is None:
            self.window_size = [1200, 800]
        if self.colors is None:
            self.colors = {
                "background": "#2c3e50",
                "text": "#ecf0f1",
                "panel": "#34495e",
                "border": "#7f8c8d",
            }


@dataclass
class Config:
    """主配置类

    包含所有游戏配置
    """
    ai: AIConfig = field(default_factory=AIConfig)
    world: WorldConfig = field(default_factory=WorldConfig)
    characters: CharacterConfig = field(default_factory=CharacterConfig)
    game: GameConfig = field(default_factory=GameConfig)
    ui: UIConfig = field(default_factory=UIConfig)

    config_file_path: str = ""


class ConfigLoader:
    """配置加载器类

    从 YAML 文件加载配置
    """

    def __init__(self):
        """初始化配置加载器"""
        self.config: Optional[Config] = None

    def load(self, config_path: str = "config.yaml") -> Config:
        """加载配置文件

        Args:
            config_path: 配置文件路径

        Returns:
            配置对象

        Raises:
            FileNotFoundError: 配置文件不存在
            yaml.YAMLError: YAML 解析错误
        """
        # 检查文件是否存在
        if not os.path.exists(config_path):
            # 返回默认配置
            self.config = Config()
            self.config.config_file_path = config_path
            return self.config

        # 读取配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        # 创建配置对象
        self.config = Config()

        # 加载 AI 配置
        if "ai" in data:
            ai_data = data["ai"]
            self.config.ai = AIConfig(
                url=ai_data.get("url", "https://api.example.com/v1/chat"),
                api_key=ai_data.get("api_key", ""),
                format=ai_data.get("format", "openai"),
                model=ai_data.get("model", "gpt-3.5-turbo"),
                timeout=ai_data.get("timeout", 30),
            )

        # 加载世界配置
        if "world" in data:
            world_data = data["world"]
            self.config.world = WorldConfig(
                name=world_data.get("name", "灵虚大陆"),
                description=world_data.get("description", ""),
                map_size=world_data.get("map_size", [1000, 1000]),
            )

        # 加载角色配置
        if "characters" in data:
            char_data = data["characters"]
            self.config.characters = CharacterConfig(
                health_range=char_data.get("health_range", [100, 200]),
                spirit_power_range=char_data.get("spirit_power_range", [50, 100]),
                consciousness_range=char_data.get("consciousness_range", [10, 50]),
                default_realm=char_data.get("default_realm", {"major": "炼气", "minor": "初期"}),
                start_items=char_data.get("start_items", ["基础飞剑", "回灵丹", "炼气决"]),
            )
        else:
            # 检查 items 配置中的 start_items
            if "items" in data and "start_items" in data["items"]:
                self.config.characters.start_items = data["items"]["start_items"]

        # 加载游戏配置
        if "game" in data:
            game_data = data["game"]
            self.config.game = GameConfig(
                round_interval=game_data.get("round_interval", 1000),
                auto_start=game_data.get("auto_start", True),
            )

        # 加载界面配置
        if "ui" in data:
            ui_data = data["ui"]
            self.config.ui = UIConfig(
                window_size=ui_data.get("window_size", [1200, 800]),
                font_size=ui_data.get("font_size", 16),
                colors=ui_data.get("colors", {
                    "background": "#2c3e50",
                    "text": "#ecf0f1",
                    "panel": "#34495e",
                    "border": "#7f8c8d",
                }),
            )

        self.config.config_file_path = config_path
        return self.config

    def save(self, config_path: str = None) -> bool:
        """保存配置到文件

        Args:
            config_path: 配置文件路径，如果为 None 则使用加载时的路径

        Returns:
            是否保存成功
        """
        if self.config is None:
            return False

        if config_path is None:
            config_path = self.config.config_file_path

        if not config_path:
            return False

        # 转换为字典
        data = {
            "ai": {
                "url": self.config.ai.url,
                "api_key": self.config.ai.api_key,
                "format": self.config.ai.format,
                "model": self.config.ai.model,
                "timeout": self.config.ai.timeout,
            },
            "world": {
                "name": self.config.world.name,
                "description": self.config.world.description,
                "map_size": self.config.world.map_size,
            },
            "characters": {
                "health_range": self.config.characters.health_range,
                "spirit_power_range": self.config.characters.spirit_power_range,
                "consciousness_range": self.config.characters.consciousness_range,
                "default_realm": self.config.characters.default_realm,
                "start_items": self.config.characters.start_items,
            },
            "game": {
                "round_interval": self.config.game.round_interval,
                "auto_start": self.config.game.auto_start,
            },
            "ui": {
                "window_size": self.config.ui.window_size,
                "font_size": self.config.ui.font_size,
                "colors": self.config.ui.colors,
            },
        }

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(data, f, allow_unicode=True, sort_keys=False)
            return True
        except Exception:
            return False

    def get_config(self) -> Config:
        """获取当前配置

        Returns:
            配置对象
        """
        if self.config is None:
            self.load()
        return self.config


# 全局配置加载器实例
_global_loader: Optional[ConfigLoader] = None


def load_config(config_path: str = "config.yaml") -> Config:
    """加载配置（使用全局加载器）

    Args:
        config_path: 配置文件路径

    Returns:
        配置对象
    """
    global _global_loader
    if _global_loader is None:
        _global_loader = ConfigLoader()
    return _global_loader.load(config_path)


def get_config() -> Config:
    """获取当前配置（使用全局加载器）

    Returns:
        配置对象
    """
    global _global_loader
    if _global_loader is None:
        _global_loader = ConfigLoader()
    return _global_loader.get_config()
