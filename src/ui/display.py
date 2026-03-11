"""主界面模块

Pygame 主窗口和事件处理
"""
import pygame
import sys
from typing import Optional, Callable
from game.config import Config
from game.world import World
from game.loop import GameLoop

from ui.panels import PanelManager
from ui.renderer import SceneRenderer


class Display:
    """主界面类

    负责初始化 Pygame、主窗口布局和事件处理
    """

    def __init__(self, config: Config):
        """初始化界面

        Args:
            config: 游戏配置
        """
        self.config = config
        self.screen = None
        self.clock = None
        self.is_running = False

        # 窗口大小
        self.window_width = config.ui.window_size[0]
        self.window_height = config.ui.window_size[1]

        # 颜色
        self.colors = {
            "background": self._hex_to_rgb(config.ui.colors.get("background", "#2c3e50")),
            "text": self._hex_to_rgb(config.ui.colors.get("text", "#ecf0f1")),
            "panel": self._hex_to_rgb(config.ui.colors.get("panel", "#34495e")),
            "border": self._hex_to_rgb(config.ui.colors.get("border", "#7f8c8d")),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "red": (231, 76, 60),
            "green": (46, 204, 113),
            "blue": (52, 152, 219),
            "yellow": (241, 196, 15),
        }

        # 字体
        self.font_size = config.ui.font_size
        self.font = None

        # 子组件
        self.panel_manager = None
        self.scene_renderer = None

        # 游戏循环引用
        self.game_loop: Optional[GameLoop] = None

        # 回调函数
        self.on_key_event: Optional[Callable] = None

    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """将十六进制颜色转换为 RGB 元组

        Args:
            hex_color: 十六进制颜色字符串

        Returns:
            RGB 元组
        """
        hex_color = hex_color.lstrip("#")
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    def init(self) -> bool:
        """初始化 Pygame

        Returns:
            是否初始化成功
        """
        try:
            pygame.init()
            pygame.display.set_caption(f"{self.config.world.name} - 修仙 AI 模拟")

            self.screen = pygame.display.set_mode(
                (self.window_width, self.window_height)
            )
            self.clock = pygame.time.Clock()

            # 尝试加载中文字体
            self.font = self._load_font()

            # 初始化子组件
            self.panel_manager = PanelManager(self)
            self.scene_renderer = SceneRenderer(self)

            self.is_running = True
            return True

        except Exception as e:
            print(f"初始化 Pygame 失败: {e}")
            return False

    def _load_font(self) -> pygame.font.Font:
        """加载字体（优先中文字体）"""

        # 尝试常见的中文字体
        font_names = [
            "simhei",  # 黑体
            "simkai",  # 楷体
            "simsun",  # 宋体
            "microsoftyahei",  # 微软雅黑
            "pingfangsc",  # 苹方
            "notosanscjksc",  # 思源黑体
            "arialunicode",  # Arial Unicode
        ]

        # 尝试加载系统字体
        available_fonts = pygame.font.get_fonts()
        for font_name in font_names:
            if font_name in available_fonts:
                try:
                    return pygame.font.SysFont(font_name, self.font_size)
                except Exception:
                    continue

        # 回退到默认字体
        return pygame.font.SysFont(None, self.font_size)

    def set_game_loop(self, game_loop: GameLoop) -> None:
        """设置游戏循环引用

        Args:
            game_loop: 游戏循环对象
        """
        self.game_loop = game_loop

    def set_key_event_callback(self, callback: Callable) -> None:
        """设置按键事件回调

        Args:
            callback: 回调函数
        """
        self.on_key_event = callback

    def handle_events(self) -> bool:
        """处理事件

        Returns:
            是否继续运行
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                # 触发回调
                if self.on_key_event:
                    self.on_key_event(event.key)

                # 默认按键处理
                self._handle_keydown(event.key)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mousedown(event.button, event.pos)

        return True

    def _handle_keydown(self, key: int) -> None:
        """处理按键

        Args:
            key: 按键码
        """
        # 空格键：暂停/继续
        if key == pygame.K_SPACE and self.game_loop:
            self.game_loop.toggle_pause()

        # S 键：单步执行
        elif key == pygame.K_s and self.game_loop:
            if self.game_loop.world.is_paused:
                self.game_loop.process_round()

    def _handle_mousedown(self, button: int, pos: tuple) -> None:
        """处理鼠标点击

        Args:
            button: 鼠标按键
            pos: 鼠标位置
        """
        # 可以在这里添加面板点击处理
        pass

    def render(self) -> None:
        """渲染一帧"""
        if not self.screen:
            return

        # 绘制背景
        self.screen.fill(self.colors["background"])

        # 渲染场景
        if self.scene_renderer and self.game_loop:
            self.scene_renderer.render(self.game_loop.world)

        # 渲染面板
        if self.panel_manager and self.game_loop:
            self.panel_manager.render(self.game_loop.world)

        # 更新显示
        pygame.display.flip()

    def run(self) -> None:
        """运行主循环"""
        if not self.init():
            return

        while self.is_running:
            # 处理事件
            if not self.handle_events():
                break

            # 处理游戏帧
            if self.game_loop:
                self.game_loop.run_frame()

            # 渲染
            self.render()

            # 控制帧率
            self.clock.tick(60)

        # 清理
        self.quit()

    def quit(self) -> None:
        """退出游戏"""
        self.is_running = False

        if self.game_loop:
            self.game_loop.stop()

        pygame.quit()
        sys.exit(0)

    def draw_text(
        self,
        text: str,
        position: tuple,
        color: tuple = None,
        font: pygame.font.Font = None,
    ) -> None:
        """绘制文本

        Args:
            text: 文本内容
            position: 位置 (x, y)
            color: 颜色
            font: 字体
        """
        if color is None:
            color = self.colors["text"]
        if font is None:
            font = self.font

        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, position)

    def draw_rect(
        self,
        rect: tuple,
        color: tuple = None,
        width: int = 0,
    ) -> None:
        """绘制矩形

        Args:
            rect: 矩形 (x, y, width, height)
            color: 颜色
            width: 线宽（0 表示填充）
        """
        if color is None:
            color = self.colors["panel"]

        pygame.draw.rect(self.screen, color, rect, width)

    def draw_line(
        self,
        start: tuple,
        end: tuple,
        color: tuple = None,
        width: int = 1,
    ) -> None:
        """绘制线条

        Args:
            start: 起点坐标
            end: 终点坐标
            color: 颜色
            width: 线宽
        """
        if color is None:
            color = self.colors["border"]

        pygame.draw.line(self.screen, color, start, end, width)
