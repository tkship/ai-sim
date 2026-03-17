## ADDED Requirements

### Requirement: Damage Calculation
系统 SHALL 根据功法、法宝、灵力注入等因素计算战斗伤害。

#### Scenario: Attack Calculation
- **WHEN** 计算攻击伤害
- **THEN** 系统考虑功法、法宝、灵力注入、环境属性、体质加成

#### Scenario: Defense Calculation
- **WHEN** 计算防御效果
- **THEN** 系统考虑防御功法、防御法宝、灵力注入、环境属性、体质、身法

#### Scenario: Damage Application
- **WHEN** 完成伤害计算
- **THEN** 系统将最终伤害应用到目标血量

### Requirement: Spiritual Power Injection
系统 SHALL 管理法宝和功法的灵力注入。

#### Scenario: Injection Limit
- **WHEN** 注入灵力
- **THEN** 系统确保注入量不超过法宝/功法的上限

#### Scenario: Injection Bonus
- **WHEN** 注入灵力
- **THEN** 系统根据注入量计算攻击/防御加成

### Requirement: Combat State Management
系统 SHALL 管理战斗中的状态和阶段。

#### Scenario: Combat Round Tracking
- **WHEN** 战斗进行
- **THEN** 系统跟踪回合数和战斗阶段

#### Scenario: Status Effect Duration
- **WHEN** 状态有持续时间
- **THEN** 系统在每回合结束时减少持续时间
