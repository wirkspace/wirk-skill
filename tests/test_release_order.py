"""Publishing waits for tested public dependencies and remains safe to dispatch for verification."""
from pathlib import Path
import re
import yaml

ROOT = Path(__file__).parent.parent
KIND = 'skill'

def workflow():
    return yaml.load((ROOT/".github/workflows/release.yml").read_text(), Loader=yaml.BaseLoader)

def test_reviewed_tags_and_read_only_verification_are_separate():
    doc=workflow()
    assert doc["on"]["push"]["tags"] == ["v*"]
    assert "verify_tag" in doc["on"]["workflow_dispatch"]["inputs"]
    assert "github.event_name == 'push'" in doc["jobs"]["build"]["if"]
    verify=doc["jobs"]["verify"]
    assert "github.event_name == 'workflow_dispatch'" in verify["if"]
    assert verify["with"]["verify_tag"] == "${{ inputs.verify_tag }}"
    assert verify["permissions"] == {"contents":"read"}
    assert doc["concurrency"]["cancel-in-progress"] == "false"

def test_publishing_reuses_a_pinned_helper_after_successful_build():
    publish=workflow()["jobs"]["publish"]
    assert publish["needs"] == "build"
    assert re.fullmatch(r"wirkspace/wirk-cli/\.github/workflows/publish-release\.yml@[0-9a-f]{40}", publish["uses"])
    assert publish["with"]["kind"] == KIND
    assert publish["permissions"] == {"contents":"write"}

def test_matching_cli_is_public_before_package_tests_run():
    steps=workflow()["jobs"]["build"]["steps"]
    wait=next(i for i,s in enumerate(steps) if "wait-cli" in s.get("run", ""))
    install=next(i for i,s in enumerate(steps) if "pip install" in s.get("run", ""))
    tests=next(i for i,s in enumerate(steps) if "pytest tests" in s.get("run", ""))
    assert wait < install <= tests
    assert "GITHUB_REF_NAME" in steps[wait]["run"]
    assert "GH_TOKEN" not in steps[wait].get("env",{})
    assert int(workflow()["jobs"]["build"]["timeout-minutes"]) <= 30
