"""
Tổng hợp TẤT CẢ phát hiện của phiên làm việc (từ thiếu trong Reading/Writing +
tổ hợp mới ghép được) thành MỘT sheet audit duy nhất, phân theo 4 loại thành
phần mà MorphLink dùng để minh họa: Root, Word, Prefix, Suffix.

Nguồn dữ liệu:
  - morphlink_missing_words_analyzed.csv (5638 từ thiếu, đã phân tích cấu trúc)
  - new_combinations.csv (1897 tổ hợp mới ghép từ root/prefix/suffix đã có sẵn)
  - affix_table.csv (nghĩa EN/VI của 89 prefix + 106 suffix hiện có)

Quy ước Root vs Word (giữ nhất quán với build_word_formation_map.py và
discover_new_combinations.py): một thành phần là "Word" nếu tự đứng được
như 1 từ tiếng Anh độc lập (có trong từ điển hệ thống), ngược lại là "Root"
(gốc bị ràng buộc, không đứng một mình được, vd "bio", "techno").

Mỗi thành phần được đánh dấu "Mới - chưa có ảnh" nếu chưa nằm trong bộ ảnh
hiện có của MorphLink (images/, prefixes/images/, suffixes/images/), hoặc
"Đã có trong MorphLink" nếu đã có ảnh minh họa rồi.
"""
import csv, os, re
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "master_audit_sheet.csv")
DICT_PATH = "/usr/share/dict/american-english"

# ---------- dict để phân biệt Root (bound) vs Word (đứng độc lập được) ----------
dict_words = set()
with open(DICT_PATH, encoding="utf-8", errors="ignore") as f:
    for line in f:
        w = line.strip()
        if w and "'" not in w and w == w.lower():
            dict_words.add(w)

def is_word(component):
    return component in dict_words

# ---------- bộ ảnh hiện có của MorphLink ----------
def load_set(sub):
    d = os.path.join(ROOT, sub)
    return {fn[:-5] for fn in os.listdir(d) if fn.endswith(".webp")}

existing_roots = load_set("images")
existing_prefixes = load_set("prefixes/images")
existing_suffixes = load_set("suffixes/images")
print("MorphLink hiện có: roots=%d prefixes=%d suffixes=%d" %
      (len(existing_roots), len(existing_prefixes), len(existing_suffixes)))

# ---------- nghĩa EN/VI cho prefix/suffix đã có sẵn ----------
affix_meaning = {}
with open(os.path.join(ROOT, "affix_table.csv"), encoding="utf-8") as f:
    for row in csv.DictReader(f):
        affix_meaning[(row["loai"], row["affix"])] = (row["nghia_en"], row["nghia_vi"])

# state: (loai, token) -> {"examples": set(), "sources": set(), "meaning": (en,vi) or None}
data = defaultdict(lambda: {"examples": set(), "sources": set(), "meaning": None})

def add(loai, token, example_word, source, meaning=None):
    key = (loai, token)
    d = data[key]
    if len(d["examples"]) < 6:
        d["examples"].add(example_word)
    d["sources"].add(source)
    if meaning and not d["meaning"]:
        if meaning[0] or meaning[1]:
            d["meaning"] = meaning

# ---------- 1) morphlink_missing_words_analyzed.csv ----------
# structure có thể có NHIỀU cặp [root] (từ ghép 2 root, vd "something" =
# "[some]-[thing]") chứ không chỉ 1 — phải tách hết TẤT CẢ các phần trong
# ngoặc vuông làm root/word, phần trước ngoặc đầu tiên là prefix, phần sau
# ngoặc cuối cùng là suffix.
def parse_structure(struct):
    if "[" not in struct or "]" not in struct:
        return None
    bracket_toks = re.findall(r"\[([^\]]+)\]", struct)
    pre_part = struct[:struct.index("[")]
    suf_part = struct[struct.rindex("]") + 1:]
    pre_toks = [t for t in re.split(r"[-+]", pre_part.strip("-+")) if t]
    suf_toks = [t for t in re.split(r"[-+]", suf_part.strip("-+")) if t]
    return pre_toks, bracket_toks, suf_toks

self_entry_meaning = {}  # root_token -> (en, vi), khi root_token chính là 1 từ trong danh sách thiếu
rows_missing = list(csv.DictReader(open(os.path.join(ROOT, "morphlink_missing_words_analyzed.csv"), encoding="utf-8")))
for row in rows_missing:
    parsed = parse_structure(row["structure"])
    if not parsed:
        continue
    pre_toks, bracket_toks, suf_toks = parsed
    if not pre_toks and not suf_toks and len(bracket_toks) == 1 and bracket_toks[0] == row["word"]:
        self_entry_meaning[bracket_toks[0]] = (row["meaning_en"], row["meaning_vi"])

for row in rows_missing:
    parsed = parse_structure(row["structure"])
    if not parsed:
        continue
    pre_toks, bracket_toks, suf_toks = parsed

    for root_tok in bracket_toks:
        loai = "Word" if is_word(root_tok) else "Root"
        meaning = self_entry_meaning.get(root_tok)
        if not meaning and root_tok == row["word"]:
            meaning = (row["meaning_en"], row["meaning_vi"])
        add(loai, root_tok, row["word"], "missing_words_analyzed", meaning)

    for t in pre_toks:
        add("Prefix", t, row["word"], "missing_words_analyzed", affix_meaning.get(("prefix", t)))
    for t in suf_toks:
        add("Suffix", t, row["word"], "missing_words_analyzed", affix_meaning.get(("suffix", t)))

# ---------- 2) new_combinations.csv ----------
rows_combo = list(csv.DictReader(open(os.path.join(ROOT, "new_combinations.csv"), encoding="utf-8")))
for row in rows_combo:
    tu_moi = row["tu_moi_phat_hien"]
    parts = row["cong_thuc"].split("+")
    for p in parts:
        if p.endswith("-"):
            tok = p[:-1]
            add("Prefix", tok, tu_moi, "new_combinations", affix_meaning.get(("prefix", tok)))
        elif p.startswith("-"):
            tok = p[1:]
            add("Suffix", tok, tu_moi, "new_combinations", affix_meaning.get(("suffix", tok)))
        elif p:
            loai = "Word" if is_word(p) else "Root"
            add(loai, p, tu_moi, "new_combinations", self_entry_meaning.get(p))

# ---------- xuất CSV ----------
def trang_thai(loai, token):
    if loai in ("Root", "Word"):
        return "Đã có trong MorphLink" if token in existing_roots else "Mới - chưa có ảnh"
    if loai == "Prefix":
        return "Đã có trong MorphLink" if token in existing_prefixes else "Mới - chưa có ảnh"
    if loai == "Suffix":
        return "Đã có trong MorphLink" if token in existing_suffixes else "Mới - chưa có ảnh"

rows_out = []
for (loai, token), d in data.items():
    en, vi = d["meaning"] if d["meaning"] else ("", "")
    rows_out.append({
        "loai": loai,
        "thanh_phan": token,
        "trang_thai": trang_thai(loai, token),
        "so_lan_xuat_hien": len(d["examples"]) if len(d["examples"]) < 6 else "6+",
        "meaning_en": en,
        "meaning_vi": vi,
        "vi_du_tu": ", ".join(sorted(d["examples"])),
        "nguon": "+".join(sorted(d["sources"])),
    })

LOAI_ORDER = {"Root": 0, "Word": 1, "Prefix": 2, "Suffix": 3}
rows_out.sort(key=lambda r: (LOAI_ORDER[r["loai"]], r["trang_thai"] != "Mới - chưa có ảnh", r["thanh_phan"]))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["loai", "thanh_phan", "trang_thai", "so_lan_xuat_hien", "meaning_en", "meaning_vi", "vi_du_tu", "nguon"])
    w.writeheader()
    w.writerows(rows_out)

print("total rows:", len(rows_out))
import collections
cnt = collections.Counter((r["loai"], r["trang_thai"]) for r in rows_out)
for k in sorted(cnt):
    print(k, cnt[k])
