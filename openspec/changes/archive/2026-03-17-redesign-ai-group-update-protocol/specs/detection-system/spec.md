## MODIFIED Requirements

### Requirement: Multi-Character Interaction
系统 SHALL 处理多角色交互场景，并将交互组作为 AI 更新的统一单位。

#### Scenario: Interaction Group Formation
- **WHEN** 多个角色在彼此探测范围内
- **THEN** 系统将这些角色组成交互组

#### Scenario: Synchronous Update
- **WHEN** 角色属于交互组
- **THEN** 系统以整个交互组为单位请求一次 AI 更新，并要求返回该组全部角色的同步结果

#### Scenario: Group AI Prompt
- **WHEN** 处理交互组
- **THEN** 系统构建包含组内全部角色信息、共享环境信息和组级协议约束的统一提示词

### Requirement: Independent Character
系统 SHALL 处理无交互的角色，并将其视为单角色交互组执行相同协议。

#### Scenario: Independent Update
- **WHEN** 角色无交互
- **THEN** 系统将该角色视为仅含一个参与者的交互组，并通过组级协议请求和处理 AI 更新

#### Scenario: Unified Processing Path
- **WHEN** 系统处理独立角色
- **THEN** 系统沿用与多人交互组相同的解析、审计和应用流程，而不是使用单独的响应协议
