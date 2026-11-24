# design-games

一个综合游戏设计、游戏策划与制作技能，采用主技能路由和按需加载的专业模块，把创意转化为可制作、可验证、可迭代的方案。

## 使用

仓库仅管理技能源码。将 `design-games/` 目录放入项目的 `.agents/skills/`，或按你的 Agent 平台规范安装该目录。技能名为 `design-games`。

## 覆盖范围

- 设计基础与核心玩法
- 系统、战斗、角色、装备与成长
- 关卡、遭遇、解谜与开放世界
- 技术策划、数据契约、性能与验收
- 叙事、任务、对白与本地化
- 数值、概率、保底、成长与经济
- 游戏美术、视觉方向与资产生产
- 技术美术、材质、Shader、LOD 与资产管线
- 原型、制作、跨专业评审与玩家测试
- AI 代理游玩、自动化回归与可测试性设计
- 各专业的可复用交付模板

## 目录

```text
design-games/
├── SKILL.md
├── references/
│   ├── foundations.md
│   ├── systems.md
│   ├── level.md
│   ├── technical.md
│   ├── narrative.md
│   ├── numerical.md
│   ├── art.md
│   ├── technical-art.md
│   ├── production.md
│   ├── agent-playtesting.md
│   └── templates.md
└── scripts/
    ├── design_math.py
    ├── art_budget.py
    └── 测试文件
```

## 工具示例

```bash
python design-games/scripts/design_math.py expected-dps \
  --damage 100 --interval 0.5 --accuracy 0.8 \
  --crit-chance 0.25 --crit-multiplier 2

python design-games/scripts/art_budget.py texture \
  --width 2048 --height 2048 --bits-per-pixel 4
```

数值和美术预算结果均带有模型假设；实际项目仍需在目标平台和玩家测试中验证。

## 测试

```bash
cd design-games/scripts
python -m unittest -v test_design_math.py test_art_budget.py
```
