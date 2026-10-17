"""Build a static, escaped HTML report from sample scores in CSV."""

import csv
import os
import shutil
from html import escape
from pathlib import Path

from grades import average, grade

ROOT = Path(__file__).resolve().parent
DATA_FILE = ROOT / "data" / "scores.csv"
STYLE_FILE = ROOT / "site.css"
OUTPUT_DIR = ROOT / "_site"


def load_scores(path: Path) -> list[tuple[str, int]]:
    """Load and validate name/score rows from a CSV file."""
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or not {"name", "score"} <= set(reader.fieldnames):
            raise ValueError("CSV must have name and score columns")

        rows = []
        for line_number, row in enumerate(reader, start=2):
            name = (row["name"] or "").strip()
            if not name:
                raise ValueError(f"name is empty on line {line_number}")
            try:
                score = int(row["score"])
            except (TypeError, ValueError) as error:
                raise ValueError(f"invalid score on line {line_number}") from error
            grade(score)
            rows.append((name, score))

    if not rows:
        raise ValueError("CSV must contain at least one score")
    return rows


def render_page(rows: list[tuple[str, int]], title: str) -> str:
    """Create the report as a complete HTML document."""
    mean = average([score for _, score in rows])
    highest = max(score for _, score in rows)
    passed = sum(score >= 50 for _, score in rows)
    body_rows = "\n".join(
        f'<tr><td><span class="row-number">{index:02d}</span></td>'
        f'<td class="student-name">{escape(name)}</td>'
        f'<td class="score">{score}</td>'
        f'<td><span class="grade grade-{grade(score).lower()}">{grade(score)}</span></td></tr>'
        for index, (name, score) in enumerate(rows, start=1)
    )
    safe_title = escape(title)
    return f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="รายงานคะแนนตัวอย่างที่สร้างอัตโนมัติด้วย Python และ GitHub Actions">
  <title>{safe_title} | Scoreboard</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <div class="page-shell">
    <header class="topbar">
      <a class="brand" href="#top" aria-label="Scoreboard หน้าแรก"><span class="brand-mark">S.</span><span>SCOREBOARD</span></a>
      <a class="top-link" href="https://github.com/CarToon890/hello-python">ดูโค้ดบน GitHub <span aria-hidden="true">↗</span></a>
    </header>
    <main id="top">
      <section class="intro" aria-labelledby="page-title">
        <div class="intro-copy">
          <p class="eyebrow"><span class="live-dot"></span> PYTHON · CI/CD · GITHUB PAGES</p>
          <h1 id="page-title">{safe_title}<span class="period">.</span></h1>
          <p class="lead">จากไฟล์ CSV สู่หน้ารายงานที่อัปเดตอัตโนมัติ ทุกครั้งที่โค้ดผ่านการตรวจสอบบน GitHub Actions</p>
          <div class="intro-meta"><span>สุรชัช ศาลาน้อย</span><span class="meta-divider"></span><span>67160378</span></div>
        </div>
        <div class="intro-decoration" aria-hidden="true"><span>01</span><span>DATA / REPORT</span></div>
      </section>

      <section class="stats" aria-label="สรุปคะแนน">
        <article class="stat-card"><p>ผู้เรียนในตัวอย่าง</p><strong>{len(rows)}<small>คน</small></strong><span>ทั้งหมดในไฟล์ข้อมูล</span></article>
        <article class="stat-card"><p>คะแนนเฉลี่ย</p><strong>{mean:.2f}<small>/ 100</small></strong><span>คำนวณโดย Python</span></article>
        <article class="stat-card"><p>คะแนนสูงสุด</p><strong>{highest}<small>/ 100</small></strong><span>คะแนนมากที่สุด</span></article>
        <article class="stat-card"><p>ผ่านเกณฑ์</p><strong>{passed}<small>คน</small></strong><span>คะแนนตั้งแต่ 50 ขึ้นไป</span></article>
      </section>

      <section class="report" aria-labelledby="report-heading">
        <div class="section-head"><div><p class="section-kicker">THE RESULTS</p><h2 id="report-heading">ตารางผลคะแนน</h2></div><span class="record-count">{len(rows):02d} RECORDS</span></div>
        <div class="table-wrap"><table><thead><tr><th scope="col">ลำดับ</th><th scope="col">ชื่อ</th><th scope="col">คะแนน</th><th scope="col">เกรด</th></tr></thead><tbody>{body_rows}</tbody></table></div>
        <p class="sample-note">ข้อมูลคะแนนในหน้านี้เป็นข้อมูลตัวอย่างสำหรับการเรียนรู้เท่านั้น</p>
      </section>
    </main>
    <footer><span>BUILT WITH PYTHON + GITHUB ACTIONS</span><a href="https://cartoon890.github.io/Lab-WebDev-Actions/">กลับไปยังเว็บแนะนำตัว <span aria-hidden="true">↗</span></a></footer>
  </div>
</body>
</html>
"""


def main() -> None:
    """Write the report and its stylesheet to the Pages artifact directory."""
    rows = load_scores(DATA_FILE)
    title = os.environ.get("SITE_TITLE", "รายงานผลคะแนน").strip() or "รายงานผลคะแนน"
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "index.html").write_text(render_page(rows, title), encoding="utf-8")
    shutil.copyfile(STYLE_FILE, OUTPUT_DIR / "style.css")


if __name__ == "__main__":
    main()
