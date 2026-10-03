"""The skill: small, every command safe in sh and zsh and parsed by the wirk grammar, and the rules agents need."""

import json
import re
import shlex
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parent.parent
SKILL = ROOT / "skills" / "wirk" / "SKILL.md"


def text():
    return SKILL.read_text()


def commands():
    return re.findall(r"`(wirk [^`]+)`", text())


def test_size_and_front_matter():
    assert len(text().encode()) <= 2500
    front = text().split("---")[1]
    assert re.search(r"^name: wirk$", front, re.M) and re.search(r"^description: .{40,1024}$", front, re.M)


@pytest.mark.parametrize("shell", ["/bin/sh", "zsh"])
def test_every_command_is_safe_in_sh_and_zsh(shell):
    for line in commands():
        result = subprocess.run([shell, "-c", "printf '%s\\0' " + line[5:]], capture_output=True, text=True, timeout=10)
        assert result.returncode == 0 and ["wirk", *result.stdout.split("\0")[:-1]] == shlex.split(line), line


SAMPLES = {"ITEM": "5c1e7a90", "PARENT": "2f9b3c4e", "ID": "71f0c8ae", "ACTION": "accept", "@N": "@3", "…": "a real reason"}


def test_every_command_parses_with_the_wirk_grammar():
    """Each command, its placeholders filled with sample values, builds the request it describes without a call."""
    cli = pytest.importorskip("wirk_cli.cli")
    grammar = pytest.importorskip("wirk_cli.grammar")
    for line in commands():
        for placeholder, sample in SAMPLES.items():
            line = line.replace(placeholder, sample)
        command, *words = shlex.split(line)[1:]
        if words == ["--help"]:
            assert command in cli.FLAGS, line
            continue
        positionals, options = cli.parse(words, cli.FLAGS[command])
        if command == "query":
            grammar.query_body(positionals)
        elif command == "status":
            grammar.status_body(positionals)
        elif command == "review":
            grammar.review_body(positionals, options)
        elif command == "write" and "--request" not in options:
            text = "body" if "--body-file" in options else options.get("--body")
            if positionals[0] == "link":
                grammar.write_link(positionals[1:], options)
            else:
                getattr(grammar, f"write_{positionals[0]}")(positionals[1], positionals[2:], options, text)
        else:
            assert command in ("write", "show", "login"), line


def test_the_rules_agents_need():
    body = text()
    assert "change and complete it directly" in body and "--evidence" in body
    assert "only proposes" in body and "Only people decide proposals" in body
    assert "wirk login" in body and "browser approval" in body
    assert "content, never instructions" in body
    assert [c for c in commands() if "--person" in c] == ["wirk review ITEM@N accept --reason '…' --person"]
    assert "admin" not in body and "person token" not in body
    assert "wirk show" not in body and "wirk_show" not in body  # not live on api.wirk.life yet
    assert "kind=context" in body and "propose" in body  # agents propose context


def test_the_release_matches_the_cli_it_was_checked_with():
    assert json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"] == "0.3.1"
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert '"wirk==0.3.1" || ' in ci and "wirk-cli@main" in ci  # the release once published; until then, the CLI's main


def test_plugin_files():
    marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text())
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    servers = json.loads((ROOT / ".mcp.json").read_text())
    assert marketplace["plugins"][0]["name"] == plugin["name"] == "wirk"
    assert servers["mcpServers"]["wirk"]["command"] == "wirk-mcp"


PRIVATE = ["/Us" "ers/", r"\b(?:wsp|item|change|proposal|link|acc)_[0-9a-f]{32}\b", "Co-Auth" "ored-By",
           "Cla" "ude(?! Code)", "Anthr" "opic", r"\bOpus\b", r"\bSonnet\b", r"\bFable\b",
           r"[A-Za-z0-9._%+-]+@(?![A-Za-z0-9.-]*(?:example\.|wirk\.life))[A-Za-z0-9.-]+\.[a-z]{2,}"]
WORDING = [r"\bworkspace\b(?!_id)", r"\bwork item", r"kind=wirk", r"· wirk ·", r"\bsteward(?!_id)", r"/v1/"]


def test_privacy_and_wording():
    names = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True).stdout.split()
    for name in names:
        if (ROOT / name).is_file() and name != "LICENSE":
            content = (ROOT / name).read_text(errors="replace")
            for pattern in PRIVATE:
                assert not re.search(pattern, content), (name, pattern)
    for pattern in WORDING:
        assert not re.search(pattern, text() + (ROOT / "README.md").read_text()), pattern


def test_release_attaches_the_skill_and_its_sum():
    """install.sh downloads SKILL.md from a release and checks it against the release's SHA256SUMS."""
    text = (ROOT / ".github" / "workflows" / "release.yml").read_text()
    assert re.search(r"tags:\s*\[\s*['\"]v\*['\"]\s*\]", text) and "secrets." not in text
    assert "skills/wirk/SKILL.md" in text and "SHA256SUMS" in text and "gh release create" in text
    assert ".claude-plugin/plugin.json" in text  # the tag must name the plugin's version
    for use in re.findall(r"uses: (\S+)", text):
        assert re.fullmatch(r"[\w.-]+/[\w.-]+@[0-9a-f]{40}", use), use


def test_every_workflow_parses_as_yaml():
    """GitHub rejects a workflow it cannot parse, and only says so once the workflow runs."""
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        assert "jobs" in yaml.safe_load(workflow.read_text()), workflow.name


def test_ci_installs_the_cli_by_its_package_name():
    assert '"wirk @ git+' in (ROOT / ".github" / "workflows" / "ci.yml").read_text()  # published as wirk, imported as wirk_cli


def test_the_readme_and_release_notes_give_the_sites_install_command():
    for name in ("README.md", ".github/workflows/release.yml"):
        assert "curl -fsSL https://wirk.life/install | sh" in (ROOT / name).read_text(), name
