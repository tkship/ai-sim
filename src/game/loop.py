"""
游戏主循环模块
"""
import asyncio
from typing import Optional, Dict, Any, List
from .world import World
from ..world import Config, Database, KeywordRetriever
from ..character import Character
from ..ai import AIInterface, AICoordinator, PromptBuilder
from ..interaction import InteractionDetector
from ..realm import BreakthroughSystem
from ..ui import UIRenderer, Colors


class GameLoop:
    """游戏主循环"""

    def __init__(self, config: Config):
        self.config = config
        self.db = Database()
        self.world = World(config)
        self.retriever = KeywordRetriever(self.db)

        # 系统初始化
        self.ai_interface = AIInterface()
        self.prompt_builder = PromptBuilder()
        self.ai_coordinator = AICoordinator(self.ai_interface, self.prompt_builder)
        self.interaction_detector = InteractionDetector()
        self.breakthrough_system = BreakthroughSystem(config)
        self.ui: Optional[UIRenderer] = None

        self.running = False
        self.paused = False

    def init_ui(self) -> None:
        """初始化 UI"""
        self.ui = UIRenderer()
        self.ui.init()

    def add_character(self, character: Character) -> None:
        """添加角色"""
        self.world.add_character(character)

    async def run(self) -> None:
        """运行游戏主循环"""
        self.running = True
        self.world.add_scene_log("游戏开始...")

        try:
            while self.running:
                # 检查退出
                if self.ui and self.ui.should_quit():
                    break

                if not self.paused:
                    await self._do_one_cycle()

                # 渲染 UI
                if self.ui:
                    self._render_ui()

                await asyncio.sleep(0.1)

        finally:
            self.running = False
            if self.ui:
                self.ui.close()

    async def _do_one_cycle(self) -> None:
        """执行一个游戏循环"""
        # 1. 更新世界时间
        new_day = self.world.advance_time()
        if new_day:
            self.world.add_scene_log(f"新的一天到来：{self.world.time.display}")

        # 2. 检测角色交互
        all_chars = self.world.get_all_characters()
        groups = self.interaction_detector.form_groups(all_chars)
        independent = self.interaction_detector.get_independent_characters(all_chars, groups)

        # 获取法宝和功法数据
        treasure_names = set()
        technique_names = set()
        for char in all_chars:
            treasure_names.update(char.equipment.values())
            technique_names.update(char.techniques.keys())

        item_data = self.retriever.retrieve_by_item_names(list(treasure_names))
        treasures_data = {t["name"]: t for t in item_data.get("treasures", [])}
        techniques_data = {t["name"]: t for t in item_data.get("techniques", [])}

        env = self.world.get_environment_dict()

        # 3. 处理交互组
        for group in groups:
            new_chars, response, logs = await self.ai_coordinator.process_interaction_group(
                group.characters, env, treasures_data, techniques_data
            )

            if response:
                if response.scene_description:
                    self.world.add_scene_log(response.scene_description)

                for char in new_chars:
                    self.world.update_character(char)

        # 4. 处理独立角色
        for char in independent:
            new_char, response, logs = await self.ai_coordinator.process_single_character(
                char, env, treasures_data, techniques_data
            )

            if response:
                if response.scene_description:
                    self.world.add_scene_log(response.scene_description)

                self.world.update_character(new_char)

        # 5. 检查境界突破
        if self.breakthrough_system.should_attempt_breakthrough(self.world.time.cycle):
            for char in self.world.get_all_characters():
                if char.realm.can_progress_minor():
                    new_char, result = self.breakthrough_system.try_minor_breakthrough(char)
                    if result.success and result.new_realm:
                        self.world.add_scene_log(f"{char.name} 突破到 {result.new_realm.full_name}！")
                        self.world.update_character(new_char)
                elif char.realm.can_progress_major():
                    new_char, result = self.breakthrough_system.try_major_breakthrough(char)
                    if result.success and result.new_realm:
                        self.world.add_scene_log(f"{char.name} 突破到 {result.new_realm.full_name}！")
                        self.world.update_character(new_char)
                    elif result.penalties:
                        for penalty in result.penalties:
                            self.world.add_scene_log(f"{char.name} 突破失败：{penalty}")
                        self.world.update_character(new_char)

    def _render_ui(self) -> None:
        """渲染 UI"""
        if not self.ui:
            return

        self.ui.clear()

        # 顶部时间显示
        self.ui.draw_text(self.world.time.display, 600, 10, Colors.GOLD, "title", "center")

        # 角色信息（左侧）
        chars = self.world.get_all_characters()
        for i, char in enumerate(chars[:2]):  # 最多显示2个角色
            x = 10
            y = 60 + i * 220
            self.ui.draw_character_info(char, x, y, 380)

        # 物品栏（左中）
        if chars:
            self.ui.draw_inventory(chars[0], 10, 500, 380, 280)

        # 场景日志（右侧）
        self.ui.draw_scene_log(self.world.scene_logs, 410, 60, 780, 720)

        self.ui.present()

    def save_game(self, slot: int = 1) -> bool:
        """保存游戏（简化版）"""
        # 暂时简化实现
        self.world.add_scene_log(f"存档功能开发中...")
        return True

    def load_game(self, slot: int = 1) -> bool:
        """加载游戏（简化版）"""
        # 暂时简化实现
        self.world.add_scene_log(f"读档功能开发中...")
        return False
