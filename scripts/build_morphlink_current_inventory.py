"""
Xuất danh sách TỔNG (toàn bộ dữ liệu MorphLink ĐÃ CÓ hiện tại, không phải
phần "mới/thiếu" như các file audit_*.csv) theo 4 loại: root, prefix,
suffix, word.

Nguồn:
  - data/ROOTS_MEANING_AND_VARIANTS.csv -> root (2148 root gốc, có ảnh minh họa)
  - affix_table.csv (loc theo loai) -> prefix (89) / suffix (106), đúng bộ
    ảnh hiện có trong prefixes/images/ và suffixes/images/
  - data/ROOT_derivatives_FULL.csv + data/COMPOUND_ROOT_derivatives_FULL.csv
    -> word: toàn bộ từ phái sinh/ghép mà MorphLink hiện có thể minh họa
    được từ các root/prefix/suffix đã có (gộp, loại trùng theo derived_word)
"""
import csv, os
from collections import OrderedDict

ROOT = os.path.join(os.path.dirname(__file__), "..")
DATA = os.path.join(ROOT, "data")

# ---------- root ----------
with open(os.path.join(DATA, "ROOTS_MEANING_AND_VARIANTS.csv"), encoding="utf-8") as f:
    root_rows = list(csv.DictReader(f))
with open(os.path.join(ROOT, "morphlink_root_full.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["root_word", "meaning_en", "meaning_vi"])
    for r in root_rows:
        w.writerow([r["root_word"], r["meaning"], r["nghia_tieng_viet"]])
print("morphlink_root_full.csv:", len(root_rows))

# ---------- prefix / suffix ----------
with open(os.path.join(ROOT, "affix_table.csv"), encoding="utf-8") as f:
    affix_rows = list(csv.DictReader(f))
for loai, fname in (("prefix", "morphlink_prefix_full.csv"), ("suffix", "morphlink_suffix_full.csv")):
    rows = [r for r in affix_rows if r["loai"] == loai]
    with open(os.path.join(ROOT, fname), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["affix", "meaning_en", "meaning_vi", "so_tu_dung", "vi_du"])
        for r in rows:
            w.writerow([r["dang_hien_thi"], r["nghia_en"], r["nghia_vi"], r["so_tu_dung"], r["vi_du"]])
    print(f"{fname}:", len(rows))

# ---------- word ----------
seen = OrderedDict()
for fn in ("ROOT_derivatives_FULL.csv", "COMPOUND_ROOT_derivatives_FULL.csv"):
    with open(os.path.join(DATA, fn), encoding="utf-8") as f:
        for r in csv.DictReader(f):
            w = r["derived_word"]
            if w not in seen:
                seen[w] = r

with open(os.path.join(ROOT, "morphlink_word_full.csv"), "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["word", "pos", "structure", "meaning_en", "meaning_vi"])
    for word, r in seen.items():
        w.writerow([word, r["pos"], r["morphology_structure"], r["definition_en"], r["nghia_tieng_viet"]])
print("morphlink_word_full.csv:", len(seen))
