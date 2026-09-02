"""
Bổ sung cho morphlink_grand_total.csv:
  1. Điền nốt 11 ô meaning_en còn trống (số đếm mười mấy/chục + "greenhouse").
  2. Thêm cột "bien_the" (biến thể): dạng bất quy tắc (động từ bất quy tắc,
     danh từ số nhiều bất quy tắc) hoặc biến thể chính tả Anh-Mỹ/Anh-Anh.

Nguồn:
  - Root đã có (2148): lấy thẳng cột "bien_the" có sẵn trong
    data/ROOTS_MEANING_AND_VARIANTS.csv (do nguồn dữ liệu gốc soạn sẵn).
  - Mọi thành phần khác: tra theo danh sách động từ bất quy tắc + danh từ
    số nhiều bất quy tắc + các cặp biến thể chính tả Anh-Mỹ/Anh-Anh chuẩn
    (kiến thức ngôn ngữ học phổ thông), mặc định "không có biến thể đáng
    kể" nếu không khớp trường hợp nào.
"""
import csv, os, re

ROOT = os.path.join(os.path.dirname(__file__), "..")
SRC = os.path.join(ROOT, "morphlink_grand_total.csv")
NO_VARIANT = "không có biến thể đáng kể"

# ---------- 11 nghia con thieu ----------
MISSING_EN = {
    "eighteen": "the number 18",
    "eighty": "the number 80",
    "fourteen": "the number 14",
    "greenhouse": "a glass building used for growing plants that need protection from cold weather",
    "nineteen": "the number 19",
    "seventeen": "the number 17",
    "seventy": "the number 70",
    "sixteen": "the number 16",
    "sixty": "the number 60",
    "thirteen": "the number 13",
    "thirty": "the number 30",
}

# ---------- dong tu bat quy tac (goc -> ghi chu) ----------
IRREGULAR_VERBS = {
    "be":"was/were/been","become":"became/become","begin":"began/begun","bend":"bent/bent",
    "bet":"bet/bet","bind":"bound/bound","bite":"bit/bitten","bleed":"bled/bled","blow":"blew/blown",
    "break":"broke/broken","breed":"bred/bred","bring":"brought/brought","build":"built/built",
    "burn":"burnt/burnt (hoặc burned)","burst":"burst/burst","buy":"bought/bought","catch":"caught/caught",
    "choose":"chose/chosen","cling":"clung/clung","come":"came/come","cost":"cost/cost","creep":"crept/crept",
    "cut":"cut/cut","deal":"dealt/dealt","dig":"dug/dug","dive":"dove/dived","do":"did/done","draw":"drew/drawn",
    "dream":"dreamt/dreamt (hoặc dreamed)","drink":"drank/drunk","drive":"drove/driven","eat":"ate/eaten",
    "fall":"fell/fallen","feed":"fed/fed","feel":"felt/felt","fight":"fought/fought","find":"found/found",
    "flee":"fled/fled","fling":"flung/flung","fly":"flew/flown","forbid":"forbade/forbidden",
    "forget":"forgot/forgotten","forgive":"forgave/forgiven","freeze":"froze/frozen","get":"got/gotten (hoặc got)",
    "give":"gave/given","go":"went/gone","grind":"ground/ground","grow":"grew/grown","hang":"hung/hung",
    "have":"had/had","hear":"heard/heard","hide":"hid/hidden","hit":"hit/hit","hold":"held/held",
    "hurt":"hurt/hurt","keep":"kept/kept","kneel":"knelt/knelt (hoặc kneeled)","know":"knew/known",
    "lay":"laid/laid","lead":"led/led","lean":"leant/leant (hoặc leaned)","leap":"leapt/leapt (hoặc leaped)",
    "learn":"learnt/learnt (hoặc learned)","leave":"left/left","lend":"lent/lent","let":"let/let",
    "lie":"lay/lain","light":"lit/lit (hoặc lighted)","lose":"lost/lost","make":"made/made","mean":"meant/meant",
    "meet":"met/met","mistake":"mistook/mistaken","pay":"paid/paid","prove":"proved/proven (hoặc proved)",
    "put":"put/put","quit":"quit/quit","read":"read/read","ride":"rode/ridden","ring":"rang/rung",
    "rise":"rose/risen","run":"ran/run","say":"said/said","see":"saw/seen","seek":"sought/sought","sell":"sold/sold",
    "send":"sent/sent","set":"set/set","sew":"sewed/sewn","shake":"shook/shaken","shed":"shed/shed",
    "shine":"shone/shone","shoot":"shot/shot","show":"showed/shown","shrink":"shrank/shrunk","shut":"shut/shut",
    "sing":"sang/sung","sink":"sank/sunk","sit":"sat/sat","sleep":"slept/slept","slide":"slid/slid",
    "smell":"smelt/smelt (hoặc smelled)","sow":"sowed/sown","speak":"spoke/spoken","speed":"sped/sped (hoặc speeded)",
    "spell":"spelt/spelt (hoặc spelled)","spend":"spent/spent","spill":"spilt/spilt (hoặc spilled)",
    "spin":"spun/spun","spit":"spat/spat","split":"split/split","spoil":"spoilt/spoilt (hoặc spoiled)",
    "spread":"spread/spread","spring":"sprang/sprung","stand":"stood/stood","steal":"stole/stolen",
    "stick":"stuck/stuck","sting":"stung/stung","stink":"stank/stunk","strike":"struck/struck",
    "swear":"swore/sworn","sweep":"swept/swept","swell":"swelled/swollen (hoặc swelled)","swim":"swam/swum",
    "swing":"swung/swung","take":"took/taken","teach":"taught/taught","tear":"tore/torn","tell":"told/told",
    "think":"thought/thought","throw":"threw/thrown","understand":"understood/understood","undo":"undid/undone",
    "upset":"upset/upset","wake":"woke/woken","wear":"wore/worn","weave":"wove/woven","weep":"wept/wept",
    "win":"won/won","wind":"wound/wound","withdraw":"withdrew/withdrawn","write":"wrote/written",
}
IRREGULAR_VERBS = {k: f"động từ bất quy tắc: {k}/{v}" for k, v in IRREGULAR_VERBS.items()}

# ---------- danh tu so nhieu bat quy tac ----------
IRREGULAR_PLURALS = {
    "child":"children","foot":"feet","tooth":"teeth","mouse":"mice","man":"men","woman":"women",
    "person":"people","goose":"geese","ox":"oxen","louse":"lice","die":"dice","half":"halves",
    "knife":"knives","wife":"wives","life":"lives","leaf":"leaves","loaf":"loaves","thief":"thieves",
    "wolf":"wolves","self":"selves","elf":"elves","shelf":"shelves","calf":"calves","scarf":"scarves (hoặc scarfs)",
    "cactus":"cacti (hoặc cactuses)","fungus":"fungi (hoặc funguses)","nucleus":"nuclei",
    "syllabus":"syllabi (hoặc syllabuses)","analysis":"analyses","crisis":"crises","thesis":"theses",
    "phenomenon":"phenomena","criterion":"criteria","datum":"data","medium":"media (hoặc mediums)",
    "index":"indices (hoặc indexes)","appendix":"appendices (hoặc appendixes)","matrix":"matrices",
    "vertex":"vertices","axis":"axes","basis":"bases","diagnosis":"diagnoses","hypothesis":"hypotheses",
    "parenthesis":"parentheses","sheep":"sheep (không đổi)","deer":"deer (không đổi)","fish":"fish (không đổi)",
    "series":"series (không đổi)","species":"species (không đổi)","aircraft":"aircraft (không đổi)",
}
IRREGULAR_PLURALS = {k: f"danh từ số nhiều bất quy tắc: {k}/{v}" for k, v in IRREGULAR_PLURALS.items()}

# ---------- cap bien the chinh ta Anh-My / Anh-Anh (tu -> tu) ----------
SPELLING_PAIRS = {
    "color":"colour","favor":"favour","honor":"honour","labor":"labour","neighbor":"neighbour",
    "rumor":"rumour","valor":"valour","vapor":"vapour","armor":"armour","behavior":"behaviour",
    "endeavor":"endeavour","flavor":"flavour","harbor":"harbour","humor":"humour","odor":"odour",
    "parlor":"parlour","rigor":"rigour","savor":"savour","splendor":"splendour","tumor":"tumour",
    "vigor":"vigour","candor":"candour","clamor":"clamour","glamor":"glamour","demeanor":"demeanour",
    "succor":"succour","tremor":"tremour","ardor":"ardour",
    "center":"centre","fiber":"fibre","liter":"litre","meter":"metre","theater":"theatre",
    "caliber":"calibre","luster":"lustre","scepter":"sceptre","somber":"sombre","specter":"spectre",
    "saber":"sabre",
    "catalog":"catalogue","dialog":"dialogue","analog":"analogue","monolog":"monologue","prolog":"prologue",
    "defense":"defence","license":"licence","offense":"offence","pretense":"pretence",
    "check":"cheque","plow":"plough","curb":"kerb","tire":"tyre","pajamas":"pyjamas","mustache":"moustache",
    "jewelry":"jewellery","aluminum":"aluminium","gray":"grey","donut":"doughnut","mold":"mould",
    "smolder":"smoulder","practice":"practise (Anh-Anh, động từ)","program":"programme (Anh-Anh)",
    "story":"storey (Anh-Anh, tầng nhà)","curbside":"kerbside","skeptic":"sceptic","artifact":"artefact",
    "disk":"disc","tidbit":"titbit",
}
SPELLING_PAIRS_REV = {v: k for k, v in SPELLING_PAIRS.items()}

# Từ có đuôi trùng hình thức "-ize" nhưng KHÔNG phải hậu tố -ize sản sinh
# (từ đơn hình vị/mượn, không có biến thể -ise thật) -> loại khỏi quy tắc.
IZE_PATTERN_BLOCKLIST = {"capsize"}

def spelling_variant_note(word):
    if word in IZE_PATTERN_BLOCKLIST:
        return None
    if word in SPELLING_PAIRS:
        return f"biến thể chính tả Anh-Anh: {SPELLING_PAIRS[word]}"
    if word in SPELLING_PAIRS_REV:
        return f"biến thể chính tả Anh-Mỹ: {SPELLING_PAIRS_REV[word]}"
    if word.endswith("ize") and len(word) >= 6:
        return f"biến thể chính tả Anh-Anh: {word[:-3]}ise"
    if word.endswith("yze") and len(word) >= 6:
        return f"biến thể chính tả Anh-Anh: {word[:-3]}yse"
    if word.endswith("izing") and len(word) >= 8:
        return f"biến thể chính tả Anh-Anh: {word[:-5]}ising"
    if word.endswith("ized") and len(word) >= 7:
        return f"biến thể chính tả Anh-Anh: {word[:-4]}ised"
    if word.endswith("ization") and len(word) >= 10:
        return f"biến thể chính tả Anh-Anh: {word[:-7]}isation"
    return None

def variant_note(word):
    if word in IRREGULAR_VERBS:
        return IRREGULAR_VERBS[word]
    if word in IRREGULAR_PLURALS:
        return IRREGULAR_PLURALS[word]
    sv = spelling_variant_note(word)
    if sv:
        return sv
    return NO_VARIANT

# ---------- root da co: lay bien_the co san tu du lieu goc ----------
root_bien_the = {}
with open(os.path.join(ROOT, "data", "ROOTS_MEANING_AND_VARIANTS.csv"), encoding="utf-8") as f:
    for r in csv.DictReader(f):
        bt = r["bien_the"].strip()
        root_bien_the[r["root_word"]] = bt if bt and bt != "không có biến thể đáng chú ý" else None

rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
for r in rows:
    if not r["meaning_en"] and r["thanh_phan"] in MISSING_EN:
        r["meaning_en"] = MISSING_EN[r["thanh_phan"]]

    tok = r["thanh_phan"]
    if r["loai"] == "Root" and r["trang_thai"] == "Đã có trong MorphLink" and tok in root_bien_the:
        r["bien_the"] = root_bien_the[tok] or NO_VARIANT
    else:
        r["bien_the"] = variant_note(tok)

still_missing = [r for r in rows if not r["meaning_en"] or not r["meaning_vi"]]
print("con thieu meaning:", len(still_missing))
for r in still_missing: print(r)

with_variant = [r for r in rows if r["bien_the"] != NO_VARIANT]
print("so dong co bien_the dang chu y:", len(with_variant))

with open(SRC, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["loai","thanh_phan","trang_thai","meaning_en","meaning_vi","bien_the","ghi_chu"])
    w.writeheader()
    w.writerows(rows)
print("saved", SRC, "- total rows:", len(rows))
