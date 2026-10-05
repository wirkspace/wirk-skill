# wirk-skill

The [WIRK](https://wirk.life) skill teaches an agent to use WIRK well in about 2 KB: start with `wirk status`, find with inline queries, write with short commands that state the revision they read, record progress as linked notes, complete wirk with its evidence, and leave proposals for background work. The repository is also a Claude Code plugin that carries the skill and registers the `wirk-mcp` server.

## Install

Install the CLI and, for MCP hosts, the MCP server with [uv](https://docs.astral.sh/uv/getting-started/installation/):

```
uv tool install wirk
uv tool install https://github.com/wirkspace/wirk-mcp/releases/download/v0.4.1/wirk_mcp-0.4.1-py3-none-any.whl
```

The CLI comes from PyPI; the MCP server comes from its public GitHub release. Both require Python 3.12 or later. If you need uv, use `brew install uv` with Homebrew or `pipx install uv` with pipx. Follow uv's PATH guidance so the commands are available to your agent host.

Run `wirk login`, approve the code in your browser, then run `wirk status`. Installing the packages, authorizing the machine and adding this skill are separate steps. See [Getting started](https://wirk.life/docs/getting-started/) for account setup and connection help.

### Claude Code

The plugin adds the skill and registers the installed `wirk-mcp` executable:

```
claude plugin marketplace add wirkspace/wirk-skill
claude plugin install wirk@wirk
```

The plugin expects `wirk-mcp` on the host's PATH; it does not install the executable. Start a new Claude Code session after installation. If you use the plugin, skip manual MCP registration and skill copying to avoid duplicate tools.

For manual setup instead, follow [wirk-mcp's registration instructions](https://github.com/wirkspace/wirk-mcp#install) and copy [skills/wirk/SKILL.md](skills/wirk/SKILL.md) to `~/.claude/skills/wirk/SKILL.md`. Replace a `wirk` folder that is a link to an earlier install rather than writing through it.

### Codex

Follow [wirk-mcp's registration instructions](https://github.com/wirkspace/wirk-mcp#install), then copy [skills/wirk/SKILL.md](skills/wirk/SKILL.md) to `~/.agents/skills/wirk/SKILL.md`. Replace an old `wirk` link itself before copying. Start a new Codex session if the tools or skill do not appear. This is Codex's [documented personal skills folder](https://learn.chatgpt.com/docs/build-skills).

An agent with only a shell needs just the `wirk` command and the skill's text. Each [release](https://github.com/wirkspace/wirk-skill/releases) attaches `SKILL.md` with its SHA-256 sum.

## License

Apache-2.0. See [LICENSE](LICENSE).
