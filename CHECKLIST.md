# BẢNG CHECKLIST KIẾN THỨC & QUY TRÌNH THỰC HIỆN LAB
## Chủ đề: Self-Evolving Agentic & Multi-Agent Harness

Tài liệu này hệ thống hóa toàn bộ **kiến thức cốt lõi**, **nguyên lý vận hành**, **checklist tự đánh giá** và **các mốc thực hành** giúp bạn nắm chắc kiến thức và hoàn thành bài lab đạt điểm tối đa.

---

## MỤC LỤC
1. [Hệ thống Kiến thức Trọng tâm Cần Hiểu](#1-hệ-thống-kiến-thức-trọng-tâm-cần-hiểu)
   - [A. Khung điều khiển tác tử (Agent Harness) & Sandbox](#a-khung-điều-khiển-tác-tử-agent-harness--sandbox)
   - [B. Đa tác tử (Multi-Agent) & Cơ chế Subagents](#b-đa-tác-tử-multi-agent--cơ-chế-subagents)
   - [C. Tác tử tự tiến hóa (Self-Evolving) qua Skill Curation](#c-tác-tử-tự-tiến-hóa-self-evolving-qua-skill-curation)
   - [D. Phương pháp luận Thí nghiệm Khoa học](#d-phương-pháp-luận-thí-nghiệm-khoa-học)
2. [Checklist Tự Kiểm Tra Mức Độ Hiểu Bài (Theory Self-Check)](#2-checklist-tự-kiểm-tra-mức-độ-hiểu-bài)
3. [Checklist Quy Trình Thực Hành Từng Bước (Implementation & Checkpoints)](#3-checklist-quy-trình-thực-hành-từng-bước)
4. [Checklist Quy Định & Phòng Tránh Trừ Điểm (Strict Rubric Checklist)](#4-checklist-quy-định--phòng-tránh-trừ-điểm)

---

## 1. HỆ THỐNG KIẾN THỨC TRỌNG TÂM CẦN HIỂU

### A. Khung điều khiển tác tử (Agent Harness) & Sandbox
* **Agent Harness là gì?** Là toàn bộ phần mềm bọc xung quanh LLM: quản lý vòng lặp suy luận - hành động (ReAct loop), cung cấp công cụ (tools), quản lý bộ nhớ, định hình system prompt và điều phối ngữ cảnh. Deep Agents (dựa trên LangChain) là một Agent Harness.
* **Cơ chế Sandbox & Cô lập Môi trường:**
  * Mỗi tác vụ khi chạy được copy sang một thư mục tạm riêng biệt bên ngoài kho mã nguồn (`tempfile.mkdtemp`), xóa sạch sau khi chạy để tránh làm bẩn dữ liệu gốc (`tasks/<id>/workspace`).
  * **Quy ước đường dẫn kép:**
    * *File Tools* (`read_file`, `write_file`, `edit_file`, `ls`): nhận diện đường dẫn ảo với gốc là sandbox (`workspace/x` hoặc `/workspace/x`).
    * *Shell Tool* (`execute`): chạy thực tế trong hệ điều hành với thư mục làm việc là sandbox root. Do đó shell **chỉ nhận đường dẫn tương đối** (`workspace/x`), nếu dùng `/workspace/x` shell sẽ báo lỗi `No such file or directory`.
* **Bảo mật biến môi trường:** Backend (`LocalShellBackend`) phải đặt `inherit_env=False` và chỉ cấp `PATH` an toàn, ngăn tác tử đọc được biến môi trường chứa API Key (`AZURE_OPENAI_KEY`, `DEEPSEEK_API_KEY`).

---

### B. Đa tác tử (Multi-Agent) & Cơ chế Subagents
* **Nguyên lý Context Isolation (Cô lập ngữ cảnh):**
  * Tác tử chính giao việc cho subagent qua công cụ `task`.
  * Mỗi khi subagent được gọi, một phiên làm việc mới được tạo ra. Subagent **không thấy** lịch sử hội thoại trước đó của tác tử chính; nó chỉ thấy nội dung prompt trong lệnh giao việc.
  * Tác tử chính bắt buộc phải truyền đầy đủ quy tắc, đường dẫn tệp vào lời gọi `task`.
* **Subagent mặc định vs Subagent tự định nghĩa:**
  * Deep Agents luôn có sẵn subagent mặc định tên là `general-purpose`.
  * Trong điều kiện `subagents`, ta bổ sung thêm các subagent chuyên trách (ví dụ: `explorer` chuyên đọc và phân tích, `implementer` chuyên sửa mã/chạy test, `reviewer` kiểm tra độc lập).
  * Subagent tự định nghĩa không tự động kế thừa `BASE_PROMPT` của tác tử chính, nên cần được nối thêm `PATHS_NOTE`.
* **Đánh đổi về chi phí (Trade-offs):**
  * Đa tác tử phân chia nhiệm vụ rõ ràng nhưng tiêu tốn lượng token gấp nhiều lần (thường từ 2x đến 15x) do phát sinh ngữ cảnh mới và nhiều lượt gọi LLM lặp lại.
  * Nếu tác tử chính tự giải quyết được công việc, việc không gọi subagent (`subagent_calls = 0`) là hành vi hoàn toàn hợp lệ và tối ưu chi phí.

---

### C. Tác tử tự tiến hóa (Self-Evolving) qua Skill Curation
* **Tiến hóa ở tầng ngữ cảnh (Context Layer Evolution):**
  * Khác với Fine-tuning (cập nhật trọng số mô hình - tốn kém, khó kiểm soát), tiến hóa ở tầng ngữ cảnh là việc hệ thống tự cải thiện **tri thức thủ tục (procedural knowledge)** qua các file hướng dẫn (`SKILL.md`).
* **Cơ chế nạp dần (Progressive Disclosure):**
  * Tác tử không đọc toàn bộ nội dung của tất cả các skill ngay từ đầu (tránh làm tràn context và tốn token).
  * Khởi đầu, tác tử chỉ nhìn thấy `name` và `description` trong YAML frontmatter.
  * Khi gặp tác vụ phù hợp với `description`, tác tử mới chủ động dùng `read_file` để nạp toàn bộ nội dung của `SKILL.md`.
* **Tiêu chuẩn chất lượng của một Skill tốt:**
  * **Tính tổng quát:** Đúc kết quy trình/quy ước chung (ví dụ: cách xử lý timezone, quy ước commit/changelog, checklist làm sạch dữ liệu), không sao chép tên biến, tên hàm, số liệu riêng của bài học.
  * **Tính mệnh lệnh & Ngắn gọn:** Dưới 40–80 dòng, trình bày dạng checklist từng bước (`1. ... 2. ...`), dễ kiểm chứng.
  * **Trường `description`:** Bắt đầu bằng *"Use when ..."*, chỉ rõ tình huống kích hoạt để tác tử biết khi nào cần đọc.
  * **Không rò rỉ dữ liệu (No Data Leakage):** Không chứa bất kỳ từ khóa, tên file hay định danh nào thuộc về tập đánh giá (`eval_markers`).

---

### D. Phương pháp luận Thí nghiệm Khoa học
* **Tách tập Học (Learn) và tập Đánh giá (Eval):**
  * 3 họ bài toán (`code`, `data`, `logs`), mỗi họ có 1 bài `learn` và 1 bài `eval`.
  * Ở bài `learn`: bot chấm điểm (`check.py`) trả về `detail` mô tả quy ước bị vi phạm (feedback). Curator dựa vào đây để học.
  * Ở bài `eval`: bot chấm điểm ẩn hoàn toàn trường `detail` (`c["detail"] = ""`). Bài `eval` bổ sung quy ước mới để kiểm tra xem tác tử có bị quá khớp (overfitting) với bài học hay không.
* **Quy trình Đóng băng (Freeze Protocol):**
  * Để đảm bảo tính trung thực khoa học, nhóm phải **viết giả thuyết trước khi thấy điểm bài eval**, commit vào git, sau đó tạo git tag `freeze` chốt toàn bộ kỹ năng trong `skills/auto/`.
  * Mọi bài chạy chính thức trên tập đánh giá phải diễn ra sau tag `freeze` và không được làm thay đổi nội dung skill (`skills_modified == False`).
* **Phân biệt Check kỹ thuật vs Check quy ước tổ chức:**
  * *Check kỹ thuật:* Chức năng chạy đúng, test ban đầu pass, parse đúng format.
  * *Check quy ước (`rule_`):* Quy định riêng của tổ chức Acme không có trong đề bài (ví dụ: type annotations, file regression tests, CHANGELOG unreleased). Kỹ năng tự sinh phát huy tác dụng lớn nhất ở nhóm check quy ước này.

---

## 2. CHECKLIST TỰ KIỂM TRA MỨC ĐỘ HIỂU BÀI

Hãy tích `[x]` vào các câu hỏi bạn đã hiểu và có thể giải thích rõ ràng:

### Khung điều khiển & Sandbox
- [x] Tôi giải thích được tại sao `LocalShellBackend` phải dùng `inherit_env=False` và nguy cơ khi dùng `inherit_env=True` là gì.
- [x] Tôi phân biệt được tại sao lệnh `execute` (shell) báo lỗi khi chạy đường dẫn `/workspace/app.py` nhưng `read_file` thì không.
- [x] Tôi hiểu tại sao hệ thống cần chạy tác vụ trong thư mục tạm (`sandbox`) thay vì chạy trực tiếp trong thư mục `tasks/`.
- [x] Tôi biết cách `UsageMetadataCallbackHandler` cộng dồn token của cả tác tử chính lẫn các subagent.

### Đa tác tử & Subagents
- [x] Tôi hiểu khái niệm Context Isolation và giải thích được vì sao subagent không biết tác tử chính đã làm những gì trước đó.
- [x] Tôi nắm rõ định dạng của một subagent (`name`, `description`, `system_prompt`) và vai trò của từng trường.
- [x] Tôi giải thích được tại sao `PATHS_NOTE` phải được nối vào `system_prompt` của mỗi subagent.
- [x] Tôi hiểu vì sao `subagent_calls = 0` vẫn là một kết quả hợp lệ và cách phân tích hiện tượng này trong báo cáo.
- [x] Tôi nắm được sự đánh đổi (trade-off) về chi phí token khi sử dụng mô hình đa tác tử so với đơn tác tử.

### Tác tử Tự tiến hóa (Self-Evolving & Curator)
- [x] Tôi hiểu sự khác biệt giữa tiến hóa ở tầng ngữ cảnh (context layer) và tinh chỉnh trọng số (fine-tuning).
- [x] Tôi nắm vững cơ chế Progressive Disclosure (nạp dần) và vai trò quyết định của trường `description` trong `SKILL.md`.
- [x] Tôi phân biệt được thế nào là skill tổng quát (tốt) và skill bị quá khớp/học vẹt (xấu).
- [x] Tôi giải thích được tại sao `curator.py` chỉ được phép đọc `run.json` của tác vụ `role == "learn"` và tuyệt đối bỏ qua `role == "eval"`.
- [x] Tôi hiểu `eval_markers` trong `validate_skill` làm nhiệm vụ gì để ngăn chặn Data Leakage.

### Phương pháp Đánh giá & Khoa học
- [x] Tôi giải thích được vì sao bot chấm điểm xóa rỗng trường `detail` đối với các tác vụ đánh giá (`eval`).
- [x] Tôi hiểu lý do vì sao phải commit giả thuyết (H1, H2, H3) TRƯỚC KHI tạo git tag `freeze`.
- [x] Tôi hiểu cách script `verify_freeze.py` hoạt động để phát hiện gian lận hoặc sai sót quy trình.
- [x] Tôi phân biệt được hai nhóm lỗi: lỗi kỹ thuật (A-D) và lỗi vi phạm quy ước tổ chức (E - `rule_`).
- [ ] Tôi hiểu khái niệm đo độ nhiễu (noise) bằng cách so sánh điểm của cùng bộ skill trước và sau khi đóng băng.

---

## 3. CHECKLIST QUY TRÌNH THỰC HÀNH TỪNG BƯỚC

### Giai đoạn 0: Chuẩn bị & Làm quen
- [x] Đã clone repo, tạo môi trường ảo Python 3.11+, cài đặt `pip install -e .`.
- [x] Đã tạo file `.env` từ `.env.example` và điền khóa API chính xác.
- [x] Đã tạo file báo cáo: `mkdir -p report && cp REPORT_TEMPLATE.md report/REPORT.md`.
- [x] Chạy kiểm tra môi trường: `pytest tests/test_01_provided.py` ➔ **Đạt 12/12 test**.
- [x] Chạy khám phá harness: `python scripts/tour.py` (zero token) và điền câu trả lời mục 3 trong `report/REPORT.md`.

### Giai đoạn 1: Lập trình Harness
- [x] **Bước 1.1:** Cài đặt `src/lab/subagents.py` (hàm `get_subagents()`).
  - Kiểm tra: `pytest tests/test_02_agent.py -k subagents` ➔ **PASSED**.
- [x] **Bước 1.2:** Cài đặt `src/lab/agent.py` (`make_backend`, `build_agent`).
  - Kiểm tra: `pytest tests/test_02_agent.py` ➔ **PASSED toàn bộ 9 tests**.
- [x] **Bước 1.3:** Cài đặt `src/lab/runner.py` (`run_task`).
  - Kiểm tra: `pytest tests/test_03_runner.py` ➔ **PASSED toàn bộ 6 tests**.
- [x] **Bước 1.4:** Chạy thử tác vụ thực tế đầu tiên:
  - Lệnh: `python -m lab.runner --condition baseline --tasks data-learn`.
  - Kiểm tra file `results/baseline/data-learn/run.json` và `trace.md` đã được ghi chuẩn xác.

### Giai đoạn 2: Chạy Tập Học & Phân loại Lỗi
- [x] Chạy nốt baseline trên tập học:
  - `python -m lab.runner --condition baseline --tasks code-learn logs-learn`.
- [x] Chạy điều kiện subagents trên tập học:
  - `python -m lab.runner --condition subagents --tasks learn`.
- [x] Đọc các check fail trong `run.json` và `trace.md`, điền bảng Phân loại lỗi (Taxonomy nhóm A đến G) vào mục 4 báo cáo kèm bằng chứng trích dẫn.
- [x] Phân tích điều kiện `subagents` vào mục 5 báo cáo (`subagent_calls`, token, lý do gọi/không gọi).

### Giai đoạn 3: Tác tử Tự tiến hóa (Curator)
- [x] Cài đặt `curate_skills` trong `src/lab/curator.py`.
  - Kiểm tra: `pytest tests/test_04_curator.py` ➔ **PASSED cả 2 tests**.
- [x] Chạy tự sinh skill: `python -m lab.curator`.
  - Kiểm tra thư mục `skills/auto/` có ít nhất 1 skill hợp lệ dạng `skills/auto/<tên-skill>/SKILL.md`.
- [x] Đánh giá chất lượng skill sinh ra và điền mục 6 báo cáo (tính tổng quát, đúng/sai, độ dài, trigger). *(Được phép xóa skill xấu hoặc chạy lại tối đa 2 lần, tuyệt đối không sửa tay)*.
- [x] Chạy thử nghiệm tác tử có skill trên tập học:
  - `python -m lab.runner --condition skills-auto --tasks learn`.
  - Kiểm tra trường `skills_read` trong `run.json` xem tác tử có đọc skill không.
  - Sao lưu kết quả trước khi sang Phần 4: `mv results/skills-auto results/skills-auto-dev` (đã làm; dùng `mv` như GUIDE 4.2 để thư mục chính thức trống trước khi chạy lại).
  - Ghi chú: curator chạy 2 lần (lần 1 xóa vì skill thiếu nội dung quy ước, xem REPORT mục 6); họ `data` không có skill.

### Giai đoạn 4: Đóng băng & Đánh giá Chính thức (CỰC KỲ QUAN TRỌNG)
- [x] **Bước 4.1:** Viết 3 giả thuyết H1, H2, H3 vào mục 2 của `report/REPORT.md`.
- [ ] **Bước 4.2:** Commit giả thuyết lên Git:
  ```bash
  git add -A && git commit -m "hypotheses"
  ```
- [ ] **Bước 4.3:** Chốt skill và tạo tag `freeze`:
  ```bash
  git add -A && git commit --allow-empty -m "freeze skills" && git tag freeze
  ```
- [ ] **Bước 4.4:** Chạy các tác vụ đánh giá và chạy lại toàn bộ với skill đóng băng:
  ```bash
  python -m lab.runner --condition baseline --tasks eval
  python -m lab.runner --condition subagents --tasks eval
  python -m lab.runner --condition skills-auto --tasks all
  ```
- [ ] **Bước 4.5:** Chạy kiểm tra tính hợp lệ của quy trình đóng băng:
  ```bash
  python scripts/verify_freeze.py
  ```
  👉 **BẮT BUỘC KẾT QUẢ PHẢI IN RA: `checked ... runs of skill conditions: OK` (Exit code 0)**.
- [ ] **Bước 4.6:** Xuất bảng so sánh tổng hợp:
  ```bash
  python -m lab.compare > report/table.md
  python scripts/check_breakdown.py
  ```

### Giai đoạn 5: Hoàn thiện Báo cáo
- [ ] Dán nội dung `report/table.md` và kết quả `check_breakdown.py` vào mục 7.
- [ ] Hoàn thành mục 8 (Phân tích chi tiết 6 câu hỏi: điểm số, check kỹ thuật vs quy ước, cơ chế vết, chi phí token, rò rỉ/quá khớp, độ nhiễu).
- [ ] Hoàn thành mục 9 (Nêu ít nhất 3 hạn chế thực tế của thí nghiệm và ảnh hưởng của chúng).
- [ ] Hoàn thành mục 10 (Kết luận ngắn gọn tối đa 5 câu).
- [ ] (Tùy chọn) Thực hiện 1 hướng mở rộng trong Phần 6 và ghi vào Phụ lục để nhận tối đa +5 điểm thưởng.

---

## 4. CHECKLIST QUY ĐỊNH & PHÒNG TRÁNH TRỪ ĐIỂM

Trước khi nộp bài, hãy rà soát từng mục sau để không bị trừ điểm oan theo [RUBRIC.md](file:///Users/dophi/Desktop/K4-DAY20-MULTIAGENTS-DoNgocPhi-2A202602531/RUBRIC.md):

- [ ] **KHÔNG lộ API Key (-10 điểm):**
  - Kiểm tra `git status` và `git log`: file `.env` tuyệt đối không được thêm vào git.
  - File `trace.md` và `report/REPORT.md` không chứa chuỗi secret key nào.
- [ ] **KHÔNG sửa tay file skill hoặc gian lận nội dung (-10 điểm):**
  - Mọi file trong `skills/auto/` phải do `python -m lab.curator` sinh ra tự động.
  - Không có nội dung sao chép từ đề bài hoặc đáp án của các tác vụ đánh giá (`*-eval`).
- [ ] **KHÔNG sửa các file hệ thống (-10 điểm):**
  - Thư mục `tests/`, `tasks/`, `scripts/` giữ nguyên gốc.
  - Các file mã nguồn có sẵn (`model.py`, `tasks.py`, `grading.py`, `testing.py`, `compare.py`, các hằng số prompt) không bị chỉnh sửa.
- [ ] **Tuân thủ quy trình Freeze (-10 điểm):**
  - Commit `hypotheses` phải nằm trước tag `freeze` trong lịch sử git.
  - `skills/auto/` không có thay đổi nào sau thời điểm gắn tag `freeze`.
  - Không có lần chạy `skills-auto` nào bị gắn cờ `skills_modified = True`.
  - Lệnh `python scripts/verify_freeze.py` chạy thành công không báo bất kỳ lỗi nào.
- [ ] **Khớp dữ liệu báo cáo (-5 đến -10 điểm):**
  - Các số điểm, số token, số tool calls trong `report/REPORT.md` và `report/table.md` khớp 100% với dữ liệu JSON trong `results/`.
- [ ] **Sản phẩm nộp đầy đủ:**
  - 4 file mã nguồn: `src/lab/agent.py`, `subagents.py`, `runner.py`, `curator.py`.
  - Thư mục `skills/auto/`.
  - Thư mục `results/` (đủ `run.json` và `trace.md` của cả 3 điều kiện x 6 tác vụ).
  - Báo cáo hoàn thiện: `report/REPORT.md` và `report/table.md`.

