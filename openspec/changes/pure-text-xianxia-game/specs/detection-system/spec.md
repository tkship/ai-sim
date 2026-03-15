## ADDED Requirements

### Requirement: Detection Range
系统 SHALL 根据角色神识计算探测范围。

#### Scenario: Detection Range Calculation
- **WHEN** 计算探测范围
- **THEN** 系统基于角色神识值确定探测范围

#### Scenario: Detection Bonus
- **WHEN** 计算探测范围
- **THEN** 系统应用法宝或功法带来的探测力加成

### Requirement: Character Detection
系统 SHALL 检测探测范围内的其他角色。

#### Scenario: Proximity Check
- **WHEN** 每游戏循环
- **THEN** 系统检查每个角色探测范围内是否有其他角色

#### Scenario: Detection Information
- **WHEN** 检测到其他角色
- **THEN** 系统提供基于神识的目标信息（境界、状态等）

### Requirement: Multi-Character Interaction
系统 SHALL 处理多角色交互场景。

#### Scenario: Interaction Group Formation
- **WHEN** 多个角色在彼此探测范围内
- **THEN** 系统将这些角色组成交互组

#### Scenario: Synchronous Update
- **WHEN** 角色属于交互组
- **THEN** 系统同步更新组内所有角色的状态和思想

#### Scenario: Group AI Prompt
- **WHEN** 处理交互组
- **THEN** 系统构建包含所有角色信息的统一提示词

### Requirement: Independent Character
系统 SHALL 处理无交互的角色。

#### Scenario: Independent Update
- **WHEN** 角色无交互
- **THEN** 系统独立与 AI 交互更新该角色
