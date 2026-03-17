## ADDED Requirements

### Requirement: Magic Treasure System
系统 SHALL 管理法宝，包括基础属性、数值加成和特殊技能。

#### Scenario: Treasure Attributes
- **WHEN** 创建或加载法宝
- **THEN** 系统设置法宝的五行属性、灵力消耗、境界要求、耐久度

#### Scenario: Treasure Numerical Bonuses
- **WHEN** 装备法宝
- **THEN** 系统应用法宝的数值加成（攻击、防御、灵力上限、血量上限、神识、遁速等）

#### Scenario: Treasure Durability
- **WHEN** 使用法宝
- **THEN** 系统减少法宝的损耗度和耐久度

### Requirement: Pill System
系统 SHALL 管理丹药，包括恢复类、突破类和特殊效果丹药。

#### Scenario: Pill Consumption
- **WHEN** 角色使用丹药
- **THEN** 系统应用丹药效果并从物品栏移除该丹药

#### Scenario: Breakthrough Pill
- **WHEN** 角色服用破境丹
- **THEN** 系统临时增加下一次突破的成功率

### Requirement: Inventory System
系统 SHALL 管理角色的物品栏，包括法宝、丹药、灵石等。

#### Scenario: Item Addition
- **WHEN** 角色获得物品
- **THEN** 系统将物品添加到物品栏

#### Scenario: Item Removal
- **WHEN** 角色失去或使用物品
- **THEN** 系统从物品栏移除对应物品

#### Scenario: Item Count
- **WHEN** 添加可堆叠物品
- **THEN** 系统增加物品数量而非创建新条目
