# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Đỗ Ngọc Phi | 2A202602531 | Toàn bộ (cá nhân) |

- Mô hình: Azure OpenAI, deployment `gpt-6-luna`; `LAB_TEMPERATURE=1`; `recursion_limit=60` (mặc định của `lab.runner`).
- Deep Agents 0.7.21, Python 3.12.4, macOS 15.3.2, chạy trực tiếp (không Docker).
- Số lần chạy tác vụ: 9 lần trước freeze (3 `baseline` học, 3 `subagents` học, 3 `skills-auto` học ở Phần 3.4) + 12 lần sau freeze (3 `baseline` eval, 3 `subagents` eval, 6 `skills-auto` all) = 21 lần; curator gọi mô hình 2 lần. Giảng viên không nêu ngân sách cụ thể.
- Commit của tag `freeze`: (điền sau khi tạo tag, xem mục 7)

## 2. Giả thuyết (commit TRƯỚC tag `freeze`, Phần 4.0)

Căn cứ chung: ở tác vụ học, check kỹ thuật đạt 18/18 cho cả `baseline` và `subagents`, còn check quy ước đạt 0/9 (mục 4). Theo README, tác vụ đánh giá dùng lại quy ước của tác vụ học và thêm **một quy ước mới**. Bộ skill đóng băng gồm 2 skill (code và logs); họ `data` không có skill (mục 6).

- H1 (subagents so với baseline): Trên tác vụ đánh giá, `subagents` có điểm **bằng** `baseline` (chênh không quá 1 check mỗi tác vụ) nhưng tốn token trung bình nhiều hơn. Lý do: ở tác vụ học, `subagents` cũng đạt 18/18 kỹ thuật và 0/9 quy ước như `baseline`, vì việc giao việc không thêm thông tin về quy ước Acme vốn không có trong đề; token trung bình cao hơn 18% (67.011 so với 56.692). Bài viết về hệ thống nghiên cứu đa tác tử của Anthropic cũng ghi nhận đa tác tử tốn token hơn nhiều mà chỉ có lợi khi việc song song hóa được.
- H2 (skills-auto so với baseline): `skills-auto` đạt điểm trung bình **cao nhất** trên tác vụ đánh giá, nhưng chỉ nhờ `code-eval` và `logs-eval`: ở hai tác vụ này các check quy ước dùng lại từ tác vụ học sẽ đạt, còn quy ước mới vẫn trượt; `data-eval` xấp xỉ `baseline` vì không có skill về dữ liệu. Token trung bình cao hơn `baseline` (tác tử đọc skill và làm thêm việc: code-learn 160.033 so với 100.449 token ở Phần 3.4). SkillsBench báo skill do mô hình tự sinh trung bình không có lợi; dự đoán ở đây khác vì skill được rút từ phản hồi `RULE:` cụ thể, nhưng lợi ích chỉ giới hạn ở những quy ước đã thấy.
- H3 (tác vụ học so với tác vụ đánh giá): Mức tăng của `skills-auto` so với `baseline` trên tác vụ học (Phần 3.4: 24/27 so với 18/27 check, tức +6) sẽ **lớn hơn** mức tăng trên tác vụ đánh giá. Lý do: mỗi tác vụ đánh giá thêm một quy ước mới mà skill không nêu, và họ `data` không được hỗ trợ. Đây là dạng quá khớp với quy ước đã thấy mà SkillEvolBench mô tả (lợi ích trên tác vụ học không chuyển trọn sang tác vụ mới).

## 3. Làm quen Deep Agents (Phần 0.3)

1. Tác tử mặc định có 9 công cụ: 
   - Công cụ tệp: `ls`, `read_file`, `write_file`, `edit_file`, `delete`, `glob`, `grep`.
   - Công cụ chạy lệnh shell: `execute`.
   - Công cụ đa tác tử (giao việc): `task`.
   Công cụ cho phép chạy lệnh shell là `execute`.

2. Mô tả của công cụ `task` cho biết subagent `general-purpose` là tác tử đa năng dùng để nghiên cứu các câu hỏi phức tạp, tìm kiếm tệp/nội dung và thực hiện các tác vụ nhiều bước; nó có quyền truy cập toàn bộ công cụ như tác tử chính.
   Subagent đó mặc định ở trạng thái phi trạng thái (stateless): nó **không thấy lịch sử hội thoại** của tác tử chính, mà chỉ thấy nội dung prompt được giao trong lời gọi `task`.

3. Trích dẫn câu hướng dẫn hành vi:
   - Từ mô tả công cụ `task`: *"Each invocation is stateless by default: the agent sees only the prompt you give it and returns a single final report. Put full detail in the prompt and state exactly what it should return..."*
   - Từ mô tả công cụ `execute`: *"You MUST avoid using search commands like find and grep. Instead use the grep, glob tools to search. Use read_file rather than cat/head/tail."*

## 4. Đường cơ sở và phân loại lỗi (Phần 2.2)

| Tác vụ | Check thất bại | Nhóm lỗi (A-G) | Bằng chứng (trích ngắn từ `detail` hoặc vết) |
|---|---|---|---|
| `code-learn` | `rule_type_hints` | E | "RULE: every public function (name not starting with '_') in the package has type annotations on all parameters and on the return value." |
| `code-learn` | `rule_regression_tests` | E | "RULE: add tests/test_regressions.py with one test function per bug you fixed (at least 3); the file must pass." |
| `code-learn` | `rule_changelog` | E | "RULE: record each fix in CHANGELOG.md under the heading '## Unreleased' as a bullet '- fix(<function name>): <short description>' (at least 3 bullets)." |
| `data-learn` | `rule_money_in_cents` | E | "RULE: money values in answer.json are integer cents (1606.67 USD is written 160667)." |
| `data-learn` | `rule_meta_block` | E | "RULE: answer.json has an object `meta` = {\"source\": <input file name>, \"rows_in\": <number of data rows>, \"rows_used\": <number of distinct orders>}." |
| `data-learn` | `rule_clean_csv` | E | "RULE: write workspace/clean.csv with the header order_id,timestamp_utc,region,amount_cents; one row per distinct order with a known amount; timestamp_utc as YYYY-MM-DDTHH:MM:SSZ (UTC)..." |
| `logs-learn` | `rule_service_names` | E | "RULE: service names in the output are lower-case with '-' replaced by '_' (payment-service -> payment_service)." |
| `logs-learn` | `rule_sorted_errors` | E | "RULE: `errors` is sorted by service, then by timestamp_utc, ascending." |
| `logs-learn` | `rule_schema_header` | E | "RULE: the top-level object has \"schema_version\": 2 and \"generated_by\": \"log-triage\"." |

Nhận xét: Toàn bộ 9/9 check thất bại đều thuộc nhóm E (Vi phạm quy ước tổ chức - House rules). Tác tử có năng lực kỹ thuật rất tốt: 100% check kỹ thuật (18/18 check thuộc nhóm A đến D, gồm parse giá, xử lý làm tròn, lọc trùng lặp, chuẩn hóa múi giờ, phân tích stacktrace) đều đạt đầy đủ. Đây là bằng chứng phủ định rõ ràng cho các nhóm A đến D. Nhóm lỗi E xảy ra do các quy ước này là đặc thù nội bộ của tổ chức Acme không được nêu trong đề bài (`instruction.md`). Do đó, việc tự tiến hóa bằng cách sinh ra Skill tổng quát ghi nhận các quy ước này là hoàn toàn có khả năng phòng ngừa nhóm lỗi E ở các lần chạy tiếp theo.

## 5. Điều kiện `subagents` (Phần 2.3)

- Các subagent đã định nghĩa (tên, vai trò, lý do thiết kế):
  1. `explorer`: Chuyên gia trinh sát – đọc file README, docstring, phân tích cấu trúc dữ liệu mà không làm thay đổi file nào; giúp tách pha tìm hiểu thông tin khỏi pha sửa đổi.
  2. `implementer`: Chuyên gia thi công – trực tiếp sửa code, tạo file mới, chạy lệnh shell và kiểm tra lỗi; tập trung thực thi cụ thể theo yêu cầu.
  3. `reviewer`: Chuyên gia kiểm định độc lập – kiểm tra lại kết quả của các bước trước đối chiếu với yêu cầu đề bài và các quy ước tổ chức trước khi hoàn thành.
- `subagent_calls` ở từng tác vụ và nhận xét (kể cả trường hợp bằng 0):
  - `code-learn`: 2 lần gọi (`subagent_calls = 2`). Tác tử chính giao việc khảo sát bug và rà soát kiểm thử cho subagent.
  - `data-learn`: 3 lần gọi (`subagent_calls = 3`). Tác tử chính phân chia các bước làm sạch dữ liệu và kiểm tra kết quả cho subagent.
  - `logs-learn`: 1 lần gọi (`subagent_calls = 1`). Tác tử chính giao việc phân tích log cho subagent.
  Nhận xét: Tác tử chính đã chủ động ủy quyền công việc cho các subagent đúng theo tinh thần của `SUBAGENTS_NOTE` ở cả 3 tác vụ.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc):
  Tác tử chính truyền khá chi tiết đường dẫn tương đối và yêu cầu bài toán vào prompt của subagent. Tuy nhiên, do bản thân đề bài (`instruction.md`) không nêu các quy ước tổ chức Acme (nhóm E), nên tác tử chính không thể truyền những quy ước này cho subagent, khiến subagent dù hoàn thành tốt phần kỹ thuật vẫn không đạt các check nhóm E.
- Ảnh hưởng đến token và thời gian:
  - Thời gian thực thi tăng lên rõ rệt: `code-learn` (79.6s -> 89.4s), `data-learn` (24.9s -> 87.5s, tăng 3.5 lần), `logs-learn` (30.0s -> 52.8s, tăng 1.7 lần).
  - Chi phí token tăng vọt ở `data-learn` (30,654 -> 79,945 tokens, tăng 2.6 lần) và `logs-learn` (38,974 -> 44,457 tokens, tăng 14%); riêng `code-learn` giảm từ 100,449 xuống 76,632 tokens do tác tử chính bớt số lượt lặp trực tiếp. Điểm số không đổi so với baseline (7/10, 5/8, 6/9) cho thấy đa tác tử phân chia ngữ cảnh tốt nhưng không tự giải quyết được các quy ước thiếu thông tin.

## 6. Self-evolving: skill do curator sinh (Phần 3)

- Số lần chạy curator, số skill bị xóa và lý do:
  - **Lần 1** (12:22, prompt theo mẫu gợi ý): sinh 3 skill hợp lệ về định dạng (`repo-change-completeness`, `structured-data-deliverables`, `machine-readable-output-contracts`, 9 đến 11 dòng). Bản lưu: `report/curator_runs/run1/`. **Xóa cả 3** vì không đạt tiêu chí "đúng" (khớp `detail`): skill chỉ nói chung chung như "Record each fix in the required changelog section and format", "Represent currency in the required exact unit", "Include all required top-level fields", mà bỏ mất chính nội dung quy ước (`## Unreleased`, `- fix(<function name>): ...`, `tests/test_regressions.py`, số nguyên cent, khối `meta`, `schema_version: 2`, `generated_by: log-triage`, quy tắc tên service). Quy ước Acme không có trong đề, nên skill kiểu này không thể giúp tác tử đạt check nhóm E. Nguyên nhân: prompt cấm nêu "tên tệp và con số", trong khi `05_skill_quality.md` cho phép nêu tên do quy ước Acme yêu cầu.
  - **Lần 2** (chạy lại lần 1/2): thêm vào prompt curator một quy tắc là quy ước trong phản hồi `RULE:` chính là bài học và phải được nêu chính xác; chỉ bỏ chi tiết gắn với dữ liệu đầu vào của một tác vụ (`src/lab/curator.py`). Curator ghi 2 skill, giữ cả 2. Mô hình không trả về skill hợp lệ nào cho họ `data` (curator không in các khối bị `validate_skill` loại nên không rõ là không sinh ra hay bị loại). Không dùng lần chạy lại thứ 2: họ `data` không có skill được giữ làm đối chứng bên trong điều kiện `skills-auto`.
  - Không sửa tay nội dung nào trong `skills/auto/`.

| Skill | Tổng quát hay riêng cho tác vụ học? | Đúng hay sai (nêu chỗ sai nếu có) | Độ dài, `description` và `skills_read` ở Phần 3.4 |
|---|---|---|---|
| `code-change-completion` | Tổng quát ở mức quy ước tổ chức: không nêu tên gói, hàm hay lỗi cụ thể của `code-learn`; chỉ nêu tên do quy ước yêu cầu (`tests/test_regressions.py`, `CHANGELOG.md`, `## Unreleased`). Không hướng dẫn quy trình sửa lỗi chung (đọc docstring, tìm nguyên nhân gốc), nhưng baseline vốn đạt các check đó. | Đúng: 6 dòng ánh xạ 1-1 với `detail` của `rule_type_hints`, `rule_regression_tests`, `rule_changelog` (kể cả "ít nhất 3", tên private bắt đầu bằng `_`). Không thấy hướng dẫn có hại. | Thân 6 dòng mệnh lệnh; `description` "Use when fixing bugs in a Python package and preparing the change for review" đúng tình huống kích hoạt. Được đọc ở `code-learn` (dòng 16 của vết) và cả ở `logs-learn` dù không liên quan. |
| `log-output-normalization` | Riêng cho kiểu đầu ra log-triage của Acme: chỉ gồm 4 quy ước của `logs-learn`, không có bước nào về cách phân tích log. Tổng quát cho mọi tác vụ log của Acme, nhưng không giúp gì cho quy ước mới. | Đúng: khớp `detail` của `rule_schema_header`, `rule_service_names`, `rule_sorted_errors`. | Thân 4 dòng; `description` "Use when extracting error records from logs and assembling a structured JSON result" đúng. Được đọc ở `logs-learn` (dòng 32) và cả ở `code-learn`. |
| (không có skill cho `data`) | - | - | Ở `data-learn` tác tử chỉ gọi `ls /skills/` (dòng 171 của vết) rồi không đọc skill nào: `skills_read = 0`. |

`skills_read` ở Phần 3.4 (`results/skills-auto-dev/`): `code-learn` = 2, `logs-learn` = 2, `data-learn` = 0. Tác tử đọc **cả hai** skill ngay ở lượt đầu của `code-learn` và `logs-learn` (một lệnh gọi chứa hai `read_file`). Như vậy `skills_read = 2` không có nghĩa là cả hai skill đều liên quan: tác tử đọc hết vì thư viện skill nhỏ (rẻ), chứ không chọn lọc theo `description`.

## 7. Kết quả so sánh (Phần 4.3, 4.4)

> Dán nội dung `report/table.md` và kết quả `python scripts/check_breakdown.py`. Nêu các lần chạy có `error` hoặc `skills_modified = true` (nếu có) và cách xử lý.

```text
(dán bảng ở đây)
```

## 8. Phân tích

> Trả lời từng câu bằng số liệu từ mục 7 và bằng chứng từ vết. Kết quả âm hoặc không có khác biệt vẫn hợp lệ nếu được phân tích tốt.

1. So với `baseline`, điều kiện nào cải thiện điểm tác vụ **học**? Điều kiện nào cải thiện điểm tác vụ **đánh giá**? Có điều kiện nào cải thiện tác vụ học nhưng không cải thiện tác vụ đánh giá? Nếu có, đó là dấu hiệu gì?
2. Tách điểm thành check kỹ thuật và check quy ước (`rule_`). Skill do curator sinh giúp nhóm check nào? Check quy ước **mới** của tác vụ đánh giá có được skill giúp không, và vì sao?
3. Dựa vào vết và `skills_read`, giải thích một check mà skill giúp đạt và một check mà skill không giúp (skill chưa được đọc, đọc nhưng không làm theo, skill thiếu hoặc sai).
4. Chi phí: so sánh số token trung bình giữa các điều kiện. Điều kiện nào có hiệu quả tốt nhất theo điểm trên mỗi token? Đa tác tử có đáng chi phí trong thí nghiệm này không?
5. Có dấu hiệu rò rỉ dữ liệu hoặc quá khớp nào trong skill sinh ra không? Nhóm đã phòng tránh như thế nào?
6. Nhiễu: so sánh điểm tác vụ học của cùng bộ skill ở Phần 3.4 (đã sao lưu) và sau đóng băng. Chênh lệch bao nhiêu? Nó cho biết điều gì về độ tin cậy của các chênh lệch trong bảng ở mục 7?

## 9. Hạn chế và tính hợp lệ

> Nêu ít nhất 3 hạn chế và ảnh hưởng của từng hạn chế đến kết luận (ví dụ: chỉ 3 tác vụ mỗi vai trò, mỗi cấu hình chạy một lần, nhiễu của mô hình, tác vụ do giảng viên thiết kế sẵn quy ước, chỉ một mô hình).

1.
2.
3.

## 10. Kết luận

> Tối đa 5 câu. Chỉ khẳng định điều số liệu hỗ trợ. Nêu một đề xuất cải tiến tiếp theo.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
- Thử thách mở rộng (nếu có): hướng chọn, kết quả, nhận xét.
- Ghi chú khác:
