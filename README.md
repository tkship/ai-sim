# 修仙 AI 模拟游戏

一个基于 Pygame 和 AI 驱动的修仙模拟游戏。游戏中所有角色的行为由 AI 决策驱动，AI 返回结构化的行动数据来影响游戏世界。

## 项目结构

```
ai-sim/
├── pyproject.toml          # uv 包管理配置
├── config.yaml             # 游戏配置（AI URL、世界观等）
├── src/
│   ├── main.py             # 程序入口
│   ├── game/               # 游戏核心模块
│   │   ├── world.py        # 游戏世界类
│   │   ├── loop.py         # 主游戏循环
│   │   └── config.py       # 配置加载
│   ├── character/          # 角色系统
│   │   ├── character.py    # 角色基类
│   │   ├── attributes.py   # 属性系统
│   │   ├── realm.py        # 境界系统
│   │   ├── inventory.py     # 物品系统
│   │   └── memory.py       # 历史记忆
│   ├── ai/                 # AI 接口层
│   │   ├── interface.py    # AI 通用接口
│   │   ├── prompt.py       # 提示词构建
│   │   └── parser.py       # AI 响应解析
│   ├── interaction/        # 交互和战斗
│   │   ├── detector.py     # 探测系统
│   │   ├── combat.py       # 战斗计算
│   │   └── event.py        # 事件系统
│   └── ui/                 # 用户界面
│       ├── display.py      # Pygame 主界面
│       ├── panels.py       # 面板渲染
│       └── renderer.py     # 场景渲染
└── tests/                 # 测试模块
```

## 核心功能

### 角色系统
- **属性系统**：血量、灵力、神识、攻击力、防御力等
- **境界系统**：炼气、筑基、金丹、元婴、化神，每个境界包含初期、中期、后期、圆满
- **物品系统**：法宝、丹药、功法，支持装备和背包管理
- **记忆系统**：记录角色的经历、战斗记录和重要事件

### AI 决策
- 支持多种 AI API 格式（OpenAI、Anthropic、通用 JSON）
- 可配置的 API URL 和参数
- Mock AI 模式用于测试
- AI 返回结构化决策数据（行动想法、场景描述、属性增量、物品变化）

### 交互系统
- **探测系统**：根据神识计算探测范围，检测附近角色
- **战斗系统**：伤害计算、暴击、命中率、境界提升判定
- **事件系统**：记录所有游戏事件，用于日志和角色记忆

### 用户界面
- Pygame 图形界面
- 角色状态面板（属性、境界、装备）
- 场景渲染（角色位置可视化）
- 游戏日志区域
- 操作提示（空格暂停/继续，S 单步执行，ESC 退出）

## 安装和运行

### 前置要求
- Python 3.10+
- uv 包管理器

### 安装依赖

```bash
uv sync
```

### 运行游戏

```bash
uv run python src/main.py
```

## 配置

编辑 `config.yaml` 文件可以自定义：

- AI API 配置（URL、API Key、模型名称等）
- 世界观设定
- 初始角色属性范围
- 初始物品列表
- 游戏循环速度
- 界面配置（窗口大小、颜色等）

## AI 响应格式

AI 应返回以下 JSON 格式：

```json
{
  "action_thought": "决定打坐修炼，恢复灵力",
  "scene_description": "灵气充盈，周围的草木在风中轻轻摇曳",
  "attribute_deltas": {
    "health": 0,
    "spirit_power": 5
  },
  "item_changes": {
    "obtained": [],
    "lost": []
  }
}
```

## 开发计划

- [ ] 添加真实 AI API 支持
- [ ] 实现更多物品类型和效果
- [ ] 添加地图探索系统
- [ ] 实现更复杂的战斗逻辑
- [ ] 添加成就系统
- [ ] 支持游戏存档和加载
- [ ] 添加更多 UI 面板和交互

## 许可证

MIT License
