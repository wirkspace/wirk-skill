# wirk-skill

The [WIRK](https://wirk.life) skill teaches an agent to use WIRK well in under 4 KB: start with `wirk status`, answer catch-ups from WIRK, find with inline queries, reserve work before starting it, write with short commands that state the revision they read, post progress and handoffs on an item's board, complete work with its evidence, and leave proposals for background work. The repository is also a Claude Code plugin that carries the skill and registers the `wirk-mcp` server.

## Install

One command sets up everything on a machine, this skill included, after asking:

```
curl -fsSL https://wirk.life/install | sh
```

For the Claude Code plugin, first install the [wirk command](https://github.com/wirkspace/wirk-cli) and [wirk-mcp](https://github.com/wirkspace/wirk-mcp) on `PATH` and run `wirk login`; the plugin does not install them:

```
claude plugin marketplace add wirkspace/wirk-skill
claude plugin install wirk@wirk
```

If you use the plugin, skip the installer’s Claude Code setup and any manual MCP registration or skill copying for Claude Code.

For manual setup in Codex, or any agent that reads skills from a folder, copy `skills/wirk/SKILL.md` into its skills folder (for Codex, `~/.agents/skills/wirk/SKILL.md`; replace a `wirk` folder that is a link to an earlier install rather than writing through it). An agent with only a shell needs just the wirk command and the skill's text. Each release attaches `SKILL.md` with its SHA-256 sum.

## Version and updates

The skill's last line names its version, for example `WIRK skill 0.4.30.`; it is the same as the plugin's version and the release tag. The `wirk` command keeps installed copies current without asking: at most once an hour, after a command, it asks GitHub for the latest release tag and, when a copy in `~/.claude/skills/wirk`, `~/.agents/skills/wirk` or `$CODEX_HOME/skills/wirk` is older, replaces it with the release's `SKILL.md` once it matches `SHA256SUMS`. A copy without a version line counts as older and is replaced. It never writes through a link or creates a folder; a copy it cannot replace is named in the line `wirk` prints once a day. Claude Code updates the plugin itself.

## Releasing

A release is a version bump of `.claude-plugin/plugin.json` and of the skill's last line merged to main with `Release: publish wirk-skill <version>` in its squash body. After the release check passes on that exact commit, the tag `v<version>` is created there; pushing main publishes nothing, and a tag is never moved. The tag's Release workflow waits up to ten minutes for the `wirk` release of the same version, tests the skill against that public CLI, and attaches `SKILL.md` and `SHA256SUMS` to a GitHub Release. Release `wirk` first: without its matching release the tag fails and stays unpublished.

New GitHub releases stay prereleases until their downloaded public bytes match the build and a clean public installation passes. Retry failed jobs to reuse the successful build artifacts: identical existing assets are retained, missing assets are uploaded, and differing bytes or a moved tag stop the run. The Release workflow's manual verification input checks an existing public tag without publishing.

## License

Apache-2.0. See [LICENSE](LICENSE).
