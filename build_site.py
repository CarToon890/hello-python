"""Build a static, escaped HTML report from sample scores in CSV."""

import csv
import hashlib
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


def render_page(rows: list[tuple[str, int]], title: str, style_version: str = "") -> str:
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
    stylesheet = "style.css" if not style_version else f"style.css?v={escape(style_version, quote=True)}"
    return f"""<!doctype html>
<html lang="th">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="รายงานคะแนนตัวอย่างที่สร้างด้วย Python ตรวจด้วย pytest และเผยแพร่ผ่าน GitHub Actions">
  <meta name="theme-color" content="#fff9ef">
  <title>{safe_title} | Scoreboard Lab</title>
  <link rel="stylesheet" href="{stylesheet}">
</head>
<body>
  <a class="skip-link" href="#main-content">ข้ามไปยังเนื้อหา</a>
  <header class="site-header"><div class="container header-inner">
    <a class="brand" href="#top" aria-label="กลับไปส่วนบนของหน้า"><span class="brand-mark" aria-hidden="true">S<span>✳</span></span><span>SURACHAT <em>/ SCORE LAB</em></span></a>
    <nav aria-label="เมนูหลัก"><a href="#how-it-works">วิธีทำงาน</a><a href="#grading">เกณฑ์เกรด</a><a href="#results">ผลคะแนน</a></nav>
    <a class="header-link" href="https://cartoon890.github.io/Lab-WebDev-Actions/">เว็บแนะนำตัว <span aria-hidden="true">↗</span></a>
  </div></header>
  <main id="main-content">
    <section class="hero" id="top" aria-labelledby="page-title"><div class="container hero-grid">
      <div class="hero-copy"><p class="eyebrow"><span class="eyebrow-dot" aria-hidden="true"></span> PYTHON · CI/CD · GITHUB PAGES</p>
        <h1 id="page-title">{safe_title}<span class="hero-accent">ที่อ่านสนุกขึ้น<span aria-hidden="true">✳</span></span></h1>
        <p class="hero-lead">ไฟล์ CSV หนึ่งไฟล์ กลายเป็นหน้ารายงานที่ดูง่าย พร้อมการตรวจโค้ดและเผยแพร่อัตโนมัติผ่าน GitHub Actions</p>
        <div class="hero-actions"><a class="button button-primary" href="#results">ดูตารางคะแนน <span aria-hidden="true">↘</span></a><a class="button button-outline" href="https://github.com/CarToon890/hello-python" target="_blank" rel="noopener noreferrer">ดูโค้ดบน GitHub ↗</a></div>
        <p class="author">สร้างโดย สุรชัช ศาลาน้อย <span>·</span> 67160378</p>
      </div>
      <div class="hero-art" aria-hidden="true"><div class="art-sun"></div><div class="art-dots"></div><div class="report-card"><div class="report-top"><span><i></i><i></i><i></i></span><small>scores.csv → index.html</small><b>↗</b></div><div class="report-body"><span class="art-label">SAMPLE SCORE / LIVE REPORT</span><strong>{mean:.2f}<small>AVG / 100</small></strong><div class="art-bars"><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div><span class="art-bottom">{len(rows):02d} RECORDS <b>✳</b> 01 WORKFLOW</span></div></div><div class="art-sticker">TESTED<br />&amp; SHIPPED!</div></div>
    </div></section>

    <section class="stats-section" aria-label="สรุปคะแนน"><div class="container stats-grid">
      <article class="stat-card stat-yellow"><span class="stat-icon" aria-hidden="true">✳</span><p>ผู้เรียนในตัวอย่าง</p><strong>{len(rows)}<small>คน</small></strong><span>ข้อมูลจากไฟล์ CSV</span></article>
      <article class="stat-card stat-coral"><span class="stat-icon" aria-hidden="true">↗</span><p>คะแนนเฉลี่ย</p><strong>{mean:.2f}<small>/ 100</small></strong><span>คำนวณโดย Python</span></article>
      <article class="stat-card stat-mint"><span class="stat-icon" aria-hidden="true">★</span><p>คะแนนสูงสุด</p><strong>{highest}<small>/ 100</small></strong><span>จากข้อมูลตัวอย่าง</span></article>
      <article class="stat-card stat-purple"><span class="stat-icon" aria-hidden="true">✓</span><p>ผ่านเกณฑ์</p><strong>{passed}<small>คน</small></strong><span>คะแนนตั้งแต่ 50 ขึ้นไป</span></article>
    </div></section>

    <section class="section process-section" id="how-it-works" aria-labelledby="process-title"><div class="container"><div class="section-intro"><div><p class="section-kicker">01 / HOW IT WORKS</p><h2 id="process-title">จากข้อมูลดิบ<br /><span>สู่หน้าเว็บจริง</span></h2></div><p>ทุกครั้งที่ push โค้ด ระบบจะตรวจสอบก่อนสร้างและเผยแพร่รายงานเวอร์ชันใหม่</p></div><div class="process-grid"><article><span class="process-number">01</span><div class="process-symbol" aria-hidden="true">▤</div><h3>อ่านข้อมูล</h3><p>Python อ่านชื่อและคะแนนตัวอย่างจากไฟล์ CSV แล้วตรวจความถูกต้อง</p></article><article><span class="process-number">02</span><div class="process-symbol" aria-hidden="true">✓</div><h3>ตรวจโค้ด</h3><p>Ruff และ pytest ตรวจโค้ด พร้อมวัด coverage ก่อนเข้าสู่ขั้นเผยแพร่</p></article><article><span class="process-number">03</span><div class="process-symbol" aria-hidden="true">↗</div><h3>เผยแพร่</h3><p>เมื่อ job ทดสอบผ่าน GitHub Actions จึงสร้างเว็บและส่งขึ้น GitHub Pages</p></article></div></div></section>

    <section class="section grading-section" id="grading" aria-labelledby="grading-title"><div class="container grading-grid"><div><p class="section-kicker">02 / GRADE GUIDE</p><h2 id="grading-title">เกณฑ์เกรด<br /><span>อ่านได้ในแวบเดียว</span></h2><p>คะแนนเต็ม 100 ใช้เกณฑ์เดียวกับฟังก์ชัน <code>grade()</code> ในโปรเจกต์</p></div><div class="grade-list"><div><span class="grade grade-a">A</span><strong>80–100</strong><span>ดีเยี่ยม</span></div><div><span class="grade grade-b">B</span><strong>70–79</strong><span>ดี</span></div><div><span class="grade grade-c">C</span><strong>60–69</strong><span>ปานกลาง</span></div><div><span class="grade grade-d">D</span><strong>50–59</strong><span>ผ่านเกณฑ์</span></div><div><span class="grade grade-f">F</span><strong>0–49</strong><span>ต่ำกว่าเกณฑ์</span></div></div></div></section>

    <section class="section results-section" id="results" aria-labelledby="report-heading"><div class="container"><div class="section-intro results-intro"><div><p class="section-kicker">03 / THE RESULTS</p><h2 id="report-heading">ตารางผลคะแนน<span>ตัวอย่าง</span></h2></div><span class="record-count">{len(rows):02d} RECORDS / FROM CSV</span></div><div class="table-wrap"><table><caption class="visually-hidden">ชื่อ คะแนน และเกรดจากข้อมูลตัวอย่าง</caption><thead><tr><th scope="col">ลำดับ</th><th scope="col">ชื่อ</th><th scope="col">คะแนน</th><th scope="col">เกรด</th></tr></thead><tbody>{body_rows}</tbody></table></div><p class="sample-note"><span aria-hidden="true">✳</span> ข้อมูลคะแนนในหน้านี้เป็นข้อมูลตัวอย่างสำหรับการเรียนรู้เท่านั้น</p></div></section>
  </main>
  <footer class="site-footer"><div class="container footer-inner"><span>© SURACHAT · 67160378</span><a href="https://cartoon890.github.io/Lab-WebDev-Actions/">กลับไปยังเว็บแนะนำตัว ↗</a><a href="https://github.com/CarToon890/hello-python">SOURCE ON GITHUB ↗</a></div></footer>
</body>
</html>
"""


def main() -> None:
    """Write the report and its stylesheet to the Pages artifact directory."""
    rows = load_scores(DATA_FILE)
    title = os.environ.get("SITE_TITLE", "รายงานผลคะแนน").strip() or "รายงานผลคะแนน"
    style_version = hashlib.sha256(STYLE_FILE.read_bytes()).hexdigest()[:8]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "index.html").write_text(render_page(rows, title, style_version), encoding="utf-8")
    shutil.copyfile(STYLE_FILE, OUTPUT_DIR / "style.css")


if __name__ == "__main__":
    main()
