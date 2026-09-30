# Template Alert và Runbook

Mỗi alert phải dựa trên triệu chứng người dùng hoặc SLO, không dựa trực tiếp vào tên implementation nội bộ.

## Alert mẫu để tham khảo

Ví dụ dưới đây minh họa mức độ cụ thể cần có. Học viên không cần copy nguyên, nhưng ba alert trong bài nộp nên rõ ràng tương tự: điều kiện là gì, kéo dài bao lâu, ảnh hưởng tới user ra sao và người trực cần kiểm tra gì trước.

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency P95 của `response_sent.latency_ms`
- Điều kiện và thời gian duy trì: `p95(latency_ms) > 3000ms` trong 5 phút
- Ảnh hưởng tới người dùng: người dùng phải chờ lâu hơn trước khi nhận câu trả lời
- Ba bước kiểm tra đầu tiên:
  1. Mở dashboard latency để xác nhận P95/P99 và khoảng thời gian tăng.
  2. Lọc `data/logs.jsonl` trong khoảng đó, lấy một `correlation_id` có `latency_ms` cao.
  3. Mở trace cùng `correlation_id` trên Langfuse, so sánh các span chính để xác định bước nào bất thường.
- Mitigation tạm thời: dựa trên evidence thực tế để rollback prompt, khôi phục cấu hình liên quan, tắt practice scenario hoặc giảm tải khi demo.
- Owner: `student-<MSSV>`

## Alert 1

- Tên: `HighLatencyP95`
- Severity: `warning`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: latency của request thành công trong primary SLO.
- Điều kiện và thời gian duy trì: `p95(response_sent.latency_ms) > 3000ms` trong 5 phút.
- Ảnh hưởng tới người dùng: phần chậm nhất của lưu lượng phải chờ quá lâu để nhận câu trả lời.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận P95/P99 và TTFT trên panel latency trong đúng khoảng cảnh báo.
  2. Lọc log `response_sent` có latency cao và lấy một `correlation_id` đại diện.
  3. Mở trace cùng correlation ID, so sánh thời gian retrieval và generation.
- Mitigation tạm thời: rollback prompt/config vừa thay đổi nếu generation tăng; tắt scenario gây chậm hoặc giảm tải nếu retrieval tăng.
- Owner: `student-02359`

## Alert 2

- Tên: `HighRequestErrorRate`
- Severity: `critical`
- Duration: `5m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: tỷ lệ request tốt trong primary SLO.
- Điều kiện và thời gian duy trì: `error_rate_pct > 2%` trong 5 phút.
- Ảnh hưởng tới người dùng: nhiều request không nhận được câu trả lời thành công.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận error rate và nhóm `error_type` trên panel errors.
  2. Lọc `request_failed`, chọn một correlation ID trong cửa sổ sự cố.
  3. Mở trace tương ứng để tìm observation lỗi và status message.
- Mitigation tạm thời: khôi phục cấu hình gần nhất, vô hiệu hóa incident scenario và chuyển sang fallback an toàn khi phù hợp.
- Owner: `student-02359`

## Alert 3

- Tên: `LowRetrievalSuccessRate`
- Severity: `warning`
- Duration: `10m`
- Kênh thông báo: Slack `#k4-l3b-alerts`
- SLI/SLO liên quan: guardrail retrieval success tối thiểu 90%.
- Điều kiện và thời gian duy trì: `retrieval_success_rate_pct < 90%` trong 10 phút.
- Ảnh hưởng tới người dùng: câu trả lời có thể thiếu context hoặc thất bại hoàn toàn.
- Ba bước kiểm tra đầu tiên:
  1. Xác nhận retrieval success và error type trên panel errors.
  2. Lọc log có `tool_name=retrieval` và `tool_success=false`, lấy correlation ID.
  3. Mở trace tương ứng, kiểm tra retrieval observation và dữ liệu đầu vào đã scrub.
- Mitigation tạm thời: dùng fallback document an toàn, khôi phục cấu hình retrieval và giảm concurrency nếu backend quá tải.
- Owner: `student-02359`
