$ErrorActionPreference = "Stop"

# Runs FastAPI print service on Windows host (USB printer via win32 backend).
# Assumes you're in the `equ` folder (same folder as `print.py` and `.env`).

if (-not (Test-Path ".\\print.py")) {
  throw "print.py not found in current folder. cd into the 'equ' folder first."
}

python -m uvicorn print:app --host 0.0.0.0 --port 8001
