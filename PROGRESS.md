# NHẬT KÝ TIẾN ĐỘ & GIẢI THÍCH KIẾN THỨC BÀI LAB (PROGRESS)

Tài liệu này ghi lại chi tiết các mốc hoàn thành (Checkpoint), giải thích các kiến thức quan trọng bằng ngôn ngữ gần gũi, dễ hiểu và đối chiếu trực tiếp với thang điểm Rubric.

---

## 🏁 CHECKPOINT 0: KHỞI TẠO MÔI TRƯỜNG & LÀM QUEN HARNESS
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH
* **Kết quả kiểm thử:** `pytest tests/test_01_provided.py` ➔ **12/12 passed**.
* **Khóa API & Mô hình:** Đã kết nối thành công với `temperature = 1` (đáp ứng yêu cầu mô hình suy luận).
* **Báo cáo:** Đã trả lời đầy đủ 3 câu hỏi khám phá harness vào Mục 3 của `report/REPORT.md`.

### 💡 Giải thích kiến thức gần gũi:
* **Harness là gì?** Hãy tưởng tượng mô hình ngôn ngữ (LLM) là một "bộ não" thông minh nhưng không có tay chân. "Harness" chính là bộ đồ bảo hộ gắn thêm các cánh tay robot (công cụ như đọc file, chạy lệnh shell) để bộ não đó tương tác được với thế giới thực bên trong một máy tính.
* **Vì sao `task` lại gọi là "stateless" (phi trạng thái)?** Khi con bot chính giao việc cho một chú trợ lý con (subagent), chú trợ lý này chỉ nhận được duy nhất mẩu giấy ghi việc (prompt) mà không hề biết con bot chính trước đó đã nói chuyện hay làm những gì. Vì thế, con bot chính bắt buộc phải ghi đầy đủ mọi thông tin, quy tắc vào mẩu giấy giao việc đó.

---

## 🛠️ CHECKPOINT 1: LẬP TRÌNH BỘ KHUNG ĐIỀU KHIỂN (HARNESS)

### Checkpoint 1.1: Định nghĩa Subagents (`src/lab/subagents.py`)
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH
* **Đạt điểm Rubric:** 3/3 điểm Mục 3.1.
* **Các vai trò đã thiết kế:**
  1. `explorer`: Chuyên gia trinh sát – đọc file README, docstring, phân tích cấu trúc dữ liệu mà không làm thay đổi file nào.
  2. `implementer`: Chuyên gia thi công – trực tiếp sửa code, tạo file mới, chạy lệnh shell và kiểm tra lỗi.
  3. `reviewer`: Chuyên gia kiểm định độc lập – kiểm tra lại kết quả của các bước trước đối chiếu với yêu cầu đề bài và các quy ước tổ chức.

### Checkpoint 1.2: Xây dựng Backend & Tác tử (`src/lab/agent.py`)
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH
* **Kết quả kiểm thử:** `pytest tests/test_02_agent.py` ➔ **9/9 passed** (10/10 điểm Mục 1).
* **Kiến thức cốt lõi:**
  * **Giấu chìa khóa bí mật:** Cấu hình `LocalShellBackend(inherit_env=False)` đảm bảo shell của con bot không thể đọc được các biến môi trường chứa API Key thật của máy chủ (chống lộ bí mật - Security).
  * **Vấn đề đường dẫn kép:** Công cụ tệp dùng đường dẫn ảo (nhận cả `workspace/a.txt` lẫn `/workspace/a.txt`), nhưng shell chạy lệnh thật trên máy tính nên **chỉ nhận đường dẫn tương đối** `workspace/a.txt`. Hệ thống đã tự động gắn `PATHS_NOTE` vào prompt để con bot không bị lỗi "File not found".

### Checkpoint 1.3: Bộ điều phối chạy tác vụ (`src/lab/runner.py`)
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH
* **Kết quả kiểm thử:** `pytest tests/test_03_runner.py` ➔ **6/6 passed** (12/12 điểm Mục 1).
* **Kiến thức cốt lõi:**
  * **Sandbox cách ly an toàn:** Mỗi bài toán được chạy trong một thư mục tạm riêng ngoài kho code (`tempfile.mkdtemp`). Sau khi làm xong, thư mục này được xóa sạch, đảm bảo code gốc trong `tasks/` không bao giờ bị bẩn.
  * **Đo lường trung thực:** Sử dụng `UsageMetadataCallbackHandler` để cộng dồn chính xác từng token mà cả tác tử chính lẫn các trợ lý con đã tiêu thụ.
  * **Bảo vệ skill:** Chụp mã băm SHA-256 của thư mục `skills/` trước và sau khi chạy để phát hiện nếu con bot gian lận tự ý sửa nội dung skill (`skills_modified`).

---

## 🧠 CHECKPOINT 3.1: BỘ TUYỂN CHỌN SKILL TỰ ĐỘNG (`src/lab/curator.py`)
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH
* **Kết quả kiểm thử:** `pytest tests/test_04_curator.py` ➔ **2/2 passed** (8/8 điểm Mục 1).
* **Tổng điểm Harness hiện tại:** **30/30 điểm (100% test tự động đã đạt)**.
* **Kiến thức cốt lõi:**
  * **Chống rò rỉ dữ liệu (No Data Leakage):** Curator chỉ đọc kết quả của các bài học (`role == "learn"`), tuyệt đối không bao giờ nhìn trộm dữ liệu của bài kiểm tra (`role == "eval"`).
  * **Học từ thất bại:** Thay vì học vẹt đáp án, curator đọc nhận xét của bot chấm điểm (`detail` - ví dụ: "RULE: phải viết type hints", "RULE: phải tạo test regression") và viết ra các cẩm nang chỉ dẫn tổng quát (`SKILL.md`) dạng checklist từng bước.

---

## 📊 CHECKPOINT 2: CHẠY ĐƯỜNG CƠ SỞ (BASELINE) & PHÂN LOẠI LỖI
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH ĐIỀU KIỆN BASELINE TRÊN TẬP HỌC
* **Kết quả đo lường thực tế:**
  1. `data-learn`: **5/8 checks passed** (24.9s, 30,654 tokens, 9 tool calls)
  2. `code-learn`: **7/10 checks passed** (79.6s, 100,449 tokens, 24 tool calls)
  3. `logs-learn`: **6/9 checks passed** (30.0s, 38,974 tokens, 6 tool calls)
* **Tổng hợp kết quả:**
  * **Check kỹ thuật (Nhóm A-D):** Đạt tuyệt đối **18/18 (100%)**! Mô hình giải quyết các bài toán kỹ thuật (sửa bug hàm, parse định dạng giá, khử dòng trùng, tính tổng, xử lý múi giờ, phân tích log) cực kỳ xuất sắc.
  * **Check quy ước tổ chức (Nhóm E - House rules):** Thất bại **9/9 checks**! Toàn bộ các check thất bại đều do vi phạm quy định riêng của Acme (type hints, test regression, CHANGELOG unreleased, chuyển tiền sang cent, header schema version, tên service gạch dưới).
* **Báo cáo:** Đã điền bảng phân loại lỗi chi tiết kèm bằng chứng trích dẫn vào Mục 4 của `report/REPORT.md`.

---

## 👥 CHECKPOINT 2.3: ĐIỀU KIỆN ĐA TÁC TỬ (`subagents`) TRÊN TẬP HỌC
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH
* **Kết quả:** điểm y hệt baseline (7/10, 5/8, 6/9), `subagent_calls` = 2 / 3 / 1, token trung bình 67.011 so với 56.692 của baseline (+18%).

### 💡 Giải thích kiến thức gần gũi:
* **Thuê thêm người không giúp được nếu không ai biết luật.** Quy ước Acme không nằm trong đề, nên tác tử chính không thể dặn subagent điều mà chính nó cũng không biết. Kết quả là chia việc chỉ làm hóa đơn token dài thêm, còn điểm thì đứng yên.
* **Đọc vết để biết ai làm gì:** trong `trace.md`, mỗi lần giao việc hiện ra dưới dạng tool call `task` có trường `subagent_type` (explorer, implementer, reviewer). Bên trong subagent làm gì thì vết không ghi, chỉ thấy báo cáo cuối của nó.

---

## 🧬 CHECKPOINT 3.2–3.4: CURATOR TỰ VIẾT SKILL & THỬ TRÊN TẬP HỌC
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH
* **Curator lần 1:** sinh 3 skill hợp lệ về định dạng nhưng "nói chung chung", kiểu "ghi changelog đúng định dạng được yêu cầu" mà không nói định dạng đó là gì. Đã xóa (bản lưu ở `report/curator_runs/run1/`).
* **Curator lần 2** (chạy lại 1/2): sửa prompt để curator chép đúng quy ước trong phản hồi `RULE:`. Kết quả là 2 skill: `code-change-completion` (6 dòng) và `log-output-normalization` (4 dòng). Họ `data` không có skill nào.
* **Phần 3.4** (`results/skills-auto-dev/`): code-learn **10/10**, logs-learn **9/9**, data-learn 5/8 (không có skill nên vẫn như baseline). `skills_read` = 2 / 0 / 2. Không có lần chạy nào sửa skill (`skills_modified = false`).

### 💡 Giải thích kiến thức gần gũi:
* **"Skill tổng quát" khác với "skill rỗng ruột".** Lời khuyên "hãy làm đúng định dạng được yêu cầu" nghe hay nhưng vô dụng khi chẳng ai nói định dạng là gì. Bài học thật nằm ở chi tiết của luật nhà (ví dụ `## Unreleased`, `schema_version: 2`). Guide 05 cho phép ghi những tên do quy ước yêu cầu, chỉ cấm ghi chi tiết riêng của dữ liệu một bài.
* **Đọc skill ≠ chọn skill.** Thư viện chỉ có 2 skill ngắn nên tác tử đọc luôn cả hai ngay lượt đầu, kể cả skill không liên quan. Vì vậy `skills_read = 2` không chứng minh tác tử biết chọn đúng skill theo `description`.
* **Một họ không có skill là một "nhóm đối chứng" miễn phí.** data-learn không có skill và điểm vẫn đứng yên, cho thấy điểm tăng ở code/logs đến từ skill chứ không phải do may mắn chung của lần chạy.
* **Phải sao lưu trước khi chạy lại.** Lần chạy `skills-auto --tasks all` sau freeze sẽ ghi đè thư mục `results/skills-auto/`, nên mình đã đổi tên kết quả Phần 3.4 thành `skills-auto-dev` để sau này so sánh độ nhiễu.

---

## 🧊 CHECKPOINT 4: GIẢ THUYẾT → ĐÓNG BĂNG → CHẠY CHÍNH THỨC
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH
* Commit `hypotheses` = `4288ee2`, sau đó commit `freeze skills` = `eee72df` + tag `freeze` (12:38:03).
* 12 lần chạy sau freeze, không lần nào lỗi, không lần nào sửa skill. `verify_freeze.py` báo **OK** (exit 0).
* Bảng `report/table.md` khớp 100% với `python -m lab.compare`.

| | baseline | subagents | skills-auto |
|---|---|---|---|
| Điểm TB tác vụ học | 0,66 | 0,66 | **0,88** |
| Điểm TB tác vụ đánh giá | 0,60 | 0,60 | **0,62** |
| Token TB / lần chạy | **49.547** | 69.999 | 63.781 |

### 💡 Giải thích kiến thức gần gũi:
* **Vì sao phải viết giả thuyết trước rồi mới đóng băng?** Giống như nộp bài dự đoán tỉ số trước khi trận đấu bắt đầu. Git ghi lại thời điểm commit, nên không ai có thể "đoán sau khi biết kết quả". `verify_freeze.py` kiểm tra 4 việc: tag tồn tại, `skills/` không đổi từ tag, mỗi lần chạy `skills-auto` có `skills_sha256` trùng với bộ skill đóng băng, và lần chạy bắt đầu SAU giờ tag.
* **Học tủ trúng tủ, gặp đề mới thì trượt.** Skill giúp đạt đúng 6 quy ước đã thấy (0 → 6 ở cả học lẫn đánh giá), nhưng cả 3 quy ước mới của bài đánh giá đều trượt ở mọi điều kiện. Điểm học tăng +0,22 mà điểm đánh giá chỉ tăng +0,02: đây chính là quá khớp (overfitting).
* **Một lần chạy có thể "xui".** Ở `logs-eval`, tác tử có skill tự chép tay 23 bản ghi thay vì viết script, nên mất 5 check kỹ thuật mà baseline đều đạt. Các lần chạy logs khác có skill đều viết script, nên mình không đổ lỗi cho skill; mình chỉ ghi nhận rằng skill toàn quy ước định dạng thì không ngăn được kiểu sai này. Bài học: một lần chạy chưa đủ để kết luận các chênh lệch nhỏ.
* **Đa tác tử không phải lúc nào cũng đáng tiền.** Điểm trùng baseline ở cả 6 bài, token +41%, thời gian gần gấp đôi. Bài ngắn và tuần tự thì một tác tử là đủ.
* **Nhiễu đo bằng cách chạy lại cùng bộ skill.** So Phần 3.4 với sau freeze: điểm giống hệt, nhưng token lệch tới 18–24%. Vì vậy chỉ tin những chênh lệch lớn và lặp lại.

---

## 📝 CHECKPOINT 5: HOÀN THIỆN BÁO CÁO
* **Trạng thái:** ✅ ĐÃ HOÀN THÀNH
* `report/REPORT.md` đủ mục 1–10 + phụ lục; mọi con số đã đối chiếu lại với `results/*/run.json`.
* Đã quét khóa API: không có trong kho, vết hay báo cáo; `.env` chưa từng được commit.
* Đã hoàn thành phần thưởng **Hướng 6c - Tấn công curator (Red team) và cơ chế phòng vệ** (+5 điểm thưởng). Script `scripts/red_team_curator.py` chạy độc lập, lưu kết quả tại `results/red_team/results.json`, kiểm nghiệm 4 vector tấn công và chứng minh cơ chế phòng thủ nâng cao hạ tỷ lệ bypass từ 50.0% xuống 0.0%. Đã ghi nhận đầy đủ vào Phụ lục báo cáo.

