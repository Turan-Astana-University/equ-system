import os
import platform
import socket
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class PrintRequest(BaseModel):
    zpl_data: str


Backend = Literal["auto", "win32", "tcp"]


def _get_backend() -> Backend:
    backend = os.getenv("PRINTER_BACKEND", "auto").strip().lower()
    if backend not in ("auto", "win32", "tcp"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PRINTER_BACKEND. Use one of: auto, win32, tcp",
        )
    return backend  # type: ignore[return-value]


def _print_via_tcp(zpl_data: str) -> dict:
    printer_host = os.getenv("PRINTER_HOST", "").strip()
    if not printer_host:
        raise HTTPException(
            status_code=500,
            detail="PRINTER_HOST is required for tcp backend (typically printer IP).",
        )

    try:
        printer_port = int(os.getenv("PRINTER_PORT", "9100").strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail="PRINTER_PORT must be an integer.") from e

    try:
        timeout_s = float(os.getenv("PRINTER_TIMEOUT", "5").strip())
    except ValueError as e:
        raise HTTPException(status_code=400, detail="PRINTER_TIMEOUT must be a number.") from e

    payload = zpl_data.encode("utf-8")
    try:
        with socket.create_connection((printer_host, printer_port), timeout=timeout_s) as sock:
            sock.sendall(payload)
        return {"message": "Label sent to printer via TCP.", "bytes_written": len(payload)}
    except OSError as e:
        raise HTTPException(status_code=500, detail=f"TCP print failed: {e}") from e


def _print_via_win32(zpl_data: str) -> dict:
    printer_name = os.getenv("PRINTER_NAME", "ZDesigner ZD220-203dpi ZPL").strip()

    try:
        import win32print  # type: ignore
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="win32 backend requires pywin32/win32print and Windows.",
        ) from e

    try:
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
        if printer_name not in printers:
            raise Exception(f"Printer '{printer_name}' not found. Available: {printers}")

        printer = win32print.OpenPrinter(printer_name)
        try:
            win32print.StartDocPrinter(printer, 1, ("ZPL Print", None, "RAW"))
            win32print.StartPagePrinter(printer)
            bytes_written = win32print.WritePrinter(printer, zpl_data.encode("utf-8"))
            win32print.EndPagePrinter(printer)
            win32print.EndDocPrinter(printer)
            return {"message": "Label sent to printer (win32).", "bytes_written": bytes_written}
        finally:
            win32print.ClosePrinter(printer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def print_label_zpl(zpl_data: str) -> dict:
    backend = _get_backend()

    if backend == "tcp":
        return _print_via_tcp(zpl_data)

    if backend == "win32":
        return _print_via_win32(zpl_data)

    # auto
    if platform.system().lower() == "windows":
        try:
            return _print_via_win32(zpl_data)
        except HTTPException:
            pass

    if os.getenv("PRINTER_HOST"):
        return _print_via_tcp(zpl_data)

    raise HTTPException(
        status_code=500,
        detail="No printer backend available. Set PRINTER_BACKEND (tcp/win32) and required env vars.",
    )


@app.post("/print")
async def print_label(request: PrintRequest):
    return print_label_zpl(request.zpl_data)


@app.get("/health")
async def health():
    return {"status": "ok", "backend": _get_backend()}
