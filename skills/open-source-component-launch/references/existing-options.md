# 现成方案与案例

核对日期：2026-11-27。以下是一手资料，不代表建议安装。选用工具前，请核对当前要求。

| 参考资料 | 适合复用什么 | 不能替代什么 |
| --- | --- | --- |
| [Superpowers 的 brainstorming Skill](https://github.com/obra/superpowers/blob/main/skills/brainstorming/SKILL.md) | 澄清需求、探索替代方案、确认设计 | 在同一场景下比较采用现成方案与自研，以及验证首发产物 |
| [GitHub 开源指南](https://opensource.guide/starting-a-project/)和 [OpenSSF 最佳实践](https://www.bestpractices.dev/en/criteria/0) | 公开项目的基础建设、成熟度和安全检查清单 | 证明这个组件值得做，且首个调用方用得起来 |
| [Scientific Python cookie](https://github.com/scientific-python/cookie) | 搭建 Python 仓库，复用打包、CI 和发布选项 | 跨技术栈的工作流程，或对实际产物的独立验证 |
| [Release Please](https://github.com/googleapis/release-please) | 发布频率值得自动化时，生成发布 PR、更新版本和变更日志、创建 GitHub Release | 向包仓库发布，或验证实际发布的产物 |
| [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) | 通过身份联邦获得短期发布凭据 | 测试 wheel 和 sdist，或确认项目权属 |

## 两个实际案例

- [思源 CLI 替换](https://github.com/0RAJA/personal-skills/pull/3)：官方 CLI 覆盖了已验证的使用场景，所以直接采用。旧补丁不用合入，获准后关闭过时事项。
- [ui-stream 的方案对比](https://github.com/0RAJA/ui-stream/blob/main/docs/comparison.md)：能用 SSE 传输不等于能把进度快照控制在一定范围内，并保证先提交最终结果、再通知完成。事务仍由宿主管理。要测失败分支：如果提交失败，就不能发成功通知。
- [ui-stream 的 CI](https://github.com/0RAJA/ui-stream/blob/main/.github/workflows/ci.yml)和[发布流程](https://github.com/0RAJA/ui-stream/blob/main/.github/workflows/release.yml)：发布任务下载并使用验证阶段构建的分发包。值得复用的是「验证过什么，就发布什么」，不必照搬整个测试矩阵。
