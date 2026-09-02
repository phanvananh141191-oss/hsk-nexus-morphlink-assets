"""Tách master_audit_sheet.csv thành 4 file riêng theo loai: Prefix, Suffix, Root, Word."""
import csv, os

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "master_audit_sheet.csv")

FIELDNAMES = ["thanh_phan", "trang_thai", "so_lan_xuat_hien", "meaning_en", "meaning_vi", "vi_du_tu", "nguon"]
FILES = {
    "Root": "audit_root.csv",
    "Word": "audit_word.csv",
    "Prefix": "audit_prefix.csv",
    "Suffix": "audit_suffix.csv",
}

rows_by_loai = {k: [] for k in FILES}
with open(SRC, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        rows_by_loai[row["loai"]].append({k: row[k] for k in FIELDNAMES})

for loai, fname in FILES.items():
    out = os.path.join(ROOT, fname)
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDNAMES)
        w.writeheader()
        w.writerows(rows_by_loai[loai])
    print(fname, len(rows_by_loai[loai]), "dong")
