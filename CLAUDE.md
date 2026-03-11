# 修仙 AI 模拟游戏 - MVP 实现计划

## 背景

创建一个基于 pygame + AI 的修仙模拟游戏，其中所有角色的行为由 AI 驱动。游戏核心是数值计算和角色交互，AI 负责决策并返回结构化的行动数据。

## 项目结构

```
ai-sim/
├── pyproject.toml          # uv 包管理配置
├── requirements.txt        # 依赖列表
├── README.md               # 项目说明
├── CLAUDE.md               # Claude Code 指南
├── config.yaml             # 游戏配置（AI URL、世界观等）
│
├── src/
│   ├── __init__.py
│   ├── main.py             # 程序入口
│   │
│   ├── game/
│   │   ├── __init__.py
│   │   ├── world.py        # 游戏世界类
│   │   ├── loop.py         # 主游戏循环
│   │   └── config.py       # 配置加载
│   │
│   ├── character/
│   │   ├── __init__.py
│   │   ├── character.py    # 角色基类
│   │   ├── attributes.py   # 属性系统（血量、灵力、神识等）
│   │   ├── realm.py        # 境界系统
│   │   ├── inventory.py     # 物品系统（法宝、丹药、功法）
│   │   └── memory.py       # 历史记忆
│   │
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── interface.py    # AI 通用接口（可配置 URL）
│   │   ├── prompt.py       # 提示词构建
│   │   └── parser.py       # AI 响应解析（固定格式）
│   │
│   ├── interaction/
│   │   ├── __init__.py
│   │   ├── detector.py     # 探测范围管理
│   │   ├── combat.py       # 战斗计算逻辑
│   │   └── event.py        # 事件系统
│   │
│   └── ui/
│       ├── __init__.py
│       ├── display.py      # Pygame 主界面
│       ├── panels.py       # 面板渲染（角色状态、日志等）
│       └── renderer.py     # 场景渲染
│
└── tests/
    ├── __init__.py
    ├── test_character.py
    └── test_ai.py
```

## 实现步骤

### 阶段 1: 项目初始化

1. **创建虚拟环境和项目配置**
   - 使用 `uv init` 初始化项目
   - 添加依赖：`pygame`, `pyyaml`, `httpx`（用于 AI API 调用）
   - 创建 `pyproject.toml` 配置

2. **创建基础配置文件**
   - `config.yaml`: 存放 AI API URL、API key、游戏世界观等配置

### 阶段 2: 核心数据模型

1. **属性系统** (`src/character/attributes.py`)
   - 核心属性：血量、灵力、神识
   - 派生属性：攻击力、防御力
   - 方法：`apply_delta(delta_dict)` 应用增量变化

2. **境界系统** (`src/character/realm.py`)
   - 大境界定义：炼气、筑基、金丹、元婴、化神
   - 小境界：初期、中期、后期、圆满
   - 境界提升概率和规则

3. **物品系统** (`src/character/inventory.py`)
   - 物品基类：法宝、丹药、功法
   - 物品属性：攻击力、防御力、灵力恢复等
   - 背包管理

4. **历史记忆** (`src/character/memory.py`)
   - 存储角色经历、战斗记录、重要事件
   - 带时间戳的记忆条目

5. **角色类** (`src/character/character.py`)
   - 整合属性、物品、记忆
   - 当前状态、位置、探测范围

### 阶段 3: AI 接口层

1. **通用 AI 接口** (`src/ai/interface.py`)
   - 可配置的 API URL 和请求格式
   - 支持 OpenAI 格式、Anthropic 格式、通用 JSON 格式
   - 统一响应处理

2. **提示词构建** (`src/ai/prompt.py`)
   - 将角色状态打包为结构化提示词
   - 包含世界观、角色信息、当前场景
   - 要求 AI 返回固定格式

3. **响应解析** (`src/ai/parser.py`)
   - 解析 AI 返回的 JSON 格式
   - 验证必需字段
   - 提取：行动想法、场景描述、属性增量

**AI 请求/响应格式设计：**
```json
// AI 应返回的格式
{
  "action_thought": "string",      // 行动想法（自然语言）
  "scene_description": "string",   // 场景描述（自然语言）
  "attribute_deltas": {            // 属性增量
    "health": int,
    "spirit_power": int,
    // ...
  },
  "item_changes": {                 // 物品变化
    "obtained": ["item_id"],
    "lost": ["item_id"]
  }
}
```

### 阶段 4: 交互和战斗系统

1. **探测系统** (`src/interaction/detector.py`)
   - 根据神识计算探测范围
   - 检测范围内的其他角色
   - 分组角色为独立/交互组

2. **战斗计算** (`src/interaction/combat.py`)
   - 核心公式：
     ```
     伤害 = 攻击者灵力 + 攻击法宝攻击力 - 防御者灵力 - 防御法宝防御力
     ```
   - 死亡检测（血量 <= 0）
   - 战斗后境界提升判定

3. **事件系统** (`src/interaction/event.py`)
   - 记录所有游戏事件
   - 用于历史记忆和日志显示

### 阶段 5: Pygame 界面

1. **主界面** (`src/ui/display.py`)
   - 初始化 pygame
   - 主窗口布局
   - 事件处理（键盘、鼠标）

2. **面板渲染** (`src/ui/panels.py`)
   - 角色状态面板（属性、境界、物品）
   - 世界观配置展示
   - 游戏日志区域

3. **场景渲染** (`src/ui/renderer.py`)
   - 文本场景展示
   - 角色位置可视化（简单方式）

### 阶段 6: 游戏循环和世界管理

1. **游戏世界** (`src/game/world.py`)
   - 管理所有角色
   - 处理角色添加/移除（死亡）
   - 世界观规则应用

2. **主循环** (`src/game/loop.py`)
   - 每一轮的逻辑：
     1. 分组角色（独立/交互）
     2. 对每组构建提示词
     3. 调用 AI 获取决策
     4. 解析增量
     5. 应用属性变化
     6. 检测死亡、境界提升
     7. 更新历史记忆
   - 控制游戏速度、暂停等

3. **入口程序** (`src/main.py`)
   - 加载配置
   - 初始化游戏世界
   - 创建初始角色（1独立+3交互）
   - 启动主循环

### 阶段 7: 初始数据和测试

1. **创建 4 个初始角色**
   - 角色A: 独立，高神识
   - 角色B, C, D: 互相探测范围内，会交互

2. **编写配置示例** (`config.yaml`)
   - AI API URL 示例
   - 世界观设定
   - 初始境界、物品

## 验证计划

### 测试游戏功能

1. **启动游戏**
   ```bash
   uv run python src/main.py
   ```

2. **验证点**
   - Pygame 窗口正常显示
   - 4 个角色状态面板正确展示
   - 日志区域显示 AI 返回的场景描述
   - 属性变化正确应用
   - 战斗场景中血量变化符合公式
   - 死亡角色被正确移除

3. **AI 接口测试**
   - 使用 mock 数据测试响应解析
   - 验证不同配置 URL 都能工作

## 关键文件

- `pyproject.toml` - uv 包管理配置
- `config.yaml` - 可配置的游戏设置
- `src/ai/interface.py` - 通用 AI 接口
- `src/character/attributes.py` - 核心属性系统
- `src/interaction/combat.py` - 战斗计算公式
