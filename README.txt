New Web Page (self-contained)

Drop your assets into:
- assets/favicon.png
- assets/images/hero.jpg
- assets/images/program-bsc.jpg
- assets/images/program-msc.jpg
- assets/images/program-drph.jpg
- assets/images/news-1.jpg
- assets/images/news-2.jpg
- assets/images/news-3.jpg
- assets/images/about-1.jpg
- assets/images/about-2.jpg
- assets/images/about-3.jpg
- assets/images/about-4.jpg
- assets/images/logo-ash.png
- assets/images/logo-hed.png
- assets/images/logo-hepa.png
- assets/images/logo-trc.png
- assets/images/logo-thaihealth.png
- assets/images/logo-path2health.png

You can safely edit titles, descriptions, and links directly in index.html.
All images currently point to local files; if a file is missing, the browser will show a broken image icon which you can fix by adding the file above.

Pages included (new design):
- index.html (home, sections + partners)
- program.html (programs overview)
- news.html (news/announcements list)
- staff.html (people directory)
- about.html (why us + image grid)
- contact.html (contact info + form)
- history.html (background/overview)
- vision.html (vision/mission)
- research.html (research projects)
- Services.html (services overview)
- alumni.html (alumni network)
- student.html (student resources)

Navigation links connect among these pages inside New_Web_page only, keeping the site self-contained.

Updating news without touching HTML:
1. ติดตั้ง Python 3 และเปิดเทอร์มินัลในโฟลเดอร์โปรเจ็กต์นี้
2. รันคำสั่ง `python tools/update_news.py`
3. เลือกเมนูตามต้องการ (ดูรายการข่าว, เพิ่มข่าวใหม่, แก้ข่าวเดิม)
4. เมื่อเพิ่ม/แก้เสร็จ หน้า news.html จะอ่านข้อมูลล่าสุดจาก `news.json` โดยอัตโนมัติเมื่อเปิดผ่านเว็บเซิร์ฟเวอร์

ต้องการอินเตอร์เฟซแบบหน้าต่าง? ใช้คำสั่ง `python tools/news_editor_gui.py` เพื่อเปิดตัวแก้ข่าวด้วย Tkinter GUI (มีรายการข่าวด้านซ้ายและแบบฟอร์มให้กรอกด้านขวา)

Fields ที่รองรับใน `news.json`:
- `images`: ใส่เป็นอาร์เรย์ของพาธรูปภาพ (เช่น `["./assets/images/news-4.jpg","./assets/images/news-4b.jpg"]`) โมดัลจะแสดงทุกภาพแบบเลื่อนลง
- `links`: ใส่เป็นอาร์เรย์ของออบเจ็กต์ `{ "label": "เอกสารเพิ่มเติม", "url": "https://..." }` หรือใส่เป็นสตริงลิงก์เฉย ๆ ก็ได้ ระบบจะสร้างปุ่ม “ดูเพิ่มเติม” ให้
