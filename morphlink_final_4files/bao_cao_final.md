# Báo cáo cuối — Bộ 4 file MorphLink (Từ tổng + Root + Prefix + Suffix)

## Ghi chú về nguồn dữ liệu (khác với yêu cầu gốc)

Yêu cầu gốc dựa vào `morphlink_grand_total_WITH_BIENTHE.csv` (16.823 dòng) làm nguồn chính cho Root/Prefix/Suffix, nhưng file này **không được cung cấp** — người dùng xác nhận "không cần quan tâm". Do đó:

- **Nguồn thực tế sử dụng**: `morphlink_MERGED_AUDITED_v3.csv` (11.411 dòng, đã audit 3 vòng trước) + `morphlink_compound_formation_FINAL3.csv` (2.626 dòng, được đính kèm giữa chừng).
- **ROOT/PREFIX/SUFFIX được xây dựng bằng cách trích xuất trực tiếp từ cột `thanh_phan_1..6`/`loai_ket_hop` của chính 11.411 từ trong v3** (không có danh sách Root/Prefix/Suffix "chuẩn" độc lập nào khác) — tổng hợp được 93 tiền tố, 126 hậu tố, 2.137 gốc từ duy nhất đang thực sự được dùng.
- Nghĩa/chức năng của từng gốc/tiền tố/hậu tố **do Claude biên soạn dựa trên kiến thức hình thái học và từ nguyên tiếng Anh**, đối chiếu với các từ ví dụ THẬT trích từ dữ liệu (không có nguồn định nghĩa affix nào khác để "trích xuất" nghĩa đen). Đây là điểm khác biệt quan trọng cần lưu ý so với yêu cầu gốc.
- Do đó, quy tắc A.1 (phân biệt Root vs Word dựa vào `structure=` có/không trong `ghi_chu`) **không áp dụng được** vì dữ liệu gốc grand_total không có — mọi dòng trong v3 đều đã có `structure` đầy đủ (không có "Word nguyên khối" nào tồn tại riêng biệt trong tập dữ liệu này để tách).

---

## 1. Số dòng mỗi file

| File | Số dòng | Số cột |
|---|---|---|
| `morphlink_TU_TONG.csv` | **11.752** | 20 |
| `morphlink_ROOT.csv` | **2.137** | 7 |
| `morphlink_PREFIX.csv` | **94** | 8 |
| `morphlink_SUFFIX.csv` | **126** | 8 |

`morphlink_TU_TONG.csv` = 11.411 dòng từ `morphlink_MERGED_AUDITED_v3.csv` (đã audit 3 vòng) + 343 từ ghép mới từ `morphlink_compound_formation_FINAL3.csv` (không trùng với v3) − 2 dòng loại bỏ (`radii`, `foreseen`) + 1 dòng bổ sung (`forbear` verb) − 1 dòng loại bỏ (`forbore`, thay bằng `forbear`) = 11.752, xem mục 3.

---

## 2. Việc A — Kiểm tra 345 từ ghép mới từ `compound_formation_FINAL3.csv`

File nguồn có 2.626 dòng; **2.283 dòng đã trùng với v3** (giữ nguyên bản v3 đã audit, không dùng bản chưa audit của file này). **345 dòng hoàn toàn mới** được rà soát độc lập theo đúng bộ quy tắc đã dùng cho toàn bộ dự án:

- **333/345 dòng đã đúng sẵn** (định nghĩa từ điển thật, không công thức ghép hình vị, không tên riêng, không nội dung nhạy cảm).
- **9 dòng sửa nghĩa/pos**: `chemosynthesis` (dịch sai), `large-scale`/`open-source`/`world-class` (pos sai — gán noun/adverb thay vì adjective), `telemarketing` (pos sai — gán adjective thay vì noun), `outspoken` (định nghĩa lặp vòng tự tham chiếu), `freekick` (định nghĩa không chính xác), `pickman` (định nghĩa đoán chung chung, sửa thành nghĩa thuật ngữ khai thác mỏ thật), `silverfish` (dịch nhầm sang tên 1 loài cá khác).
- **2 dòng loại bỏ** (thuật ngữ phân biệt chủng tộc, không phù hợp từ điển học thuật):
  - `paleface` — thuật ngữ miệt thị/khuôn mẫu chỉ người da trắng
  - `redskin` — ethnic slur nặng nề đối với người bản địa Bắc Mỹ
  (2 từ này trùng với 2 từ đã bị loại khỏi v3 từ Vòng 1 của dự án — xác nhận nhất quán).

343 dòng còn lại (345 − 2 loại) đã được đưa vào `morphlink_TU_TONG.csv` với đầy đủ biến thể ngữ pháp tự sinh (số nhiều, chia động từ, so sánh — áp dụng bảng bất quy tắc + quy tắc CVC/y→i/gấp đôi phụ âm theo đúng A.4), và điều chỉnh `noun_type=N[U]` cho các danh từ dạng "-ics/-ology/-onomy" (aerodynamics, aeronautics, archaeology...) để tránh sinh số nhiều vô nghĩa.

---

## 3. Việc B — Phát hiện phụ trong lúc build TU_TONG (ngoài phạm vi yêu cầu, nhưng cần sửa)

Khi build `morphlink_TU_TONG.csv`, phát hiện **6 dòng `pos=unknown`** còn sót từ dữ liệu gốc, mang định nghĩa kiểu từ điển Webster 1913 cổ (`"p. p. of Fly"`, `"imp. of Forbear"`, `"pl. of Radius"`...) — đây chính là **biến thể ngữ pháp bị tách thành headword riêng** (vi phạm quy tắc A.8/A.4) chưa từng được quét tới ở 3 vòng audit trước vì `pos=unknown` nằm ngoài phạm vi các script rà theo `pos=noun/verb/adjective`:

| word | Vấn đề | Xử lý |
|---|---|---|
| `radii` | Số nhiều bất quy tắc của `radius` (đã có trong file) | **Loại bỏ**; bổ sung `radius.noun_so_nhieu = "radii"` (trước đó bị gán nhầm ghi chú "có vẻ đã ở dạng số nhiều sẵn" — sai, vì "radius" không phải số nhiều) |
| `flown` | pp của "fly" (không có trong file) | Sửa `pos=adjective`, viết lại nghĩa thật (không có "fly" động từ để trỏ về) |
| `forbore` | quá khứ của "forbear" (nghĩa "nhịn", verb — chỉ có noun "forbear"=tổ tiên trong file, chưa có verb) | **Sửa lại**: bổ sung `forbear` (verb, "kiềm chế, nhịn không làm điều gì") làm headword riêng với đủ 4 dạng chia (forbears/forbearing/forbore/forborne), **loại bỏ** `forbore` (nay dư thừa) |
| `foreseen` | pp của "foresee" (**đã có sẵn trong file**, `verb_pp` của "foresee" vốn đã là "foreseen") | **Loại bỏ** — đây là bản sao thừa của thông tin đã có, đúng loại lỗi "biến thể ngữ pháp làm headword riêng" mà dự án đã loại bỏ nhiều lần (tương tự case "arose" ở Vòng 2) |
| `shown` | pp của "show" (không có trong file) | Sửa `pos=adjective`, viết lại nghĩa thật |
| `spilt` | quá khứ/pp của "spill" (không có trong file) | Sửa `pos=adjective` (cách dùng thành ngữ "spilt milk"), viết lại nghĩa thật |

*Sửa lần 2 (sau khi người dùng phát hiện `forbore` bất thường):* ban đầu `forbore` và `foreseen` được giữ lại với định nghĩa kiểu "dạng quá khứ của X" — đây vẫn là cách "biến thể làm headword riêng", chỉ khác là có viết lại câu cho tự nhiên hơn, không nhất quán với cách xử lý các case khác (vd `arose` đã bị xóa hẳn ở Vòng 2 khi "arise" đã có sẵn). Đã sửa lại: `foreseen` bị xóa hẳn (vì "foresee" đã có sẵn), còn `forbore` được thay bằng cách bổ sung đúng headword còn thiếu (`forbear` verb) rồi xóa `forbore`.

Sau khi sửa: **0 dòng `pos=unknown`** còn lại, **0 dòng biến thể-làm-headword** còn sót trong `morphlink_TU_TONG.csv` (đã quét lại toàn bộ file bằng thuật toán độc lập sau khi sửa).

---

## 4. Số dòng N[C]/N[U] có 2 nghĩa khác nhau

`morphlink_TU_TONG.csv` có **128 từ** xuất hiện đúng 2 lần dưới `pos=noun` với `noun_type` khác nhau (N[C] và N[U]) — toàn bộ đã được xác nhận **có nghĩa khác biệt rõ ràng, không dòng nào trùng nghĩa** (kết quả từ Vòng 3 của quá trình audit trước, giữ nguyên khi build file này). Ví dụ: `ability` (N[C]="một kỹ năng cụ thể" / N[U]="năng lực nói chung"), `depression` (N[C]="chỗ trũng/suy thoái kinh tế" / N[U]="chứng trầm cảm"), `weight` (N[C]="một vật nặng dùng để tập/đo" / N[U]="trọng lượng nói chung").

---

## 5. Thống kê chức năng Prefix/Suffix

| | Tổng số | Có chức năng rõ rệt (≥1 pos áp đảo) | "Không có pos áp đảo rõ rệt" |
|---|---|---|---|
| Prefix | 94 | 76 (80,9%) | 18 (19,1%) |
| Suffix | 126 | 111 (88,1%) | 15 (11,9%) |

"Không có pos áp đảo rõ rệt" xảy ra khi 1 affix tạo ra nhiều pos gần như đều nhau (không có pos nào ≥15% chênh lệch rõ so với pos đứng thứ 2) — ví dụ `-y` (tạo cả noun/adjective/verb gần như ngang nhau), `tri-` (tạo cả noun và adjective).

**Xử lý đặc biệt tiền tố `im-`/`in-`/`a-`** (theo đúng lưu ý A.6 trong yêu cầu): dữ liệu gốc gộp chung mọi biến thể đồng hóa dưới 2 nhãn `"im-"` (284 từ) và `"a-"` (122 từ) — đã dùng 2 agent riêng đọc và phân loại lại theo NGHĨA THẬT (không chỉ chính tả) của từng từ:
- Nhãn `"im-"`/`"in-"`/`"ir-"`/`"il-"` (421 từ gộp) → tách thành **2 tiền tố riêng biệt về nghĩa**: `in-/im-/il-/ir- (phủ định)` = 280 từ, `in-/im- (vào trong)` = 128 từ, 13 từ "khác" (không rõ nghĩa, ví dụ artifact tách hình vị sai) bị loại khỏi cả 2 nhóm.
- Nhãn `"a-"` (120 từ) → tách thành **3 tiền tố**: `ad-` (đồng hóa Latin "hướng tới") = 92 từ, `a- (phủ định, gốc Hy Lạp)` = 11 từ, `a- (trạng thái, gốc Anh cổ)` = 17 từ.

---

## 6. Từ bị loại (tên riêng / biến thể / nhạy cảm)

Trong phạm vi công việc của lần build này (345 từ ghép mới), **2 từ bị loại** (đã liệt kê ở mục 2: `paleface`, `redskin`). Không phát hiện thêm tên riêng hay biến thể ngữ pháp nào khác trong 345 từ này (đã quét độc lập bằng thuật toán, xem mục 2 và kiểm tra biến thể ngữ pháp ở cuối file — 0 vi phạm).

11.411 dòng còn lại kế thừa nguyên trạng kết quả đã audit qua 3 vòng trước đó (audit_report.md), đã loại tổng cộng 47+ dòng tên riêng/biến thể/nhạy cảm trong các vòng trước — không audit lại trong lần build này (ngoài phạm vi yêu cầu).

**Phát hiện phụ mới trong lần build này**: 1 dòng `radii` bị loại vì là số nhiều bất quy tắc của `radius` đã có sẵn (xem mục 3) — biến thể ngữ pháp bị tách headword riêng, sót lại từ trước do nằm dưới `pos=unknown` (ngoài phạm vi quét trước đây).

---

## 7. Root — độ tin cậy

- **2.137 gốc từ** được định nghĩa, trích xuất từ toàn bộ 11.411 từ trong v3 (không có nguồn Root "chuẩn" riêng biệt nào khác để đối chiếu — xem ghi chú đầu báo cáo).
- **2.110 gốc tự do** (free root — bản thân là 1 từ tiếng Anh độc lập, nghĩa = nghĩa từ điển thông thường) / **27 gốc ràng buộc** (bound root — hình vị Latin/Hy Lạp không tồn tại độc lập, vd `spec, duc, ject, path, log, phon...`).
- **21 gốc** được gắn `bien_the` (thuộc 1 họ biến thể chính tả đã biết, vd `pound` thuộc họ `pos/pon/pound`, `verse` thuộc họ `vert/vers`).
- **11/2.137 gốc (0,5%) được đánh dấu "chưa chắc chắn - cần rà tay"**: `monster, bore, may, bat, rid, bit, spain, for, discours, hap, a` — đa số là trường hợp 1 chuỗi ký tự trùng ngẫu nhiên giữa 2 nghĩa gốc khác nhau (ví dụ gốc "monster" thực chất các từ ví dụ đều thuộc gốc Latin "monstr-" nghĩa "chỉ ra", không liên quan nghĩa "quái vật"; gốc "for" trong "forties/fortieth" thực chất là biến thể của "four", không phải giới từ "for") — cần người biết tiếng Anh rà lại thủ công.

---

## 8. Mẫu 30 dòng ngẫu nhiên mỗi file (đã in ra terminal khi build, tóm tắt lại đại diện)

### `morphlink_TU_TONG.csv` (trích 8/30)
```
detector (noun, N[C]) | any device that receives a signal or stimulus... | thiết bị nhận tín hiệu...
birthmark (noun, N[C]) | a blemish on the skin formed before birth | một tì vết trên da hình thành trước khi sinh
promotion (noun, N[C]) | advancement to a higher position; a special price reduction | sự thăng chức; chương trình khuyến mãi
protestant (adjective) | relating to Christian churches that separated from Rome | thuộc đạo Tin Lành
handler (noun, N[C]) | (sports) someone in charge of training an athlete | (thể thao) người huấn luyện
preschool (noun, N[C]) | an educational institution for children too young for elementary school | trường mầm non
alcoholic (adjective) | connected with or containing alcohol | liên quan đến hoặc chứa cồn
arrowhead (noun, N[C]) | the pointed head or striking tip of an arrow | đầu nhọn mũi tên
```

### `morphlink_ROOT.csv` (trích 8/30)
```
elephant (noun) | a very large mammal with a trunk and tusks | ràng buộc: không
premier (adjective) | first in importance, order, or position | ràng buộc: không
guitar (noun) | a stringed musical instrument | ràng buộc: không
tender (adjective) | gentle and kind; easily hurt or bruised | ràng buộc: không
enterprise (noun) | a business organization; a bold undertaking | ràng buộc: không
might (noun) | great power or strength | ràng buộc: không
proud (adjective) | feeling deep pleasure from one's achievements | ràng buộc: không
wide (adjective) | measuring a large distance from side to side | ràng buộc: không
```

### `morphlink_PREFIX.csv` (trích 8/15)
```
under-  | ở dưới, bên dưới, không đủ mức | tan_suat=73  | Tạo danh từ ~45%
en-     | đưa vào, làm cho, khiến trở nên | tan_suat=85  | Tạo động từ ~53%
anti-   | chống lại, đối lập, ngăn ngừa   | tan_suat=17  | Tạo tính từ ~47%
mega-   | lớn, to; một triệu              | tan_suat=4   | Tạo danh từ 75%
in-/im-/il-/ir- (phủ định) | không, trái với | tan_suat=280 | Tạo tính từ đa số
tri-    | ba, có ba phần                  | tan_suat=4   | Không có pos áp đảo rõ rệt
epi-    | trên, bên ngoài, thêm vào       | tan_suat=6   | Tạo danh từ 50%
syn-    | cùng, cùng nhau, đồng thời      | tan_suat=4   | Tạo tính từ 50%
```

### `morphlink_SUFFIX.csv` (trích 8/15)
```
-al   | liên quan đến, thuộc về            | tan_suat=581 | Tạo tính từ 54%
-ize  | làm cho, biến thành, coi như       | tan_suat=162 | Tạo động từ 54%
-ment | trạng thái, hành động, kết quả     | tan_suat=208 | Tạo danh từ 96%
-or   | chỉ tác nhân/công cụ               | tan_suat=126 | Tạo danh từ 89%
-ward | chỉ hướng "về phía"                | tan_suat=32  | Tạo trạng từ 81%
-ish  | hơi, có tính chất của              | tan_suat=95  | Tạo tính từ 58%
-ee   | chỉ người là đối tượng/người nhận  | tan_suat=31  | Tạo danh từ 97%
-y    | có tính chất của, đầy, phủ...      | tan_suat=677 | Không có pos áp đảo rõ rệt
```

(Xem file CSV đầy đủ để có toàn bộ dữ liệu; bảng trên chỉ trích một phần để minh họa.)

---

## 9. Kiểm tra tính toàn vẹn cuối cùng

| Kiểm tra | Kết quả |
|---|---|
| `morphlink_TU_TONG.csv`: `tu/pos/nghia_en/nghia_vi` rỗng | 0 |
| `pos=noun` thiếu `noun_type` | 0 |
| `N[C]` thiếu `noun_so_nhieu` (không ghi chú bất quy tắc) | 0 |
| `pos=verb` chia thiếu 1-2/4 cột | 0 |
| `pos=adjective` thiếu cả so sánh lẫn ghi chú | 0 |
| Trùng `(tu, pos, noun_type)` | 0 |
| Biến thể ngữ pháp còn sót trong 343 từ mới (quét độc lập) | 0 |
| `morphlink_ROOT.csv` / `PREFIX.csv` / `SUFFIX.csv`: trùng khóa chính | 0 |
