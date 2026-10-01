& .venv/Scripts/python.exe -X utf8 scripts/pii_evidence.py
if ($LASTEXITCODE -ne 0) {
    throw "PII evidence check failed."
}
