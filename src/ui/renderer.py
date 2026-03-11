"""场景渲染模块

渲染游戏场景、角色位置可视化等
"""
import pygame
import math
from typing import TYPE_CHECKING
from game.world import World

if TYPE_CHECKING:
    from ui.display import Display
else:
    Display = object


class SceneRenderer:
    """场景渲染器

    负责渲染游戏场景和角色
    """

    def __init__(self, display: Display):
        """初始化场景渲染器

        Args:
            display: 主显示对象
        """
        self.display = display

        # 场景区域
        self.scene_rect = (300, 120, 600, 500)

        # 角色颜色
        self.character_colors = {
            0: (231, 76, 60),    # 红色
            1: (46, 204, 113),   # 绿色
            2: (52, 152, 219),   # 蓝色
            3: (241, 196, 15),   # 黄色
        }

    def render(self, world: World) -> None:
        """渲染场景

        Args:
            world: 游戏世界
        """
        if not self.display.screen:
            return

        # 绘制场景背景
        self._draw_scene_background()

        # 绘制角色
        self._draw_characters(world)

        # 绘制场景边框
        self.display.draw_rect(self.scene_rect, self.display.colors["border"], 2)

        # 绘制场景标题
        self._draw_scene_title(world)

    def _draw_scene_background(self) -> None:
        """绘制场景背景"""
        # 绘制深色背景
        self.display.draw_rect(self.scene_rect, (30, 30, 40))

        # 绘制网格（可选）
        x, y, width, height = self.scene_rect
        grid_size = 50

        # 垂直线
        for i in range(0, width, grid_size):
            line_x = x + i
            pygame.draw.line(
                self.display.screen,
                (50, 50, 60),
                (line_x, y),
                (line_x, y + height),
                1,
            )

        # 水平线
        for i in range(0, height, grid_size):
            line_y = y + i
            pygame.draw.line(
                self.display.screen,
                (50, 50, 60),
                (x, line_y),
                (x + width, line_y),
                1,
            )

    def _draw_characters(self, world: World) -> None:
        """绘制角色

        Args:
            world: 游戏世界
        """
        characters = world.characters
        if not characters:
            return

        # 获取世界地图大小
        map_width, map_height = world.config.world.map_size

        # 场景区域
        scene_x, scene_y, scene_width, scene_height = self.scene_rect

        # 计算缩放比例
        scale_x = scene_width / map_width
        scale_y = scene_height / map_height
        scale = min(scale_x, scale_y)

        # 居中偏移
        offset_x = scene_x + (scene_width - map_width * scale) / 2
        offset_y = scene_y + (scene_height - map_height * scale) / 2

        # 绘制每个角色
        for i, char in enumerate(characters):
            # 将角色位置转换到场景坐标
            char_x = offset_x + char.position[0] * scale
            char_y = offset_y + char.position[1] * scale

            # 确定角色颜色
            color = self.character_colors.get(i, self.display.colors["white"])

            # 绘制探测范围（半透明）
            self._draw_detection_range(char_x, char_y, char, scale)

            # 绘制角色圆点
            radius = 8
            pygame.draw.circle(
                self.display.screen,
                color,
                (int(char_x), int(char_y)),
                radius,
            )

            # 绘制角色名称
            name_text = char.name[:2]  # 只显示前两个字符
            self.display.draw_text(
                name_text,
                (int(char_x) - 10, int(char_y) - 20),
                color,
            )

            # 如果角色死亡，绘制死亡标记
            if not char.is_alive:
                self._draw_dead_mark(int(char_x), int(char_y))

    def _draw_detection_range(self, x: float, y: float, char, scale: float) -> None:
        """绘制探测范围

        Args:
            x: 角色X坐标
            y: 角色Y坐标
            char: 角色对象
            scale: 缩放比例
        """
        # 计算探测范围的半径
        detection_radius = char.detection_range * scale

        # 创建一个带透明度的表面
        surface = pygame.Surface(
            (int(detection_radius * 2), int(detection_radius * 2)),
            pygame.SRCALPHA,
        )

        # 绘制半透明圆
        pygame.draw.circle(
            surface,
            (100, 100, 100, 30),
            (int(detection_radius), int(detection_radius)),
            int(detection_radius),
        )

        # 将表面绘制到屏幕
        self.display.screen.blit(
            surface,
            (int(x - detection_radius), int(y - detection_radius)),
        )

    def _draw_dead_mark(self, x: int, y: int) -> None:
        """绘制死亡标记

        Args:
            x: X坐标
            y: Y坐标
        """
        # 绘制X形标记
        offset = 5
        pygame.draw.line(
            self.display.screen,
            self.display.colors["red"],
            (x - offset, y - offset),
            (x + offset, y + offset),
            2,
        )
        pygame.draw.line(
            self.display.screen,
            self.display.colors["red"],
            (x + offset, y - offset),
            (x - offset, y + offset),
            2,
        )

    def _draw_scene_title(self, world: World) -> None:
        """绘制场景标题

        Args:
            world: 游戏世界
        """
        scene_x, scene_y, scene_width, scene_height = self.scene_rect

        # 标题位置
        title_x = scene_x + 10
        title_y = scene_y + 10

        # 绘制标题背景
        title_rect = (title_x - 5, title_y - 5, 200, 25)
        self.display.draw_rect(title_rect, (40, 40, 50))

        # 绘制标题
        title_text = f"场景 - {world.config.world.name}"
        self.display.draw_text(
            title_text,
            (title_x, title_y),
            self.display.colors["yellow"],
        )


class MapRenderer:
    """地图渲染器

    负责渲染世界地图
    """

    def __init__(self, display: Display):
        """初始化地图渲染器

        Args:
            display: 主显示对象
        """
        self.display = display

    def render(self, world: World, rect: tuple) -> None:
        """渲染地图

        Args:
            world: 游戏世界
            rect: 地图区域 (x, y, width, height)
        """
        # 绘制地图背景
        self.display.draw_rect(rect, (40, 40, 50))

        # 绘制边框
        self.display.draw_rect(rect, self.display.colors["border"], 2)

        # 绘制角色点
        self._draw_character_dots(world, rect)

    def _draw_character_dots(self, world: World, rect: tuple) -> None:
        """绘制角色点

        Args:
            world: 游戏世界
            rect: 地图区域
        """
        characters = world.characters
        if not characters:
            return

        # 获取世界地图大小
        map_width, map_height = world.config.world.map_size

        # 地图区域
        map_x, map_y, map_width_ui, map_height_ui = rect

        # 计算缩放比例
        scale_x = map_width_ui / map_width
        scale_y = map_height_ui / map_height
        scale = min(scale_x, scale_y)

        # 居中偏移
        offset_x = map_x + (map_width_ui - map_width * scale) / 2
        offset_y = map_y + (map_height_ui - map_height * scale) / 2

        # 绘制每个角色
        for i, char in enumerate(characters):
            # 计算角色位置
            char_x = offset_x + char.position[0] * scale
            char_y = offset_y + char.position[1] * scale

            # 确定颜色
            if not char.is_alive:
                color = self.display.colors["red"]
            else:
                color = self.display.colors["green"]

            # 绘制点
            pygame.draw.circle(
                self.display.screen,
                color,
                (int(char_x), int(char_y)),
                3,
            )


class TextSceneRenderer:
    """文本场景渲染器

    使用文字描述场景状态（简单版本）
    """

    def __init__(self, display: Display):
        """初始化文本场景渲染器

        Args:
            display: 主显示对象
        """
        self.display = display

    def render(self, world: World, rect: tuple) -> None:
        """渲染文本场景

        Args:
            world: 游戏世界
            rect: 渲染区域
        """
        x, y, width, height = rect

        # 绘制背景
        self.display.draw_rect(rect, (30, 30, 40))
        self.display.draw_rect(rect, self.display.colors["border"], 2)

        # 绘制标题
        self.display.draw_text(
            "=== 场景状态 ===",
            (x + 10, y + 10),
            self.display.colors["yellow"],
        )

        # 绘制角色信息
        characters = world.characters
        current_y = y + 40

        for char in characters:
            status = "存活" if char.is_alive else "死亡"
            info = f"{char.name}: {status}, 位置({char.position[0]}, {char.position[1]}), 境界{char.realm.name}"

            self.display.draw_text(info, (x + 10, current_y))
            current_y += 25

            if current_y > y + height - 30:
                break

        # 如果角色太多，显示省略号
        if len(characters) * 25 > height - 50:
            self.display.draw_text("...", (x + 10, current_y))
