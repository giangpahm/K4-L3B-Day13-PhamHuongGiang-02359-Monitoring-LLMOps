# Báo cáo cá nhân — K4-L3B Day 13 Monitoring & LLMOps

## 1. Thông tin học viên

- **Họ và tên:** Phạm Hương Giang
- **MSSV:** 02359
- **Lớp:** K4-L3B
- **Repository URL:** https://github.com/giangpahm/K4-L3B-Day13-PhamHuongGiang-02359-Monitoring-LLMOps
- **Commit SHA cuối:** điền SHA sau khi commit toàn bộ thay đổi và evidence trong báo cáo này
- **Challenge ID:** `day13-k4-l3b-monitoring-llmops-v1`
- **Tên project Langfuse cá nhân:** `day13-k4-l3b-02359`

## 2. Evidence index

| Evidence | Đường dẫn |
|---|---|
| Pytest cuối | [evidence/01-pytest.txt](evidence/01-pytest.txt) |
| Log validator | [evidence/02-log-validator.txt](evidence/02-log-validator.txt) |
| Dashboard validator | [evidence/03-dashboard-validator.txt](evidence/03-dashboard-validator.txt) |
| Structured log | [evidence/04-structured-log.png](evidence/04-structured-log.png) |
| PII redaction | [evidence/05-pii-redaction.png](evidence/05-pii-redaction.png); đủ email/điện thoại/CCCD/thẻ và bảo toàn correlation ID |
| Trace list | [evidence/06-trace-list.png](evidence/06-trace-list.png) |
| Trace waterfall | [evidence/07-trace-waterfall.png](evidence/07-trace-waterfall.png) |
| Trace metadata | [Root metadata](evidence/08a-trace-metadata.png), [Generation model/token/cost](evidence/08b-generation-usage-cost.png) |
| Prompt versions | [evidence/09-prompt-versions.png](evidence/09-prompt-versions.png) |
| Prompt rollback | [Promote production sang v2](evidence/10a-prompt-promoted.png), [Rollback production về v1](evidence/10b-prompt-rollback.png) |
| Dashboard runtime | [evidence/11-dashboard-overview.png](evidence/11-dashboard-overview.png) |
| Incident metric | [evidence/12-incident-metric.png](evidence/12-incident-metric.png) |
| Incident log | [evidence/13-incident-log.png](evidence/13-incident-log.png) |
| Incident trace | [evidence/14-incident-trace.png](evidence/14-incident-trace.png) |

## 3. Kết quả kỹ thuật

| Nội dung | Baseline | Kết quả cuối | Nhận xét |
|---|---:|---:|---|
| `validate_logs.py` | Không được lưu trước khi sửa | 100/100 | 0 thiếu field, 0 thiếu enrichment, 0 PII leak |
| `validate_dashboard.py` | Không được lưu trước khi sửa | 6/6 | Đủ contract của sáu panel |
| `pytest` | Không được lưu trước khi sửa | 24 passed | Chạy ngày 01/10/2026 sau test hồi quy PII |
| Số traces hợp lệ | 0 | ≥ 11 | Mỗi trace có agent/retrieval/generation |
| Số PII leak | Chưa đo | 0 | Validator quét 100 log sau challenge |
| Latency P95 / TTFT P95 | Chưa đo | 4,664 ms / 50 ms | P95 vượt SLO sau khi inject `rag_slow` |
| Retrieval success rate | Chưa đo | 100% | 46/46 response có `tool_success=true` |

Dashboard được sinh lại bằng `python scripts/generate_dashboard.py` từ nguồn chuẩn `data/logs.jsonl`.

## 4. Logging và PII

- **Correlation ID:** `CorrelationIdMiddleware` xóa context cũ, nhận `x-request-id` hợp lệ hoặc sinh `req-<8-hex>`, bind vào `structlog`, lưu ở `request.state` và trả lại qua response header.
- **Metadata:** log API có `ts`, `level`, `service`, `event`, `correlation_id`, `user_id_hash`, `session_id`, `feature`, `model`, `env`; response bổ sung latency, TTFT, token, cost, quality và trạng thái retrieval.
- **PII scrub:** processor `scrub_event` đệ quy qua string/dict/list/tuple và chạy trước `JsonlFileProcessor` lẫn `JSONRenderer`. Email, số điện thoại Việt Nam, CCCD, thẻ thanh toán và passport được thay bằng marker `[REDACTED_*]`.
- **Kiểm chứng:** [PII runtime](evidence/05-pii-redaction.png) cho thấy cả email, điện thoại, CCCD và thẻ trong bốn input giả đã được che trong persisted runtime log; `correlation_id` vẫn được giữ nguyên và validator độc lập báo 0 leak. Test hồi quy cũng bảo đảm chuỗi có dạng `req-A1234567` không bị regex passport che nhầm.

## 5. Tracing và prompt versioning

- Workload do tôi chạy ngày 01/10/2026 tạo trace trong project `day13-k4-l3b-02359`; [danh sách trace](evidence/06-trace-list.txt) ghi 11 ID gần nhất.
- Root `lab-agent-run` có hai child observations: `retrieval` loại `RETRIEVER` và `generation` loại `GENERATION`. `parentObservationId` trong [waterfall](evidence/07-trace-waterfall.txt) chứng minh quan hệ cha-con.
- `correlation_id` xuất hiện trong structured log và metadata của cả root/child, ví dụ `req-5b2360be` nối log với trace `33637eeba04592241d6452c324e006e4`.
- [Ảnh versions](evidence/09-prompt-versions.png) cho thấy v1 có `baseline`, `production` và v2 có `candidate`, `latest` trước lần promote được chụp sau đó.
- Trace v1: `33637eeba04592241d6452c324e006e4`; trace v2: `e5c3d1d603ad603e4b6257fd69dc1b2a`.
- Lần promote/rollback qua API trước đây được ghi trong [output hỗ trợ](evidence/10-prompt-rollback.txt). Ảnh [10a](evidence/10a-prompt-promoted.png), chụp lúc 12:19 ngày 01/10/2026, cho thấy `production` ở v2; ảnh [10b](evidence/10b-prompt-rollback.png), chụp lúc 12:30 cùng ngày, cho thấy nhãn đã quay về v1, còn v2 giữ `candidate` và `latest`. Ảnh 10b có tên project cá nhân trong khung hình.
- Trace chỉ lưu preview đã scrub và metadata vận hành, không capture raw prompt/output.

## 6. Dashboard, SLO và alerts

- Dashboard có sáu panel: latency/TTFT, traffic, errors/retrieval, cost, tokens và quality. Ảnh runtime hiển thị time range 60 phút, refresh 30 giây, đơn vị và threshold của từng panel.
- Primary SLO trong [`config/slo.yaml`](../config/slo.yaml): 99.5% request trong 28 ngày phải trả `response_sent` với latency ≤ 3,000 ms.
- Error budget là 0.5%; với 10,000 request trong cửa sổ, tối đa 50 request có thể lỗi hoặc chậm hơn ngưỡng.
- Ba alert symptom-based trong [`config/alert_rules.yaml`](../config/alert_rules.yaml): `HighLatencyP95`, `HighRequestErrorRate`, `LowRetrievalSuccessRate`. Mỗi rule có duration, severity, owner `student-02359`, Slack channel và liên kết tới [`docs/alerts.md`](../docs/alerts.md).

## 7. Điều tra challenge

- **Challenge:** `day13-k4-l3b-monitoring-llmops-v1`, incident `rag_slow`, feature `monitoring`, ngưỡng challenge 2.000 ms. File chính thức được giữ trong `.gitignore` và không được commit.
- **Metric:** sau khi enable incident và chạy năm query chính thức, 5/5 request vượt ngưỡng. Trong cửa sổ `06:00:26.120262Z`–`06:00:44.817903Z`, latency min/avg/P95/max là 4.660/4.672,6/4.707/4.707 ms. [Evidence metric](evidence/12-incident-metric.png) cho thấy P95 vượt cả ngưỡng challenge 2.000 ms và SLO dashboard 3.000 ms.
- **Log:** request chậm nhất có `correlation_id=req-7fe7b69a`, session `k4-l3b-challenge-s02`, latency 4.707 ms, TTFT 50 ms, `tool_name=retrieval`, `tool_success=true`. Vì request thành công nhưng chậm, đây là latency degradation chứ không phải retrieval failure. Xem [evidence log](evidence/13-incident-log.png).
- **Trace:** session trên nối tới trace `f7bd7597078cd53c2e503dee321d638b` trong project `day13-k4-l3b-02359`. Root `lab-agent-run` kéo dài 4.708 ms; child `retrieval` 2.502 ms; child `generation` chỉ 153 ms. `retrieval` có parent là root và riêng span này đã vượt ngưỡng 2.000 ms. Xem [evidence trace](evidence/14-incident-trace.png).
- **Root cause:** độ trễ được inject tại RAG retrieval (`rag_slow`), không phải generation. Prompt fetch cũng rơi về local fallback trong lần chạy do timeout mạng, làm tổng root latency cao hơn, nhưng dấu hiệu quyết định của challenge là retrieval span 2.502 ms vượt ngưỡng trong khi generation chỉ 153 ms.
- **Fix action:** tắt incident ngay sau workload; xác nhận endpoint control trả `rag_slow=false`. Trong vận hành thật, rollback/revert thay đổi retrieval gần nhất, đặt timeout và fallback cho backend RAG, rồi chạy lại cùng query để xác nhận P95 trở về dưới SLO.
- **Preventive measure:** theo dõi riêng histogram latency của retrieval theo feature/model, alert trên retrieval P95 và end-to-end P95, đặt timeout/circuit breaker, cache kết quả phù hợp, và duy trì `correlation_id`/session trong log–trace để khoanh vùng nhanh.

## 8. Giải thích và tự đánh giá

- **Quyết định kỹ thuật:** scrub toàn bộ event dictionary ở processor chung ngay trước bước render/persist thay vì chỉ scrub `message`. Cách này giảm nguy cơ PII lọt qua field mới hoặc exception payload.
- **Blocker:** API trace legacy của Langfuse trả HTTP 410 cho organization mới. Tôi chuyển phần kiểm chứng sang Observations API v2, vẫn xác minh được trace ID, parent-child tree, metadata, token và cost.
- **Metrics → Logs → Traces:** metric phát hiện cửa sổ có latency/error/quality bất thường; log thu hẹp xuống request cụ thể bằng `correlation_id`; trace cùng ID tách retrieval và generation để xác định bước gây ảnh hưởng; evidence ở span là cơ sở kết luận root cause.
- **Prompt/version và rollback:** lưu version/label trên trace giúp so sánh regression với đúng prompt. Label `production` cho phép promote/rollback mà không sửa code. Token/cost cho biết thay đổi prompt có làm context/output phình lên; SLO biến trải nghiệm mong muốn thành ngưỡng đo và error budget.
- **Điều quan trọng nhất:** observability có giá trị khi metric, log và trace dùng cùng định danh và metadata nhất quán, không phải khi từng nguồn đứng riêng.
- **Hạn chế còn lại:** lần challenge có thêm độ trễ do Langfuse prompt fetch timeout và dùng local fallback; phân tích đã tách riêng yếu tố này khỏi injected retrieval delay bằng thời lượng từng span. Ảnh generation baseline hiện thấy tổng 115 tokens nhưng chưa có breakdown trực quan input/output. Một số ảnh chi tiết không có tên project trong khung hình, nhưng có trace ID hoặc prompt name để đối chiếu với ảnh 06/10b.

## 9. Checklist trước khi nộp

- [x] Tests, log validator và dashboard validator đều đạt.
- [x] Có ảnh ≥10 root observations trong project cá nhân, waterfall và prompt v1/v2.
- [x] Có ảnh 04–05, 08a và 10b; ảnh 10b chứng minh `production` trở về v1 sau promote.
- [x] Runtime redaction đủ email/điện thoại/CCCD/thẻ; ảnh 05 đã chụp lại với terminal sạch.
- [x] Dashboard runtime đủ sáu panel, time range, đơn vị và threshold.
- [x] Repository chạy lại được theo README; không commit `.env`, key hoặc log thô.
- [x] Challenge chính thức đã được điều tra; evidence `12`–`14` nối metric → log → trace.
- [ ] Commit thay đổi cuối, cập nhật Commit SHA ở mục 1, rồi nộp URL + SHA lên LMS/Codelabs.
