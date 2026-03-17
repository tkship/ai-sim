"""Main game loop orchestration."""

from __future__ import annotations

import asyncio
from typing import Any

from ..ai import AICoordinator, AIInterface, PromptBuilder
from ..character import Character
from ..interaction import InteractionDetector
from ..realm import BreakthroughSystem
from ..ui import Colors, UIRenderer
from ..world import Config, Database, GameState, KeywordRetriever, SaveManager
from .world import World


class GameLoop:
    """Game loop and top-level orchestration."""

    def __init__(self, config: Config):
        self.config = config
        self.db = Database()
        self.world = World(config)
        self.retriever = KeywordRetriever(self.db)
        self.save_manager = SaveManager(self.db, config)

        self.ai_interface = AIInterface()
        self.prompt_builder = PromptBuilder()
        self.ai_coordinator = AICoordinator(self.ai_interface, self.prompt_builder)
        self.interaction_detector = InteractionDetector()
        self.breakthrough_system = BreakthroughSystem(config)
        self.ui: UIRenderer | None = None

        self.running = False
        self.paused = False

    def init_ui(self) -> None:
        self.ui = UIRenderer()
        self.ui.init()

    def add_character(self, character: Character) -> None:
        self.world.add_character(character)

    async def run(self) -> None:
        self.running = True
        self.world.add_scene_log("游戏开始...")

        try:
            while self.running:
                if self.ui and self.ui.should_quit():
                    break

                if not self.paused:
                    await self._do_one_cycle()

                if self.ui:
                    self._render_ui()

                await asyncio.sleep(0.1)
        finally:
            self.running = False
            if self.ui:
                self.ui.close()

    async def _do_one_cycle(self) -> None:
        new_day = self.world.advance_time()
        if new_day:
            self.world.add_scene_log(f"新的一天到来：{self.world.time.display}")

        all_characters = self.world.get_all_characters()
        groups = self.interaction_detector.form_groups(all_characters)
        independent = self.interaction_detector.get_independent_characters(all_characters, groups)

        treasures_data, techniques_data = self._load_ai_knowledge(all_characters)
        for character in all_characters:
            synced = character.sync_treasure_templates(treasures_data)
            synced = synced.sync_technique_templates(techniques_data)
            self.world.update_character(synced)

        environment = self.world.get_environment_dict()

        for group in groups:
            await self._process_ai_group(
                group.characters,
                environment,
                treasures_data,
                techniques_data,
            )

        for character in independent:
            await self._process_ai_group(
                [character],
                environment,
                treasures_data,
                techniques_data,
            )

        self._process_breakthroughs()

    def _load_ai_knowledge(
        self,
        characters: list[Character],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        treasure_names = set()
        technique_names = set()
        for character in characters:
            treasure_names.update(character.equipment.values())
            technique_names.update(character.techniques.keys())

        data = self.retriever.retrieve_by_item_names(list(treasure_names | technique_names))
        treasures = {entry["name"]: entry for entry in data.get("treasures", [])}
        techniques = {entry["name"]: entry for entry in data.get("techniques", [])}
        return treasures, techniques

    async def _process_ai_group(
        self,
        characters: list[Character],
        environment: dict[str, Any],
        treasures_data: dict[str, Any],
        techniques_data: dict[str, Any],
    ) -> None:
        result = await self.ai_coordinator.process_character_group(
            characters,
            environment,
            treasures_data,
            techniques_data,
        )

        if result.audit_result and result.audit_result.ok and result.audit_result.update is not None:
            update = result.audit_result.update
            if update.scene_summary:
                self.world.add_scene_log(update.scene_summary)
            if update.scene_description:
                self.world.add_scene_log(update.scene_description)
            for character in result.updated_characters:
                self.world.update_character(character)
            return

        if result.audit_result and not result.audit_result.ok:
            for issue in result.audit_result.errors:
                self.world.add_scene_log(f"AI审计失败: {issue.message}")

    def _process_breakthroughs(self) -> None:
        if not self.breakthrough_system.should_attempt_breakthrough(self.world.time.total_cycles):
            return

        for character in self.world.get_all_characters():
            if character.realm.can_progress_minor():
                new_character, result = self.breakthrough_system.try_minor_breakthrough(character)
                if result.success and result.new_realm:
                    self.world.add_scene_log(f"{character.name} 突破到 {result.new_realm.full_name}！")
                    self.world.update_character(new_character)
            elif character.realm.can_progress_major():
                new_character, result = self.breakthrough_system.try_major_breakthrough(character)
                if result.success and result.new_realm:
                    self.world.add_scene_log(f"{character.name} 突破到 {result.new_realm.full_name}！")
                    self.world.update_character(new_character)
                elif result.penalties:
                    for penalty in result.penalties:
                        self.world.add_scene_log(f"{character.name} 突破失败：{penalty}")
                    self.world.update_character(new_character)

    def _render_ui(self) -> None:
        if not self.ui:
            return

        self.ui.clear()
        self.ui.draw_text(self.world.time.display, 600, 10, Colors.GOLD, "title", "center")

        characters = self.world.get_all_characters()
        for index, character in enumerate(characters[:2]):
            x = 10
            y = 60 + index * 220
            self.ui.draw_character_info(character, x, y, 380)

        if characters:
            self.ui.draw_map(self.world.map, characters, 10, 500, 380, 145)
            self.ui.draw_inventory(characters[0], 10, 655, 380, 125)

        self.ui.draw_scene_log(self.world.scene_logs, 410, 60, 780, 720)
        self.ui.present()

    def save_game(self, slot: int = 1) -> bool:
        state = GameState()
        state.current_year = self.world.time.year
        state.current_month = self.world.time.month
        state.current_day = self.world.time.day
        state.cycle_count = self.world.time.total_cycles
        state.characters = {character.id: character.to_save_dict() for character in self.world.get_all_characters()}

        success = self.save_manager.save_game(state, slot)
        if success:
            self.world.add_scene_log(f"已保存到存档位 {slot}")
        else:
            self.world.add_scene_log(f"存档失败（槽位 {slot}）")
        return success

    def load_game(self, slot: int = 1) -> bool:
        state = self.save_manager.load_game(slot)
        if not state:
            self.world.add_scene_log(f"读取存档失败（槽位 {slot}）")
            return False

        self.world.time.year = state.current_year
        self.world.time.month = state.current_month
        self.world.time.day = state.current_day
        self.world.time.total_cycles = state.cycle_count
        self.world.time.cycle = state.cycle_count % self.config.world.get("cycles_per_day", 12)

        self.world.characters = {}
        for payload in state.characters.values():
            self.world.add_character(Character.from_save_dict(payload))

        self.world.add_scene_log(f"已加载存档位 {slot}")
        return True
