# ai-interaction Specification

## Purpose
TBD - created by archiving change pure-text-xianxia-game. Update Purpose after archive.
## Requirements
### Requirement: Prompt Construction
系统 SHALL 将角色信息打包成结构化提示词发送给 AI。

#### Scenario: Single Character Prompt
- **WHEN** 角色无交互
- **THEN** 系统构建包含角色信息、功法、法宝、物品栏、记忆、环境的提示词

#### Scenario: Multi-Character Prompt
- **WHEN** 多个角色交互
- **THEN** 系统构建包含所有交互角色信息的提示词

#### Scenario: Keyword Retrieval
- **WHEN** 构建提示词
- **THEN** 系统根据关键词检索相关法宝、功法的完整信息

### Requirement: Response Parsing
系统 SHALL 解析 AI 返回的固定格式内容。

#### Scenario: JSON Parsing
- **WHEN** 收到 AI 响应
- **THEN** 系统解析 JSON 格式的响应

#### Scenario: Validation
- **WHEN** 解析 AI 响应
- **THEN** 系统验证响应包含必需字段（交互概述、场景描述、属性变化）

### Requirement: Attribute Change Application
系统 SHALL 应用 AI 返回的属性变化。

#### Scenario: Numeric Attribute Change
- **WHEN** 属性变化包含数值增量
- **THEN** 系统将增量应用到对应属性

#### Scenario: Item Change
- **WHEN** 属性变化包含物品获得或失去
- **THEN** 系统更新物品栏

#### Scenario: Status Change
- **WHEN** 属性变化包含状态新增或移除
- **THEN** 系统更新角色状态

#### Scenario: Treasure Change
- **WHEN** 属性变化包含法宝变化
- **THEN** 系统更新法宝的损耗度、耐久度、注入灵力

