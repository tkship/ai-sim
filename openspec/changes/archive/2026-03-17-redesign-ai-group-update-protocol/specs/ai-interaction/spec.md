## MODIFIED Requirements

### Requirement: Prompt Construction
系统 SHALL 将角色信息打包成结构化提示词发送给 AI，并明确声明按交互组返回的响应协议。

#### Scenario: Single Character Prompt
- **WHEN** 角色无交互
- **THEN** 系统构建仅包含该角色的单角色交互组提示词，并要求 AI 以组级 `GroupUpdate` 结构返回结果

#### Scenario: Multi-Character Prompt
- **WHEN** 多个角色交互
- **THEN** 系统构建包含同一交互组全部角色信息的统一提示词，并要求 AI 返回组级场景、组事件和组内全部角色账本

#### Scenario: Keyword Retrieval
- **WHEN** 构建提示词
- **THEN** 系统根据关键词检索相关法宝、功法的完整信息，并将白名单 `action_type`、`event.type`、必须字段和最小 `basis` 结构一并声明给 AI

### Requirement: Response Parsing
系统 SHALL 解析 AI 返回的组级固定格式内容，并将其结构化为可审计的交互组更新对象。

#### Scenario: Group JSON Parsing
- **WHEN** 收到 AI 响应
- **THEN** 系统解析包含 `participants`、`scene_summary`、`scene_description`、`events` 和 `character_updates` 的组级 JSON 结构

#### Scenario: Character Payload Parsing
- **WHEN** 解析 `character_updates`
- **THEN** 系统将每个角色的 `intent`、`action`、`basis`、`attribute_changes`、`item_changes` 结构化为对应对象

#### Scenario: Basic Shape Validation
- **WHEN** 解析 AI 响应
- **THEN** 系统至少验证组级必须字段、角色级必须字段以及 `basis.resource_basis` / `basis.effect_basis` 的存在性

### Requirement: Attribute Change Application
系统 SHALL 仅对已通过审计的交互组结果应用角色变化。

#### Scenario: Apply Audited Group Update
- **WHEN** 交互组响应通过审计
- **THEN** 系统按角色账本依次应用属性变化、物品变化和法宝状态变化

#### Scenario: Reject Failed Group Update
- **WHEN** 交互组响应未通过审计
- **THEN** 系统不得应用该组任何角色的状态变化

#### Scenario: Group Scene Logging
- **WHEN** 交互组响应通过审计
- **THEN** 系统记录组级场景摘要和场景描述作为本轮共享日志
