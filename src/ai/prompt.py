"""提示词构建模块

将角色状态和游戏信息打包为结构化的 AI 提示词
"""
import json
from typing import Dict, List, Optional


class PromptBuilder:
    """提示词构建器"""

    SYSTEM_PROMPT = """你是一个修仙模拟游戏中的角色决策 AI。

## 你的任务
根据提供的角色信息和环境信息，决定角色本轮的行动。

## 响应格式要求
你必须严格返回以下 JSON 格式，不要包含任何其他文字：

```json
{
  "action_thought": "string",      // 行动想法（自然语言描述）
  "scene_description": "string",   // 场景描述（自然语言，1-2句话）
  "attribute_deltas": {            // 属性增量变化
    "health": int,                  // 血量变化（负数表示减少）
    "spirit_power": int,            // 灵力变化
    "consciousness": int,          // 神识变化（可选）
    "luck": int                     // 运气变化（可选）
  },
  "item_changes": {                 // 物品变化
    "obtained": ["item_id"],        // 获得的物品ID列表
    "lost": ["item_id"]             // 失去的物品ID列表
  }
}
```

## 决策逻辑
1. 如果探测到其他角色：
   - 判断对方是敌是友（境界差距、过往记忆）
   - 敌人：考虑攻击、逃跑、求援
   - 朋友：考虑交流、合作、交易

2. 如果独自一人：
   - 考虑修炼（打坐、炼丹）
   - 考虑探索（寻找机缘）
   - 考虑整理物品

## 数值约束
- 每轮属性变化应在合理范围内（health: -50~+50, spirit_power: -30~+100）
- 确保血量不会变成负数
"""

    def __init__(self, world_info: Dict, max_nearby_characters: int = 5):
        """初始化提示词构建器

        Args:
            world_info: 世界观信息
            max_nearby_characters: 最多显示的附近角色数量
        """
        self.world_info = world_info
        self.max_nearby_characters = max_nearby_characters

    def build_character_prompt(
        self,
        character_info: Dict,
        nearby_characters: List[Dict] = None,
        world_context: Dict = None,
    ) -> str:
        """构建角色决策提示词

        Args:
            character_info: 当前角色的信息
            nearby_characters: 附近角色列表
            world_context: 世界上下文

        Returns:
            完整的提示词
        """
        if nearby_characters is None:
            nearby_characters = []
        if world_context is None:
            world_context = {}

        # 构建用户消息
        user_message = f"""# 当前角色信息
{self._format_character_info(character_info)}

# 附近角色
{self._format_nearby_characters(nearby_characters)}

# 世界背景
{self._format_world_info(world_context)}

# 当前情况
{self._format_current_situation(character_info, nearby_characters)}

请根据以上信息，返回你的决策。"""

        return user_message

    def _format_character_info(self, info: Dict) -> str:
        """格式化角色信息"""
        lines = [
            f"名称: {info.get('name', '未知')}",
            f"境界: {info.get('realm', '未知')}",
            f"状态: {info.get('state', '未知')}",
            f"位置: {info.get('position', (0, 0))}",
            "",
            "## 属性",
            f"血量: {info.get('health', 0)} / {info.get('max_health', 0)} ({info.get('health_percent', 0) * 100:.1f}%)",
            f"灵力: {info.get('spirit_power', 0)} / {info.get('max_spirit_power', 0)} ({info.get('spirit_power_percent', 0) * 100:.1f}%)",
            f"神识: {info.get('consciousness', 0)}",
            f"攻击力: {info.get('attack_power', 0)}",
            f"防御力: {info.get('defense_power', 0)}",
            f"探测范围: {info.get('detection_range', 0)}",
            "",
            "## 装备",
            f"法宝: {info.get('equipped_artifact', '无')}",
            f"功法: {info.get('equipped_technique', '无')}",
            "",
            "## 背包物品",
        ]

        items = info.get('items', [])
        if items:
            for item in items:
                lines.append(f"  - {item}")
        else:
            lines.append("  (无)")

        return "\n".join(lines)

    def _format_nearby_characters(self, characters: List[Dict]) -> str:
        """格式化附近角色信息"""
        if not characters:
            return "附近没有其他角色，当前独自一人。"

        # 限制显示数量
        display_chars = characters[:self.max_nearby_characters]

        lines = [f"探测到 {len(characters)} 名附近的修仙者：", ""]

        for i, char in enumerate(display_chars, 1):
            lines.append(f"### 角色 {i}")
            lines.append(f"名称: {char.get('name', '未知')}")
            lines.append(f"境界: {char.get('realm', '未知')}")
            lines.append(f"状态: {char.get('state', '未知')}")
            lines.append(f"距离: {char.get('distance', 0)}")
            lines.append(f"血量: {char.get('health', 0)} / {char.get('max_health', 0)}")
            lines.append(f"攻击力: {char.get('attack_power', 0)}")
            lines.append(f"防御力: {char.get('defense_power', 0)}")
            lines.append(f"法宝: {char.get('equipped_artifact', '未知')}")
            lines.append("")

        if len(characters) > self.max_nearby_characters:
            lines.append(f"... 还有 {len(characters) - self.max_nearby_characters} 名角色")

        return "\n".join(lines)

    def _format_world_info(self, context: Dict) -> str:
        """格式化世界观信息"""
        return f"""世界名称: {self.world_info.get('name', '未知')}
{self.world_info.get('description', '')}

当前游戏轮数: {context.get('round', 0)}
存活角色数: {context.get('alive_count', 0)}
死亡角色数: {context.get('dead_count', 0)}"""

    def _format_current_situation(self, character: Dict, nearby: List[Dict]) -> str:
        """格式化当前情况"""
        health_percent = character.get('health_percent', 0)
        spirit_percent = character.get('spirit_power_percent', 0)

        situation = "你的当前状态："

        if health_percent < 0.3:
            situation += "身受重伤，需要疗伤或使用回血丹；"
        elif health_percent < 0.6:
            situation += "有些受伤，需要注意；"
        else:
            situation += "身体状况良好；"

        if spirit_percent < 0.3:
            situation += "灵力不足，需要打坐恢复；"
        elif spirit_percent < 0.6:
            situation += "灵力有些低；"
        else:
            situation += "灵力充沛；"

        if nearby:
            situation += f"附近有 {len(nearby)} 名角色，需要注意观察他们的行动和意图。"

        return situation

    def build_messages(
        self,
        character_info: Dict,
        nearby_characters: List[Dict] = None,
        world_context: Dict = None,
    ) -> List[Dict[str, str]]:
        """构建完整的消息列表

        Args:
            character_info: 当前角色的信息
            nearby_characters: 附近角色列表
            world_context: 世界上下文

        Returns:
            消息列表
        """
        user_message = self.build_character_prompt(
            character_info,
            nearby_characters,
            world_context,
        )

        return [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]


class GroupPromptBuilder(PromptBuilder):
    """多角色交互组提示词构建器"""

    GROUP_SYSTEM_PROMPT = """你是一个修仙模拟游戏中的多人交互决策 AI。

## 你的任务
为一组互相探测范围内的角色协调本轮的行动。

## 响应格式要求
你必须返回一个数组，每个元素对应一个角色的决策：

```json
[
  {
    "character_id": "string",      // 角色ID
    "action_thought": "string",     // 行动想法
    "scene_description": "string",  // 场景描述
    "attribute_deltas": {           // 属性增量
      "health": int,
      "spirit_power": int
    },
    "item_changes": {
      "obtained": ["item_id"],
      "lost": ["item_id"]
    }
  }
]
```

## 决策逻辑
1. 分析角色之间的关系（境界差距、装备对比）
2. 考虑可能的互动方式：战斗、交易、合作、竞争
3. 为每个角色生成合理的决策
4. 确保行动之间的逻辑一致性（战斗双方都应该有反应）
"""

    def build_group_prompt(
        self,
        characters: List[Dict],
        world_context: Dict = None,
    ) -> str:
        """构建多角色交互组的提示词

        Args:
            characters: 角色信息列表
            world_context: 世界上下文

        Returns:
            完整的提示词
        """
        if world_context is None:
            world_context = {}

        lines = [
            "# 角色组信息",
            "",
        ]

        for i, char in enumerate(characters, 1):
            lines.append(f"## 角色 {i}")
            lines.append(f"ID: {char.get('id', 'unknown')}")
            lines.append(self._format_character_info(char))
            lines.append("")

        lines.append("# 世界背景")
        lines.append(self._format_world_info(world_context))
        lines.append("")
        lines.append("# 请根据以上信息，为所有角色返回决策。")

        return "\n".join(lines)

    def build_group_messages(
        self,
        characters: List[Dict],
        world_context: Dict = None,
    ) -> List[Dict[str, str]]:
        """构建多角色交互的消息列表

        Args:
            characters: 角色信息列表
            world_context: 世界上下文

        Returns:
            消息列表
        """
        user_message = self.build_group_prompt(characters, world_context)

        return [
            {"role": "system", "content": self.GROUP_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ]
