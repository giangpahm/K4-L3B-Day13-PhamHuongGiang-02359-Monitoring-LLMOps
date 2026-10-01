# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

## 1. Thông tin học viên

- **Họ và tên:** Phạm Hương Giang
- **MSSV:** 02359
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/giangpahm/K4-L3B-Day13-PhamHuongGiang-02359-Monitoring-LLMOps
- **Commit SHA cuối:** điền SHA sau khi commit toàn bộ thay đổi và evidence trong báo cáo này
- **Challenge ID:** chưa có — `config/challenge.json` chính thức chưa được Lab Coach cung cấp trong workspace
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-02359`

## 2. Evidence index

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | [evidence/01-pytest.txt](evidence/01-pytest.txt) |
| Log validator | [evidence/02-log-validator.txt](evidence/02-log-validator.txt) |
| Dashboard validator | [evidence/03-dashboard-validator.txt](evidence/03-dashboard-validator.txt) |
| Structured log | [evidence/04-structured-log.txt](evidence/04-structured-log.txt) |
| PII redaction | [evidence/05-pii-redaction.txt](evidence/05-pii-redaction.txt) |
| Trace list | [evidence/06-trace-list.txt](evidence/06-trace-list.txt) |
| Trace waterfall | [evidence/07-trace-waterfall.txt](evidence/07-trace-waterfall.txt) |
| Trace metadata | [evidence/08-trace-metadata.txt](evidence/08-trace-metadata.txt) |
| Prompt versions | [evidence/09-prompt-versions.txt](evidence/09-prompt-versions.txt) |
| Prompt rollback | [evidence/10-prompt-rollback.txt](evidence/10-prompt-rollback.txt) |
| Dashboard runtime | [evidence/11-dashboard-overview.png](evidence/11-dashboard-overview.png) |
| Incident metric | Chưa có — cần challenge chính thức |
| Incident log | Chưa có — cần challenge chính thức |
| Incident trace | Chưa có — cần challenge chính thức |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---:|---:|---|
| `validate_logs.py` | Không được lưu trước khi sửa | 100/100 | 0 thiếu field, 0 thiếu enrichment, 0 PII leak |
| `validate_dashboard.py` | Không được lưu trước khi sửa | 6/6 | Đủ contract của sáu panel |
| `pytest` | Không được lưu trước khi sửa | 22 passed | Chạy ngày 01/10/2026 |
| Số traces hợp lệ | 0 | ≥ 11 | Mỗi trace có agent/retrieval/generation |
| Số PII leak | Chưa đo | 0 | Validator quét 87 log tại thời điểm evidence |
| Latency P95 / TTFT P95 | Chưa đo | 2,169 ms / 50 ms | Dưới ngưỡng P95 3,000 ms |
| Retrieval success rate | Chưa đo | 100% | 41/41 response có `tool_success=true` |

Dashboard được sinh lại bằng `python scripts/generate_dashboard.py` từ nguồn chuẩn `data/logs.jsonl`.

## 4. Logging và PII

- **Correlation ID:** `CorrelationIdMiddleware` xóa context cũ, nhận `x-request-id` hợp lệ hoặc sinh `req-<8-hex>`, bind vào `structlog`, lưu ở `request.state` và trả lại qua response header.
- **Metadata:** log API có `ts`, `level`, `service`, `event`, `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`; response bổ sung latency, TTFT, token, cost, quality và trạng thái retrieval.
- **PII scrub:** processor `scrub_event` đệ quy qua string/dict/list/tuple và chạy trước `JsonlFileProcessor` lẫn `JSONRenderer`. Email, số điện thoại Việt Nam, CCCD, thẻ thanh toán và passport được thay bằng marker `[REDACTED_*]`.
- **Kiểm chứng:** [PII runtime](evidence/05-pii-redaction.txt) cho thấy ba input giả đã được che; validator độc lập báo 0 leak.

## 5. Tracing và prompt versioning

- Workload do tôi chạy ngày 01/10/2026 tạo trace trong project `day13-k4-l3b-02359`; [danh sách trace](evidence/06-trace-list.txt) ghi 11 ID gần nhất.
- Root `lab-agent-run` có hai child observations: `retrieval` loại `RETRIEVER` và `generation` loại `GENERATION`. `parentObservationId` trong [waterfall](evidence/07-trace-waterfall.txt) chứng minh quan hệ cha-con.
- `correlation_id` xuất hiện trong structured log và metadata của cả root/child, ví dụ `req-5b2360be` nối log với trace `33637eeba04592241d6452c324e006e4`.
- Prompt `day13-chat` v1 có labels `baseline`, `production`; v2 có `candidate`, `latest` sau rollback.
- Trace v1: `33637eeba04592241d6452c324e006e4`; trace v2: `e5c3d1d603ad603e4b6257fd69dc1b2a`.
- Promote đã chuyển `production` sang v2; rollback chuyển lại v1. Trạng thái trước/sau được ghi trong [prompt rollback](evidence/10-prompt-rollback.txt).
- Trace chỉ lưu preview đã scrub và metadata vận hành, không capture raw prompt/output.

## 6. Dashboard, SLO và alerts

- Dashboard có sáu panel: latency/TTFT, traffic, errors/retrieval, cost, tokens và quality. Ảnh runtime hiển thị time range 60 phút, refresh 30 giây, đơn vị và threshold của từng panel.
- Primary SLO trong [`config/slo.yaml`](../config/slo.yaml): 99.5% request trong 28 ngày phải trả `response_sent` với latency ≤ 3,000 ms.
- Error budget là 0.5%; với 10,000 request trong cửa sổ, tối đa 50 request có thể lỗi hoặc chậm hơn ngưỡng.
- Ba alert symptom-based trong [`config/alert_rules.yaml`](../config/alert_rules.yaml): `HighLatencyP95`, `HighRequestErrorRate`, `LowRetrievalSuccessRate`. Mỗi rule có duration, severity, owner `student-02359`, Slack channel và liên kết tới [`docs/alerts.md`](../docs/alerts.md).

## 7. Điều tra challenge

Challenge chính thức chưa thể điều tra vì workspace không có `config/challenge.json`. Theo quy định của lab, file này phải do Lab Coach gửi riêng, nằm trong `.gitignore`, và không được tự tạo/sửa hoặc lấy từ lớp khác. Vì vậy tôi không tạo evidence `12`–`14` giả.

Khi nhận file hợp lệ, quy trình sẽ là: chạy injector và workload challenge; khoanh cửa sổ bất thường trên metric; lọc log trong cửa sổ để lấy `correlation_id`; mở trace cùng ID để tìm span bất thường; ghi challenge ID, root cause, fix action và preventive measure vào phần này.

## 8. Giải thích và tự đánh giá

- **Quyết định kỹ thuật:** scrub toàn bộ event dictionary ở processor chung ngay trước bước render/persist thay vì chỉ scrub `message`. Cách này giảm nguy cơ PII lọt qua field mới hoặc exception payload.
- **Blocker:** API trace legacy của Langfuse trả HTTP 410 cho organization mới. Tôi chuyển phần kiểm chứng sang Observations API v2, vẫn xác minh được trace ID, parent-child tree, metadata, token và cost.
- **Metrics → Logs → Traces:** metric phát hiện cửa sổ có latency/error/quality bất thường; log thu hẹp xuống request cụ thể bằng `correlation_id`; trace cùng ID tách retrieval và generation để xác định bước gây ảnh hưởng; evidence ở span là cơ sở kết luận root cause.
- **Prompt/version và rollback:** lưu version/label trên trace giúp so sánh regression với đúng prompt. Label `production` cho phép promote/rollback mà không sửa code. Token/cost cho biết thay đổi prompt có làm context/output phình lên; SLO biến trải nghiệm mong muốn thành ngưỡng đo và error budget.
- **Điều quan trọng nhất:** observability có giá trị khi metric, log và trace dùng cùng định danh và metadata nhất quán, không phải khi từng nguồn đứng riêng.
- **Hạn chế còn lại:** thiếu challenge chính thức và ba evidence incident; browser tích hợp không khởi tạo được nên evidence Langfuse hiện lưu dưới dạng output API `.txt` thay vì ảnh UI. Không có secret hoặc PII thô trong các file evidence.

## 9. Checklist trước khi nộp

- [x] Tests, log validator và dashboard validator đều đạt.
- [x] Có ≥10 traces trong project cá nhân, waterfall, metadata, prompt v1/v2 và rollback.
- [x] Dashboard runtime đủ sáu panel, time range, đơn vị và threshold.
- [x] Repository chạy lại được theo README; không commit `.env`, key hoặc log thô.
- [ ] Nhận challenge chính thức và bổ sung evidence `12`–`14`.
- [ ] Commit thay đổi cuối, cập nhật Commit SHA ở mục 1, rồi nộp URL + SHA lên LMS/Codelabs.
