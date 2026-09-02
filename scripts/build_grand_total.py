"""
Gom TẤT CẢ (đã có trong MorphLink + mới phát hiện) của 4 loại Root/Word/
Prefix/Suffix thành 1 file duy nhất.

Nguồn "đã có" (morphlink_*_full.csv): toàn bộ 2148 root / 89 prefix /
106 suffix / 11450 word MorphLink hiện có thể minh họa được.
Nguồn "mới" (audit_*.csv, lọc trang_thai == "Mới - chưa có ảnh"): các
thành phần phát hiện thêm từ Reading/Writing còn thiếu, chưa từng có
trong MorphLink.
"""
import csv, os

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "morphlink_grand_total.csv")

rows_out = []

def add(loai, thanh_phan, trang_thai, meaning_en, meaning_vi, ghi_chu):
    rows_out.append({
        "loai": loai,
        "thanh_phan": thanh_phan,
        "trang_thai": trang_thai,
        "meaning_en": meaning_en,
        "meaning_vi": meaning_vi,
        "ghi_chu": ghi_chu,
    })

# ---------- ROOT ----------
with open(os.path.join(ROOT, "morphlink_root_full.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        add("Root", r["root_word"], "Đã có trong MorphLink", r["meaning_en"], r["meaning_vi"], "")
with open(os.path.join(ROOT, "audit_root.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["trang_thai"] == "Mới - chưa có ảnh":
            add("Root", r["thanh_phan"], "Mới - chưa có ảnh", r["meaning_en"], r["meaning_vi"], r["vi_du_tu"])

# ---------- WORD ----------
# Một từ được tính "Đã có" nếu MorphLink ghép được từ root+affix sẵn có
# (có mặt trong morphlink_word_full.csv) — ưu tiên hơn cách audit_word.csv
# đánh giá (chỉ dựa vào ảnh RIÊNG của chính từ đó), vì bản thân các từ ghép
# vốn không cần ảnh riêng, chỉ cần ảnh của root/affix cấu thành.
already_covered_words = set()
with open(os.path.join(ROOT, "morphlink_word_full.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        ghi_chu = f"pos={r['pos']}; structure={r['structure']}" if r["pos"] or r["structure"] else ""
        add("Word", r["word"], "Đã có trong MorphLink", r["meaning_en"], r["meaning_vi"], ghi_chu)
        already_covered_words.add(r["word"])
with open(os.path.join(ROOT, "audit_word.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        if r["trang_thai"] == "Mới - chưa có ảnh" and r["thanh_phan"] not in already_covered_words:
            add("Word", r["thanh_phan"], "Mới - chưa có ảnh", r["meaning_en"], r["meaning_vi"], r["vi_du_tu"])

# ---------- PREFIX / SUFFIX ----------
for loai, full_fn, audit_fn in (
    ("Prefix", "morphlink_prefix_full.csv", "audit_prefix.csv"),
    ("Suffix", "morphlink_suffix_full.csv", "audit_suffix.csv"),
):
    with open(os.path.join(ROOT, full_fn), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            ghi_chu = f"so_tu_dung={r['so_tu_dung']}; vi_du={r['vi_du']}"
            add(loai, r["affix"], "Đã có trong MorphLink", r["meaning_en"], r["meaning_vi"], ghi_chu)
    with open(os.path.join(ROOT, audit_fn), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["trang_thai"] == "Mới - chưa có ảnh":
                add(loai, r["thanh_phan"], "Mới - chưa có ảnh", r["meaning_en"], r["meaning_vi"], r["vi_du_tu"])

LOAI_ORDER = {"Root": 0, "Word": 1, "Prefix": 2, "Suffix": 3}
rows_out.sort(key=lambda r: (LOAI_ORDER[r["loai"]], r["trang_thai"] != "Đã có trong MorphLink", r["thanh_phan"]))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["loai", "thanh_phan", "trang_thai", "meaning_en", "meaning_vi", "ghi_chu"])
    w.writeheader()
    w.writerows(rows_out)

print("total rows:", len(rows_out))
import collections
cnt = collections.Counter((r["loai"], r["trang_thai"]) for r in rows_out)
for k in sorted(cnt):
    print(k, cnt[k])

# kiem tra trung thanh_phan trong cung 1 loai
seen = collections.defaultdict(list)
for r in rows_out:
    seen[(r["loai"], r["thanh_phan"])].append(r["trang_thai"])
dup = {k: v for k, v in seen.items() if len(v) > 1}
print("so cap (loai, thanh_phan) bi trung:", len(dup))
for k, v in list(dup.items())[:10]:
    print(k, v)
