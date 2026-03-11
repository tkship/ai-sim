"""主游戏循环模块

处理游戏的主要逻辑流程
"""
import time
import json
from typing import List, Optional, Dict, Any

from game.world import World
from game.config import Config
from character.character import Character
from interaction.detector import Detector
from interaction.combat import Combat
from interaction.event import EventType
from ai.interface import AIInterface, MockAIInterface
from ai.prompt import PromptBuilder, GroupPromptBuilder
from ai.parser import AIResponseParser


class GameLoop:
    """游戏循环类

    负责游戏的每一轮逻辑
    """

    def __init__(
        self,
        world: World,
        config: Config,
        use_mock_ai: bool = True,
    ):
        """初始化游戏循环

        Args:
            world: 游戏世界
            config: 游戏配置
            use_mock_ai: 是否使用 Mock AI（测试用）
        """
        self.world = world
        self.config = config
        self.use_mock_ai = use_mock_ai

        # 初始化各系统
        self.detector = Detector()
        self.combat = Combat()

        # 初始化 AI
        if use_mock_ai:
            self.ai_interface = MockAIInterface()
        else:
            self.ai_interface = AIInterface(
                url=config.ai.url,
                api_key=config.ai.api_key,
                format_type=config.ai.format,
                model=config.ai.model,
                timeout=config.ai.timeout,
            )

        self.prompt_builder = PromptBuilder(world.get_world_info())
        self.group_prompt_builder = GroupPromptBuilder(world.get_world_info())
        self.response_parser = AIResponseParser(strict_mode=False)

        # 循环控制
        self.should_stop = False
        self.last_round_time = 0

    def start(self) -> None:
        """启动游戏循环"""
        self.world.start()
        self.should_stop = False

    def stop(self) -> None:
        """停止游戏循环"""
        self.should_stop = True
        self.world.stop()

    def process_round(self) -> Dict[str, Any]:
        """处理一轮游戏

        Returns:
            轮次结果
        """
        if not self.world.is_running or self.world.is_paused:
            return {"status": "paused" if self.world.is_paused else "stopped"}

        # 进入下一轮
        self.world.next_round()

        round_result = {
            "round": self.world.current_round,
            "character_actions": [],
            "events": [],
        }

        # 获取存活角色
        alive_characters = self.world.get_alive_characters()

        if not alive_characters:
            # 所有角色死亡，游戏结束
            self.stop()
            round_result["status"] = "game_over"
            return round_result

        # 分组角色
        character_groups = self.detector.group_characters(alive_characters)

        # 处理每个分组
        for group in character_groups:
            group_result = self._process_group(group)
            round_result["character_actions"].extend(group_result["actions"])
            round_result["events"].extend(group_result["events"])

        # 结束本轮
        self.world.end_round()

        round_result["status"] = "completed"
        return round_result

    def _process_group(self, group: List[Character]) -> Dict[str, Any]:
        """处理一个角色分组

        Args:
            group: 角色分组

        Returns:
            分组处理结果
        """
        group_result = {
            "actions": [],
            "events": [],
        }

        if len(group) == 1:
            # 单个角色，独立处理
            action_result = self._process_single_character(group[0])
            group_result["actions"].append(action_result)
        else:
            # 多个角色，交互处理
            group_results = self._process_character_group(group)
            group_result["actions"].extend(group_results)

        return group_result

    def _process_single_character(self, character: Character) -> Dict[str, Any]:
        """处理单个角色的行动

        Args:
            character: 角色

        Returns:
            行动结果
        """
        # 检测附近角色
        nearby = self.detector.detect_nearby_characters(character, self.world.characters)

        # 构建 AI 提示词
        world_context = self.world.get_world_info()
        character_info = character.get_info_for_ai()
        nearby_info = self.detector.get_group_info_for_ai(character, nearby)

        messages = self.prompt_builder.build_messages(
            character_info=character_info,
            nearby_characters=nearby_info,
            world_context=world_context,
        )

        # 调用 AI
        try:
            response_text = self.ai_interface.chat(messages)
        except Exception as e:
            # AI 调用失败，返回默认行动
            self.world.event_manager.emit(
                event_type=EventType.AI_ERROR,
                description=f"AI调用失败: {str(e)}",
                related_characters=[character.id],
                data={"error": str(e)},
            )
            return self._get_default_action(character)

        # 解析 AI 响应
        try:
            ai_response = self.response_parser.parse_single_response(response_text)
        except Exception as e:
            # 解析失败，返回默认行动
            return self._get_default_action(character)

        # 应用 AI 决策
        return self._apply_ai_decision(character, ai_response)

    def _process_character_group(self, group: List[Character]) -> List[Dict[str, Any]]:
        """处理角色交互组

        Args:
            group: 角色分组

        Returns:
            行动结果列表
        """
        # 构建分组提示词
        world_context = self.world.get_world_info()
        characters_info = [char.get_info_for_ai() for char in group]

        messages = self.group_prompt_builder.build_group_messages(
            characters=characters_info,
            world_context=world_context,
        )

        # 调用 AI
        try:
            response_text = self.ai_interface.chat(messages)
        except Exception as e:
            # AI 调用失败，返回默认行动
            self.world.event_manager.emit(
                event_type=EventType.AI_ERROR,
                description=f"分组AI调用失败: {str(e)}",
                related_characters=[char.id for char in group],
                data={"error": str(e)},
            )
            return [self._get_default_action(char) for char in group]

        # 解析 AI 响应
        try:
            ai_responses = self.response_parser.parse_group_response(response_text)
        except Exception as e:
            # 解析失败，返回默认行动
            return [self._get_default_action(char) for char in group]

        # 应用 AI 决策
        results = []
        for i, char in enumerate(group):
            # 找到对应的响应
            ai_response = None
            for resp in ai_responses:
                if "character_id" in resp and resp["character_id"] == char.id:
                    ai_response = resp
                    break
            if ai_response is None and i < len(ai_responses):
                ai_response = ai_responses[i]

            if ai_response:
                results.append(self._apply_ai_decision(char, ai_response))
            else:
                results.append(self._get_default_action(char))

        return results

    def _apply_ai_decision(self, character: Character, ai_response: Dict[str, Any]) -> Dict[str, Any]:
        """应用 AI 决策到角色

        Args:
            character: 角色
            ai_response: AI 响应

        Returns:
            行动结果
        """
        result = {
            "character_id": character.id,
            "character_name": character.name,
            "action_thought": ai_response.get("action_thought", "沉思中..."),
            "scene_description": ai_response.get("scene_description", ""),
            "attribute_changes": {},
            "item_changes": {},
        }

        # 应用属性变化
        attr_deltas = ai_response.get("attribute_deltas", {})
        if attr_deltas:
            # 限制属性变化范围
            attr_deltas = self.response_parser.clamp_attribute_deltas(attr_deltas)
            actual_changes = character.apply_attribute_delta(attr_deltas)
            result["attribute_changes"] = actual_changes

        # 处理物品变化
        item_changes = ai_response.get("item_changes", {})
        if item_changes:
            # 处理获得物品
            for item_id in item_changes.get("obtained", []):
                # 这里简化处理，实际应该从物品库获取
                pass
            # 处理失去物品
            for item_id in item_changes.get("lost", []):
                character.inventory.remove_item(item_id)
            result["item_changes"] = item_changes

        # 检查死亡
        if not character.is_alive:
            self.world.event_manager.emit(
                event_type=EventType.CHARACTER_DIED,
                description=f"{character.name} 身陨",
                related_characters=[character.id],
                data={"round": self.world.current_round},
            )

        # 检查境界提升
        if character.try_realm_advance():
            self.world.event_manager.emit(
                event_type=EventType.REALM_ADVANCED,
                description=f"{character.name} 境界提升至 {character.realm.name}",
                related_characters=[character.id],
                data={"new_realm": character.realm.to_dict()},
            )

        return result

    def _get_default_action(self, character: Character) -> Dict[str, Any]:
        """获取默认行动（用于 AI 失败时）

        Args:
            character: 角色

        Returns:
            默认行动结果
        """
        # 默认行为：打坐恢复灵力
        recovery = min(10, character.attributes.max_spirit_power - character.attributes.spirit_power)

        actual_changes = character.apply_attribute_delta({"spirit_power": recovery})

        return {
            "character_id": character.id,
            "character_name": character.name,
            "action_thought": "打坐修炼，恢复灵力",
            "scene_description": "周围灵气充盈，静心修炼",
            "attribute_changes": actual_changes,
            "item_changes": {},
        }

    def run(self) -> None:
        """运行游戏循环（阻塞式）"""
        self.start()

        while not self.should_stop:
            # 检查时间间隔
            current_time = time.time()
            if current_time - self.last_round_time < self.config.game.round_interval / 1000:
                time.sleep(0.01)
                continue

            self.last_round_time = current_time

            # 处理一轮
            self.process_round()

            # 检查是否所有角色死亡
            if not self.world.get_alive_characters():
                self.stop()

    def run_frame(self) -> Optional[Dict[str, Any]]:
        """运行一帧（用于非阻塞模式）

        Returns:
            轮次结果（如果是新的一轮）
        """
        current_time = time.time()

        # 检查是否应该处理新的一轮
        if self.world.is_running and not self.world.is_paused:
            if current_time - self.last_round_time >= self.config.game.round_interval / 1000:
                self.last_round_time = current_time
                return self.process_round()

        return None

    def toggle_pause(self) -> None:
        """切换暂停状态"""
        if self.world.is_paused:
            self.world.resume()
        else:
            self.world.pause()
