import csv, os, re
from collections import Counter, defaultdict

BASE = os.path.join(os.path.dirname(__file__), "..", "data")
ASSETS = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(os.path.dirname(__file__), "..", "affix_table.csv")

def load_affixes(sub):
    d = os.path.join(ASSETS, sub)
    return sorted(fn[:-5] for fn in os.listdir(d) if fn.endswith(".webp"))

prefixes = load_affixes("prefixes/images")
suffixes = load_affixes("suffixes/images")
print("prefixes:", len(prefixes), "suffixes:", len(suffixes))

# "token(gloss)" segments, gloss may contain one level of nested parens
SEGMENT_RE = re.compile(r"([A-Za-z]+-|-[A-Za-z]+)\(((?:[^()]|\([^^()]*\))*)\)")

def extract_segments(text):
    """Trả về list (token, gloss) từ chuỗi kiểu 'un-(không...) + able(có khả năng)'."""
    out = []
    for m in SEGMENT_RE.finditer(text):
        out.append((m.group(1), m.group(2)))
    return out

vi_glosses = defaultdict(Counter)   # affix -> Counter(gloss text)
en_glosses = defaultdict(Counter)
usage_count = Counter()             # affix -> số từ phái sinh dùng affix này
examples = defaultdict(list)        # affix -> [derived_word,...]

prefix_set = set(prefixes)
suffix_set = set(suffixes)

with open(f"{BASE}/ROOT_derivatives_FULL.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        struct = row["morphology_structure"]
        # tách phần trước "[" (tiền tố) và sau "]" (hậu tố)
        m = re.match(r"^(.*)\[(.+)\](.*)$", struct)
        if not m:
            continue
        pre_part, root_part, suf_part = m.groups()
        pre_tokens = [p for p in pre_part.strip("-").split("-") if p]
        suf_tokens = [s for s in suf_part.strip("-").split("-") if s]

        vi_segs = dict(extract_segments(row["nghia_tieng_viet"]))
        en_segs = dict(extract_segments(row["definition_en"])) if row["source"].startswith("compositional") else {}

        for tok in pre_tokens:
            if tok not in prefix_set:
                continue
            usage_count[("prefix", tok)] += 1
            key_variants = [f"{tok}-"]
            for kv in key_variants:
                if kv in vi_segs:
                    vi_glosses[("prefix", tok)][vi_segs[kv]] += 1
                if kv in en_segs:
                    en_glosses[("prefix", tok)][en_segs[kv]] += 1
            if len(examples[("prefix", tok)]) < 6:
                examples[("prefix", tok)].append(row["derived_word"])

        for tok in suf_tokens:
            if tok not in suffix_set:
                continue
            usage_count[("suffix", tok)] += 1
            kv = f"-{tok}"
            if kv in vi_segs:
                vi_glosses[("suffix", tok)][vi_segs[kv]] += 1
            if kv in en_segs:
                en_glosses[("suffix", tok)][en_segs[kv]] += 1
            if len(examples[("suffix", tok)]) < 6:
                examples[("suffix", tok)].append(row["derived_word"])

rows_out = []
for kind, affix_list in (("prefix", prefixes), ("suffix", suffixes)):
    for affix in affix_list:
        key = (kind, affix)
        vi = vi_glosses[key].most_common(1)
        vi_text = vi[0][0] if vi else ""
        en = en_glosses[key].most_common(1)
        en_text = en[0][0] if en else ""
        rows_out.append({
            "affix": affix,
            "loai": "prefix" if kind == "prefix" else "suffix",
            "dang_hien_thi": f"{affix}-" if kind == "prefix" else f"-{affix}",
            "nghia_en": en_text,
            "nghia_vi": vi_text,
            "so_tu_dung": usage_count[key],
            "vi_du": ", ".join(examples[key]),
        })

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["affix", "loai", "dang_hien_thi", "nghia_en", "nghia_vi", "so_tu_dung", "vi_du"])
    w.writeheader()
    w.writerows(rows_out)

no_vi = [r for r in rows_out if not r["nghia_vi"]]
no_en = [r for r in rows_out if not r["nghia_en"]]
print("total rows:", len(rows_out))
print("thiếu nghĩa tiếng Việt:", len(no_vi), [r["dang_hien_thi"] for r in no_vi])
print("thiếu nghĩa tiếng Anh:", len(no_en), [r["dang_hien_thi"] for r in no_en])
