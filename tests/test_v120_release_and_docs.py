from __future__ import annotations

from pathlib import Path

from tscfbench.narrative import write_release_kit



def test_v120_release_kit_includes_positioning_assets(tmp_path: Path) -> None:
    manifest = write_release_kit(tmp_path)
    assert manifest["kind"] == "release_kit"
    assert (tmp_path / "README_GITHUB.md").exists()
    assert (tmp_path / "WEBSITE_HOME.md").exists()
    assert (tmp_path / "WHY_TSCFBENCH.md").exists()
    assert (tmp_path / "AGENT_FIRST_DESIGN.md").exists()



def test_v120_repo_docs_have_key_files() -> None:
    root = Path(__file__).resolve().parents[1]
    assert (root / 'docs' / 'ecosystem-audit.md').exists()
    assert (root / 'docs' / 'feature-coverage.md').exists()
    assert (root / 'docs' / 'why-tscfbench.md').exists()
    assert (root / 'docs' / 'agent-first-design.md').exists()
    assert '# tscfbench (v1.8.0)' in (root / 'README.md').read_text(encoding='utf-8')
    assert (root / 'docs' / 'essential-commands.md').exists()
    assert (root / 'docs' / 'tool-profiles.md').exists()
    assert (root / 'docs' / 'doctor.md').exists()
