"""Tests for CSV validation and the generated report."""

from pathlib import Path

import pytest

import build_site


def write_csv(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "scores.csv"
    path.write_text(content, encoding="utf-8")
    return path


def test_load_scores_reads_thai_names_and_numbers(tmp_path: Path) -> None:
    path = write_csv(tmp_path, "name,score\n มานี ,85\nชูใจ,70\n")
    assert build_site.load_scores(path) == [("มานี", 85), ("ชูใจ", 70)]


@pytest.mark.parametrize(
    "content",
    ["student,score\nมานี,85\n", "name,score\n", "name,score\n,85\n", "name,score\nมานี,abc\n", "name,score\nมานี,101\n"],
)
def test_load_scores_rejects_invalid_data(tmp_path: Path, content: str) -> None:
    with pytest.raises(ValueError):
        build_site.load_scores(write_csv(tmp_path, content))


def test_render_page_escapes_csv_names_and_title() -> None:
    html = build_site.render_page([("<script>alert(1)</script>", 85)], "<Report>")
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "&lt;Report&gt;" in html
    assert "<script>" not in html
    assert "<Report>" not in html


def test_render_page_reports_statistics_and_grades() -> None:
    html = build_site.render_page([("มานี", 84), ("ชูใจ", 40)], "คะแนนตัวอย่าง")
    assert "62.00" in html
    assert "grade-a" in html
    assert "grade-f" in html
    assert "คะแนนตั้งแต่ 50 ขึ้นไป" in html
    assert "ข้อมูลตัวอย่าง" in html


def test_main_writes_deployable_site(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    csv_path = write_csv(tmp_path, "name,score\nมานี,90\n")
    css_path = tmp_path / "source.css"
    css_path.write_text("body { color: green; }", encoding="utf-8")
    output_dir = tmp_path / "published"
    monkeypatch.setattr(build_site, "DATA_FILE", csv_path)
    monkeypatch.setattr(build_site, "STYLE_FILE", css_path)
    monkeypatch.setattr(build_site, "OUTPUT_DIR", output_dir)
    monkeypatch.setenv("SITE_TITLE", "ผลคะแนนของเรา")

    build_site.main()

    html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "ผลคะแนนของเรา" in html
    assert "มานี" in html
    assert "style.css" in html
    assert (output_dir / "style.css").read_text(encoding="utf-8") == "body { color: green; }"


def test_main_uses_default_title_when_environment_is_blank(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(build_site, "DATA_FILE", write_csv(tmp_path, "name,score\nมานี,80\n"))
    monkeypatch.setattr(build_site, "STYLE_FILE", build_site.STYLE_FILE)
    monkeypatch.setattr(build_site, "OUTPUT_DIR", tmp_path / "published")
    monkeypatch.setenv("SITE_TITLE", " ")
    build_site.main()
    assert "รายงานผลคะแนน" in (tmp_path / "published" / "index.html").read_text(encoding="utf-8")
