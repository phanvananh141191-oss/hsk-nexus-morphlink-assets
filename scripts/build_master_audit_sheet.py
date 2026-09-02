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

# Từ nào chỉ xuất hiện dạng VIẾT HOA trong từ điển hệ thống -> tên riêng
# (người/địa danh/thương hiệu), vd Kenya, Washington, Fleming... Danh sách
# 5638 "từ thiếu" được trích từ Reading/Writing đã lowercase hết nên không
# còn phân biệt hoa/thường được nữa -> phải dựa vào từ điển gốc để lọc lại.
dict_words_lower_only = set()
dict_words_any_case_lower = set()
with open(DICT_PATH, encoding="utf-8", errors="ignore") as f:
    for line in f:
        w = line.strip()
        if w and "'" not in w:
            dict_words_any_case_lower.add(w.lower())
proper_noun_only = dict_words_any_case_lower - dict_words

PROPER_NOUN_KEYWORDS = re.compile(r"given name|surname|proper noun|not a common english word", re.I)
_NOUN = r"(country|city|capital(?:\s+city)?|continent|island|nation|province|river|mountain\s+range)"
PROPER_NOUN_STARTS = re.compile(r"^(a|an|the)\s+(?:[a-z]+[,\s]+){0,3}" + _NOUN + r"\s+(in|of|near|on|along|bordering)\b", re.I)
PROPER_NOUN_STATE = re.compile(r"^(a|an|the)\s+(?:[a-z]+[,\s]+){0,3}state\s+in\b", re.I)

def proper_noun_reason(token, meaning_en):
    if token[:1].isupper():
        return "viết hoa (tên riêng/viết tắt/quốc tịch)"
    if token in proper_noun_only:
        return "chỉ viết hoa trong từ điển (tên riêng)"
    m = (meaning_en or "").strip()
    if PROPER_NOUN_KEYWORDS.search(m):
        return "nghĩa mô tả tên người/tên riêng"
    if PROPER_NOUN_STARTS.match(m) or PROPER_NOUN_STATE.match(m):
        return "nghĩa mô tả quốc gia/thành phố/địa danh"
    return None

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
    raw_bracket_toks = re.findall(r"\[([^\]]+)\]", struct)
    pre_part = struct[:struct.index("[")]
    suf_part = struct[struct.rindex("]") + 1:]
    pre_toks = [t for t in re.split(r"[-+]", pre_part.strip("-+")) if t]
    suf_toks = [t for t in re.split(r"[-+]", suf_part.strip("-+")) if t]
    # Vài dòng do agent viết structure kiểu "[-ing]" (đánh dấu rõ đây là hậu
    # tố chứ không phải root, vd từ "ing" bị lẫn vào danh sách "từ thiếu")
    # -> phải tách các token trong ngoặc có dấu "-" ra prefix/suffix thay vì
    # coi là root/word.
    bracket_toks = []
    for t in raw_bracket_toks:
        if t.startswith("-"):
            suf_toks.append(t[1:])
        elif t.endswith("-"):
            pre_toks.append(t[:-1])
        else:
            bracket_toks.append(t)
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
rows_excluded = []
for (loai, token), d in data.items():
    en, vi = d["meaning"] if d["meaning"] else ("", "")
    row = {
        "loai": loai,
        "thanh_phan": token,
        "trang_thai": trang_thai(loai, token),
        "so_lan_xuat_hien": len(d["examples"]) if len(d["examples"]) < 6 else "6+",
        "meaning_en": en,
        "meaning_vi": vi,
        "vi_du_tu": ", ".join(sorted(d["examples"])),
        "nguon": "+".join(sorted(d["sources"])),
    }
    # Root/Word là tên riêng (người, địa danh, thương hiệu...) không phải
    # thành phần cấu tạo từ thật -> loại khỏi sheet audit chính, nhưng vẫn
    # ghi lại riêng để minh bạch (không âm thầm xóa).
    reason = proper_noun_reason(token, en) if loai in ("Root", "Word") else None
    if reason:
        row["ly_do_loai"] = reason
        rows_excluded.append(row)
    else:
        rows_out.append(row)

LOAI_ORDER = {"Root": 0, "Word": 1, "Prefix": 2, "Suffix": 3}
rows_out.sort(key=lambda r: (LOAI_ORDER[r["loai"]], r["trang_thai"] != "Mới - chưa có ảnh", r["thanh_phan"]))
rows_excluded.sort(key=lambda r: (LOAI_ORDER[r["loai"]], r["thanh_phan"]))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["loai", "thanh_phan", "trang_thai", "so_lan_xuat_hien", "meaning_en", "meaning_vi", "vi_du_tu", "nguon"])
    w.writeheader()
    w.writerows(rows_out)

EXCLUDED_OUT = os.path.join(ROOT, "master_audit_sheet_excluded_proper_nouns.csv")
with open(EXCLUDED_OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["loai", "thanh_phan", "trang_thai", "so_lan_xuat_hien", "meaning_en", "meaning_vi", "vi_du_tu", "nguon", "ly_do_loai"])
    w.writeheader()
    w.writerows(rows_excluded)

print("total rows:", len(rows_out), "| loai tru (ten rieng):", len(rows_excluded))
import collections
cnt = collections.Counter((r["loai"], r["trang_thai"]) for r in rows_out)
for k in sorted(cnt):
    print(k, cnt[k])
