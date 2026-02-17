# equ-system

## Запуск FastAPI print-сервиса в Docker

1) Создай `./.env` (можно скопировать из `./.env.example`).
2) Запусти сервис:

```bash
cd equ
docker compose up --build print
```

- Healthcheck: `http://localhost:8001/health`
- Config: `http://localhost:8001/config`
- Печать: `POST http://localhost:8001/print` JSON: `{ "zpl_data": "^XA...^XZ" }`

### Бэкенды печати

- `PRINTER_BACKEND=tcp` (по умолчанию для Docker): отправляет ZPL на `PRINTER_HOST:PRINTER_PORT` (обычно 9100)
- `PRINTER_TCP_VERIFY=1`: перед печатью делает TCP-probe (`~HI`) и вернёт 500, если `PRINTER_HOST:PRINTER_PORT` не похож на Zebra (помогает, когда `/print` отдаёт 200, но «ничего не печатает»).
- `PRINT_SERVICE_LOG_LEVEL=DEBUG`: подробные логи (видно `host/port`, `sha256`, длительность, probe и т.д.).
- `PRINT_SERVICE_LOG_PAYLOAD_SNIPPET_BYTES=200`: (только при DEBUG) логирует первые N байт ZPL (осторожно, может содержать текст).
- `PRINT_SERVICE_RETURN_DIAGNOSTICS=1`: добавляет блок `diagnostics` в JSON-ответ `/print`.
- `PRINTER_BACKEND=win32`: работает только на Windows с установленным `pywin32` (в Linux-контейнере не поддерживается)

## USB-принтер (Windows хост, без Docker)

Если принтер подключён по USB (например, `ZDesigner ZD220-203dpi ZPL`), то печать должна выполняться на том Windows-компьютере, где этот принтер установлен. Удалённый Linux/Docker-сервис не сможет печатать на USB.

1) На Windows-хосте (где подключён USB-принтер):
   - Установи Python.
   - В папке `equ` выполни `pip install -r requirements.txt` (на Windows подтянется `pywin32`).
   - В `.env` выставь `PRINTER_BACKEND=win32` и `PRINTER_NAME=...`.
   - Запусти сервис: `powershell -ExecutionPolicy Bypass -File .\\run_print_windows.ps1`

2) На сервере (где крутится Django) в `.env` укажи URL этого Windows-хоста:
   - `PRINT_SERVICE_URL=http://<IP_Windows_хоста>:8001/print`
