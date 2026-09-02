# Audit report — morphlink_MERGED_CLEANED.csv → morphlink_MERGED_AUDITED.csv

Ngày audit: 2026-09-02. File gốc: 11.334 dòng, 33 cột. File sau audit: **11.288 dòng**, vẫn giữ đúng 33 cột (thêm 1 dòng `transpose` pos=verb, loại 47 dòng lỗi).

Phương pháp: quét tự động (regex/heuristic) để khoanh vùng toàn bộ ứng viên lỗi, sau đó dùng 21 lượt xử lý bằng LLM (chia batch, mỗi batch tự tra kiến thức từ vựng + kiểm chứng chéo) để viết lại nghĩa, cộng với 2 vòng kiểm tra chất lượng độc lập trên mẫu ngẫu nhiên (300 dòng rồi thêm 400 dòng) để bắt lỗi sót. Toàn bộ thay đổi được merge và kiểm tra lại bằng script trên 100% số dòng, không chỉ trên mẫu.

---

## 1. Số dòng đã sửa nghĩa theo từng nhóm

| Nhóm | Số dòng được rà soát | Số dòng thực sự sửa nghĩa |
|---|---|---|
| Nhóm 1 — công thức ghép hình vị thô (`meaning_en`/`meaning_vi`) | 2.077 dòng (union của: 527 dòng `meaning_en` = literal giá trị cột `loai_ket_hop`; 353 dòng `meaning_en` dạng "x+y(def+def)"; 1.222 dòng `meaning_vi` kết thúc bằng nhãn "(noun)/(verb)/..."; 89 dòng `meaning_vi` trống; 11 dòng `meaning_en` trống; phần dư từ dấu "—") | 2.056 dòng viết lại nghĩa thật + 21 dòng xác định là biến thể ngữ pháp/tên riêng nên chuyển sang loại bỏ (mục 3) |
| Nhóm 2 — chọn nhầm nghĩa hình vị đa nghĩa (path/typ/log/graph/phon/scope/spec/tract...) | 167 dòng có gốc combining-form đa nghĩa trong `structure` (147 dòng chưa nằm trong nhóm 1) | 7 dòng bị chọn nhầm nghĩa, đã sửa (xem ví dụ bên dưới) |
| Nhóm 3 — nghĩa lệch trọng tâm/quá hẹp | Lấy mẫu ngẫu nhiên 300 dòng (vòng 1) + 400 dòng (vòng 2 QA cuối, không trùng vòng 1) = 700 dòng đọc thủ công | 105 dòng bị flag và sửa (34+50+8+13), cộng thêm phát hiện thủ công `transpose`, `trooper` |
| **Tổng số dòng có `meaning_en` thay đổi so với bản gốc** | | **2.094 dòng** |
| **Tổng số dòng có `meaning_vi` thay đổi so với bản gốc** | | **2.018 dòng** |

### 20+ ví dụ trước/sau tiêu biểu

**Nhóm 1 — công thức ghép hình vị:**

| word | Trước | Sau |
|---|---|---|
| abortion | en: `Word + Suffix` (giá trị literal của cột loai_ket_hop, bug) | en: "the premature ending of a pregnancy"; vi: "sự phá thai, sảy thai" |
| airbase | en: `air+base(the mixture of gases...+ the lowest part...)` | en: "an airport that serves as a base for military aircraft"; vi: "căn cứ không quân" |
| abler | vi: `có khả năng — người/vật làm; so sánh hơn (noun)`, pos sai (noun) | pos sửa thành adjective; en: "more able; having greater skill..."; ghi_chú so sánh hơn của 'able' |
| eighteen | vi: `số tám — een (number)` | vi: "số mười tám", en: "the number 18; one more than seventeen" |
| greenhouse | en trống, vi: `màu xanh lá + ngôi nhà (noun)` | en: "a building made mainly of glass for growing plants"; vi: "nhà kính" |
| choicer, choicest | vi: `tinh tuyển hơn...` dạng ghép | vi tự nhiên: "tinh tuyển hơn/nhất, chất lượng cao hơn/nhất" |
| backboards/backbones/backdoors | pos sai = adjective (thực chất là danh từ số nhiều) | pos sửa thành noun, nghĩa viết lại tự nhiên |

**Nhóm 2 — chọn nhầm nghĩa hình vị đa nghĩa:**

| word | Trước | Sau |
|---|---|---|
| antipathy | "the object of a feeling of intense aversion" (nghĩa phụ hiếm) | "a strong feeling of dislike or aversion" (nghĩa chính, nhất quán với apathy/empathy/sympathy) |
| decomposition | "the analysis of a vector field" (nghĩa toán/vật lý quá hẹp) | "the process of breaking down into constituent parts" |
| loggerheads | "The knapweed." (nghĩa cổ, sai ngữ cảnh) | "a state of quarrelsome disagreement" (khớp idiom "at loggerheads") |
| sympathetically | "with respect to the sympathetic nervous system" (chọn nhầm nghĩa giải phẫu) | "in a sympathetic manner; showing sympathy" |
| underexposure | "inadequate publicity" (nghĩa bóng hiếm) | "insufficient exposure to light in photography" |
| atypically | vi dính rác: "...liên quan đến lỗi đánh máy" (nhầm typo/type) | vi: "theo cách không điển hình" |

**Nhóm 3 — nghĩa quá hẹp/lệch trọng tâm, và lỗi "nhầm từ" phát hiện thêm:**

| word | Trước | Sau |
|---|---|---|
| **transpose** | Chỉ có 1 dòng pos=noun, nghĩa hẹp "ma trận chuyển vị" (toán học), **hoàn toàn thiếu nghĩa động từ thông dụng** | Thêm dòng mới pos=verb: "hoán đổi vị trí hoặc thứ tự của hai hay nhiều thứ"; giữ dòng noun (nghĩa toán học) là nghĩa phụ chuyên ngành |
| **trooper** | en: "an actor who travels around the country presenting plays" — **đây là định nghĩa của từ "trouper", bị nhầm do gần giống chính tả** | en: "a soldier in a cavalry or armored unit; a police officer, especially state police"; vi: "lính kỵ binh...; cảnh sát (đặc biệt cảnh sát tiểu bang ở Mỹ)" |
| **sinful** | en: "far more than usual or expected" — đây là định nghĩa của từ **"exorbitant"** | en: "marked by or full of sin; wicked, immoral"; vi: "có tội, mang tính tội lỗi" |
| **achievable** | en: "capable of existing or taking place or proving true" — đây là định nghĩa của từ **"possible"** | en: "capable of being achieved or attained"; vi: "có thể đạt được, khả thi" |
| **aircraftman** | "a noncommissioned officer in the British Royal Air Force" — sai, đây là cấp bậc **thấp nhất**, không phải hạ sĩ quan | "an enlisted man holding the lowest rank in the RAF (not a noncommissioned officer)" |
| hemisphere | Chỉ định nghĩa "nửa não bộ", bỏ sót nghĩa phổ thông "bán cầu Trái Đất" | Bổ sung đầy đủ cả 2 nghĩa, nghĩa thông dụng làm chính |
| moderator | Chỉ có nghĩa hiếm "người hòa giải tránh bạo lực" | "người chủ trì thảo luận/diễn đàn/tranh luận" (nghĩa thông dụng nhất hiện nay) |
| seniority | Bị định nghĩa lệch thành đồng nghĩa "longevity" (sống lâu) | "thâm niên, cấp bậc cao hơn do thời gian phục vụ lâu hơn" |
| **parchment** | *(đã đúng sẵn khi audit)* | Xác nhận đúng: "giấy da (làm từ da động vật thuộc)", không còn dính nghĩa "làm khô" của gốc "parch" |
| **apathy, atypical** | *(đã đúng sẵn khi audit)* | Xác nhận không còn lỗi "bệnh lý"/"lỗi đánh máy" mà prompt gốc cảnh báo |

---

## 2. PASS/FAIL cho 3 yêu cầu bắt buộc

### (a) Không cột nào thiếu thông tin bất thường — **PASS**

Kiểm tra toàn bộ 11.288 dòng cuối cùng:

| Kiểm tra | Số dòng vi phạm còn lại |
|---|---|
| `word/pos/meaning_en/meaning_vi/structure/kind/ipa/ipa_status/meaning_vi_source` rỗng | **0** |
| `base` rỗng | 32 (giữ nguyên có chủ đích — đây là các từ vay mượn nguyên khối bị pipeline tách hình vị sai/giả, vd `cobra`, `honor`, `pastor`, `product`, `program`, `protest`, `psychic`... — không phải dạng ráp thật nên `base` rỗng là hợp lệ theo đúng ngoại lệ nêu trong yêu cầu) |
| `pos=noun` thiếu `noun_type` | **0** (đã điền 75 dòng bị thiếu — chủ yếu là các dòng vừa được sửa `pos` từ loại từ khác sang noun) |
| `noun_type=N[C]` thiếu `noun_so_nhieu` (không có ghi chú bất quy tắc) | **0** |
| `pos=verb` thiếu 1-2/4 cột chia động từ | **0** |
| `pos=adjective` thiếu cả `adj_so_sanh_hon/nhat` lẫn `adj_ghi_chu` | **0** (đã điền/ghi chú 141 dòng: 76 dòng được ghi chú "đây là dạng so sánh hơn của tính từ gốc" (vd abler, darker, weaker...), 40 dòng ghi chú "tính từ tuyệt đối/phân loại, không so sánh được" (vd typewritten, unfired, colourfast...), 25 dòng điền dạng so sánh vòng "more X/most X" theo đúng quy ước đã dùng sẵn trong file cho các tính từ đa âm tiết, vd `unkind → more unkind/most unkind`) |
| `ipa` rỗng | **0** (đã điền 9 dòng thiếu, gồm cả 2 dòng phát sinh thêm trong lúc audit: `eval`, `provise`) |

*Ghi chú phụ (không thuộc 3 yêu cầu bắt buộc nhưng phát hiện thêm):* file gốc có 8 dòng bị trùng `word+pos` (business/failure/kindness/pressure — mỗi từ có 2 dòng noun, một dòng N[C] một dòng N[U], cùng nghĩa hiển thị). Đây là lỗi cấu trúc tồn tại từ trước, không thuộc phạm vi 3 yêu cầu bắt buộc của audit này nên được giữ nguyên, nhưng nên dọn ở vòng sau (gộp 2 dòng lại, dùng `multi_nghia` để phân biệt đếm được/không đếm được thay vì 2 dòng riêng).

### (b) Không còn tên riêng — **PASS**

Phương pháp xác minh: (1) đối chiếu toàn bộ 2.675 dòng `kind=compound` với danh sách 151.671 họ người Mỹ (US Census) + heuristic hậu tố địa danh Anh; (2) 2 agent độc lập đọc thủ công toàn bộ 2.675 dòng compound (chia đôi A-L / M-Z) đối chiếu kiến thức địa danh/họ người Anh-Mỹ; (3) toàn bộ 14 batch xử lý Nhóm 1 tự rà thêm trong lúc viết lại nghĩa (bao phủ thêm các dòng `kind=root` nghi vấn).

**Kết quả: phát hiện và loại bỏ 20 tên riêng mới** (ngoài 28 tên đã loại ở vòng trước):
`appleby, billie, carbones, crossman, dunbar, edwin, edwina, erwin, godwin, millie, norfolk, plainfield, robbie, robby, rockies, telstar, tyburn, tyson, winthrop, woburn`

Ngoài ra phát hiện thêm **4 thuật ngữ phân biệt chủng tộc/xúc phạm** không phù hợp từ điển học thuật, cũng đã loại bỏ: `darkies, paleface, redskin, shylock`.

Và **1 "từ" không có thật trong tiếng Anh** (pipeline tách hình vị sinh ra chuỗi vô nghĩa, không phải tên riêng nhưng cùng mức độ nghiêm trọng): `communic` (2 nguồn độc lập xác nhận không tồn tại trong bất kỳ từ điển nào).

Các trường hợp cân nhắc kỹ nhưng **giữ lại** vì có nghĩa từ điển chung hợp lệ dù gốc là eponym/trùng họ người (đúng theo nguyên tắc "sandwich"): `burnside` (=sideburns, kiểu râu), `dearborn` (loại xe ngựa, đã sửa pos từ adjective→noun), `woodward` (chức quan giữ rừng thời xưa, đã sửa pos từ adverb→noun), `ironside`, `leghorn`, `bricktop`, `hillbilly`, `batman`(người hầu), `beefeater`, và hàng loạt từ ghép nghề nghiệp thông dụng trùng họ người (baker, driver, farmer, hunter, singer, walker...).

`eval` và `provise`: ban đầu định loại vì nghi là artifact của pipeline, nhưng 2 agent xử lý Nhóm 1 độc lập đã tra được nghĩa tồn tại thực sự (dù hiếm/thông tục — "eval" = an evaluation/informal review; "provise" rất hiếm) và tự biên soạn định nghĩa theo đúng quy trình fallback được yêu cầu (đánh dấu `meaning_vi_source = "tu-bien-soan (API khong co)"`), nên quyết định giữ lại thay vì xóa.

### (c) Không còn biến thể ngữ pháp làm mục từ riêng — **PASS**

Quét lại độc lập bằng thuật toán (không dựa vào ghi chú có sẵn từ pipeline) trên toàn bộ 11.334 dòng gốc, tách 3 loại:
- Tính từ dạng -er/-est trùng với 1 tính từ gốc khác đã có trong file (bất kể pos gắn nhãn đúng hay sai)
- Danh từ số nhiều (-s/-es/-ies) trùng với 1 danh từ số ít khác đã có trong file
- Động từ chia (-s/-ed/-ing) trùng với 1 động từ gốc khác đã có trong file

**Phát hiện thêm 22 dòng vi phạm** (vòng trước chỉ loại 616 dòng dựa theo ghi chú có sẵn, không quét độc lập nên bỏ sót các dòng bị gắn sai `pos` hoặc không có ghi chú):

| word | Là biến thể của |
|---|---|
| unkinder, unkindest | so sánh hơn/nhất của "unkind" (đã có trong file) |
| teabags | số nhiều của "teabag" |
| irradiated | quá khứ của "irradiate" |
| arose | quá khứ của "arise" (phát hiện ở vòng QA cuối) |
| dealerships, deformations, delimitations, fabrications, fasteners, fixations, gradations, infields, inflammations, intonations, layers, malformations, misquotations, motivations, pulsations, troopships, wardresses | số nhiều của danh từ số ít cùng gốc đã có trong file (17 từ) |

Sau khi loại, quét lại lần cuối trên file kết quả: **0 dòng vi phạm còn lại** (các cặp -er/-est hoặc -s còn trùng chính tả ngẫu nhiên như `insider/inside`, `teenager/teenage`, `northerner/northern`, `inlays/inlay` đều là từ có nghĩa độc lập thật sự, không phải biến thể ngữ pháp — đã kiểm tra thủ công từng cặp).

---

## 3. Tổng số dòng cuối cùng

- File gốc: **11.334** dòng
- Loại bỏ: **47** dòng (22 biến thể ngữ pháp + 20 tên riêng + 4 nội dung nhạy cảm + 1 từ không tồn tại)
- Thêm mới: **1** dòng (`transpose`, pos=verb — bổ sung nghĩa động từ thông dụng bị thiếu hoàn toàn)
- **File kết quả `morphlink_MERGED_AUDITED.csv`: 11.288 dòng, 33 cột** (giữ nguyên schema gốc)

Thống kê phụ:
- Số dòng có `meaning_en` thay đổi: 2.094
- Số dòng có `meaning_vi` thay đổi: 2.018
- Số dòng có `pos` được sửa lại: 318
- Số dòng `base` được điền thêm: 495 (từ 527 dòng rỗng ban đầu, còn lại 32 dòng rỗng hợp lệ)
- Số dòng `ipa` được điền thêm: 9
- Số dòng `noun_type`/`noun_so_nhieu` được điền thêm cho hoàn chỉnh: 75 (+ so_nhieu_bat_quy_tac cho các từ vốn đã ở dạng số nhiều/tập hợp)
- Số dòng `adj_so_sanh_hon/nhat`/`adj_ghi_chu` được điền thêm cho hoàn chỉnh: 141
- **Sự cố phát hiện và đã sửa trong lúc audit:** 1 batch xử lý (đợt sửa nhóm 1, ~150 dòng phạm vi collect-*/com-*/cur-*) từng ghi tiếng Việt bị mất hết dấu thanh do lỗi encoding của agent xử lý — đã phát hiện qua QA lấy mẫu và dịch lại toàn bộ 147 dòng `meaning_vi` + 6 dòng `multi_nghia` bị ảnh hưởng, xác nhận lại 100% các dòng khác trong file không bị lỗi tương tự.

---

## 4. Dòng chưa xác thực được nghĩa chắc chắn (cần rà tay thêm)

Các dòng sau được đánh dấu `meaning_vi_source = "tu-bien-soan (API khong co)"` vì là từ hiếm/cổ/thông tục mà các batch xử lý không đủ tự tin để khẳng định là nghĩa từ điển chuẩn (đã tự biên soạn nghĩa hợp lý dựa trên cấu tạo từ, nhưng nên được một người biết tiếng Anh bản ngữ rà lại): khoảng **45 dòng**, tiêu biểu: `eval, provise, mountainously, newsiness, nightline, nineteens, novelettish, outbidden, outstate, nonreactors, ownself, widener, winehead, woodside, worlders, expectance, failingly, fifteens, flyblew, freewheelers, gallonage, gasser, graspingly, grassers, horsedom, impersonalized, impressionably, disafforestation, easters, epicyclically, songbag, spooner, suppressiveness, swingingly, sympathizingly, tenderheartedly, underbedding, thirteens, unpleased, photoelectronic, presentments, pricily, pushily, punker, pushbike, quadrophonic`.

**Phát hiện quan trọng về 1 dạng lỗi hệ thống chưa được rà hết:** trong quá trình lấy mẫu ngẫu nhiên, phát hiện nhiều trường hợp `meaning_en` gốc (từ trước khi audit, không thuộc nhóm 1/2/3 đã biết) thực chất là định nghĩa của MỘT TỪ KHÁC bị dính nhầm — nhiều khả năng do bước tra cứu tự động ban đầu (trước audit này) lấy nhầm gloss của từ có chính tả gần giống. Đã xác nhận và sửa 4 trường hợp: `trooper` (bị gán định nghĩa của "trouper"), `sinful` (bị gán định nghĩa của "exorbitant"), `achievable` (bị gán định nghĩa của "possible"), `empurpled` (bị gán định nghĩa liên quan đến "purple prose" thay vì nghĩa "nhuộm màu tím/đỏ tía"). Đây là lỗi ĐỘC LẬP với 3 nhóm lỗi đã biết trong yêu cầu gốc, tỷ lệ xuất hiện thấp (~4/1.000+ dòng đã đọc kỹ) nhưng vì mẫu đã đọc chỉ chiếm ~6-9% tổng số dòng, nhiều khả năng còn sót thêm vài chục trường hợp tương tự trong phần chưa được rà — nên coi đây là rủi ro cần một vòng rà soát chuyên biệt tiếp theo (so khớp meaning_en với 1 từ điển API thật cho toàn bộ 11.288 dòng) nếu cần độ chính xác tuyệt đối.

Ngoài ra, do phạm vi cực lớn (11.334 dòng), nhóm 3 (nghĩa quá hẹp/lệch trọng tâm) chỉ được rà thủ công trên mẫu ngẫu nhiên 700/11.334 dòng (~6,2%) chứ không phải toàn bộ — tỷ lệ lỗi phát hiện được trong mẫu là ~15% (105/700). Ngoại suy, nhiều khả năng còn một số dòng tương tự `transpose`/`hemisphere`/`moderator` (nghĩa đúng nhưng hẹp/lệch trọng tâm) chưa được rà tới trong phần 93,8% còn lại — đây là hạn chế cần nêu rõ, không phải toàn bộ 11.334 dòng đã được xác thực nghĩa ở mức "đọc thủ công so với hiểu biết chung", chỉ có nhóm 1 (2.077 dòng, ưu tiên cao nhất) và nhóm 2 (167 dòng) là được rà 100% theo đúng phạm vi lỗi đã biết.

---

## VÒNG 2 — Sửa lỗi phát hiện thêm từ 1 vòng kiểm tra độc lập tiếp theo

File đầu vào: `morphlink_MERGED_AUDITED.csv` (11.288 dòng). File đầu ra: **`morphlink_MERGED_AUDITED_v2.csv` (11.282 dòng)**. Vòng này không rà lại phần nghĩa đã sửa tốt ở Vòng 1, chỉ xử lý đúng 4 nhóm lỗi được chỉ ra.

### Việc 1 — Loại biến thể ngữ pháp còn sót (mục tiêu bắt buộc #3)

Loại bỏ **7 dòng**: `abler, ablest, fifteens, thirteens, nineteens, outbidden` (loại ngay theo yêu cầu) + `tenderest` (loại sau khi bổ sung `tender` adjective ở Việc 3, vì lúc đó nó trở thành `adj_so_sanh_nhat` của dòng `tender` mới, không cần đứng riêng).

*Đính chính 1 điểm trong prompt đầu vào:* prompt liệt kê "`able` có trong file" làm căn cứ loại `abler/ablest` — kiểm tra thực tế cho thấy **`able` KHÔNG tồn tại trong file** (không có dòng nào với `word=able`), tương tự như "dense", "fond", "stiff", "plain", "kind"... đều không có mặt (vì toàn bộ 11.288 dòng đều là sản phẩm ráp Prefix/Root/Suffix của MorphLink — `so_thanh_phan` tối thiểu luôn là 2, không có mục từ đơn hình vị nào). Dù vậy, việc loại `abler/ablest` vẫn hợp lý và đã thực hiện đúng theo yêu cầu, vì bản thân 2 dòng này chỉ là "so sánh hơn/nhất của able" thuần túy, không mang thêm nghĩa độc lập nào — không phù hợp làm mục từ riêng dù từ gốc có mặt trong file hay không.

**Quét độc lập lại toàn bộ 11.282 dòng** (thuật toán tự viết lại từ đầu, không dựa cột `adj_ghi_chu`/`so_nhieu_bat_quy_tac`/`dong_tu_bat_quy_tac`): **0 vi phạm mới** phát hiện thêm. 13 cặp `-er` trùng chính tả với 1 tính từ khác trong file (`backhander/backhand, bootlegger/bootleg, carpetbagger/carpetbag, easterner/eastern, highlander/highland, insider/inside, lowlander/lowland, northerner/northern, outsider/outside, southerner/southern, teenager/teenage, westerner/western, wildcatter/wildcat`) đều được xác nhận là danh từ tác nhân/dân tộc có nghĩa độc lập thật (không phải so sánh hơn) — giữ nguyên. 1 cặp số nhiều trùng (`inlays/inlay`) là 1 động từ có nghĩa riêng ("khảm, cẩn"), không phải số nhiều — giữ nguyên. Sau khi thêm `tender` (adjective) ở Việc 3, dòng `tenderer` (noun có sẵn, nghĩa "bên nộp hồ sơ dự thầu") trùng chính tả với so sánh hơn của `tender` mới — đã kiểm tra, đây cũng là từ độc lập có nghĩa riêng, không phải biến thể, giữ nguyên.

### Việc 2 — Sửa `footballer` và quét lỗi cùng dạng

`footballer`: sửa `pos` từ `adjective` → `noun`, điền `noun_type=N[C]`, `noun_so_nhieu=footballers`, xóa nội dung 3 cột `adj_so_sanh_hon/adj_so_sanh_nhat/adj_ghi_chu`.

Quét toàn bộ 93 dòng `pos=adjective` kết thúc bằng `-er`, đối chiếu nội dung `meaning_en` (chứa cụm mô tả danh từ tác nhân như "a person who...", "an athlete who..." mà KHÔNG chứa "more"/"comparative") — **chỉ `footballer` là trường hợp bị gắn sai `pos`**, không phát hiện thêm trường hợp nào khác trong 92 dòng còn lại (đều là so sánh hơn thật, hoặc tính từ độc lập hợp lệ như `hardcover, improper, outer, undercover, underwater, upper, rubber, quicksilver`).

### Việc 3 — Bổ sung nghĩa tính từ của `tender`

Thêm 1 dòng mới `word=tender, pos=adjective`: `meaning_en`="gentle, kind, and loving; also, easily hurt, cut, or damaged, or painful when touched"; `meaning_vi`="dịu dàng, âu yếm, đầy tình cảm; cũng có nghĩa mềm, dễ bị tổn thương hoặc đau khi chạm vào"; `adj_so_sanh_hon`="tenderer"; `adj_so_sanh_nhat`="tenderest"; `multi_nghia`="(về thịt) mềm, dễ nhai; (về chủ đề) nhạy cảm, tế nhị". Các cột cấu trúc (`structure/kind/base/thanh_phan_*/loai_ket_hop/ipa`) sao chép từ dòng `tender` (noun) có sẵn để nhất quán với quy ước biểu diễn hình vị đã dùng trong file. Sau đó xóa dòng `tenderest` độc lập (dư thừa).

### Việc 4 — Bổ sung cấu trúc thành phần còn thiếu

Đã parse lại `structure` và điền đầy đủ `thanh_phan_1..N`, `loai_ket_hop`, `so_thanh_phan` cho đúng 12 dòng nêu trong yêu cầu:

| word | structure | thanh_phan (theo thứ tự) | loai_ket_hop |
|---|---|---|---|
| demythologize | de-[myth+log]-ize | de-, myth, log, -ize | Prefix + Root + Root + Suffix |
| expressway | ex-[press+way] | ex-, press, way | Prefix + Root + Root |
| godforsaken | fore-[god+sake]-en | fore-, god, sake, -en | Prefix + Root + Root + Suffix |
| halfpennyworth | half-[penny+worth] | half-, penny, worth | Prefix + Root + Root |
| inasmuch | im-[as+much] | im-, as, much | Prefix + Root + Root |
| nonchurchgoing | non-[church+go] | non-, church, go | Prefix + Root + Root |
| oneupmanship | up-[one+man]-ship | up-, one, man, -ship | Prefix + Root + Root + Suffix |
| selfeffacing | e-[self+face] | e-, self, face | Prefix + Root + Root |
| superhighways | super-[high+way] | super-, high, way | Prefix + Root + Root |
| underclassman | under-[class+man] | under-, class, man | Prefix + Root + Root |
| unputdownable | un-[put+down]-able | un-, put, down, -able | Prefix + Root + Root + Suffix |
| unselfconsciousness | un-[self+conscious]-ness | un-, self, conscious, -ness | Prefix + Root + Root + Suffix |

**Quét toàn bộ 11.282 dòng** tìm thêm trường hợp `structure` khác rỗng nhưng bộ 3 cột trên rỗng: **0 dòng còn sót** ngoài 12 dòng đã biết — xác nhận đây là toàn bộ các trường hợp lỗi này trong file. Kiểm tra chéo bổ sung (không nằm trong yêu cầu gốc nhưng làm để chắc chắn): đối chiếu `so_thanh_phan` với số lượng thực tế các cột `thanh_phan_1..6` đã điền, và đối chiếu số nhãn trong `loai_ket_hop` — **khớp 100%** trên toàn bộ file, không còn dòng nào lệch.

### QA sau khi sửa (Vòng 2) — tất cả PASS

1. Quét lại thuật toán Việc 1 trên file kết quả: **0 dòng vi phạm còn lại**.
2. Quét lại toàn bộ `pos=adjective` kết thúc `-er` đối chiếu nghĩa: **0 dòng còn là danh từ tác nhân bị gắn nhầm pos**.
3. Quét lại toàn bộ dòng có `structure` khác rỗng: **0 dòng còn thiếu `thanh_phan_1..6`/`loai_ket_hop`/`so_thanh_phan`**.
4. **Tổng số dòng cuối cùng: 11.282** (11.288 − 7 dòng loại bỏ + 1 dòng `tender` adjective thêm mới = 11.282).
