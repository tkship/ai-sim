## ADDED Requirements

### Requirement: Character Attributes
系统 SHALL 维护角色的核心属性，包括血量、灵力、神识、状态。

#### Scenario: Attribute Initialization
- **WHEN** 创建新角色
- **THEN** 系统根据角色境界初始化血量、灵力、神识的最大值和当前值

#### Scenario: Attribute Modification
- **WHEN** 角色属性发生变化
- **THEN** 系统应用增量变化，确保属性不低于0且不超过最大值

### Requirement: Character Realm
系统 SHALL 管理角色的境界，包括大境界和小境界。

#### Scenario: Realm Progression
- **WHEN** 角色突破境界
- **THEN** 系统更新角色境界，并按对应倍率提升血量和灵力上限

#### Scenario: Realm Bonuses
- **WHEN** 角色达到新的大境界
- **THEN** 系统解锁该境界对应的特殊能力

### Requirement: Character Spirit Root
系统 SHALL 管理角色的灵根属性，包括单属性、双属性、三属性、四属性、五属性和混沌灵根。

#### Scenario: Spirit Root Cultivation Speed
- **WHEN** 计算修炼速度
- **THEN** 系统根据灵根纯净度应用修炼速度加成（单属性 > 双属性 > 三属性 > 四属性 > 五属性）

#### Scenario: Spirit Root Technique Constraint
- **WHEN** 角色尝试修炼功法
- **THEN** 系统验证灵根与功法属性是否兼容

### Requirement: Character Memory
系统 SHALL 记录角色的历史记忆和长期目标。

#### Scenario: Memory Storage
- **WHEN** 重要事件发生
- **THEN** 系统将事件添加到角色记忆中

#### Scenario: Memory Retrieval
- **WHEN** 构建 AI 提示词
- **THEN** 系统检索并包含相关记忆
