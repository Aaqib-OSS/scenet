"""Build and deep check report the same diagnostic notes for generated panels."""

from pathlib import Path

import pytest
from hypothesis import given

from scenet import compile_source
from scenet.cli import main
from tests.properties.test_panel_properties import EXPECTED_FAILURES
from tests.strategies import LIBRARY, Drawn, panels


@given(panels(images=False))
def test_build_and_deep_check_report_the_same_notes(
    drawn: Drawn, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The build diagnostic notes are exactly the checker notes, across generated panels."""
    try:
        compile_source(drawn.text, library=LIBRARY)
    except EXPECTED_FAILURES:
        return

    source = tmp_path / "generated.panel.yaml"
    source.write_text(drawn.text, encoding="utf-8")

    assert main(["build", str(source)]) == 0
    built = capsys.readouterr()
    assert main(["check", "--deep", str(source)]) == 0
    checked = capsys.readouterr()

    build_notes = [line for line in built.err.splitlines() if ": note: " in line]
    check_notes = [line for line in checked.err.splitlines() if ": note: " in line]
    assert build_notes == check_notes
