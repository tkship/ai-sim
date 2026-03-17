# realm-system Specification

## Purpose
TBD - created by archiving change pure-text-xianxia-game. Update Purpose after archive.
## Requirements
### Requirement: Small Realm Breakthrough
系统 SHALL 处理小境界突破，包括成功率计算和突破尝试。

#### Scenario: Base Success Rate
- **WHEN** 计算小境界突破成功率
- **THEN** 系统使用该境界对应的基础成功率

#### Scenario: Breakthrough Bonus
- **WHEN** 计算小境界突破成功率
- **THEN** 系统叠加战斗感悟、丹药辅助、功法加成、灵根影响等因素

#### Scenario: Breakthrough Attempt
- **WHEN** 每 N 个循环
- **THEN** 系统按概率自动尝试小境界突破

### Requirement: Major Realm Breakthrough
系统 SHALL 处理大境界突破，包括质变提升和失败惩罚。

#### Scenario: Major Realm Base Rate
- **WHEN** 计算大境界突破成功率
- **THEN** 系统使用该大境界对应的基础成功率

#### Scenario: Qualitative Change
- **WHEN** 大境界突破成功
- **THEN** 系统按对应倍率提升血量和灵力上限

#### Scenario: Special Ability Unlock
- **WHEN** 大境界突破成功
- **THEN** 系统解锁该境界的特殊能力

#### Scenario: Breakthrough Failure
- **WHEN** 大境界突破失败
- **THEN** 系统应用对应的失败惩罚

### Requirement: Breakthrough Probability Calculation
系统 SHALL 使用先加后乘的方式计算突破成功率。

#### Scenario: Probability Stacking
- **WHEN** 计算总成功率
- **THEN** 系统先将所有加法因素相加，再乘以所有乘法因素

#### Scenario: Probability Cap
- **WHEN** 计算总成功率
- **THEN** 系统确保成功率不超过 100%

