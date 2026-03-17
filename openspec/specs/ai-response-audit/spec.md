# ai-response-audit Specification

## Purpose
TBD - created by archiving change redesign-ai-group-update-protocol. Update Purpose after archive.
## Requirements
### Requirement: Group Response Audit
系统 SHALL 对每个交互组响应执行独立的强审计，再决定是否允许应用结果。

#### Scenario: Validate group boundary
- **WHEN** 系统收到交互组响应
- **THEN** 系统验证 `participants` 与当前交互组完全一致，且 `character_updates` 覆盖组内全部角色且不包含组外角色

#### Scenario: Validate required structure
- **WHEN** 系统解析交互组响应
- **THEN** 系统验证组级必须字段、事件级必须字段、角色级必须字段和 `basis` 必须字段全部存在

#### Scenario: Validate existence and conservation
- **WHEN** 系统审计角色账本
- **THEN** 系统验证角色、目标、物品、法宝和功法引用真实存在，并验证库存、灵力消耗和法宝状态变化满足资源守恒约束

### Requirement: Conservative Failure Strategy
系统 SHALL 对共享事实错误和资源守恒错误采用整组失败策略。

#### Scenario: Fail whole group on hard errors
- **WHEN** 任一角色账本出现关键字段缺失、非法引用、库存不足、严重资源超支或共享事实冲突
- **THEN** 系统拒绝应用该交互组的全部角色变化

#### Scenario: Reject unsupported event and action types
- **WHEN** AI 返回不在白名单中的 `action_type` 或 `event.type`
- **THEN** 系统将该交互组视为审计失败并拒绝应用结果

#### Scenario: Require basis for material results
- **WHEN** 角色账本包含显著属性变化、状态变化或物品消耗
- **THEN** 系统要求 `resource_basis` 和 `effect_basis` 能解释主要消耗和主要结果，否则整组失败

### Requirement: Safe Clipping
系统 SHALL 仅对安全的边界型数值执行裁剪，不得裁剪事实类错误。

#### Scenario: Clip bounded state values
- **WHEN** HP、MP、神识、法宝耐久、损耗度或轻微超上的注灵量在应用前超出合法边界
- **THEN** 系统将其裁剪到允许范围内并记录警告

#### Scenario: Do not clip fact errors
- **WHEN** 审计发现角色不存在、组成员不一致、库存不足、非法类型或严重资源超支
- **THEN** 系统不得通过自动修正使其通过审计

#### Scenario: Emit audit diagnostics
- **WHEN** 系统完成一组响应审计
- **THEN** 系统输出结构化的错误、警告和裁剪结果，供调用方决定记录日志或中止应用

