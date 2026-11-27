# 开源组件从立项到首发

当你想把一个内部组件拆成开源包，或准备做一个新的库、CLI 或 SDK，可以用这个 Skill 判断是否值得做、该验证什么，以及什么时候可以发布。不必从头开始，已有项目可直接从当前阶段切入。

## 怎么用

例如，可以直接说：

- 「我想为某个服务做一套 CLI，先帮我对比官方替代方案，看看要不要自己做。」
- 「这个库准备第一次发包，帮我检查文档和 CI/CD，并在干净环境验证用户将拿到的包。先不发布。」

工作流程见 [SKILL.md](./SKILL.md)。[现成方案与案例](./references/existing-options.md) 用于参考和比选；[Python 首发清单](./references/python-pypi-release.md) 只在通过 GitHub Actions 发布到 PyPI 时使用。
