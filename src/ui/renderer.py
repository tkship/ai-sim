"""
UI 渲染器模块
"""
import pygame
from typing import Optional, List
from ..character import Character
from ..world import WorldMap


class Colors:
    """颜色定义"""
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    LIGHT_GRAY = (192, 192, 192)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    GOLD = (255, 215, 0)
    CYAN = (0, 255, 255)
    ORANGE = (255, 165, 0)


class UIRenderer:
    """UI 渲染器"""

    def __init__(self, screen_width: int = 1200, screen_height: int = 800):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen: Optional[pygame.Surface] = None
        self.fonts: dict[str, pygame.font.Font] = {}
        self.clock = pygame.time.Clock()

    def init(self) -> None:
        """初始化 pygame 和 UI"""
        pygame.init()
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("修仙 AI 模拟器")

        # 初始化字体
        self.fonts["small"] = pygame.font.SysFont("SimHei", 16)
        self.fonts["normal"] = pygame.font.SysFont("SimHei", 20)
        self.fonts["large"] = pygame.font.SysFont("SimHei", 28)
        self.fonts["title"] = pygame.font.SysFont("SimHei", 36, bold=True)

    def clear(self) -> None:
        """清屏"""
        if self.screen:
            self.screen.fill(Colors.BLACK)

    def present(self) -> None:
        """刷新显示"""
        if self.screen:
            pygame.display.flip()
            self.clock.tick(30)

    def draw_text(
        self,
        text: str,
        x: int,
        y: int,
        color: tuple = Colors.WHITE,
        font_size: str = "normal",
        align: str = "left"
    ) -> None:
        """绘制文本"""
        if not self.screen or text is None:
            return

        font = self.fonts.get(font_size, self.fonts["normal"])
        text_surface = font.render(str(text), True, color)

        if align == "center":
            x = x - text_surface.get_width() // 2
        elif align == "right":
            x = x - text_surface.get_width()

        self.screen.blit(text_surface, (x, y))

    def draw_panel(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        title: str = "",
        color: tuple = Colors.DARK_GRAY
    ) -> None:
        """绘制面板"""
        if not self.screen:
            return

        # 面板背景
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        # 面板边框
        pygame.draw.rect(self.screen, Colors.GRAY, (x, y, width, height), 2)

        # 标题
        if title:
            self.draw_text(title, x + 10, y + 5, Colors.GOLD, "large")

    def draw_progress_bar(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        current: int,
        maximum: int,
        color: tuple = Colors.GREEN,
        label: str = ""
    ) -> None:
        """绘制进度条"""
        if not self.screen:
            return

        # 背景
        pygame.draw.rect(self.screen, Colors.DARK_GRAY, (x, y, width, height))
        pygame.draw.rect(self.screen, Colors.GRAY, (x, y, width, height), 1)

        # 进度
        ratio = min(1.0, max(0.0, current / maximum if maximum > 0 else 0))
        progress_width = int(width * ratio)
        pygame.draw.rect(self.screen, color, (x + 1, y + 1, progress_width - 2, height - 2))

        # 标签
        if label:
            label_text = f"{label}: {current}/{maximum}"
            self.draw_text(label_text, x + width // 2, y + height // 2 - 8, Colors.WHITE, "small", "center")

    def draw_character_info(self, character: Character, x: int, y: int, width: int) -> None:
        """绘制角色信息面板"""
        if not self.screen:
            return

        panel_height = 200
        self.draw_panel(x, y, width, panel_height, f"【{character.name}】")

        # 境界
        self.draw_text(f"境界: {character.realm.full_name}", x + 10, y + 40, Colors.CYAN)
        self.draw_text(f"灵根: {character.spirit_root.display_name}", x + 10, y + 65, Colors.CYAN)
        self.draw_text(
            f"坐标: ({character.position.x:.1f}, {character.position.y:.1f})",
            x + 10,
            y + 85,
            Colors.LIGHT_GRAY,
            "small",
        )

        # 进度条
        bar_width = width - 20
        bar_x = x + 10

        # 血量
        hp_color = Colors.RED if character.attributes.hp.ratio < 0.3 else Colors.GREEN
        self.draw_progress_bar(bar_x, y + 110, bar_width, 20,
                                character.attributes.hp.current, character.attributes.hp.max,
                                hp_color, "血量")

        # 灵力
        self.draw_progress_bar(bar_x, y + 140, bar_width, 20,
                                character.attributes.mp.current, character.attributes.mp.max,
                                Colors.BLUE, "灵力")

        # 神识
        self.draw_progress_bar(bar_x, y + 170, bar_width, 20,
                                character.attributes.spirit.current, character.attributes.spirit.max,
                                Colors.GOLD, "神识")

    def draw_map(self, world_map: WorldMap, characters: List[Character], x: int, y: int, width: int, height: int) -> None:
        """绘制地图面板和角色坐标。"""
        if not self.screen:
            return

        self.draw_panel(x, y, width, height, f"【地图 - {world_map.name}】")
        map_margin = 12
        map_x = x + map_margin
        map_y = y + 38
        map_w = width - map_margin * 2
        map_h = height - 68

        pygame.draw.rect(self.screen, Colors.BLACK, (map_x, map_y, map_w, map_h))
        pygame.draw.rect(self.screen, Colors.GRAY, (map_x, map_y, map_w, map_h), 1)

        # 简单网格辅助观察位置关系
        for i in range(1, 4):
            grid_x = map_x + int(map_w * i / 4)
            grid_y = map_y + int(map_h * i / 4)
            pygame.draw.line(self.screen, Colors.DARK_GRAY, (grid_x, map_y), (grid_x, map_y + map_h), 1)
            pygame.draw.line(self.screen, Colors.DARK_GRAY, (map_x, grid_y), (map_x + map_w, grid_y), 1)

        for idx, char in enumerate(characters):
            x_ratio, y_ratio = world_map.normalize(char.position)
            dot_x = map_x + int(x_ratio * map_w)
            dot_y = map_y + map_h - int(y_ratio * map_h)
            color = Colors.ORANGE if idx == 0 else Colors.CYAN
            pygame.draw.circle(self.screen, color, (dot_x, dot_y), 6)
            self.draw_text(char.name, dot_x + 8, dot_y - 8, color, "small")

        footer = f"x:[{world_map.min_x:.0f},{world_map.max_x:.0f}] y:[{world_map.min_y:.0f},{world_map.max_y:.0f}]"
        self.draw_text(footer, x + 10, y + height - 24, Colors.LIGHT_GRAY, "small")

    def draw_scene_log(self, logs: List[str], x: int, y: int, width: int, height: int) -> None:
        """绘制场景日志"""
        if not self.screen:
            return

        self.draw_panel(x, y, width, height, "【场景描述】")

        line_y = y + 40
        line_height = 25
        max_lines = (height - 50) // line_height

        # 只显示最近的日志
        recent_logs = logs[-max_lines:] if logs else []

        for i, log in enumerate(recent_logs):
            self.draw_text(log, x + 10, line_y + i * line_height, Colors.WHITE, "small")

    def draw_inventory(self, character: Character, x: int, y: int, width: int, height: int) -> None:
        """绘制物品栏"""
        if not self.screen:
            return

        self.draw_panel(x, y, width, height, "【物品栏】")

        line_y = y + 40
        line_height = 22

        if character.inventory:
            for item_name, count in character.inventory.items():
                self.draw_text(f"• {item_name} ×{count}", x + 10, line_y, Colors.WHITE, "small")
                line_y += line_height
                if line_y > y + height - 20:
                    break
        else:
            self.draw_text("(空)", x + 10, line_y, Colors.GRAY, "small")

    def should_quit(self) -> bool:
        """检查是否应该退出"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
        return False

    def close(self) -> None:
        """关闭 UI"""
        pygame.quit()
