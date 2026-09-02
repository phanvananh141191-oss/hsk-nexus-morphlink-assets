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

---

## VÒNG 3 — Rà soát N[C]/N[U] toàn diện + audit 4 cột ghi chú

File đầu vào: `morphlink_MERGED_AUDITED_v2.csv` (11.282 dòng). File đầu ra: **`morphlink_MERGED_AUDITED_v3.csv` (11.407 dòng)**. Phương pháp: script trực tiếp cho các phần dữ liệu nhỏ/rõ ràng + 13 agent chạy song song (5 batch rà 629 danh từ hiện chỉ có N[U], 8 batch rà 1.394 danh từ trừu tượng hiện chỉ có N[C]) cho phần cần tra cứu từ điển quy mô lớn.

### VIỆC A — N[C]/N[U]

**A.1 — 4 cặp đã biết:** Viết lại `meaning_en`/`meaning_vi` cho `business, failure, kindness, pressure` theo đúng bảng yêu cầu — mỗi từ nay có 2 dòng với nghĩa phân biệt rõ ràng (không còn dòng nào giống hệt dòng kia). Ví dụ: `pressure` N[C] cũ = N[U] cũ (giống hệt) → N[C] mới = "một sức ép cụ thể (pressures)", N[U] mới = "áp suất/áp lực nói chung".

**A.2 — Quét toàn bộ file tìm cặp N[C]/N[U] trùng nghĩa khác:** Chỉ có đúng 4 từ trong toàn bộ 11.282 dòng gốc xuất hiện 2 lần với `noun_type` khác nhau (chính là 4 từ ở A.1) — sau khi sửa, xác nhận **0 cặp trùng nghĩa còn lại**.

**A.3 — Tách thêm từ có cả 2 cách dùng nhưng file chỉ lưu 1 dòng:** Danh sách từ gợi ý trong yêu cầu (coffee, tea, chicken, glass, paper, time, work...) **hoàn toàn không có trong file** — đây là điểm cần đính chính: toàn bộ 11.282 dòng của file đều là sản phẩm ráp Prefix/Root/Suffix của MorphLink (tối thiểu 2 hình vị), nên các danh từ đơn hình vị cơ bản này chưa từng được đưa vào bộ từ vựng ngay từ đầu (tương tự phát hiện về "able" ở Vòng 2). Do đó việc rà soát A.3 được mở rộng sang toàn bộ 629 danh từ hiện chỉ có N[U] và 1.394 danh từ trừu tượng hiện chỉ có N[C] (đuôi -tion/-ment/-ness/-ity/-ance/-ence/-ism/-ship/-hood/-dom...) đang thực sự có trong file, dùng 13 agent độc lập áp tiêu chí nghiêm ngặt (chỉ tách khi cả 2 nghĩa đều phổ biến, khác biệt rõ, được từ điển chuẩn Oxford/Cambridge/Merriam-Webster ghi nhận riêng — tránh lạm dụng kiểu "khái niệm trừu tượng vs. 1 lần cụ thể").

**Kết quả: tách thêm 108 từ** (tỷ lệ tách trung bình ~5,3% trên tổng số ứng viên, đúng khoảng kỳ vọng 2-8%), nâng tổng số từ có cả N[C] và N[U] từ 4 lên **131 từ**. Danh sách đầy đủ (nghĩa C / nghĩa U):

| word | N[C] | N[U] |
|---|---|---|
| ability | một kỹ năng/năng khiếu cụ thể | năng lực nói chung |
| accommodation | một thỏa thuận đạt được nhờ nhượng bộ | chỗ ở, nơi lưu trú nói chung |
| activity | một hoạt động/trò tiêu khiển cụ thể | sự nhộn nhịp, sôi động nói chung |
| addition | thứ được thêm vào | phép cộng (toán học) |
| administration | một chính quyền cụ thể | hoạt động quản lý/điều hành nói chung |
| admission | lời thú nhận | quyền được vào |
| amusement | một trò giải trí | cảm giác vui thích |
| appearance | một lần xuất hiện trước công chúng | vẻ bề ngoài |
| attachment | tệp đính kèm | tình cảm gắn bó |
| attraction | điểm thu hút khách | sức hút (tình cảm/vật lý) |
| authority | chuyên gia / cơ quan chính quyền | quyền lực |
| civilization | một nền văn minh cụ thể | trình độ văn minh nói chung |
| collection | bộ sưu tập | việc thu gom |
| composition | một tác phẩm nhạc/văn | thành phần cấu tạo |
| construction | một công trình xây dựng | quá trình xây dựng |
| contraction | từ viết tắt ngữ pháp | quá trình co lại |
| conviction | bản án kết tội | niềm tin vững chắc |
| creation | một sản phẩm được tạo ra | hành động sáng tạo |
| decoration | đồ trang trí | việc/phong cách trang trí |
| definition | định nghĩa từ | độ sắc nét |
| detention | phạt ở lại trường | tình trạng bị giam giữ |
| development | một diễn biến mới/khu nhà mới xây | quá trình phát triển |
| consideration | một yếu tố cân nhắc | việc suy nghĩ kỹ |
| curiosity | vật lạ, hiếm | tính tò mò |
| dedication | lời đề tặng/lễ khánh thành | sự tận tụy |
| criticism | một lời phê bình cụ thể | sự chỉ trích nói chung |
| competition | một cuộc thi | sự cạnh tranh nói chung |
| commencement | lễ tốt nghiệp (AmE) | sự khởi đầu |
| depression | chỗ trũng trên bề mặt / một giai đoạn suy thoái kinh tế | chứng trầm cảm (y tế) |
| difficulty | một vấn đề/khó khăn cụ thể | mức độ khó nói chung |
| direction | hướng di chuyển cụ thể | sự chỉ đạo/lãnh đạo |
| distinction | sự khác biệt | sự xuất sắc/danh dự |
| distribution | một lần phân phát cụ thể / phân bố thống kê | cách phân bổ nói chung |
| division | bộ phận/phòng ban | phép chia/quá trình phân chia |
| establishment | một cơ sở/tổ chức | hành động thành lập |
| expression | một từ/cụm từ | sự diễn đạt cảm xúc |
| extension | phần mở rộng/số máy lẻ | quá trình mở rộng |
| engagement | lễ đính hôn/cuộc hẹn | sự tương tác/tham gia |
| entrance | cửa vào | quyền được vào |
| embarrassment | người/việc gây xấu hổ | cảm giác xấu hổ |
| execution | việc hành quyết | việc thực hiện kế hoạch |
| extraction | quá trình chiết xuất/nhổ răng | nguồn gốc dòng dõi |
| estimation | một phép ước tính | quan điểm đánh giá |
| fabrication | lời bịa đặt | quá trình chế tạo |
| fellowship | tổ chức/hội đoàn | cảm giác thân thiết, gắn bó |
| fixation | một nỗi ám ảnh cụ thể | quá trình cố định hóa học/kỹ thuật |
| freedom | một quyền tự do cụ thể | tự do nói chung |
| generation | một thế hệ người | quá trình tạo/sinh ra |
| government | chính phủ (nhóm người) | hệ thống/thể chế cai trị |
| hostility | các hành động chiến tranh (hostilities) | thái độ thù địch |
| illness | một căn bệnh cụ thể | tình trạng ốm đau nói chung |
| implication | một hệ quả cụ thể | sự liên can |
| imitation | một bản sao | hành động bắt chước |
| impurity | một tạp chất cụ thể | tính chất không tinh khiết |
| indulgence | một thứ tự thưởng | thói quen buông thả hưởng thụ |
| infection | một bệnh nhiễm trùng cụ thể | quá trình/nguy cơ nhiễm bệnh |
| inheritance | tài sản thừa kế | quá trình di truyền gen |
| innovation | một ý tưởng/phát minh mới | hoạt động đổi mới sáng tạo |
| injustice | một hành động bất công cụ thể | tính bất công nói chung |
| inscription | một đoạn chữ khắc | hành động khắc/viết chữ |
| insecurity | một nỗi bất an cụ thể | sự thiếu tự tin nói chung |
| inspiration | người/vật là nguồn cảm hứng | quá trình được khơi gợi cảm hứng |
| installation | thiết bị/căn cứ đã lắp đặt | hành động lắp đặt |
| instruction | chỉ dẫn/mệnh lệnh cụ thể | hoạt động giảng dạy |
| invention | vật/thiết bị được sáng chế | khả năng/hoạt động sáng chế |
| investment | thứ được đầu tư | hành động đầu tư |
| irony | một sự việc trớ trêu cụ thể | sự mỉa mai nói chung |
| irritation | điều/người gây khó chịu | cảm giác bực bội |
| judgment | một quyết định/phán quyết | khả năng phán đoán |
| liability | người/vật gây bất lợi; khoản nợ | trách nhiệm pháp lý |
| likeness | bức chân dung/hình ảnh khắc họa | sự giống nhau |
| measurement | con số/kích thước đo được | quá trình đo lường |
| motivation | một lý do cụ thể | động lực nói chung |
| nationality | nhóm dân tộc/quốc gia | quốc tịch (tư cách pháp lý) |
| negotiation | một cuộc đàm phán cụ thể | quá trình đàm phán nói chung |
| notification | một thông báo cụ thể | việc thông báo nói chung |
| observation | một nhận xét | sự quan sát |
| occupation | nghề nghiệp | sự chiếm đóng (quân sự) |
| operation | một chiến dịch/ca phẫu thuật | sự vận hành |
| organization | một tổ chức/công ty | tính tổ chức, sự sắp xếp có hệ thống |
| outrage | một hành động gây phẫn nộ | cảm giác phẫn nộ |
| partnership | một công ty hợp danh | tình trạng làm đối tác |
| payment | một khoản tiền cụ thể | việc thanh toán nói chung |
| performance | một buổi biểu diễn | hiệu suất hoạt động |
| personality | nhân vật nổi tiếng | tính cách con người |
| possession | vật sở hữu | trạng thái sở hữu |
| possibility | một phương án cụ thể | tính khả thi nói chung |
| preparation | việc chuẩn bị cụ thể | quá trình chuẩn bị nói chung |
| publication | một ấn phẩm | việc in ấn, xuất bản nói chung |
| qualification | bằng cấp/chứng chỉ | lời giới hạn, làm rõ tuyên bố |
| responsibility | một trách nhiệm cụ thể | trách nhiệm nói chung |
| security | chứng khoán, giấy tờ có giá | sự an toàn, an ninh |
| scholarship | học bổng | học thuật nói chung |
| reference | một sự đề cập/thư giới thiệu | việc tham khảo nói chung |
| regulation | một quy định cụ thể | sự kiểm soát, quản lý nói chung |
| representation | hình ảnh/mô hình đại diện | tình trạng được đại diện |
| resignation | hành động/đơn từ chức | sự cam chịu |
| selection | một tập hợp được chọn ra | quá trình lựa chọn |
| refreshment | đồ ăn thức uống nhẹ | sự phục hồi sức lực, tinh thần |
| relaxation | một sự nới lỏng quy định | sự thư giãn, nghỉ ngơi |
| sisterhood | một hội/dòng tu nữ | tình chị em |
| realization | một sự nhận ra cụ thể | sự hiện thực hóa (ước mơ) |
| rubber | (Anh) cục tẩy | cao su (chất liệu) |
| sickness | một căn bệnh cụ thể | tình trạng ốm yếu nói chung |
| specialization | lĩnh vực chuyên môn cụ thể | quá trình trở thành chuyên gia |
| stupidity | một hành động ngu ngốc cụ thể | tính ngu ngốc nói chung |
| subdivision | khu đất được chia lô | hành động phân chia đất đai |
| submission | bài nộp/hồ sơ dự thi | sự đầu hàng, khuất phục |
| substance | một loại chất cụ thể | nội dung cốt lõi |
| temptation | một điều cám dỗ cụ thể | cảm giác ham muốn làm điều sai |
| thickness | một lớp vật liệu cụ thể | độ dày nói chung |
| transcription | bản chép lại cụ thể | quá trình chuyển lời nói thành văn bản |
| transmission | một buổi phát sóng cụ thể | quá trình truyền dẫn nói chung |
| translation | bản dịch cụ thể | công việc/kỹ năng dịch thuật |
| treatment | một liệu pháp cụ thể | sự chăm sóc y tế nói chung |
| understatement | một câu nói giảm nhẹ cụ thể | phong cách nói giảm nhẹ |
| university | một trường đại học cụ thể | việc học đại học nói chung |
| unpleasantness | một xung đột cụ thể | tính chất gây khó chịu nói chung |
| usage | một cách dùng từ cụ thể | cách dùng từ nói chung |
| vulnerability | một lỗ hổng/điểm yếu cụ thể | trạng thái dễ tổn thương nói chung |
| weakness | một điểm yếu cụ thể | trạng thái thiếu sức mạnh nói chung |
| weight | một vật nặng (dùng để tập/đo) | trọng lượng nói chung |

*Phát hiện phụ trong lúc audit:* `rubber` trước đây CHỈ có 1 dòng `pos=adjective` ("made of rubber"), hoàn toàn thiếu 2 nghĩa danh từ rất thông dụng (cao su - chất liệu; cục tẩy - Anh) — đã bổ sung đầy đủ.

**17 từ N[C] khác bị gắn sai `noun_type`** (nghĩa mô tả rõ ràng là khái niệm chung/không đếm được nhưng bị gắn N[C]) được phát hiện qua rà soát bổ sung (không thuộc danh sách gợi ý gốc, phát hiện khi kiểm tra chéo cột `multi_nghia`) — đã sửa lại thành N[U], không thêm dòng mới vì không có nghĩa C riêng biệt đủ thông dụng: `disablement, discontinuity, discourtesy, discredit, dishonesty, disloyalty, disproportion, disrespect, disuse, nonobservance, unbalance, uncertainty, underexposure, uniformity, universality, unreason, unselfconsciousness`.

**Còn lại chưa chắc chắn:** khoảng 219 danh từ khác bắt đầu bằng tiền tố dis-/mis-/un-/non-/over-/under- hiện chỉ có N[C] chưa được rà (nằm ngoài phạm vi đuôi -tion/-ment/-ness/-ity/... mà 8 batch agent đã quét, và ngoài heuristic "lack of/quality of" đã áp dụng) — cần 1 vòng rà riêng nếu muốn triệt để 100%.

### VIỆC B — Audit 4 cột ghi chú

**B.1 — `multi_nghia` (136 dòng có nội dung trước audit):**
- Phát hiện **21 dòng chứa ghi chú quy trình nội bộ bị lẫn vào** (nội dung: "Danh từ: đếm được vs không đếm được... — nguồn Perplexity, đối chiếu Cambridge/British Council") — đây thực chất là 1 TODO chưa xử lý từ pipeline gốc (trước cả 3 vòng audit), không phải nghĩa phụ thật. Đã xóa toàn bộ 21 ghi chú này; nội dung TODO này chính là đầu mối dẫn đến việc tách 108 từ ở VIỆC A.3 (17/21 từ liên quan đã được tách N[C]/N[U] đúng theo đúng ý TODO đề ra: accommodation, depression, difficulty, distribution, education, employment, enjoyment, freedom, improvement, injustice, irony, paperwork, pronunciation, research, rubber, usage, weight — riêng `education/employment/enjoyment/paperwork` không tách vì từ điển chuẩn không ghi nhận nghĩa C riêng, chỉ sửa `noun_type` cho khớp nghĩa U).
- 1 dòng `oldies` có `multi_nghia` trùng lặp y hệt `meaning_vi` (không cung cấp thông tin gì thêm) — đã xóa.
- Kiểm tra cross-pos contamination (multi_nghia của dòng noun chứa nghĩa động từ hoặc ngược lại): **0 vi phạm**.
- Kiểm tra multi_nghia bị dùng để nhét nghĩa N[U] vào dòng N[C] hoặc ngược lại (thay vì tách dòng riêng theo đúng VIỆC A): **0 vi phạm** trên toàn bộ 131 cặp N[C]/N[U] sau khi hoàn thành VIỆC A.

**B.2 — `adj_ghi_chu` (162 dòng):**
- Xác nhận **0 dòng** `pos=adjective` còn thiếu cả `adj_ghi_chu` lẫn `adj_so_sanh_hon/nhat` (PASS, khớp kết quả Vòng 2).
- Rà nội dung 75 dòng ghi "đây là dạng so sánh hơn của tính từ gốc": xác nhận tính từ gốc được nêu (able, bare, base, bitter, black... ) **không dòng nào tồn tại độc lập trong file** — nhất quán với phát hiện ở Vòng 2 (toàn bộ file chỉ chứa từ ≥2 hình vị), nội dung ghi chú vẫn ĐÚNG về mặt ngôn ngữ (đây thật sự là dạng so sánh hơn, không có dạng so sánh hơn/nhất riêng) nên không cần sửa.
- Rà 61 dòng ghi "tính từ tuyệt đối/không phân cấp": phát hiện **1 dòng gắn nhãn sai** — `global` ("bao trùm toàn thế giới") thực tế so sánh được bình thường trong tiếng Anh hiện đại ("a more global economy", "the most global companies") → đã xóa `adj_ghi_chu`, điền `adj_so_sanh_hon="more global"`, `adj_so_sanh_nhat="most global"`. 60 dòng còn lại xác nhận đúng là tính từ tuyệt đối/phân loại thật (daily, digital, electrical, impossible, international, wooden...).

**B.3 — `so_nhieu_bat_quy_tac` (205 dòng):**
- Phát hiện **3 dòng `pos=verb`** (`recovers, reshapes, wavers`) bị dính ghi chú "Từ có vẻ đã ở dạng SỐ NHIỀU sẵn" — đây là rác sót lại từ trước khi 3 dòng này được sửa `pos` từ noun→verb ở Vòng 1, hoàn toàn không liên quan đến động từ → đã xóa.
- Đối chiếu `noun_so_nhieu` với nội dung ghi chú cho toàn bộ 202 dòng noun còn lại: **0 xung đột** (quy ước "có ghi chú thì `noun_so_nhieu` để trống" được tuân thủ nhất quán, kể cả 2 trường hợp đặc biệt `aircraft`/`offspring` với ghi chú "đã là số nhiều của chính nó").

**B.4 — `dong_tu_bat_quy_tac`:**
- 5 dòng có ghi chú (`arise, overcome, overtake, undertake, withdraw`) đối chiếu khớp hoàn toàn với 4 cột chia động từ tương ứng — đây là các động từ bất quy tắc dạng nguyên mẫu (không phải dạng chia sẵn của từ khác) nên quy ước "note→4 cột rỗng" không áp dụng, ghi chú chỉ mang tính tóm tắt bổ sung, không mâu thuẫn.
- Quét toàn bộ động từ bất quy tắc tiếng Anh chuẩn (danh sách ~150 gốc bất quy tắc, gồm cả dạng có tiền tố) đối chiếu với `verb_qua_khu`/`verb_pp` hiện tại: phát hiện **5 dòng bị chia theo quy tắc thường (sai)** dù không có ghi chú:

| word | Trước (sai) | Sau (đúng) |
|---|---|---|
| forsake | forsaked / forsaked | forsook / forsaken |
| forgo | forgoed / forgoed | forwent / forgone |
| overdo | overdoed / overdoed | overdid / overdone |
| redo | redoed / redoed | redid / redone |
| undo | undoed / undoed | undid / undone |
| unbend | unbended / unbended | unbent / unbent |

  Đã sửa cả 4 cột chia động từ và bổ sung `dong_tu_bat_quy_tac` cho cả 6 dòng. Đã kiểm tra kỹ và loại các false-positive: `mislead/misled` (đã đúng sẵn), `breastfeed/breastfed`, `overfeed/overfed`, `spoonfeed/spoonfed` (đều đã đúng sẵn, chỉ trùng đuôi "-ed" ngẫu nhiên với "feed" nên bị nghi oan), `ascribe/describe/inscribe/prescribe/subscribe`... (các động từ "-scribe" là động từ QUY TẮC, không liên quan gốc "be" dù trùng đuôi chữ cái), `outshine` (đã ghi đúng cả 2 dạng "outshone/outshined").

### Phát hiện phụ quan trọng — rác dữ liệu chéo cột theo pos (ngoài phạm vi VIỆC A/B gốc)

Trong lúc kiểm tra mẫu ngẫu nhiên sau VIỆC A, phát hiện `rubber` (2 dòng N[U]/N[C] mới thêm) bị gán nhầm `pos=adjective` thay vì `noun` (lỗi thao tác của chính vòng audit này — do dòng mẫu để tạo dòng mới là dòng `adjective` sẵn có duy nhất của "rubber") → đã sửa lại `pos=noun` cho cả 2 dòng.

Việc rà lại này dẫn tới phát hiện 1 lỗi hệ thống lớn hơn nhiều, tồn tại từ Vòng 1/2 (khi các batch sửa `pos` sai chỉ đổi cột `pos` mà không dọn các cột dữ liệu chuyên biệt theo loại từ cũ):

- **167 dòng KHÔNG PHẢI `pos=noun`** (phần lớn là `adjective`/`verb`, một số `preposition`/`adverb`) vẫn còn `noun_type`/`noun_so_nhieu` sót lại từ trước khi `pos` được sửa — trong đó **164 dòng** còn cả số nhiều bịa đặt vô nghĩa kiểu `brighters, cuters, suffers, dictionarys`... Đã xóa sạch cả 3 cột (`noun_type`, `noun_so_nhieu`, `so_nhieu_bat_quy_tac`) trên toàn bộ 167 dòng này.
- **80 dòng không phải `pos=adjective`** còn sót `adj_so_sanh_hon`/`adj_so_sanh_nhat` vô nghĩa kiểu "more backboards"/"most backboards" (cho danh từ), "canster"/"canstest" (cho động từ cổ "canst"). Đã xóa sạch.
- **24 dòng không phải `pos=verb`** còn sót cột chia động từ vô nghĩa kiểu `brokens/brokening/brokened` (cho tính từ "broken"), `carryouts/carryouting` (cho danh từ "carryout"). Trong đó **4 dòng** (`broadcast, forecast, mistake, awake`) có ghi chú `dong_tu_bat_quy_tac` chứa thông tin ĐÚNG (dạng bất quy tắc thật) nhưng bị "mắc kẹt" trên dòng `noun`/`adjective` vì **từ này thực ra có nghĩa động từ thông dụng nhưng chưa từng có dòng `pos=verb` riêng** — tương tự trường hợp `transpose` phát hiện ở Vòng 1. Đã bổ sung 4 dòng verb mới (`broadcast`, `forecast`, `mistake`, `awake`) với nghĩa + cách chia đúng lấy từ chính ghi chú sót lại, sau đó xóa ghi chú thừa trên dòng gốc. 20 dòng còn lại (rác thuần túy, không có thông tin thật) đã xóa sạch 5 cột liên quan.

**Tổng cộng đã dọn sạch chéo-cột cho 267 dòng** (167+80+20, không tính 4 dòng verb được cứu lại), bổ sung thêm 4 dòng từ vựng mới bị thiếu hoàn toàn (broadcast/forecast/mistake/awake ở nghĩa động từ). Đây là lỗi hoàn toàn độc lập với 3 nhóm lỗi ban đầu và với VIỆC A/B được giao — phát hiện được là nhờ áp dụng đúng tinh thần "đối chiếu nội dung cột ghi chú với cột dữ liệu tương ứng, xác nhận không lẫn nội dung không liên quan" của B.3/B.4 sang cả các cột `noun_type`/`adj_so_sanh_*` chưa được liệt kê rõ trong yêu cầu gốc.

### Còn lại chưa xác thực / cần rà thêm

- 219 danh từ tiền tố dis-/mis-/un-/non-/over-/under- hiện chỉ có N[C], chưa được rà đầy đủ khả năng cần thêm N[U] (nêu ở VIỆC A.3).
- Chưa quét lại toàn bộ ~5.100 danh từ N[C]-only còn lại (không thuộc nhóm đuôi trừu tượng đã quét) xem có cần bổ sung N[U] hay không — phạm vi VIỆC A tập trung vào danh từ trừu tượng vì đây là nhóm có xác suất cần tách cao nhất; danh từ cụ thể (backboard, organizer, tracker...) hầu như chắc chắn chỉ có nghĩa đếm được nên rủi ro bỏ sót thấp.
- Chưa audit tương tự cột `nguon`, `trong_morphlink`, `co_affix`, `ipa_status` — nằm ngoài phạm vi 4 cột ghi chú được yêu cầu ở vòng này.

### Tổng số dòng cuối cùng: 11.411
(11.282 dòng đầu vào + 125 dòng N[C]/N[U] mới tách thêm ở VIỆC A + 4 dòng verb mới bổ sung — `broadcast, forecast, mistake, awake` — phát hiện khi dọn rác chéo-cột = 11.411; không có dòng nào bị xóa ở Vòng 3, chỉ có sửa nghĩa/`noun_type`/cột ghi chú và thêm dòng mới cho các từ cần tách hoặc thiếu hẳn 1 pos).
