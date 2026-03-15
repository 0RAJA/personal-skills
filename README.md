# Personal AI Skills

A collection of reusable AI agent skills for development workflows. Compatible with Codex, Cursor, and other AI coding assistants.

## Project Structure

```text
.
├── AGENTS.md              # Agent configuration
└── skills/
    └── auditing-skills/   # Security auditing for external scripts and skills
        ├── SKILL.md
        └── README.md
```

## Skills Index

### 🛡️ [Auditing Skills](./skills/auditing-skills/README.md)

Security review workflow for externally downloaded code, scripts, and skills before execution.

- **Core features**: Keyword scanning, sensitive path detection, obfuscated code analysis, sandbox verification guidance.
- **Use cases**: After downloading third-party skills, before running unknown scripts, code security assessment.

## Installation

Install via Codex skill installer:

```bash
# From GitHub
git@github.com:0RAJA/personal-skills.git
```

## License

MIT
