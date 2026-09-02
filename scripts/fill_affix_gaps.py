import csv, os

OUT = os.path.join(os.path.dirname(__file__), "..", "affix_table.csv")

# Nghĩa bổ sung cho các tiền tố/hậu tố mà dữ liệu nguồn (ROOT_derivatives_FULL.csv)
# không có sẵn dòng "compositional" nào để trích nghĩa tiếng Anh (hoặc thiếu cả
# tiếng Việt, trường hợp "-iz"). Điền thủ công theo kiến thức ngôn ngữ học chuẩn,
# cùng văn phong (cụm ngắn, phân cách bằng dấu phẩy) với các dòng đã trích được.
FILL = {
    ("prefix", "ab"): ("away from, off", "rời khỏi, tách khỏi"),
    ("prefix", "after"): ("after, following", "sau, theo sau"),
    ("prefix", "al"): ("to, toward (assimilated form of ad-)", "đến, hướng về (biến thể của ad-)"),
    ("prefix", "ante"): ("before", "trước"),
    ("prefix", "auto"): ("self (Greek)", "tự, bản thân (Hy Lạp)"),
    ("prefix", "centi"): ("hundred, one hundredth", "trăm, một phần trăm"),
    ("prefix", "circum"): ("around (Latin)", "xung quanh (La Tinh)"),
    ("prefix", "demi"): ("half", "một nửa"),
    ("prefix", "di"): ("two, twice (Greek)", "hai, gấp đôi (Hy Lạp)"),
    ("prefix", "dia"): ("through, across (Greek)", "xuyên qua, băng qua (Hy Lạp)"),
    ("prefix", "dys"): ("bad, difficult, abnormal (Greek)", "xấu, khó khăn, bất thường (Hy Lạp)"),
    ("prefix", "extra"): ("outside, beyond", "bên ngoài, vượt ra ngoài"),
    ("prefix", "half"): ("half", "một nửa"),
    ("prefix", "hemi"): ("half (Greek)", "một nửa (Hy Lạp)"),
    ("prefix", "hyper"): ("over, excessive (Greek)", "quá mức, vượt trội (Hy Lạp)"),
    ("prefix", "hypo"): ("under, below normal (Greek)", "dưới mức, thấp hơn bình thường (Hy Lạp)"),
    ("prefix", "infra"): ("below, beneath (Latin)", "dưới, bên dưới (La Tinh)"),
    ("prefix", "intra"): ("within, inside (Latin)", "bên trong (La Tinh)"),
    ("prefix", "juxta"): ("next to, beside (Latin)", "kề bên, sát cạnh (La Tinh)"),
    ("prefix", "kilo"): ("thousand (Greek)", "nghìn (Hy Lạp)"),
    ("prefix", "macro"): ("large (Greek)", "lớn, vĩ mô (Hy Lạp)"),
    ("prefix", "melli"): ("honey (Latin)", "mật ong (La Tinh)"),
    ("prefix", "milli"): ("thousand, one thousandth", "nghìn, một phần nghìn"),
    ("prefix", "min"): ("small, less", "nhỏ, ít hơn"),
    ("prefix", "o"): ("connective vowel, little independent meaning", "nguyên âm nối, ít mang nghĩa riêng"),
    ("prefix", "ob"): ("against, toward, in the way of (Latin)", "chống lại, hướng về, cản trở (La Tinh)"),
    ("prefix", "omni"): ("all (Latin)", "tất cả, toàn bộ (La Tinh)"),
    ("prefix", "on"): ("on, onto", "trên, lên trên"),
    ("prefix", "pent"): ("five (Greek)", "năm (Hy Lạp)"),
    ("prefix", "peri"): ("around (Greek)", "xung quanh (Hy Lạp)"),
    ("prefix", "poly"): ("many (Greek)", "nhiều (Hy Lạp)"),
    ("prefix", "post"): ("after", "sau"),
    ("prefix", "quad"): ("four (Latin)", "bốn (La Tinh)"),
    ("prefix", "sur"): ("over, above (variant of super-)", "trên, vượt lên (biến thể của super-)"),
    ("prefix", "sus"): ("under, from below (variant of sub-)", "dưới, từ bên dưới (biến thể của sub-)"),
    ("prefix", "syn"): ("together, with (Greek)", "cùng, với nhau (Hy Lạp)"),
    ("prefix", "through"): ("through", "xuyên qua"),
    ("prefix", "thru"): ("through (informal spelling)", "xuyên qua (cách viết thân mật)"),
    ("prefix", "trans"): ("across, beyond, change", "băng qua, vượt qua, thay đổi"),
    ("prefix", "tri"): ("three", "ba"),
    ("prefix", "u"): ("variant connective form, little independent meaning", "dạng nối biến thể, ít mang nghĩa riêng"),
    ("prefix", "ultra"): ("beyond, extremely", "vượt xa, cực kỳ"),
    ("prefix", "uni"): ("one", "một"),

    ("suffix", "acy"): ("state, quality, condition (noun)", "trạng thái, tính chất (danh từ)"),
    ("suffix", "ade"): ("action, product of an action (noun)", "hành động, sản phẩm của hành động (danh từ)"),
    ("suffix", "ancy"): ("state, quality (noun)", "trạng thái, tính chất (danh từ)"),
    ("suffix", "ar"): ("relating to, like (adjective)", "liên quan đến, giống như (tính từ)"),
    ("suffix", "ard"): ("one who does something, often excessively (noun)", "người làm việc gì, thường quá mức (danh từ)"),
    ("suffix", "astic"): ("relating to, characterized by (adjective)", "liên quan đến, mang đặc điểm (tính từ)"),
    ("suffix", "ated"): ("having, characterized by (adjective)", "có, mang đặc điểm (tính từ)"),
    ("suffix", "atoire"): ("place for (borrowed from French)", "nơi để làm gì (mượn từ tiếng Pháp)"),
    ("suffix", "bie"): ("informal noun-forming suffix (e.g. newbie)", "hậu tố khẩu ngữ tạo danh từ (vd newbie)"),
    ("suffix", "een"): ("diminutive (from Irish)", "chỉ vật/người nhỏ (gốc Ireland)"),
    ("suffix", "enne"): ("female form (from French)", "dạng giống cái (gốc Pháp)"),
    ("suffix", "esque"): ("in the style of, resembling (adjective)", "theo phong cách, giống như (tính từ)"),
    ("suffix", "et"): ("small, diminutive (noun)", "nhỏ, chỉ vật nhỏ (danh từ)"),
    ("suffix", "fold"): ("times, multiplied by", "lần, nhân lên"),
    ("suffix", "hood"): ("state, condition, group (noun)", "trạng thái, tình trạng, nhóm (danh từ)"),
    ("suffix", "ia"): ("condition, disease, place (noun, Greek/Latin)", "tình trạng, bệnh, nơi chốn (danh từ, Hy-La)"),
    ("suffix", "iac"): ("relating to, suffering from (adjective)", "liên quan đến, mắc phải (tính từ)"),
    ("suffix", "iance"): ("state, quality (noun)", "trạng thái, tính chất (danh từ)"),
    ("suffix", "ics"): ("science, study, practice of (noun)", "khoa học, ngành nghiên cứu (danh từ)"),
    ("suffix", "ile"): ("capable of, relating to (adjective)", "có khả năng, liên quan đến (tính từ)"),
    ("suffix", "illion"): ("number-forming suffix (million, billion...)", "hậu tố tạo số đếm lớn (million, billion...)"),
    ("suffix", "ine"): ("relating to, made of, feminine (adjective/noun)", "liên quan đến, làm từ, giống cái (tính từ/danh từ)"),
    ("suffix", "issimo"): ("most, extremely (Italian superlative)", "nhất, cực kỳ (so sánh nhất gốc Ý)"),
    ("suffix", "iste"): ("one who practices (noun, French)", "người thực hành (danh từ, gốc Pháp)"),
    ("suffix", "ite"): ("mineral, follower of, resident of (noun)", "khoáng chất, người theo, cư dân (danh từ)"),
    ("suffix", "itis"): ("inflammation of (Greek, medical)", "viêm (Hy Lạp, y học)"),
    ("suffix", "itize"): ("to make into, to convert to (verb)", "biến thành, chuyển đổi thành (động từ)"),
    ("suffix", "itorium"): ("place for (noun)", "nơi để làm gì (danh từ)"),
    ("suffix", "itude"): ("state, quality (noun)", "trạng thái, tính chất (danh từ)"),
    ("suffix", "ivore"): ("eating, feeding on (Latin)", "ăn, tiêu thụ (La Tinh)"),
    ("suffix", "iz"): ("to make, to become (verb, variant of -ize)", "làm cho, biến thành (động từ, biến thể của -ize)"),
    ("suffix", "most"): ("superlative, farthest degree", "nhất, mức độ xa nhất"),
    ("suffix", "ock"): ("small, diminutive (noun)", "nhỏ, chỉ vật nhỏ (danh từ)"),
    ("suffix", "ode"): ("way, path (Greek)", "đường, lối (Hy Lạp)"),
    ("suffix", "ogy"): ("study of, science of (noun, Greek)", "ngành nghiên cứu, khoa học (danh từ, Hy Lạp)"),
    ("suffix", "oid"): ("resembling, like (adjective)", "giống như, có dạng (tính từ)"),
    ("suffix", "on"): ("unit, particle, state (noun)", "đơn vị, hạt, trạng thái (danh từ)"),
    ("suffix", "opath"): ("one who treats/practices (noun, Greek)", "người trị liệu/thực hành (danh từ, Hy Lạp)"),
    ("suffix", "ose"): ("full of, having qualities of (adjective); sugar (chemistry)", "đầy, mang tính chất (tính từ); đường (hoá học)"),
    ("suffix", "our"): ("state, quality, action (British spelling variant)", "trạng thái, tính chất, hành động (biến thể chính tả Anh-Anh)"),
    ("suffix", "ous"): ("full of, having (adjective)", "đầy, có tính chất (tính từ)"),
    ("suffix", "some"): ("tending to, characterized by (adjective)", "có xu hướng, mang đặc điểm (tính từ)"),
    ("suffix", "ster"): ("one who does, associated with (noun)", "người làm việc gì, liên quan đến (danh từ)"),
    ("suffix", "teen"): ("plus ten (numbers 13-19)", "cộng mười (số 13-19)"),
    ("suffix", "tograph"): ("instrument that writes/records (variant of -graph)", "dụng cụ ghi/viết (biến thể của -graph)"),
    ("suffix", "tography"): ("process of writing/recording (variant of -graphy)", "quá trình ghi/viết (biến thể của -graphy)"),
    ("suffix", "tude"): ("state, quality (noun)", "trạng thái, tính chất (danh từ)"),
    ("suffix", "ulin"): ("protein or substance (biology/chemistry)", "protein hoặc chất (sinh/hoá học)"),
    ("suffix", "us"): ("Latin masculine noun ending", "đuôi danh từ giống đực trong tiếng La Tinh"),
}

rows = list(csv.DictReader(open(OUT, encoding="utf-8")))
filled_en = filled_vi = 0
for r in rows:
    key = (r["loai"], r["affix"])
    if key in FILL and not r["nghia_en"]:
        r["nghia_en"] = FILL[key][0]
        filled_en += 1
    if key in FILL and not r["nghia_vi"]:
        r["nghia_vi"] = FILL[key][1]
        filled_vi += 1

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["affix", "loai", "dang_hien_thi", "nghia_en", "nghia_vi", "so_tu_dung", "vi_du"])
    w.writeheader()
    w.writerows(rows)

print("filled EN:", filled_en, "filled VI:", filled_vi)
still_missing_en = [r["dang_hien_thi"] for r in rows if not r["nghia_en"]]
still_missing_vi = [r["dang_hien_thi"] for r in rows if not r["nghia_vi"]]
print("still missing EN:", still_missing_en)
print("still missing VI:", still_missing_vi)
