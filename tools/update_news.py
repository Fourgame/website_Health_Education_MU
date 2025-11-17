#!/usr/bin/env python3
"""Interactive helper to add or edit news entries stored in news.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
NEWS_PATH = ROOT / "news.json"


def load_news() -> List[Dict[str, Any]]:
    if not NEWS_PATH.exists():
        print(f"ไม่พบไฟล์ {NEWS_PATH} เมื่อบันทึกจะสร้างไฟล์ใหม่ให้อัตโนมัติ")
        return []
    try:
        with NEWS_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as exc:
        print("อ่าน news.json ไม่ได้ กรุณาตรวจสอบว่าเป็นไฟล์ JSON ที่ถูกต้องก่อน")
        print(exc)
        sys.exit(1)
    if not isinstance(data, list):
        print("รูปแบบ news.json ต้องเป็นลิสต์ของข่าว จะรีเซ็ตเป็นลิสต์ว่าง")
        return []
    return data


def save_news(items: List[Dict[str, Any]]) -> None:
    with NEWS_PATH.open("w", encoding="utf-8") as handle:
        json.dump(items, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    print(f"บันทึกข้อมูลลง {NEWS_PATH} แล้ว")


def list_news(items: List[Dict[str, Any]]) -> None:
    if not items:
        print("ยังไม่มีข่าวในไฟล์ news.json")
        return
    print("\nรายการข่าวปัจจุบัน:")
    for idx, entry in enumerate(items, start=1):
        date = entry.get("date", "-")
        title = entry.get("title", "(ไม่มีชื่อข่าว)")
        print(f" {idx:>2}. {date} | {title}")
    print("")


def prompt_text(label: str, default: str = "", required: bool = False) -> str:
    while True:
        hint = f" [{default}]" if default else ""
        value = input(f"{label}{hint}: ").strip()
        if not value:
            if default:
                return default
            if not required:
                return ""
            print("จำเป็นต้องกรอกค่านี้")
            continue
        return value


def prompt_multiline(label: str, default: str = "", required: bool = False) -> str:
    while True:
        print(f"{label}:")
        if default:
            print("  (กด Enter เปล่าเพื่อใช้ข้อความเดิม หรือพิมพ์ข้อความใหม่แล้วพิมพ์ END เพื่อจบ)")
        else:
            print("  (พิมพ์ข้อความทีละบรรทัด และพิมพ์ END เมื่อจบ)")

        first_line = input("> ").rstrip("\r")
        if not first_line:
            if default:
                return default
            if not required:
                return ""
            print("จำเป็นต้องมีข้อความอย่างน้อยหนึ่งบรรทัด")
            continue

        lines = [first_line]
        while True:
            line = input("> ")
            if line.strip().upper() == "END":
                break
            lines.append(line)
        value = "\n".join(lines).strip()
        if value or not required:
            return value
        print("ข้อความต้องไม่ว่าง")


def normalize_images(entry: Dict[str, Any]) -> List[str]:
    value = entry.get("images")
    if isinstance(value, list):
        items = [str(v).strip() for v in value if str(v).strip()]
        if items:
            return items
    single = str(entry.get("image", "")).strip()
    return [single] if single else []


def normalize_links(entry: Dict[str, Any]) -> List[Dict[str, str]]:
    result: List[Dict[str, str]] = []
    value = entry.get("links")
    if isinstance(value, list):
        for item in value:
            if isinstance(item, dict):
                url = str(item.get("url", "")).strip()
                label = str(item.get("label", "")).strip()
                if url:
                    result.append({"label": label, "url": url})
            elif isinstance(item, str):
                url = item.strip()
                if url:
                    result.append({"label": "", "url": url})
    link = str(entry.get("link", "")).strip()
    if link and not result:
        label = str(entry.get("linkLabel", "")).strip()
        result.append({"label": label, "url": link})
    return result


def show_images(images: List[str]) -> None:
    if not images:
        print("  - ยังไม่มีรูปภาพ")
        return
    for idx, img in enumerate(images, start=1):
        print(f"  {idx}. {img}")


def show_links(links: List[Dict[str, str]]) -> None:
    if not links:
        print("  - ยังไม่มีลิงก์")
        return
    for idx, item in enumerate(links, start=1):
        label = item.get("label") or f"ดูเพิ่มเติม {idx}"
        print(f"  {idx}. {label} -> {item.get('url', '')}")


def prompt_images(current: List[str]) -> List[str]:
    print("\nรายการรูปภาพเดิม:")
    show_images(current)
    answer = input("ต้องการแก้ไขรูปภาพหรือไม่? (y/N): ").strip().lower()
    if answer != "y":
        return current
    print("พิมพ์พาธรูปภาพทีละบรรทัด (เช่น ./assets/images/news-4.jpg). กด Enter เปล่าเพื่อจบ")
    items: List[str] = []
    while True:
        path = input("รูปภาพ: ").strip()
        if not path:
            break
        items.append(path)
    return items


def prompt_links(current: List[Dict[str, str]]) -> List[Dict[str, str]]:
    print("\nรายการลิงก์เพิ่มเติมเดิม:")
    show_links(current)
    answer = input("ต้องการแก้ไขลิงก์หรือไม่? (y/N): ").strip().lower()
    if answer != "y":
        return current
    print("ป้อน URL และชื่อปุ่ม (ไม่บังคับ). กด Enter ที่ช่อง URL เพื่อจบรายการ")
    items: List[Dict[str, str]] = []
    while True:
        url = input("URL: ").strip()
        if not url:
            break
        label = input("ชื่อปุ่ม (เว้นว่างใช้คำว่า 'ดูเพิ่มเติม'): ").strip()
        if not label:
            label = f"ดูเพิ่มเติม {len(items)+1}"
        items.append({"label": label, "url": url})
    return items


def apply_media_fields(entry: Dict[str, Any], images: List[str], links: List[Dict[str, str]]) -> None:
    entry["images"] = images
    entry["image"] = images[0] if images else ""
    entry["links"] = links
    if links:
        entry["link"] = links[0]["url"]
        entry["linkLabel"] = links[0].get("label", "")
    else:
        entry["link"] = ""
        entry["linkLabel"] = ""


def add_entry(items: List[Dict[str, Any]]) -> None:
    print("\n== เพิ่มข่าวใหม่ ==")
    title = prompt_text("หัวข้อข่าว", required=True)
    date = prompt_text("วันที่ (เช่น 17 พ.ย. 2567)", required=True)
    tag = prompt_text("ป้ายกำกับ", "ข่าว/ประกาศ")
    author = prompt_text("ผู้เขียน/ผู้เผยแพร่")
    summary = prompt_text("สรุปสั้น ๆ 1 ย่อหน้า")
    body = prompt_multiline("เนื้อหาฉบับเต็ม (พิมพ์ END เมื่อจบ)", required=True)
    images = prompt_images([])
    links = prompt_links([])

    entry: Dict[str, Any] = {
        "title": title,
        "date": date,
        "tag": tag,
        "by": author,
        "summary": summary,
        "body": body,
    }
    apply_media_fields(entry, images, links)
    items.insert(0, entry)
    save_news(items)


def select_entry(items: List[Dict[str, Any]]) -> int:
    if not items:
        print("ไม่มีข่าวให้แก้ไข")
        return -1
    list_news(items)
    while True:
        choice = input("เลือกหมายเลขข่าวที่ต้องการแก้ไข (หรือ Enter เพื่อยกเลิก): ").strip()
        if not choice:
            return -1
        if not choice.isdigit():
            print("กรุณาใส่ตัวเลข")
            continue
        idx = int(choice)
        if 1 <= idx <= len(items):
            return idx - 1
        print("หมายเลขไม่ถูกต้อง")


def edit_entry(items: List[Dict[str, Any]]) -> None:
    print("\n== แก้ไขข่าวที่มีอยู่ ==")
    idx = select_entry(items)
    if idx < 0:
        return
    entry = items[idx]
    entry["title"] = prompt_text("หัวข้อข่าว", entry.get("title", ""), required=True)
    entry["date"] = prompt_text("วันที่", entry.get("date", ""), required=True)
    entry["tag"] = prompt_text("ป้ายกำกับ", entry.get("tag", "ข่าว/ประกาศ"))
    entry["by"] = prompt_text("ผู้เขียน/ผู้เผยแพร่", entry.get("by", ""))
    entry["summary"] = prompt_text("สรุปสั้น ๆ", entry.get("summary", ""))
    entry["body"] = prompt_multiline("เนื้อหาฉบับเต็ม (พิมพ์ END เมื่อจบ)", entry.get("body", ""), required=True)
    images = prompt_images(normalize_images(entry))
    links = prompt_links(normalize_links(entry))
    apply_media_fields(entry, images, links)
    save_news(items)


def main() -> None:
    items = load_news()
    while True:
        print("\n====== เมนูจัดการข่าว ======")
        print("1. แสดงรายการข่าว")
        print("2. เพิ่มข่าวใหม่")
        print("3. แก้ไขข่าวที่มีอยู่")
        print("4. ออกจากโปรแกรม")
        choice = input("เลือกหมายเลขเมนู: ").strip()
        if choice == "1":
            list_news(items)
        elif choice == "2":
            add_entry(items)
        elif choice == "3":
            edit_entry(items)
        elif choice == "4":
            print("จบการทำงาน")
            break
        else:
            print("กรุณาเลือกเมนู 1-4")


if __name__ == "__main__":
    main()
