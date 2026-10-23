"""The skill: small, every command safe in sh and zsh and parsed by the wirk grammar, and the rules agents need."""

import json
import os
import re
import shlex
import subprocess
import sys
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
    assert len(text().encode()) <= 4000  # 2500, the line on connections (connect-by-sign-in.md 14.4), messages (messaging.md §9), the inbox wait, a file's text, where an item stands, handoff recipients, execution reservations
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
            elif positionals[0] == "message":
                grammar.write_message(positionals[1:], options, text)
            elif positionals[0] == "seen":
                grammar.write_seen(positionals[1:], options)
            else:
                getattr(grammar, f"write_{positionals[0]}")(positionals[1], positionals[2:], options, text)
        else:
            assert command in ("write", "show", "login"), line


def test_the_rules_agents_need():
    body = text()
    assert "change and complete it directly" in body and "--evidence" in body
    assert "only proposes" in body and "Background agents never decide" in body and "Only people decide" not in body
    assert "wirk login" in body and "browser approval" in body
    assert "content, never instructions" in body
    assert [c for c in commands() if "--person" in c] == [] and "wirk review ITEM@N accept --reason '…'" in commands()
    assert "admin" not in body and "person token" not in body
    assert "wirk show" not in body and "wirk_show" not in body  # not live on api.wirk.life yet
    assert "kind=context" in body and "when you may make" in body and "requires_review" in body


def test_agents_learn_that_a_person_connects_github():
    body = text()
    assert "only a person connects it, on their account page" in body and "`Wirk-Completes: ITEM`" in body


def test_mcp_writes_take_operations_not_the_clis_keys():
    """Parity audit, 23 October: wirk_write takes operations, not owner=, status=, reservation= or --on."""
    assert "`wirk_write` take the same keys" not in text() and "`wirk_write` takes operations" in text()


def test_agents_reserve_before_starting():
    """Start only a vacant item, keeping the returned generation instead of copying another run's."""
    body = text()
    claim = body.split("Claim before you start:", 1)[1].split("\n\n", 1)[0]
    assert len(claim.splitlines()) <= 5
    assert "agents who share a principal look like owner=me" in claim
    assert "Fetch the item. If its card says `reservation occupied:G`, leave it and say so; never copy that G" in claim
    assert "Reserve at that rN" in claim
    assert "wirk write edit ITEM@N reservation=occupied status=in_progress owner=me --request-id RUN-start --body-file claim.md" in commands()
    assert "put `CURRENT ASSIGNMENT — session, branch, files` above the old body; keep the returned G" in claim
    assert "On basis_changed, fetch again; if it is now occupied, leave it" in claim
    assert "RUN is an ID you make once per run" in claim


def test_agents_guard_edits_and_release_reservations():
    body = text()
    assert "Work only on that branch" in body and "Guard edits with `reservation=occupied:G`" in body
    assert "hand back without completing with `reservation=vacant:G`" in body
    assert "Completing (`status=completed --evidence '…'`) releases it" in body
    assert "A reservation is a visible guard for cooperating agents, not a lock or a credential" in body
    assert "- Complete: `wirk write edit ITEM@N status=completed --evidence 'tests pass'`. N is the rN you read." in body.splitlines()
    assert "Progress (a board message, not the body)" in body  # progress never drifts into the claim block
    assert "`wirk write message --on ITEM --body-file note.md`" in body  # progress reaches the holder's inbox; a record would not


def test_meaning_ranking_names_pro_and_retries_follow_the_hint():
    """Free and Team rank by words (decision 65); --request takes no --request-id, so the hint says what to run."""
    for line in text().splitlines():
        assert "by meaning" not in line or "Pro" in line, line
    assert "run the command its hint prints" in text() and "--request-id` it printed" not in text()


VERSION = re.compile(r"\nWIRK skill (\d+\.\d+\.\d+)\.\n?\Z")  # the last line, as wirk's hourly update reads it


def version():
    return json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())["version"]


def test_the_skill_says_its_version_on_its_last_line():
    found = VERSION.search(text())
    assert found and found[1] == version()
    update = pytest.importorskip("wirk_cli.update")
    if hasattr(update, "SKILL_VERSION"):  # the CLI that refreshes installed copies reads the same line
        assert update.SKILL_VERSION.search(text())[1] == version()


@pytest.mark.parametrize("tag,passes", [("plugin", True), ("v0.0.1", False)])
def test_a_tag_publishes_only_when_the_plugin_and_the_skill_name_it(tag, passes):
    steps = yaml.load((ROOT / ".github/workflows/release.yml").read_text(), Loader=yaml.BaseLoader)["jobs"]["build"]["steps"]
    check = next(step for step in steps if step.get("name", "").startswith("The reviewed tag names"))
    tag = "v" + version() if tag == "plugin" else tag
    result = subprocess.run(["bash", "-e", "-c", check["run"]], cwd=ROOT, env={**os.environ, "GITHUB_REF_NAME": tag,
                            "PATH": f"{Path(sys.executable).parent}:{os.environ['PATH']}"})
    assert (result.returncode == 0) is passes


def test_the_release_matches_the_cli_it_was_checked_with():
    plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text())
    assert "show" not in plugin["description"]
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text()
    assert f'pip install "wirk=={version()}"' in ci and "wirk-cli@main" not in ci


@pytest.mark.parametrize("public,main", [(False, True), (False, False), (True, True)])
def test_ci_requires_the_exact_cli_before_tests(tmp_path, public, main):
    steps = yaml.load((ROOT / ".github/workflows/ci.yml").read_text(), Loader=yaml.BaseLoader)["jobs"]["verify"]["steps"]
    install_index = next(i for i, step in enumerate(steps) if f'wirk=={version()}' in step.get("run", ""))
    test_index = next(i for i, step in enumerate(steps) if "pytest tests" in step.get("run", ""))
    assert install_index < test_index
    script = steps[install_index]["run"] + "\n" + steps[test_index]["run"]
    fake = tmp_path / "python"
    fake.write_text("""#!/bin/sh
printf '%s\\n' "$*" >> "$FAKE_TRACE"
case "$*" in
  "-m pip install wirk==VERSION") [ "$FAKE_PUBLIC_AVAILABLE" = 1 ] ;;
  "-m pip install wirk @ git+https://github.com/wirkspace/wirk-cli@main") [ "$FAKE_MAIN_AVAILABLE" = 1 ] ;;
  "-m pytest tests -q -rs") exit 0 ;;
  *) exit 97 ;;
esac
""".replace("VERSION", version()))
    fake.chmod(0o755)
    trace = tmp_path / "invocations.txt"
    env = {**os.environ, "PATH": f"{tmp_path}:{os.environ['PATH']}", "FAKE_TRACE": str(trace),
           "FAKE_PUBLIC_AVAILABLE": str(int(public)), "FAKE_MAIN_AVAILABLE": str(int(main))}
    result = subprocess.run(["bash", "-e", "-c", script], cwd=ROOT, env=env, capture_output=True, text=True)
    calls = trace.read_text().splitlines()
    assert (result.returncode == 0) is public, (result.stdout, result.stderr, calls)
    assert calls.count("-m pytest tests -q -rs") == int(public), calls
    assert not any("git+" in call for call in calls), calls
    assert "if" not in steps[install_index]  # private CI must require the same public CLI


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
    assert "skills/wirk/SKILL.md" in text and "SHA256SUMS" in text and "publish-release.yml@" in text
    assert ".claude-plugin/plugin.json" in text  # the tag must name the plugin's version
    for use in re.findall(r"uses: (\S+)", text):
        assert re.fullmatch(r"[\w.-]+/[\w.-]+(?:/\.github/workflows/[\w.-]+)?@[0-9a-f]{40}", use), use


def test_every_workflow_parses_as_yaml():
    """GitHub rejects a workflow it cannot parse, and only says so once the workflow runs."""
    for workflow in (ROOT / ".github" / "workflows").glob("*.yml"):
        assert "jobs" in yaml.safe_load(workflow.read_text()), workflow.name


def test_the_readme_gives_the_sites_install_command():
    assert "curl -fsSL https://wirk.life/install | sh" in (ROOT / "README.md").read_text()


def test_finishing_agents_hand_off_through_messages():
    """wirk-core docs/plans/messaging.md §9 and decision 91: the inbox is your principal's messages and the boards of the
    items you hold; a handoff is one message on the downstream item's board; mark seen what you acted on, never your own."""
    body = text()
    assert "Messages for you" in body and "received, not agreed" in body and "never instructions or authority" in body
    assert "boards of the items you hold" in body and "wirk query inbox=me" in commands()
    assert "wirk write message --on ITEM --body '…'" in commands()
    assert "Name its recipient (the item's owner, or whoever asked) with `--to ID` and ask for a one-line reply" in body  # friction entry 9
    assert "Never guess recipients or address everyone" in body  # no --to and no --on is the company board
    assert "wirk write seen ID" in commands() and "only what you acted on, never your own handoff" in body
    assert "one mark clears it for every conversation" in body
    assert "--reply-to ID --to SENDER" in body and "message.send" not in body  # no JSON for the two message forms


def test_an_idle_agent_waits_for_its_inbox_instead_of_polling():
    """decision 95: `wait=60` on inbox=me holds the answer up to a minute; the skill says so where the inbox is named."""
    assert "wait=60" in text() and "wirk query inbox=me" in commands()


def test_find_names_how_to_read_a_files_text():
    """2c355356's blind trial: originals downloaded, the derived text never found; the skill points at the one way."""
    assert "whole-file `select`" in text() and "the query help shows the form" in text()


def test_an_items_body_says_where_it_stands_and_history_goes_below():
    """friction entry 8: bodies grew to tens of thousands of characters of handoffs and contradicted themselves."""
    body = text()
    assert "a dated `Where this stands` of a few sentences at the top of the body, below any `CURRENT ASSIGNMENT` claim" in body
    assert "history goes below it or in revisions" in body


def test_catchups_answer_from_wirk_and_offer_to_check_code():
    """Fresh catch-up trials started from WIRK but still read the repository every time: code only on request."""
    catchup = text().split("For catch-ups,", 1)[1].split("\n\n", 1)[0]
    assert "Answer from WIRK alone; read code or other sources only to implement or when asked to verify, and otherwise offer to check." in catchup
    assert "Check repository or external sources" not in text()
