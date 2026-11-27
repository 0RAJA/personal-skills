# Python 包首发清单：用 GitHub Actions 发布到 PyPI

仅在选用 GitHub Actions 和 PyPI 时参考。优先沿用现有流程，这是一份清单，不是模板。

1. **PR 检查**：覆盖文档承诺的 Python 版本和影响公开行为的可选依赖（extras）。以只读权限运行代码检查和测试。来自 fork 的 PR 不得访问发布凭据。
2. **构建并验证**：在拟发布的提交上核对包名、版本、README、许可证和 Git 标签（若使用）。按需构建 wheel 和源码分发包（sdist），检查包的元数据。在源码目录之外的隔离环境安装并跑一遍公开的快速上手。若发布 sdist，也确认它能构建和安装。保留产物和校验值，供发布阶段直接使用。
3. **发布**：获准后，条件允许时用 PyPI Trusted Publishing。核对 PyPI 中配置的仓库、工作流文件名和环境（若有）。只给发布任务授予 `id-token: write`。直接发布已验证的产物，不重新构建。只要能保留验证步骤并把实际发布单独控制，也可手动首发。
4. **从 PyPI 验证**：确认公开版本和文件符合预期，核对校验值，再在干净环境里从 PyPI 安装该确切版本。如果上传结果不确定，先查 PyPI 上是否已有对应产物，再决定要不要重试。

官方资料：[Python 打包指南](https://packaging.python.org/en/latest/tutorials/packaging-projects/) · [PyPI Trusted Publishing 使用指南](https://docs.pypi.org/trusted-publishers/using-a-publisher/)。
