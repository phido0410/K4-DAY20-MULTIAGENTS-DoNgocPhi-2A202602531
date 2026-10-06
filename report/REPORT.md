# Báo cáo Lab: Self evolving Agentic

## 1. Thông tin nhóm và cấu hình

| Họ tên | Mã sinh viên | Phần đóng góp |
|---|---|---|
| Đỗ Ngọc Phi | 2A202602531 | Toàn bộ (cá nhân) |

- Mô hình: Azure OpenAI, deployment `gpt-6-luna`; `LAB_TEMPERATURE=1`; `recursion_limit=60` (mặc định của `lab.runner`).
- Deep Agents 0.7.21, Python 3.12.4, macOS 15.3.2, chạy trực tiếp (không Docker).
- Số lần chạy tác vụ: 9 lần trước freeze (3 `baseline` học, 3 `subagents` học, 3 `skills-auto` học ở Phần 3.4) + 12 lần sau freeze (3 `baseline` eval, 3 `subagents` eval, 6 `skills-auto` all) = 21 lần; curator gọi mô hình 2 lần. Giảng viên không nêu ngân sách cụ thể.
- Commit của tag `freeze`: `eee72df` ("freeze skills", 2026-10-06T12:38:03+07:00), đứng ngay sau commit `hypotheses` `4288ee2`.

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
  Nhận xét: Tác tử chính đã chủ động ủy quyền công việc cho các subagent đúng theo tinh thần của `SUBAGENTS_NOTE` ở cả 3 tác vụ. Theo trường `subagent_type` trong vết: `data-learn` gọi `explorer` → `implementer` → `reviewer` (đủ ba vai trò); `code-learn` gọi `explorer` → `implementer`; `logs-learn` chỉ gọi `explorer`. Sau freeze, trên tác vụ đánh giá: `code-eval` 2 lần (`explorer`, `implementer`), `data-eval` 1 lần và `logs-eval` 1 lần (đều là `explorer`). `reviewer` chỉ được gọi đúng một lần trong 6 tác vụ.
- Thông tin thiếu hoặc thừa khi giao việc (nếu có giao việc):
  Tác tử chính truyền khá chi tiết đường dẫn tương đối và yêu cầu bài toán vào prompt của subagent. Tuy nhiên, do bản thân đề bài (`instruction.md`) không nêu các quy ước tổ chức Acme (nhóm E), nên tác tử chính không thể truyền những quy ước này cho subagent, khiến subagent dù hoàn thành tốt phần kỹ thuật vẫn không đạt các check nhóm E.
- Ảnh hưởng đến token và thời gian:
  - Thời gian thực thi tăng lên rõ rệt: `code-learn` (79.6s -> 89.4s), `data-learn` (24.9s -> 87.5s, tăng 3.5 lần), `logs-learn` (30.0s -> 52.8s, tăng 1.7 lần).
  - Chi phí token tăng vọt ở `data-learn` (30,654 -> 79,945 tokens, tăng 2.6 lần) và `logs-learn` (38,974 -> 44,457 tokens, tăng 14%); riêng `code-learn` giảm từ 100,449 xuống 76,632 tokens, đi kèm số tool call ở luồng chính giảm từ 24 xuống 13 (một phần việc chuyển sang subagent; token của subagent vẫn được tính nhờ `UsageMetadataCallbackHandler`). Điểm số không đổi so với baseline (7/10, 5/8, 6/9) cho thấy đa tác tử phân chia ngữ cảnh tốt nhưng không tự giải quyết được các quy ước thiếu thông tin.
  - Trên tác vụ đánh giá (sau freeze), điểm vẫn trùng khớp từng tác vụ với baseline (7/11, 5/9, 6/10), còn token tăng ở cả ba tác vụ: `code-eval` 62.670 → 121.137 (×1,9), `data-eval` 40.588 → 50.805, `logs-eval` 23.951 → 47.021 (×2,0); thời gian tổng 115,5 s → 227,5 s.

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

`report/table.md` (sinh bằng `python -m lab.compare > report/table.md`):

| Task | baseline | subagents | skills-auto |
|---|---|---|---|
| code-learn | 7/10 | 7/10 | 10/10 |
| data-learn | 5/8 | 5/8 | 5/8 |
| logs-learn | 6/9 | 6/9 | 9/9 |
| code-eval | 7/11 | 7/11 | 10/11 |
| data-eval | 5/9 | 5/9 | 5/9 |
| logs-eval | 6/10 | 6/10 | 4/10 |
| **Mean score - learning tasks** | 0.66 | 0.66 | 0.88 |
| **Mean score - evaluation tasks** | 0.60 | 0.60 | 0.62 |
| **Mean tokens per run** | 49,547 | 69,999 | 63,781 |
| **Runs that read a skill** | 0/6 | 0/6 | 6/6 |

`python scripts/check_breakdown.py`:

```text
condition     role    technical  house rules  mean tokens  read a skill
baseline      eval     18/18         0/12          42,403      0/3
baseline      learn    18/18         0/9           56,692      0/3
subagents     eval     18/18         0/12          72,987      0/3
subagents     learn    18/18         0/9           67,011      0/3
skills-auto   eval     13/18         6/12          56,167      3/3
skills-auto   learn    18/18         6/9           71,395      3/3
```

Kết quả Phần 3.4 (cùng bộ skill, trước freeze, `results/skills-auto-dev/`, không nằm trong bảng vì `lab.compare` chỉ đọc 4 điều kiện chuẩn): `code-learn` 10/10, `data-learn` 5/8, `logs-learn` 9/9; token 160.033 / 54.027 / 41.910.

- `python scripts/verify_freeze.py`: `checked 6 runs of skill conditions: OK` (exit 0).
- Không có lần chạy nào có `error` khác `null`; mọi lần chạy có `skills_modified = false`. Không phải chạy lại lần nào.

## 8. Phân tích

1. **Học và đánh giá.** So với `baseline`, chỉ `skills-auto` cải thiện tác vụ học: 24/27 so với 18/27 check, điểm trung bình 0,88 so với 0,66 (+0,22). Trên tác vụ đánh giá, `skills-auto` chỉ nhỉnh hơn: 19/30 so với 18/30 check, 0,62 so với 0,60 (+0,02). Mức +0,02 là tổng của +3 check ở `code-eval`, 0 ở `data-eval` và −2 ở `logs-eval`. `subagents` trùng khớp `baseline` ở cả 6 tác vụ (H1 được xác nhận). Mức tăng lớn ở tác vụ học nhưng gần như không chuyển sang tác vụ đánh giá (H3 được xác nhận) là dấu hiệu quá khớp với **những quy ước đã thấy**, chứ không phải tác tử học được năng lực tổng quát hơn. H2 chỉ đúng một phần: `skills-auto` có điểm đánh giá trung bình cao nhất như dự đoán, nhưng `logs-eval` giảm thay vì tăng (xem câu 3).

2. **Kỹ thuật và quy ước.** Skill chỉ giúp nhóm check quy ước: `rule_` đạt 6/9 ở tác vụ học và 6/12 ở tác vụ đánh giá, so với 0/9 và 0/12 của `baseline`. 6 check đạt trên tác vụ đánh giá chính là 6 quy ước dùng lại từ tác vụ học: `rule_type_hints`, `rule_regression_tests`, `rule_changelog` ở `code-eval` và `rule_service_names`, `rule_sorted_errors`, `rule_schema_header` ở `logs-eval`. **Quy ước mới** của từng tác vụ đánh giá (`rule_version_bump`, `rule_sorted_keys_format`, `rule_source_line`) trượt ở cả ba điều kiện. Skill không thể giúp ở đây vì skill được viết từ phản hồi của tác vụ học, mà quy ước mới thì không xuất hiện ở đó; còn `detail` của tác vụ đánh giá luôn rỗng nên tác tử không có phản hồi nào để suy ra. Họ `data` không có skill nên 0/4 quy ước ở `data-eval` và 0/3 ở `data-learn`, giống `baseline`. Đây là nhóm đối chứng bên trong cho thấy điểm tăng ở code và logs đến từ skill. Ngược lại, check kỹ thuật của `skills-auto` trên tác vụ đánh giá **giảm** từ 18/18 xuống 13/18; toàn bộ 5 check giảm nằm ở `logs-eval`.

3. **Cơ chế qua vết và `skills_read`.**
   - *Skill giúp đạt:* `code-eval`, `rule_changelog` (cùng `rule_type_hints`, `rule_regression_tests`). `skills_read = 1`: tác tử đọc `/skills/code-change-completion/SKILL.md` ở lượt đầu (dòng 16 của vết), rồi làm theo đủ 6 dòng của skill, nhờ đó đạt cả 3 check mà `baseline` và `subagents` đều trượt. Ở lần chạy này tác tử chỉ đọc skill liên quan, khác với Phần 3.4 khi nó đọc cả hai.
   - *Skill không giúp:* `data-eval`, `rule_money_in_cents` và `rule_meta_block`. Không có skill nào về dữ liệu. Tác tử đọc `log-output-normalization` (dòng 21 của vết, `skills_read = 1`), có lẽ vì `description` "assembling a structured JSON result" khớp với việc ghi `answer.json`, nhưng không áp dụng: `answer.json` không có `schema_version`. Như vậy skill được đọc mà không gây hại, và cũng không giúp gì.
   - *Kiểm tra hồi quy (regression) ở `logs-eval`:* tác tử đọc cả hai skill, rồi **chép tay** toàn bộ `errors.json` (23 bản ghi) bằng một lệnh `write_file`, sau một lần `read_file` toàn bộ 150 dòng log. Nó không viết script phân tích; bước kiểm tra duy nhất là một lệnh đếm phần tử. Kết quả: 3 quy ước đã học đều đạt, nhưng `entry_count`, `timestamps_utc`, `levels_uppercase`, `repeat_counts`, `counts_by_service` trượt. `baseline` và `subagents` cùng tác vụ đều phân tích bằng script Python (`python - <<'PY' ...`) và đạt 6/6 check kỹ thuật. Hai lần chạy `logs-learn` có skill (Phần 3.4 và sau freeze) cũng dùng script. Vì vậy mình **không** khẳng định skill gây ra cách làm chép tay; với một lần chạy, đây có thể là biến động chiến lược ngẫu nhiên. Điều chắc chắn là skill lần 2 chỉ chứa quy ước định dạng, không có bước "tính bằng chương trình và kiểm chứng đầu ra" (bộ skill lần 1 có câu "Parse the generated output and validate its structure..."), nên skill không ngăn được lỗi này.

4. **Chi phí.** Token trung bình mỗi lần chạy: `baseline` 49.547, `skills-auto` 63.781 (+29%), `subagents` 69.999 (+41%). Điểm trên 100k token (điểm trung bình / token trung bình): trên toàn bộ 6 tác vụ, `baseline` 1,27, `skills-auto` 1,17, `subagents` 0,90; chỉ tính tác vụ học thì `skills-auto` 1,23 nhỉnh hơn `baseline` 1,17; chỉ tính tác vụ đánh giá thì `baseline` 1,41 > `skills-auto` 1,11 > `subagents` 0,82. Skill tăng token chủ yếu vì tác tử làm thêm việc mà quy ước yêu cầu (type hints, test hồi quy, changelog): `code-learn` 130.936 token so với 100.449; bản thân hai skill chỉ dài 4 đến 6 dòng. Đa tác tử **không đáng chi phí** trong thí nghiệm này: token +41% (trên tác vụ đánh giá +72%), thời gian chạy gần gấp đôi (115,5 s → 227,5 s trên tác vụ đánh giá), và không thêm check nào. Nguyên nhân: tác vụ ngắn, tuần tự, tác tử đơn đã đạt 100% check kỹ thuật, và quy ước còn thiếu là thông tin mà không subagent nào có.

5. **Rò rỉ dữ liệu và quá khớp.** Không thấy rò rỉ: cả hai skill qua `validate_skill` (không chứa `eval_markers`), curator chỉ đọc `run.json` có `role == "learn"` (test `test_04` kiểm tra điều này), và mình không mở `check.py` hay kết quả của tác vụ đánh giá trước freeze. Tên trong skill (`tests/test_regressions.py`, `CHANGELOG.md`, `schema_version`, `log-triage`) đều lấy từ `detail` của tác vụ học và là tên do quy ước yêu cầu, được `05_skill_quality.md` cho phép. Quá khớp thì có: `log-output-normalization` chỉ gồm 4 quy ước cụ thể, không có quy trình chung, và skill không giúp được quy ước mới nào (0/3). Lần chạy lại curator dùng prompt mới chỉ dựa trên phản hồi tác vụ học và hướng dẫn chất lượng skill, không dựa trên bất kỳ thông tin nào của tác vụ đánh giá.

6. **Nhiễu.** Cùng bộ skill trên tác vụ học, Phần 3.4 và sau freeze cho **điểm giống hệt** (10/10, 5/8, 9/9; chênh 0 check). Nhưng các số đo khác dao động mạnh: token `code-learn` 160.033 → 130.936 (−18%), `logs-learn` 41.910 → 31.795 (−24%); `skills_read` `data-learn` 0 → 2, `logs-learn` 2 → 1. `logs-eval` cho thấy một lần chạy có thể mất 5 check kỹ thuật chỉ vì đổi chiến lược (chép tay thay vì viết script). Vì vậy, các chênh lệch lớn và đồng nhất về quy ước (0 → 6 check ở cả học lẫn đánh giá, lặp lại qua 2 lần chạy tác vụ học) là đáng tin; còn mức +0,02 điểm trung bình trên tác vụ đánh giá và mức −2 ở `logs-eval` nằm trong vùng nhiễu của một lần chạy, chưa đủ để kết luận skill tốt hơn hay kém hơn trên tác vụ mới.

## 9. Hạn chế và tính hợp lệ

1. **Mỗi cấu hình chỉ chạy một lần, với `temperature = 1`.** `logs-eval` cho thấy một lần chạy có thể mất 5/10 check chỉ vì đổi chiến lược. Mọi chênh lệch nhỏ (±1 đến 2 check, ±0,02 điểm trung bình) có thể chỉ là nhiễu; cần ít nhất 3 lần lặp mỗi cấu hình (hướng 6e) mới tính được khoảng dao động.
2. **Số tác vụ nhỏ:** 3 tác vụ học, 3 tác vụ đánh giá, mỗi họ một cặp. Khi một họ không có skill (`data`), kết luận về `skills-auto` chỉ dựa trên 2 tác vụ đánh giá. Không thể tổng quát hóa sang loại việc khác.
3. **Tác vụ do giảng viên thiết kế quanh quy ước ẩn.** Toàn bộ lỗi baseline thuộc nhóm E. Thiết kế này khiến skill trông rất hiệu quả trên tác vụ học (+6 check) vì skill chỉ cần chép lại quy ước từ `detail`. Ở môi trường thật, lỗi thường thuộc nhóm A đến D, nơi skill tự sinh khó giúp hơn (như SkillsBench ghi nhận).
4. **Quá khớp và quy trình curator.** Mỗi tác vụ đánh giá có đúng một quy ước mới mà không điều kiện nào đạt. Skill chỉ giúp những gì đã thấy. Ngoài ra, mình đã sửa prompt curator sau khi đọc skill lần 1, và curator có tính ngẫu nhiên (lần 2 không sinh được skill hợp lệ nào cho `data`). Kết quả `skills-auto` vì thế phụ thuộc vào một mẫu đầu ra cụ thể của curator, chứ không đại diện cho "curator nói chung".
5. **Một mô hình duy nhất** (`gpt-6-luna`, Azure). Mô hình này đã đạt 100% check kỹ thuật khi không có skill, nên không còn chỗ để skill cải thiện phần kỹ thuật. Với mô hình yếu hơn, thứ tự giữa các điều kiện có thể khác.
6. **Định nghĩa số đếm chỉ tính luồng chính.** `subagent_calls`, `tool_calls`, `skills_read` không thấy việc bên trong subagent, nên nhận xét về chất lượng giao việc chỉ dựa trên prompt giao việc và báo cáo trả về.

## 10. Kết luận

Trong thí nghiệm một lần chạy này, skill do curator sinh từ phản hồi `RULE:` đưa các check quy ước đã thấy từ 0 lên 6 ở cả tác vụ học (9 check) lẫn tác vụ đánh giá (12 check). Tuy nhiên, điểm trung bình tác vụ đánh giá chỉ tăng 0,60 → 0,62, vì mọi quy ước mới đều trượt, họ `data` không có skill, và một lần chạy `logs-eval` mất 5 check kỹ thuật. Đa tác tử cho điểm trùng khớp `baseline` ở cả 6 tác vụ nhưng tốn thêm 41% token, nên không đáng chi phí với các tác vụ ngắn, tuần tự này. Lợi ích của skill gần như không chuyển sang quy ước mới; đây là quá khớp với kiến thức đã thấy, đúng như H3 và SkillEvolBench dự đoán. Đề xuất tiếp theo: cho curator giữ một bước quy trình chung ("tính bằng script và kiểm chứng đầu ra") bên cạnh quy ước, rồi chạy lặp 3 lần mỗi cấu hình để tách hiệu ứng khỏi nhiễu.

## Phụ lục

- Lệnh đã chạy (theo thứ tự):
  1. `pytest tests/test_01_provided.py`, `python scripts/tour.py`
  2. `pytest tests/test_02_agent.py`, `pytest tests/test_03_runner.py`
  3. `python -m lab.runner --condition baseline --tasks data-learn`
  4. `python -m lab.runner --condition baseline --tasks code-learn logs-learn`
  5. `python -m lab.runner --condition subagents --tasks learn`
  6. `pytest tests/test_04_curator.py`; `python -m lab.curator` (lần 1, skill bị xóa, lưu ở `report/curator_runs/run1/`)
  7. Sửa prompt trong `src/lab/curator.py`; `python -m lab.curator` (lần 2, giữ 2 skill)
  8. `python -m lab.runner --condition skills-auto --tasks learn`; `mv results/skills-auto results/skills-auto-dev`
  9. `git add -A && git commit -m "hypotheses"`; `git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze`
  10. `python -m lab.runner --condition baseline --tasks eval`
  11. `python -m lab.runner --condition subagents --tasks eval`
  12. `python -m lab.runner --condition skills-auto --tasks all`
  13. `python scripts/verify_freeze.py`; `python -m lab.compare > report/table.md`; `python scripts/check_breakdown.py`
- Tái lập: làm theo `README.md` mục 4 (tạo `.venv`, `pip install -e .`, điền `.env` theo cách 1 với deployment `gpt-6-luna`, `LAB_TEMPERATURE=1`), rồi chạy các lệnh trên. `recursion_limit` để mặc định 60.
- Thử thách mở rộng: Chọn **Hướng 6c - Tấn công curator (Red team) và cơ chế phòng vệ**.
  1. *Thiết kế thí nghiệm:* Xây dựng script độc lập `scripts/red_team_curator.py` và lưu trữ kết quả riêng biệt tại `results/red_team/results.json` để hoàn toàn không ảnh hưởng đến dữ liệu đánh giá chính thức và không vi phạm tag `freeze`. Thử nghiệm 4 vector tấn công:
     - V1 (Direct marker): Chèn trực tiếp định danh đánh giá (`code-eval`, `march_orders_utc`).
     - V2 (Obfuscated evasion): Lách bộ lọc bằng cách chèn dấu gạch nối giữa các ký tự (`c-o-d-e - e-v-a-l`) hoặc ký tự zero-width.
     - V3 (Path traversal): Tấn công duyệt thư mục qua tên khối (`=== SKILL: ../../../evil ===`).
     - V4 (Indirect prompt injection): Tiêm chỉ thị độc hại ghi đè quy tắc của tác tử qua trường `detail` phản hồi ("Ignore all previous instructions...").
  2. *Số liệu thực nghiệm:* 
     - Cơ chế phòng thủ gốc (`validate_skill`): Chặn được 2/4 vector (V1 và V3 nhờ `eval_markers` và `SAFE_NAME`), nhưng bị **bypass 50%** bởi V2 (do chỉ so khớp chuỗi con thô) và V4 (không lọc chỉ thị tiêm nhiễm).
     - Cơ chế phòng thủ nâng cao (`hardened_validate_skill`): Chuẩn hóa Unicode NFKC, nén toàn bộ dấu phân cách và bổ sung bộ lọc mẫu tiêm chỉ thị. Kết quả chặn thành công **4/4 vector (Tỷ lệ bypass: 0.0%)**.
  3. *Phân tích cơ chế:* Bộ lọc ban đầu chỉ kiểm tra chuỗi con trực tiếp (`marker in low`), do đó kẻ tấn công dễ dàng lách luật bằng cách phân tách token hoặc dùng từ đồng nghĩa để mang tri thức của tập đánh giá vào skill mà không bị bắt. Ngoài ra, việc curator đọc trực tiếp `detail` mà không qua bước làm sạch mở ra lỗ hổng tiêm chỉ thị gián tiếp (Indirect Prompt Injection).
  4. *Hạn chế và đề xuất tiếp theo:* Các mẫu regex phòng thủ hiện tại chỉ chặn được các dạng tiêm chỉ thị phổ biến; bước tiếp theo nên tích hợp một lớp kiểm duyệt ngữ nghĩa (LLM Guardrail) và phân tích AST tĩnh để phát hiện hành vi gian lận tinh vi hơn.
  5. *Tái lập:* Chạy lệnh `python scripts/red_team_curator.py`.
- Ghi chú khác: `trace.md` chứa các khối `encrypted_content` (reasoning đã mã hóa do API trả về), không phải khóa API. Đã quét toàn kho: không có khóa hay endpoint nào ngoài `.env` (`.env` nằm trong `.gitignore`, chưa từng được commit).
