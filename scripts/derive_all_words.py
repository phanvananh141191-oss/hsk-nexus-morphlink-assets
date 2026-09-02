"""
Sinh TOÀN BỘ từ phái sinh/ghép thật (có trong từ điển hệ thống, không phải
tên riêng) có thể tạo được từ tập root+word+prefix+suffix ĐÃ CÓ (gộp cả
phần cũ của MorphLink lẫn phần mới phát hiện, tức toàn bộ
morphlink_grand_total.csv).

Base "root/word" component = mọi thanh_phan loai Root (cũ+mới) và loai
Word CHỈ PHẦN MỚI (vì Word "Đã có" trong grand_total thực ra là các từ
ĐÃ ĐƯỢC ghép ra rồi — là OUTPUT chứ không phải component đầu vào).

Kết quả cuối = hợp của:
  A) toàn bộ 11450 từ "Word - Đã có" (đã xác nhận là từ thật từ nguồn gốc)
  B) mọi tổ hợp root/root, prefix/root, root/suffix (+ mở rộng 3 thành
     phần) sinh ra từ tập base mở rộng, lọc còn TỪ THẬT trong từ điển hệ
     thống và KHÔNG phải tên riêng (áp lại đúng bộ lọc đã dùng ở
     build_master_audit_sheet.py).
"""
import csv, os, re
from collections import defaultdict

ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "morphlink_all_derived_words.csv")
DICT_PATH = "/usr/share/dict/american-english"

# ---------- từ điển hệ thống ----------
dict_words = set()
dict_words_any_case_lower = set()
with open(DICT_PATH, encoding="utf-8", errors="ignore") as f:
    for line in f:
        w = line.strip()
        if w and "'" not in w:
            dict_words_any_case_lower.add(w.lower())
            if w == w.lower():
                dict_words.add(w)
proper_noun_only = dict_words_any_case_lower - dict_words

PROPER_NOUN_KEYWORDS = re.compile(r"given name|surname|proper noun|not a common english word", re.I)
_NOUN = r"(country|city|capital(?:\s+city)?|continent|island|nation|province|river|mountain\s+range)"
PROPER_NOUN_STARTS = re.compile(r"^(a|an|the)\s+(?:[a-z]+[,\s]+){0,3}" + _NOUN + r"\s+(in|of|near|on|along|bordering)\b", re.I)
PROPER_NOUN_STATE = re.compile(r"^(a|an|the)\s+(?:[a-z]+[,\s]+){0,3}state\s+in\b", re.I)

def proper_noun_reason(token, meaning_en=""):
    if token[:1].isupper():
        return "viet hoa (ten rieng/viet tat)"
    if token in proper_noun_only:
        return "chi viet hoa trong tu dien (ten rieng)"
    m = (meaning_en or "").strip()
    if PROPER_NOUN_KEYWORDS.search(m):
        return "nghia mo ta ten nguoi/ten rieng"
    if PROPER_NOUN_STARTS.match(m) or PROPER_NOUN_STATE.match(m):
        return "nghia mo ta quoc gia/thanh pho/dia danh"
    return None

def is_real_word(w):
    return w in dict_words and not proper_noun_reason(w)

# ---------- đọc grand_total, tách base components ----------
grand = list(csv.DictReader(open(os.path.join(ROOT, "morphlink_grand_total.csv"), encoding="utf-8")))

roots_base = set()   # component đầu vào để ghép (Root toàn bộ + Word chỉ phần Mới)
prefixes = []
suffixes = []
existing_words = {}  # word -> (meaning_en, meaning_vi) từ Word/Đã có (đã xác nhận là từ thật)

for r in grand:
    loai, tok, trang_thai = r["loai"], r["thanh_phan"], r["trang_thai"]
    if loai == "Root":
        roots_base.add(tok)
    elif loai == "Word" and trang_thai == "Mới - chưa có ảnh":
        roots_base.add(tok)
    elif loai == "Word" and trang_thai == "Đã có trong MorphLink":
        existing_words[tok] = (r["meaning_en"], r["meaning_vi"])
    elif loai == "Prefix":
        prefixes.append(tok)
    elif loai == "Suffix":
        suffixes.append(tok)

MIN_LEN = 4
roots_list = sorted(t for t in roots_base if len(t) >= MIN_LEN)
prefixes = sorted(set(p for p in prefixes if len(p) >= 2))
suffixes = sorted(set(s for s in suffixes if len(s) >= 2))
print("roots_base(component):", len(roots_list), "prefixes:", len(prefixes), "suffixes:", len(suffixes))
print("existing_words (output, da co):", len(existing_words))

results = {}  # word -> cong_thuc (ghi chú cách ghép)

# ---------- 1) root + root ----------
roots_set = set(roots_list)
for r1 in roots_list:
    for r2 in roots_list:
        if r1 == r2:
            continue
        cand = r1 + r2
        if is_real_word(cand) and cand not in results:
            results[cand] = f"{r1}+{r2}"
print("sau root+root:", len(results))

# ---------- 2) prefix + root ----------
for root in roots_list:
    for pre in prefixes:
        cand = pre + root
        if is_real_word(cand) and cand not in results:
            results[cand] = f"{pre}-+{root}"
print("sau prefix+root:", len(results))

# ---------- 3) root + suffix (co xu ly quy tac chinh ta) ----------
VOWELS = set("aeiou")
def suffix_add_candidates(root, suf):
    cands = [root + suf]
    if root.endswith("e") and suf[0] in VOWELS:
        cands.append(root[:-1] + suf)
    if root.endswith("y") and len(root) > 1 and root[-2] not in VOWELS:
        cands.append(root[:-1] + "i" + suf)
    if len(root) >= 3 and root[-1] not in VOWELS and root[-2] in VOWELS and root[-3] not in VOWELS and suf[0] in VOWELS:
        cands.append(root + root[-1] + suf)
    return cands

for root in roots_list:
    for suf in suffixes:
        for cand in suffix_add_candidates(root, suf):
            if is_real_word(cand) and cand not in results:
                results[cand] = f"{root}+-{suf}"
                break
print("sau root+suffix:", len(results))

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["word", "trang_thai", "cong_thuc_hoac_nguon", "meaning_en", "meaning_vi"])
    for word, (en, vi) in existing_words.items():
        w.writerow([word, "Đã có trong MorphLink", "co san trong du lieu goc", en, vi])
    for word, formula in results.items():
        if word in existing_words:
            continue
        w.writerow([word, "Mới - ghép được nhưng chưa có trong dữ liệu MorphLink", formula, "", ""])

print("TOTAL rows:", len(existing_words) + sum(1 for w in results if w not in existing_words))
