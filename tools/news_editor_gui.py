#!/usr/bin/env python3
"""Simple Tkinter GUI to manage news entries in news.json."""

from __future__ import annotations

import json
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
NEWS_PATH = ROOT / "news.json"


def load_news_file() -> List[Dict[str, Any]]:
    if not NEWS_PATH.exists():
        return []
    try:
        with NEWS_PATH.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
            if isinstance(data, list):
                return data
    except json.JSONDecodeError as exc:
        messagebox.showerror("อ่านไฟล์ไม่ได้", f"news.json ไม่ใช่ JSON ที่ถูกต้อง:\n{exc}")
    return []


def save_news_file(items: List[Dict[str, Any]]) -> None:
    with NEWS_PATH.open("w", encoding="utf-8") as handle:
        json.dump(items, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def normalize_images(entry: Dict[str, Any]) -> List[str]:
    value = entry.get("images")
    if isinstance(value, list):
        cleaned = [str(v).strip() for v in value if str(v).strip()]
        if cleaned:
            return cleaned
    image = str(entry.get("image", "")).strip()
    return [image] if image else []


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


class NewsEditor(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("News Editor (news.json)")
        self.geometry("1100x700")
        self.news: List[Dict[str, Any]] = []
        self.current_index: int | None = None
        self._build_ui()
        self._load_news()

    def _build_ui(self) -> None:
        main = ttk.Frame(self, padding=12)
        main.pack(fill="both", expand=True)

        # Left list
        left = ttk.Frame(main)
        left.pack(side="left", fill="y")
        ttk.Label(left, text="รายการข่าว").pack(anchor="w")

        list_frame = ttk.Frame(left)
        list_frame.pack(fill="y", expand=True)
        self.listbox = tk.Listbox(list_frame, width=38, height=34)
        self.listbox.pack(side="left", fill="y", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.listbox.configure(yscrollcommand=scrollbar.set)
        self.listbox.bind("<<ListboxSelect>>", self._on_select)

        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill="x", pady=10)
        ttk.Button(btn_frame, text="ข่าวใหม่", command=self._new_entry).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btn_frame, text="ลบข่าว", command=self._delete_entry).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btn_frame, text="รีเฟรช", command=self._load_news).pack(side="left", fill="x", expand=True, padx=2)

        # Right form
        right = ttk.Frame(main, padding=(12, 0))
        right.pack(side="left", fill="both", expand=True)
        right.columnconfigure(0, weight=1)

        form = ttk.Frame(right)
        form.grid(row=0, column=0, sticky="nsew")
        form.columnconfigure(1, weight=1)

        self.var_title = tk.StringVar()
        self.var_date = tk.StringVar()
        self.var_tag = tk.StringVar(value="ข่าว/ประกาศ")
        self.var_by = tk.StringVar()

        self._add_entry_field(form, "หัวข้อข่าว*", self.var_title, 0)
        self._add_entry_field(form, "วันที่*", self.var_date, 1)
        self._add_entry_field(form, "ป้ายกำกับ", self.var_tag, 2)
        self._add_entry_field(form, "ชื่อผู้เผยแพร่", self.var_by, 3)

        ttk.Label(form, text="รูปภาพ (พิมพ์ 1 พาธต่อบรรทัด)").grid(row=4, column=0, sticky="nw", pady=4)
        images_frame = ttk.Frame(form)
        images_frame.grid(row=4, column=1, sticky="ew", pady=4)
        images_frame.columnconfigure(0, weight=1)
        self.images_text = tk.Text(images_frame, height=4, width=70)
        self.images_text.grid(row=0, column=0, sticky="ew")
        ttk.Button(images_frame, text="เพิ่มจากไฟล์...", command=self._add_image_from_dialog).grid(row=0, column=1, padx=6)

        ttk.Label(form, text="สรุป (ข้อความสั้น)").grid(row=5, column=0, sticky="nw", pady=4)
        self.summary_text = tk.Text(form, height=4, width=70)
        self.summary_text.grid(row=5, column=1, sticky="ew", pady=4)

        ttk.Label(form, text="เนื้อหาหลัก*").grid(row=6, column=0, sticky="nw", pady=4)
        self.body_text = tk.Text(form, height=12, width=70)
        self.body_text.grid(row=6, column=1, sticky="nsew", pady=4)

        ttk.Label(form, text="ลิงก์เพิ่มเติม (รูปแบบ ป้าย|URL ต่อบรรทัด)").grid(row=7, column=0, sticky="nw", pady=4)
        links_frame = ttk.Frame(form)
        links_frame.grid(row=7, column=1, sticky="ew", pady=4)
        links_frame.columnconfigure(0, weight=1)
        self.links_text = tk.Text(links_frame, height=4, width=70)
        self.links_text.grid(row=0, column=0, sticky="ew")
        ttk.Button(links_frame, text="เพิ่มลิงก์...", command=self._add_link_via_dialog).grid(row=0, column=1, padx=6)

        action_frame = ttk.Frame(right)
        action_frame.grid(row=1, column=0, pady=10, sticky="ew")
        ttk.Button(action_frame, text="บันทึก", command=self._save_entry).pack(side="left", expand=True, fill="x", padx=4)
        ttk.Button(action_frame, text="ปิด", command=self.destroy).pack(side="left", expand=True, fill="x", padx=4)

    def _add_entry_field(self, parent: ttk.Frame, label: str, variable: tk.StringVar, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=4)
        entry = ttk.Entry(parent, textvariable=variable)
        entry.grid(row=row, column=1, sticky="ew", pady=4)

    def _load_news(self) -> None:
        self.news = load_news_file()
        self._refresh_list()
        if not self.news:
            self._new_entry()

    def _refresh_list(self) -> None:
        self.listbox.delete(0, tk.END)
        for idx, entry in enumerate(self.news):
            title = entry.get("title", "(ไม่มีชื่อข่าว)")
            date = entry.get("date", "-")
            self.listbox.insert(tk.END, f"{idx + 1:02d}. {date} | {title[:60]}")

    def _on_select(self, event: tk.Event[tk.Listbox]) -> None:
        selection = event.widget.curselection()
        if not selection:
            return
        index = selection[0]
        self.current_index = index
        self._populate_form(self.news[index])

    def _populate_form(self, entry: Dict[str, Any]) -> None:
        self.var_title.set(entry.get("title", ""))
        self.var_date.set(entry.get("date", ""))
        self.var_tag.set(entry.get("tag", "ข่าว/ประกาศ"))
        self.var_by.set(entry.get("by", ""))
        self.summary_text.delete("1.0", tk.END)
        self.summary_text.insert(tk.END, entry.get("summary", ""))
        self.body_text.delete("1.0", tk.END)
        self.body_text.insert(tk.END, entry.get("body", ""))
        self._set_images_text(normalize_images(entry))
        self._set_links_text(normalize_links(entry))

    def _set_images_text(self, items: List[str]) -> None:
        self.images_text.delete("1.0", tk.END)
        if items:
            self.images_text.insert(tk.END, "\n".join(items))

    def _set_links_text(self, items: List[Dict[str, str]]) -> None:
        self.links_text.delete("1.0", tk.END)
        lines = []
        for item in items:
            label = (item.get("label") or "").strip()
            url = (item.get("url") or "").strip()
            if not url:
                continue
            lines.append(f"{label}|{url}" if label else url)
        if lines:
            self.links_text.insert(tk.END, "\n".join(lines))

    def _get_images_from_text(self) -> List[str]:
        lines = self.images_text.get("1.0", tk.END).splitlines()
        return [line.strip() for line in lines if line.strip()]

    def _get_links_from_text(self) -> List[Dict[str, str]]:
        lines = self.links_text.get("1.0", tk.END).splitlines()
        results: List[Dict[str, str]] = []
        for idx, line in enumerate(lines, start=1):
            if not line.strip():
                continue
            if "|" in line:
                label, url = line.split("|", 1)
                label = label.strip()
                url = url.strip()
            else:
                label, url = "", line.strip()
            if not url:
                continue
            if not label:
                label = f"ดูเพิ่มเติม {len(results)+1}"
            results.append({"label": label, "url": url})
        return results

    def _new_entry(self) -> None:
        self.current_index = None
        self.var_title.set("")
        self.var_date.set("")
        self.var_tag.set("ข่าว/ประกาศ")
        self.var_by.set("")
        self.summary_text.delete("1.0", tk.END)
        self.body_text.delete("1.0", tk.END)
        self._set_images_text([])
        self._set_links_text([])
        self.listbox.selection_clear(0, tk.END)

    def _add_image_from_dialog(self) -> None:
        paths = filedialog.askopenfilenames(
            title="เลือกไฟล์รูปภาพ",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.webp"), ("All files", "*.*")],
            initialdir=str((ROOT / "assets" / "images").resolve()),
        )
        if not paths:
            return
        current = self._get_images_from_text()
        for raw in paths:
            path = Path(raw)
            try:
                rel = path.relative_to(ROOT)
                current.append("./" + rel.as_posix())
            except ValueError:
                current.append(path.as_posix())
        self._set_images_text(current)

    def _add_link_via_dialog(self) -> None:
        url = simpledialog.askstring("เพิ่มลิงก์", "URL:", parent=self)
        if not url:
            return
        label = simpledialog.askstring("เพิ่มลิงก์", "ชื่อปุ่ม (ปล่อยว่างให้ใส่อัตโนมัติ):", parent=self) or ""
        current = self.links_text.get("1.0", tk.END).strip()
        line = f"{label}|{url}" if label else url
        if current:
            current += "\n" + line
        else:
            current = line
        self.links_text.delete("1.0", tk.END)
        self.links_text.insert(tk.END, current)

    def _save_entry(self) -> None:
        title = self.var_title.get().strip()
        date = self.var_date.get().strip()
        body = self.body_text.get("1.0", tk.END).strip()
        if not title or not date or not body:
            messagebox.showerror("ข้อมูลไม่ครบ", "กรุณากรอกหัวข้อ วันที่ และเนื้อหาหลักให้ครบ")
            return
        entry: Dict[str, Any] = {
            "title": title,
            "date": self.var_date.get().strip(),
            "tag": self.var_tag.get().strip(),
            "by": self.var_by.get().strip(),
            "summary": self.summary_text.get("1.0", tk.END).strip(),
            "body": body,
        }
        images = self._get_images_from_text()
        links = self._get_links_from_text()
        apply_media_fields(entry, images, links)

        if self.current_index is None:
            self.news.insert(0, entry)
            self.current_index = 0
        else:
            self.news[self.current_index] = entry
        save_news_file(self.news)
        self._refresh_list()
        self.listbox.selection_clear(0, tk.END)
        if self.current_index is not None:
            self.listbox.selection_set(self.current_index)
        messagebox.showinfo("บันทึกแล้ว", "บันทึกข้อมูลข่าวเรียบร้อย")

    def _delete_entry(self) -> None:
        if self.current_index is None:
            messagebox.showwarning("ยังไม่ได้เลือก", "กรุณาเลือกรายการจากด้านซ้ายก่อน")
            return
        confirm = messagebox.askyesno("ยืนยันการลบ", "ต้องการลบข่าวนี้หรือไม่?")
        if not confirm:
            return
        del self.news[self.current_index]
        save_news_file(self.news)
        self.current_index = None
        self._refresh_list()
        self._new_entry()


def main() -> None:
    app = NewsEditor()
    app.mainloop()


if __name__ == "__main__":
    main()
