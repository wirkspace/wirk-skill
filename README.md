# wirk-skill

The [WIRK](https://wirk.life) skill teaches an agent to use WIRK well in about 2 KB: start with `wirk status`, find with inline queries, write with short commands that state the revision they read, record progress as linked notes, complete wirk with its evidence, and leave proposals for background work. The repository is also a Claude Code plugin that carries the skill and registers the `wirk-mcp` server.

## Install

One command sets up everything on a machine, this skill included, after asking:

```
curl -fsSL https://wirk.life/install | sh
```

Or, in Claude Code, the plugin brings the skill and the `wirk-mcp` server together (install the [wirk command](https://github.com/wirkspace/wirk-cli) and [wirk-mcp](https://github.com/wirkspace/wirk-mcp) first, and run `wirk login`):

```
claude plugin marketplace add wirkspace/wirk-skill
claude plugin install wirk@wirk
```

In Codex, or any agent that reads skills from a folder, copy `skills/wirk/SKILL.md` into its skills folder (for Codex, `~/.agents/skills/wirk/SKILL.md`; replace a `wirk` folder that is a link to an earlier install rather than writing through it). An agent with only a shell needs just the wirk command and the skill's text. Each release attaches `SKILL.md` with its SHA-256 sum.

## License

Apache-2.0. See [LICENSE](LICENSE).
