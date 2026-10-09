# wirk-skill

The [WIRK](https://wirk.life) skill teaches an agent to use WIRK well in about 2 KB: start with `wirk status`, find with inline queries, claim wirk before starting it, write with short commands that state the revision they read, record progress as linked notes, complete wirk with its evidence, and leave proposals for background work. The repository is also a Claude Code plugin that carries the skill and registers the `wirk-mcp` server.

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

### Automated publication

Push the exact reviewed version tags for the CLI, MCP and skill. Each existing Release workflow then tests and publishes its component; MCP and skill wait up to ten minutes for the matching CLI wheel and its identical PyPI distribution. Tags choose reviewed source; pushing main does not publish a release.

New GitHub releases stay prereleases until their downloaded public bytes match the build and a clean public installation passes. The shared publication workflow is pinned to an exact revision. Failures appear in Actions. Retry failed jobs to reuse the successful build artifacts: identical existing assets are retained, missing assets are uploaded, and differing bytes or a moved tag stop the run. Do not overwrite a published asset to make a retry pass.

The Release workflow's manual verification input checks an existing public tag without publishing. This publication automation does not update already-installed or running clients.
