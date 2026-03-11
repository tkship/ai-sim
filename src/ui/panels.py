"""面板渲染模块

渲染角色状态面板、日志区域等UI组件
"""
import pygame
from typing import List, TYPE_CHECKING
from game.world import World

if TYPE_CHECKING:
    from ui.display import Display
else:
    Display = object


class PanelManager:
    """面板管理器

    负责渲染所有UI面板
    """

    def __init__(self, display: Display):
        """初始化面板管理器

        Args:
            display: 主显示对象
        """
        self.display = display
        self.panels = []

        # 面板布局配置
        self._setup_panels()

    def _setup_panels(self) -> None:
        """设置面板布局"""
        window_width = self.display.window_width
        window_height = self.display.window_height

        # 创建角色面板（左侧）
        for i in range(4):  # 最多显示4个角色面板
            panel = CharacterPanel(
                display=self.display,
                rect=(10, 10 + i * 190, 280, 180),
                character_index=i,
            )
            self.panels.append(panel)

        # 创建世界信息面板（顶部中间）
        world_panel = WorldInfoPanel(
            display=self.display,
            rect=(300, 10, 300, 100),
        )
        self.panels.append(world_panel)

        # 创建日志面板（底部）
        log_panel = LogPanel(
            display=self.display,
            rect=(300, 120, window_width - 310, window_height - 130),
        )
        self.panels.append(log_panel)

        # 创建控制提示面板（右上角）
        hint_panel = HintPanel(
            display=self.display,
            rect=(window_width - 280, 10, 270, 100),
        )
        self.panels.append(hint_panel)

    def render(self, world: World) -> None:
        """渲染所有面板

        Args:
            world: 游戏世界
        """
        for panel in self.panels:
            panel.render(world)


class BasePanel:
    """面板基类"""

    def __init__(self, display: Display, rect: tuple):
        """初始化面板

        Args:
            display: 主显示对象
            rect: 面板区域 (x, y, width, height)
        """
        self.display = display
        self.rect = rect

    def render(self, world: World) -> None:
        """渲染面板

        Args:
            world: 游戏世界
        """
        # 绘制面板背景
        self.display.draw_rect(self.rect, self.display.colors["panel"])

        # 绘制边框
        self.display.draw_rect(self.rect, self.display.colors["border"], 2)


class CharacterPanel(BasePanel):
    """角色状态面板"""

    def __init__(self, display: Display, rect: tuple, character_index: int = 0):
        """初始化角色面板

        Args:
            display: 主显示对象
            rect: 面板区域
            character_index: 角色索引
        """
        super().__init__(display, rect)
        self.character_index = character_index

    def render(self, world: World) -> None:
        """渲染角色面板

        Args:
            world: 游戏世界
        """
        # 绘制背景和边框
        super().render(world)

        # 获取角色
        characters = world.get_alive_characters() + world.get_dead_characters()
        if self.character_index >= len(characters):
            # 没有角色
            self.display.draw_text(
                f"角色 {self.character_index + 1}: 无",
                (self.rect[0] + 10, self.rect[1] + 10),
            )
            return

        character = characters[self.character_index]

        # 角色名称和状态
        x = self.rect[0] + 10
        y = self.rect[1] + 10

        status_text = "存活" if character.is_alive else "死亡"
        status_color = self.display.colors["green"] if character.is_alive else self.display.colors["red"]

        name_text = f"{character.name} ({status_text})"
        self.display.draw_text(name_text, (x, y), status_color)

        # 境界
        y += 25
        realm_text = f"境界: {character.realm.name}"
        self.display.draw_text(realm_text, (x, y))

        # 血量
        y += 25
        health_percent = character.attributes.health / character.attributes.max_health
        health_color = self._get_health_color(health_percent)
        health_text = f"血量: {character.attributes.health}/{character.attributes.max_health} ({int(health_percent * 100)}%)"
        self.display.draw_text(health_text, (x, y), health_color)

        # 绘制血量条
        y += 20
        self._draw_health_bar(x, y, 260, health_percent, health_color)

        # 灵力
        y += 15
        spirit_percent = character.attributes.spirit_power / character.attributes.max_spirit_power
        spirit_text = f"灵力: {character.attributes.spirit_power}/{character.attributes.max_spirit_power} ({int(spirit_percent * 100)}%)"
        self.display.draw_text(spirit_text, (x, y), self.display.colors["blue"])

        # 绘制灵力条
        y += 20
        self._draw_health_bar(x, y, 260, spirit_percent, self.display.colors["blue"])

        # 攻击力和防御力
        y += 15
        stats_text = f"攻: {character.total_attack_power}  防: {character.total_defense_power}"
        self.display.draw_text(stats_text, (x, y))

        # 装备
        y += 20
        artifact_text = f"法宝: {character.inventory.equipped_artifact.name if character.inventory.equipped_artifact else '无'}"
        self.display.draw_text(artifact_text, (x, y), self.display.colors["yellow"])

    def _get_health_color(self, percent: float) -> tuple:
        """根据血量百分比获取颜色

        Args:
            percent: 血量百分比

        Returns:
            颜色元组
        """
        if percent > 0.6:
            return self.display.colors["green"]
        elif percent > 0.3:
            return self.display.colors["yellow"]
        else:
            return self.display.colors["red"]

    def _draw_health_bar(self, x: int, y: int, width: int, percent: float, color: tuple) -> None:
        """绘制进度条

        Args:
            x: X 坐标
            y: Y 坐标
            width: 宽度
            percent: 进度百分比
            color: 颜色
        """
        # 背景
        self.display.draw_rect((x, y, width, 10), (50, 50, 50), 0)

        # 进度
        if percent > 0:
            fill_width = int(width * percent)
            self.display.draw_rect((x, y, fill_width, 10), color, 0)

        # 边框
        self.display.draw_rect((x, y, width, 10), self.display.colors["border"], 1)


class WorldInfoPanel(BasePanel):
    """世界信息面板"""

    def render(self, world: World) -> None:
        """渲染世界信息面板

        Args:
            world: 游戏世界
        """
        super().render(world)

        x = self.rect[0] + 10
        y = self.rect[1] + 10

        # 世界名称
        self.display.draw_text(
            f"世界: {world.config.world.name}",
            (x, y),
            self.display.colors["yellow"],
        )

        y += 25

        # 轮次
        self.display.draw_text(f"轮次: {world.current_round}", (x, y))

        y += 25

        # 状态
        status = "运行中" if world.is_running and not world.is_paused else "暂停" if world.is_paused else "停止"
        status_color = self.display.colors["green"] if world.is_running and not world.is_paused else self.display.colors["yellow"]
        self.display.draw_text(f"状态: {status}", (x, y), status_color)

        y += 25

        # 角色数量
        alive_count = len(world.get_alive_characters())
        dead_count = len(world.get_dead_characters())
        self.display.draw_text(f"存活: {alive_count}  死亡: {dead_count}", (x, y))


class LogPanel(BasePanel):
    """日志面板"""

    def __init__(self, display: Display, rect: tuple):
        """初始化日志面板

        Args:
            display: 主显示对象
            rect: 面板区域
        """
        super().__init__(display, rect)
        self.max_lines = 20

    def render(self, world: World) -> None:
        """渲染日志面板

        Args:
            world: 游戏世界
        """
        super().render(world)

        x = self.rect[0] + 10
        y = self.rect[1] + 10

        # 标题
        self.display.draw_text("=== 游戏日志 ===", (x, y), self.display.colors["yellow"])

        y += 25

        # 获取最近事件
        recent_events = world.event_manager.get_recent_events(self.max_lines)

        # 绘制事件
        for event in reversed(recent_events):
            event_text = f"[{event.timestamp.strftime('%H:%M:%S')}] {event.description}"

            # 截断过长的文本
            if len(event_text) > 50:
                event_text = event_text[:47] + "..."

            self.display.draw_text(event_text, (x, y))
            y += 20

            if y > self.rect[1] + self.rect[3] - 20:
                break


class HintPanel(BasePanel):
    """控制提示面板"""

    def render(self, world: World) -> None:
        """渲染控制提示面板

        Args:
            world: 游戏世界
        """
        super().render(world)

        x = self.rect[0] + 10
        y = self.rect[1] + 10

        # 标题
        self.display.draw_text("=== 操作提示 ===", (x, y), self.display.colors["yellow"])

        y += 25

        # 提示信息
        hints = [
            "空格键: 暂停/继续",
            "S 键: 单步执行",
            "ESC 键: 退出游戏",
        ]

        for hint in hints:
            self.display.draw_text(hint, (x, y))
            y += 20
