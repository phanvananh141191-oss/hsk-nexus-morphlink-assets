"""
Tìm các tổ hợp MỚI (chưa có trong data/ROOT_derivatives_FULL.csv và
data/COMPOUND_ROOT_derivatives_FULL.csv) bằng cách ghép các root word
(2148 "mono" - từ gốc đơn) với nhau, hoặc với prefix/suffix đã có ảnh
trong morphlink, rồi chỉ giữ lại tổ hợp nào là TỪ THẬT (có trong từ điển
tiếng Anh hệ thống). Không bịa từ.

Ba loại tổ hợp:
  1. root + root  -> compound 2 thành phần (vd sun+flower -> sunflower)
  2. prefix + root -> (vd un+happy -> unhappy)
  3. root + suffix (có xử lý quy tắc chính tả: bỏ e cuối, y->i, nhân đôi
     phụ âm) -> (vd happy+ness -> happiness)

Sau đó thử nối thêm MỘT thành phần nữa vào các từ mới tìm được ở bước 1
(root+root) để ra tổ hợp 3 thành phần thật sự tồn tại:
  4. (root+root) + suffix
  5. prefix + (root+root)
"""
import csv, os
from collections import defaultdict

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
ASSETS = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(os.path.dirname(__file__), "..", "new_combinations.csv")
DICT_PATH = "/usr/share/dict/american-english"

dict_words = set()
with open(DICT_PATH, encoding="utf-8", errors="ignore") as f:
    for line in f:
        w = line.strip()
        # Chỉ nhận từ nếu nó xuất hiện ở dạng CHỮ THƯỜNG trong từ điển nguồn.
        # Nhiều tên riêng (Brandon, Reno, Dido, Jamal, Maya, Acton, Rankin...)
        # chỉ có mục viết hoa — nếu chấp nhận cả viết hoa rồi hạ về chữ thường,
        # rất nhiều tổ hợp trùng ngẫu nhiên với tên riêng sẽ lọt qua sai.
        if w and "'" not in w and w == w.lower():
            dict_words.add(w)

def load_affixes(sub):
    d = os.path.join(ASSETS, sub)
    return [fn[:-5] for fn in os.listdir(d) if fn.endswith(".webp")]

# Tiền tố/hậu tố 1 ký tự (a, e, o, u, i, n, t, y...) gây báo sai rất nhiều
# khi tự do ghép với mọi root (trùng ngẫu nhiên với từ có thật không liên
# quan, vd "ski"+"t" -> "skit", "of"+"t" -> "oft") — bỏ khỏi bước SINH tổ
# hợp mới này (khác với affix_table.csv là liệt kê đầy đủ, ở đây ưu tiên
# độ chính xác của từ MỚI tạo ra).
prefixes = [p for p in load_affixes("prefixes/images") if len(p) >= 2]
suffixes = [s for s in load_affixes("suffixes/images") if len(s) >= 2]

roots = set()
existing_prefix_root = set()
existing_root_suffix = set()
with open(f"{BASE}/ROOT_derivatives_FULL.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        roots.add(row["root_word"])
        pat = row["pattern_PRS"]
        p, r, s = (int(x) for x in pat.split("-"))
        struct = row["morphology_structure"]
        import re
        m = re.match(r"^(.*)\[(.+)\](.*)$", struct)
        if not m:
            continue
        pre_part, root_part, suf_part = m.groups()
        if r == 1:
            for tok in [t for t in pre_part.strip("-").split("-") if t]:
                existing_prefix_root.add((tok, row["root_word"]))
            for tok in [t for t in suf_part.strip("-").split("-") if t]:
                existing_root_suffix.add((row["root_word"], tok))

existing_compound_pairs = set()
with open(f"{BASE}/COMPOUND_ROOT_derivatives_FULL.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        comps = row["component_roots"].split("+")
        if len(comps) >= 2:
            existing_compound_pairs.add((comps[0], comps[1]))

print("roots:", len(roots), "prefixes:", len(prefixes), "suffixes:", len(suffixes))
print("existing prefix+root pairs:", len(existing_prefix_root))
print("existing root+suffix pairs:", len(existing_root_suffix))
print("existing compound pairs:", len(existing_compound_pairs))

roots_list = sorted(roots)
results = []  # (kieu, thanh_phan, tu_moi)

# Root/từ quá ngắn (<=3 ký tự) dễ trùng ngẫu nhiên với một từ có thật hoàn
# toàn không liên quan (vd "line"+"n" -> "linen", "of"+"t" -> "oft") — bỏ
# qua để giảm báo sai, đổi lại bỏ sót một số từ ghép ngắn thật (chấp nhận
# được, ưu tiên độ chính xác theo đúng yêu cầu "chỉ từ thật").
MIN_LEN = 4

# ---------- 1) root + root (compound) ----------
new_compounds = {}  # (r1,r2) -> word
for r1 in roots_list:
    if len(r1) < MIN_LEN:
        continue
    for r2 in roots_list:
        if r1 == r2 or len(r2) < MIN_LEN:
            continue
        if (r1, r2) in existing_compound_pairs:
            continue
        cand = r1 + r2
        if cand in dict_words:
            new_compounds[(r1, r2)] = cand
            results.append(("root+root (compound)", f"{r1}+{r2}", cand))

print("new root+root compounds:", len(new_compounds))

# ---------- 2) prefix + root ----------
new_prefix_root = 0
for root in roots_list:
    if len(root) < MIN_LEN:
        continue
    for pre in prefixes:
        if (pre, root) in existing_prefix_root:
            continue
        cand = pre + root
        if cand in dict_words:
            results.append(("prefix+root", f"{pre}-+{root}", cand))
            new_prefix_root += 1
print("new prefix+root:", new_prefix_root)

# ---------- 3) root + suffix (với quy tắc chính tả) ----------
VOWELS = set("aeiou")
def suffix_add_candidates(root, suf):
    cands = [root + suf]
    if root.endswith("e") and suf[0] in VOWELS:
        cands.append(root[:-1] + suf)
    if root.endswith("y") and len(root) > 1 and root[-2] not in VOWELS:
        cands.append(root[:-1] + "i" + suf)
    if len(root) >= 3 and root[-1] not in VOWELS and root[-2] in VOWELS and root[-3] not in VOWELS and suf[0] in VOWELS:
        cands.append(root + root[-1] + suf)  # nhân đôi phụ âm cuối (CVC)
    return cands

new_root_suffix = 0
for root in roots_list:
    if len(root) < MIN_LEN:
        continue
    for suf in suffixes:
        if (root, suf) in existing_root_suffix:
            continue
        hit = None
        for cand in suffix_add_candidates(root, suf):
            if cand in dict_words:
                hit = cand
                break
        if hit:
            results.append(("root+suffix", f"{root}+-{suf}", hit))
            new_root_suffix += 1
print("new root+suffix:", new_root_suffix)

# ---------- 4) (root+root) + suffix : mở rộng 3 thành phần ----------
new_compound_suffix = 0
for (r1, r2), word2 in list(new_compounds.items())[:2000]:  # giới hạn để tránh nổ tổ hợp
    for suf in suffixes:
        hit = None
        for cand in suffix_add_candidates(word2, suf):
            if cand in dict_words:
                hit = cand
                break
        if hit:
            results.append(("root+root+suffix", f"{r1}+{r2}+-{suf}", hit))
            new_compound_suffix += 1
print("new (root+root)+suffix:", new_compound_suffix)

# ---------- 5) prefix + (root+root) : mở rộng 3 thành phần ----------
new_prefix_compound = 0
for (r1, r2), word2 in list(new_compounds.items())[:2000]:
    for pre in prefixes:
        cand = pre + word2
        if cand in dict_words:
            results.append(("prefix+root+root", f"{pre}-+{r1}+{r2}", cand))
            new_prefix_compound += 1
print("new prefix+(root+root):", new_prefix_compound)

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["kieu_ket_hop", "cong_thuc", "tu_moi_phat_hien"])
    seen = set()
    for kieu, ct, tu in results:
        key = (kieu, tu)
        if key in seen:
            continue
        seen.add(key)
        w.writerow([kieu, ct, tu])

print("total rows written:", len(seen))
