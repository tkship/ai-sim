## Why

当前项目已存在角色坐标字段与探测距离计算，但缺少明确的“地图”概念与可视化，导致坐标在 UI 和玩法层面价值不足。

需要补上一个可运行、可扩展的一版地图系统，让角色位置在主循环中持续可见、可约束，并可被 AI 决策上下文使用。

## What Changes

- 新增世界地图模型（尺寸、边界、坐标归一化、边界约束）
- 将地图接入 `World`：
  - 角色加入/更新时自动进行边界裁剪
  - 环境信息输出包含地图元数据和角色坐标
- 扩展 AI 变化解析与应用：支持可选的位置变化字段（绝对坐标或位移）
- 更新 UI：新增地图面板，显示角色在地图中的相对位置
- 更新配置与文档：在 `config.yaml` 增加 `map` 段，README 增加地图说明
- 增补测试：覆盖地图边界约束、位置变化应用、存档坐标回环

## Capabilities

### New Capabilities
- `world-map-system`: 世界地图配置、边界约束、坐标归一化
- `map-visualization`: UI 地图面板显示角色位置

### Modified Capabilities
- `ai-interaction`: 增加位置变化字段解析与应用
- `world-environment`: 环境字典输出地图与坐标上下文

## Impact

- 新增 `src/world/map.py`
- 变更 `src/game/world.py`, `src/game/loop.py`, `src/ui/renderer.py`
- 变更 `src/ai/parser.py`, `src/ai/interface.py`, `src/ai/prompt.py`
- 更新 `config.yaml`, `README.md`, `test/test_game.py`
