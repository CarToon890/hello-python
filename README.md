# Hello Python — Scoreboard

โปรเจกต์ Python CI/CD ของ **สุรชัช ศาลาน้อย (67160378)** ตามใบงาน GitHub Actions ภาค 2

เว็บไซต์: https://cartoon890.github.io/hello-python/  
GitHub Actions: https://github.com/CarToon890/hello-python/actions

ข้อมูลใน `data/scores.csv` เป็น **ข้อมูลตัวอย่าง** สำหรับสาธิตการคำนวณเกรด ไม่ใช่คะแนนจริงของนิสิต

## ทำงานอย่างไร

1. `grades.py` แปลงคะแนน 0–100 เป็นเกรด A–F และหาค่าเฉลี่ย
2. `build_site.py` อ่านและตรวจสอบ CSV แล้วสร้าง `_site/index.html` พร้อม CSS โดย escape ข้อความก่อนแสดงใน HTML
3. GitHub Actions ตรวจโค้ดด้วย Ruff และรัน pytest พร้อม coverage ขั้นต่ำ 80%
4. เมื่อ job ทดสอบผ่าน จึงสร้างและ deploy รายงานไป GitHub Pages

## รันในเครื่อง

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements-dev.txt
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m pytest --cov=grades --cov=build_site --cov-report=term-missing --cov-fail-under=80
.venv\Scripts\python build_site.py
```

เปิด `_site/index.html` เพื่อตรวจรายงานที่สร้างขึ้น เมื่อแก้ `data/scores.csv` แล้ว push ขึ้น `main` ระบบจะตรวจและเผยแพร่ข้อมูลใหม่อัตโนมัติ
