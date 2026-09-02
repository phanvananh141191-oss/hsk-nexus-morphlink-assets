import csv, os, re
from collections import defaultdict

# Chạy: python3 scripts/build_word_formation_map.py  (từ gốc repo)
BASE = os.path.join(os.path.dirname(__file__), "..", "data")
OUT = os.path.join(os.path.dirname(__file__), "..", "word_formation_map.csv")

# Cần gói từ điển tiếng Anh hệ thống để phân biệt Root (không đứng độc lập
# được, vd "bio", "eco") và Word (đứng độc lập được, vd "sun", "happy").
# Debian/Ubuntu: apt-get install wamerican
DICT_PATH = "/usr/share/dict/american-english"

dict_words = set()
with open(DICT_PATH, encoding="utf-8", errors="ignore") as f:
    for line in f:
        w = line.strip()
        if w and "'" not in w:
            dict_words.add(w.lower())

def is_word(component):
    return component.lower() in dict_words

MAX_EXAMPLES = 8

# key: (root_word, type_label) -> {"examples": [...], "formula": str or None}
groups = defaultdict(lambda: {"examples": [], "formula": None})

# ---------- 1) ROOT_derivatives_FULL.csv : prefix / suffix on ONE root ----------
with open(f"{BASE}/ROOT_derivatives_FULL.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        root = row["root_word"]
        pat = row["pattern_PRS"]
        try:
            p, r, s = (int(x) for x in pat.split("-"))
        except ValueError:
            continue
        if r != 1:
            continue  # compound patterns (r>=2) are handled in file 2
        if p == 0 and s >= 1:
            type_label = "Root + Suffix"
            formula = f"{root} + suffix"
        elif p >= 1 and s == 0:
            type_label = "Prefix + Root"
            formula = f"prefix + {root}"
        elif p >= 1 and s >= 1:
            type_label = "Prefix + Root + Suffix"
            formula = f"prefix + {root} + suffix"
        else:
            continue  # p=0,s=0 shouldn't occur in a derivatives file
        key = (root, type_label)
        g = groups[key]
        g["formula"] = formula
        g["examples"].append(row["derived_word"])

# ---------- 2) COMPOUND_ROOT_derivatives_FULL.csv : root+root / root+word / word+word ----------
with open(f"{BASE}/COMPOUND_ROOT_derivatives_FULL.csv", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        components = row["component_roots"].split("+")
        if len(components) < 2:
            continue
        # Attribute the row to the FIRST component root (matches the convention
        # in the requested example table: "bio + logy -> biology" is listed
        # under "bio", not under "logy").
        primary = components[0]
        second = components[1]
        kinds = [is_word(c) for c in components[:2]]
        if not kinds[0] and not kinds[1]:
            type_label = "Root + Root"
        elif kinds[0] and kinds[1]:
            type_label = "Word + Word"
        else:
            type_label = "Root + Word"
        formula = f"{primary} + {second}"
        key = (primary, type_label)
        g = groups[key]
        if g["formula"] is None:
            g["formula"] = formula
        g["examples"].append(row["derived_word"])

# ---------- write output ----------
rows_out = []
for (root, type_label), g in groups.items():
    examples = sorted(set(g["examples"]))
    total = len(examples)
    shown = examples[:MAX_EXAMPLES]
    example_str = ", ".join(shown)
    if total > MAX_EXAMPLES:
        example_str += f" (+{total - MAX_EXAMPLES} từ khác)"
    rows_out.append({
        "root_word": root,
        "kieu_ket_hop": type_label,
        "cong_thuc": g["formula"],
        "vi_du_tu_moi": example_str,
        "so_luong_vi_du": total,
    })

# order: by root_word, then a fixed type order matching the user's list
TYPE_ORDER = ["Root + Root", "Root + Word", "Word + Word", "Prefix + Root", "Root + Suffix", "Prefix + Root + Suffix"]
def sort_key(r):
    return (r["root_word"], TYPE_ORDER.index(r["kieu_ket_hop"]) if r["kieu_ket_hop"] in TYPE_ORDER else 99)
rows_out.sort(key=sort_key)

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["root_word", "kieu_ket_hop", "cong_thuc", "vi_du_tu_moi", "so_luong_vi_du"])
    w.writeheader()
    w.writerows(rows_out)

print("total rows:", len(rows_out))
distinct_roots = len(set(r["root_word"] for r in rows_out))
print("distinct root words covered:", distinct_roots)
import collections
print(collections.Counter(r["kieu_ket_hop"] for r in rows_out))
