## Why

当前 AI 交互链路以“解析并直接应用属性变化”为主，缺少按交互组组织的统一响应协议和独立的强审计层，导致多人交互的一致性、资源守恒、以及非法输出拦截能力不足。现在项目已经明确采用“AI 同时输出意图与数值结果、代码负责强审计”的路线，需要先把协议、审计规则和模块边界正式固化下来，才能安全继续实现。

## What Changes

- 将 AI 更新结果统一为按交互组返回的 `GroupUpdate` 协议，单人更新也视为单角色交互组。
- 为 AI 响应定义最小强审计字段集：组级场景与事件、角色级意图、行为、依据、属性变化、物品变化。
- 新增独立的 AI 响应审计能力，实施保守策略：共享事实或资源守恒类硬错误直接整组失败，轻微数值超界允许裁剪并记录警告。
- 重构 AI 处理链路的职责边界：`PromptBuilder` 负责协议声明，`ResponseParser` 负责结构化解析，新增 validator/audit 层负责强审计与裁剪，`ChangeApplier` 只消费已通过审计的结果。
- 将 AI 输出中的 `action_type` 和 `event.type` 收敛到白名单集合，禁止自由发明类型，确保后续审计可控。

## Capabilities

### New Capabilities
- `ai-response-audit`: 定义交互组响应的强审计、裁剪、整组失败策略和审计结果处理规则。

### Modified Capabilities
- `ai-interaction`: 将 AI 的提示词、响应协议、解析和应用流程升级为基于交互组的结构化更新协议，并要求输出依据字段以支撑强审计。
- `detection-system`: 明确探测形成的交互组是 AI 更新的统一单位，单角色更新视为单角色交互组，与组级响应协议对齐。

## Impact

- 变更 `src/ai/parser.py`, `src/ai/interface.py`, `src/ai/prompt.py`
- 新增独立的 AI 审计/校验模块（例如 `src/ai/audit.py` 或同类模块）
- 变更 `src/game/loop.py` 以统一单人/多人组处理路径
- 可能调整 `src/interaction/detector.py` 输出在 AI 流程中的使用方式，但不改变其分组职责
- 更新或新增测试，覆盖协议解析、整组失败、轻微裁剪、白名单类型、资源守恒与共享事实一致性
