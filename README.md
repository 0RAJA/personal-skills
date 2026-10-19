# 个人 AI 技能库

可复用的 AI Agent 技能集合，适用于 Codex、Cursor 等 AI 编码助手。

## 项目结构

```text
.
├── AGENTS.md                              # Agent 配置与维护须知
└── skills/
    ├── auditing-skills/                   # 安全审计技能
    │   ├── SKILL.md
    │   └── README.md
    ├── deep-topic-learning/               # 深度技术主题学习
    │   ├── SKILL.md
    │   ├── README.md
    │   └── references/
    │       └── artifact-templates.md
    ├── local-context-maintenance/         # 本地上下文维护
    │   ├── SKILL.md
    │   ├── README.md
    │   ├── references/
    │   │   └── project-examples.md
    │   ├── assets/
    │   │   └── maintenance-record.md
    │   └── agents/
    │       └── openai.yaml
    └── siyuan-openclaw-kb-maintenance/    # 思源笔记知识库维护
        ├── SKILL.md
        ├── README.md
        ├── scripts/
        │   └── siyuanctl.py
        └── tests/
            ├── __init__.py
            └── test_siyuanctl.py
```

## 技能索引

### [安全审计技能](./skills/auditing-skills/README.md)

安全审查外部代码、脚本和技能的标准化流程，在运行外部来源代码之前识别并拦截潜在威胁。

- **核心能力**：关键词扫描、敏感路径检测、混淆代码分析、沙箱验证引导
- **适用场景**：下载第三方技能后审查、运行未知脚本前评估

### [深度技术主题学习](./skills/deep-topic-learning/README.md)

面向复杂技术主题的结构化学习方法论，五段式循环工作流配合四层文档体系。

- **核心能力**：建地图 → 拆模块跑通 → 源码对齐 → 主动总结纠错 → 疑惑档案
- **适用场景**：系统性学习大型代码库、新框架、多层架构，沉淀学习笔记与教程

### [本地上下文维护](./skills/local-context-maintenance/README.md)

根据当前项目背景与既有目录、命名和文档风格整理本地材料，便于查找、理解与后续接续。

- **核心能力**：材料归属与入口梳理、目录层级调整、引用修补、原件和已有工作保全
- **适用场景**：材料归类、目录重构、历史整理续接、旧结论及冲突材料复核

### [思源笔记知识库维护](./skills/siyuan-openclaw-kb-maintenance/README.md)

通过 SiYuan API 进行知识库自动化维护的脚本优先工具集。

- **核心能力**：笔记本/文档 CRUD、资产管理、模板操作、Markdown 导出
- **适用场景**：API 自动化维护思源笔记、批量操作笔记库内容

## 安装

```bash
git clone git@github.com:0RAJA/personal-skills.git
```

## 许可证

MIT
