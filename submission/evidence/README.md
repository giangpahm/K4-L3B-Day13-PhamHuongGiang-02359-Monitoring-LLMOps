# Evidence cá nhân

Đặt ảnh hoặc output text dùng để chấm vào thư mục này. Danh sách đầy đủ xem tại [docs/SUBMISSION.md](../../docs/SUBMISSION.md).

Tên file gợi ý:

```text
01-pytest.png
02-log-validator.png
03-dashboard-validator.png
04-structured-log.png
05-pii-redaction.png
06-trace-list.png
07-trace-waterfall.png
08-trace-metadata.png
09-prompt-versions.png
10-prompt-rollback.png
11-dashboard-overview.png
12-incident-metric.png
13-incident-log.png
14-incident-trace.png
```

Có thể dùng `.txt` cho output của tests/validators. Có thể tách dashboard thành nhiều ảnh nếu một ảnh không đọc rõ.

Ảnh `04`, `05`, `13` lấy từ terminal hoặc `data/logs.jsonl`. Ảnh `06`–`10`, `14` lấy từ project Langfuse cá nhân `day13-k4-l3b-<MSSV>` và nên nhìn thấy tên project. Không mở/chụp trang API Keys.

Từ `submission/REPORT.md`, dẫn ảnh bằng đường dẫn tương đối:

```markdown
![Trace waterfall](evidence/07-trace-waterfall.png)
```

Không commit secret, API key, PII thô hoặc evidence của học viên/lớp khác.

## Kiểm tra ảnh ngày 01/10/2026

| File hiện có | Kết quả kiểm tra |
|---|---|
| `06-trace-list.png` | Đúng project, lọc root, thấy hơn 10 dòng và tổng 21 root observations. |
| `07-trace-waterfall.png` | Có trace ID và timeline root/generation/retrieval, chữ rõ. Retrieval hiển thị 0 ms do độ phân giải thời gian; không cần sửa ảnh. |
| `08b-generation-usage-cost.png` | Có model, prompt v1, 115 tokens và USD 0.001389. Nên bổ sung ảnh breakdown input/output nếu giao diện có. |
| `09-prompt-versions.png` | Có v1/v2 và labels baseline/candidate/production; trạng thái trước promote. |
| `10a-prompt-promoted.png` | Production ở v2, chụp trước ảnh rollback. |
| `04-structured-log.png` | Đủ timestamp, event, correlation ID, model, env, feature và latency. |
| `05-pii-redaction.png` | Terminal sạch; đủ email/điện thoại/CCCD/thẻ đã che, correlation ID được bảo toàn và có dòng PASS. |
| `08a-trace-metadata.png` | Có correlation ID, model, prompt source/name/version/label; không lộ key. |
| `10b-prompt-rollback.png` | Đúng project, production về v1, v2 giữ candidate/latest; chụp sau 10a. |

Incident 12–14 đã hoàn tất cho challenge `day13-k4-l3b-monitoring-llmops-v1`: metric và log chọn request `req-7fe7b69a`; trace `f7bd7597078cd53c2e503dee321d638b` cho thấy retrieval 2.502 ms vượt ngưỡng 2.000 ms. Có thể bổ sung breakdown input/output tokens cho 08b nếu giao diện có.

Ảnh `Ảnh chụp màn hình 2026-10-01 123005.png` có nội dung thừa, chồng chữ và chỉ thấy một phần kết quả; đã chuyển sang `.tmp/evidence-review/` (ngoài bộ evidence nộp, được gitignore) để có thể khôi phục. Các ảnh dùng để nộp được đổi tên, không chỉnh sửa pixel hoặc số liệu.

Các `.txt` 04–10 được giữ làm dữ liệu đối chiếu; report dẫn PNG hiện có làm evidence chính. Không xóa output tests/validators 01–03 vì định dạng text được phép.
