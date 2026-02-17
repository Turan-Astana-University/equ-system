import os
import platform
import socket
import logging
import time
import uuid
import hashlib
from typing import Any, Literal, Optional

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel

app = FastAPI()
logger = logging.getLogger("print_service")


@app.middleware("http")
async def _request_id_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex
    request.state.request_id = request_id
    started = time.monotonic()
    try:
        response = await call_next(request)
    finally:
        elapsed_ms = int((time.monotonic() - started) * 1000)
        logger.info(
            "http %s %s request_id=%s ms=%s client=%s",
            request.method,
            request.url.path,
            request_id,
            elapsed_ms,
            getattr(request.client, "host", None),
        )
    response.headers["X-Request-ID"] = request_id
    return response


def _load_dotenv_if_present() -> None:
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
    if not os.path.exists(dotenv_path):
        return

    try:
        with open(dotenv_path, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("'").strip('"')
                if not key:
                    continue
                os.environ.setdefault(key, value)
    except OSError:
        logger.exception("Failed to read .env at %s", dotenv_path)


_load_dotenv_if_present()


def _env_flag(name: str, *, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in ("1", "true", "yes", "y", "on")


def _env_log_level() -> int:
    raw = os.getenv("PRINT_SERVICE_LOG_LEVEL") or os.getenv("LOG_LEVEL") or ""
    level = raw.strip().upper() or "INFO"
    return getattr(logging, level, logging.INFO)


logger.setLevel(_env_log_level())
if not logging.getLogger().handlers:
    logging.basicConfig(
        level=_env_log_level(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


class PrintRequest(BaseModel):
    zpl_data: str
    backend: Optional[str] = None
    printer_host: Optional[str] = None
    printer_port: Optional[int] = None
    printer_name: Optional[str] = None
    printer_timeout: Optional[float] = None
    verify_tcp: Optional[bool] = None
    return_diagnostics: Optional[bool] = None


Backend = Literal["auto", "win32", "tcp"]


def _env_int(name: str, *, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw.strip())
    except ValueError:
        return default


def _mask_host(host: str) -> str:
    host = (host or "").strip()
    if not host:
        return ""
    if len(host) <= 6:
        return "***"
    return f"{host[:3]}***{host[-3:]}"


def _normalize_zpl(zpl_data: str) -> str:
    """
    Best-effort cleanup for ZPL coming from templates/DB:
    - remove leading/trailing whitespace
    - normalize newlines
    - drop inline '; ...' comments on command lines (often accidentally added in templates)
    """
    zpl = (zpl_data or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    if not zpl:
        raise HTTPException(status_code=400, detail="zpl_data is empty.")

    cleaned_lines = []
    for raw_line in zpl.split("\n"):
        line = raw_line.strip()
        if not line.strip():
            continue
        semicolon_idx = line.find(";")
        if semicolon_idx != -1 and line.startswith("^"):
            line = line[:semicolon_idx].rstrip()
        if line:
            cleaned_lines.append(line)

    cleaned = "\n".join(cleaned_lines).strip()
    if not cleaned:
        raise HTTPException(status_code=400, detail="zpl_data became empty after normalization.")

    if "^XA" not in cleaned or "^XZ" not in cleaned:
        raise HTTPException(status_code=400, detail="zpl_data does not look like ZPL (missing ^XA/^XZ).")

    return cleaned + "\n"


def _get_backend(override_backend: Optional[str] = None) -> Backend:
    backend_raw = (override_backend or os.getenv("PRINTER_BACKEND", "")).strip().lower()
    backend = backend_raw or "auto"
    if backend not in ("auto", "win32", "tcp"):
        raise HTTPException(
            status_code=400,
            detail="Invalid PRINTER_BACKEND. Use one of: auto, win32, tcp",
        )
    return backend  # type: ignore[return-value]


def _probe_zebra_tcp(
    *,
    printer_host: str,
    printer_port: int,
    printer_timeout: float,
    request_id: Optional[str] = None,
) -> dict:
    """
    Tries to confirm that the target is a Zebra-like device speaking ZPL on port 9100.
    We send a lightweight identification command and expect a response.
    """
    started = time.monotonic()
    try:
        with socket.create_connection((printer_host, printer_port), timeout=printer_timeout) as sock:
            sock.settimeout(printer_timeout)
            sock.sendall(b"~HI\n")
            data = sock.recv(4096)

        if not data:
            raise HTTPException(
                status_code=500,
                detail="TCP target accepted connection but returned no data to ~HI probe; check PRINTER_HOST/PORT.",
            )

        result = {
            "probe": "ok",
            "probe_bytes": len(data),
            "probe_sample": data[:200].decode("utf-8", errors="replace"),
            "probe_ms": int((time.monotonic() - started) * 1000),
        }
        logger.info(
            "tcp_probe ok request_id=%s host=%s port=%s bytes=%s ms=%s",
            request_id,
            _mask_host(printer_host),
            printer_port,
            result["probe_bytes"],
            result["probe_ms"],
        )
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug("tcp_probe sample request_id=%s sample=%r", request_id, result["probe_sample"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(
            "tcp_probe failed request_id=%s host=%s port=%s",
            request_id,
            _mask_host(printer_host),
            printer_port,
        )
        raise HTTPException(status_code=500, detail=f"TCP probe failed: {e}") from e


def _print_via_tcp(
    zpl_data: str,
    *,
    printer_host: Optional[str] = None,
    printer_port: Optional[int] = None,
    printer_timeout: Optional[float] = None,
    verify_tcp: Optional[bool] = None,
    already_normalized: bool = False,
    request_id: Optional[str] = None,
) -> dict:
    printer_host = (printer_host or os.getenv("PRINTER_HOST", "")).strip()
    if not printer_host:
        logger.error("TCP backend selected but PRINTER_HOST is empty.")
        raise HTTPException(
            status_code=500,
            detail="PRINTER_HOST is required for tcp backend (typically printer IP).",
        )

    if printer_port is None:
        try:
            printer_port = int(os.getenv("PRINTER_PORT", "9100").strip())
        except ValueError as e:
            raise HTTPException(status_code=400, detail="PRINTER_PORT must be an integer.") from e

    if printer_timeout is None:
        try:
            printer_timeout = float(os.getenv("PRINTER_TIMEOUT", "5").strip())
        except ValueError as e:
            raise HTTPException(status_code=400, detail="PRINTER_TIMEOUT must be a number.") from e

    verify_effective = (
        _env_flag("PRINTER_TCP_VERIFY", default=False) if verify_tcp is None else bool(verify_tcp)
    )
    if not verify_effective:
        logger.warning(
            "tcp_print note request_id=%s: tcp send success does not guarantee the printer actually printed; enable PRINTER_TCP_VERIFY=1 for target validation",
            request_id,
        )
    if verify_effective:
        _probe_zebra_tcp(
            printer_host=printer_host,
            printer_port=printer_port,
            printer_timeout=printer_timeout,
            request_id=request_id,
        )

    normalized = zpl_data if already_normalized else _normalize_zpl(zpl_data)
    payload = normalized.encode("utf-8")
    payload_hash = hashlib.sha256(payload).hexdigest()
    snippet_bytes = max(0, _env_int("PRINT_SERVICE_LOG_PAYLOAD_SNIPPET_BYTES", default=0))
    started = time.monotonic()
    try:
        with socket.create_connection((printer_host, printer_port), timeout=printer_timeout) as sock:
            local = None
            peer = None
            try:
                peer = sock.getpeername()
            except OSError:
                peer = None
            try:
                local = sock.getsockname()
            except OSError:
                local = None

            sock.sendall(payload)
            try:
                sock.shutdown(socket.SHUT_WR)
            except OSError:
                pass

        send_ms = int((time.monotonic() - started) * 1000)
        logger.info(
            "tcp_print ok request_id=%s host=%s port=%s bytes=%s sha256=%s send_ms=%s local=%s peer=%s verify=%s",
            request_id,
            _mask_host(printer_host),
            printer_port,
            len(payload),
            payload_hash,
            send_ms,
            local,
            peer,
            verify_effective,
        )
        if snippet_bytes and logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "tcp_print zpl_snippet request_id=%s snippet=%r",
                request_id,
                payload[:snippet_bytes].decode("utf-8", errors="replace"),
            )
        return {
            "message": "Label sent to printer via TCP.",
            "bytes_written": len(payload),
            "send_ms": send_ms,
            "sha256": payload_hash,
        }
    except OSError as e:
        logger.exception(
            "tcp_print failed request_id=%s host=%s port=%s verify=%s sha256=%s",
            request_id,
            _mask_host(printer_host),
            printer_port,
            verify_effective,
            payload_hash,
        )
        raise HTTPException(status_code=500, detail=f"TCP print failed: {e}") from e


def _print_via_win32(zpl_data: str, *, printer_name: Optional[str] = None) -> dict:
    printer_name = (printer_name or os.getenv("PRINTER_NAME", "ZDesigner ZD220-203dpi ZPL")).strip()

    os_name = platform.system().strip().lower()
    if os_name != "windows":
        raise HTTPException(
            status_code=500,
            detail=f"win32 backend requires Windows, but service is running on {platform.system()}. "
            "Run print_service on the Windows machine that has the USB printer, or use tcp backend for network printers.",
        )

    try:
        import win32print  # type: ignore
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"win32 backend requires pywin32/win32print. Import failed: {e}",
        ) from e

    try:
        flags = win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        printers = [printer[2] for printer in win32print.EnumPrinters(flags)]
        if printer_name not in printers:
            raise Exception(f"Printer '{printer_name}' not found. Available: {printers}")

        printer = win32print.OpenPrinter(printer_name)
        try:
            win32print.StartDocPrinter(printer, 1, ("ZPL Print", None, "RAW"))
            win32print.StartPagePrinter(printer)
            bytes_written = win32print.WritePrinter(printer, _normalize_zpl(zpl_data).encode("utf-8"))
            win32print.EndPagePrinter(printer)
            win32print.EndDocPrinter(printer)
            return {"message": "Label sent to printer (win32).", "bytes_written": bytes_written}
        finally:
            win32print.ClosePrinter(printer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


def _auto_backend_diagnostics(
    *,
    os_name: str,
    has_printer_host: bool,
    win32_error: Optional[Any],
    tcp_error: Optional[Any],
) -> dict:
    attempts = []
    if win32_error is not None:
        attempts.append({"backend": "win32", "error": win32_error})
    if tcp_error is not None:
        attempts.append({"backend": "tcp", "error": tcp_error})

    hints = []
    if os_name != "windows":
        hints.append(
            "In Linux/Docker, use tcp backend with PRINTER_HOST (printer IP) and PRINTER_PORT (default 9100)."
        )
    else:
        hints.append("On Windows, install/configure a printer and use win32 backend with PRINTER_NAME (optional).")
        hints.append("Alternatively, use tcp backend with PRINTER_HOST (printer IP) and PRINTER_PORT (default 9100).")

    if not has_printer_host:
        hints.append("PRINTER_HOST is empty, so tcp backend cannot be used.")

    return {
        "error": "No printer backend available.",
        "attempts": attempts,
        "hints": hints,
        "config_seen": {
            "os": os_name,
            "has_printer_host": has_printer_host,
            "env_printer_backend": os.getenv("PRINTER_BACKEND"),
        },
    }


def print_label_zpl(
    zpl_data: str,
    *,
    backend: Optional[str] = None,
    printer_host: Optional[str] = None,
    printer_port: Optional[int] = None,
    printer_name: Optional[str] = None,
    printer_timeout: Optional[float] = None,
    verify_tcp: Optional[bool] = None,
    request_id: Optional[str] = None,
) -> dict:
    resolved_backend = _get_backend(backend)
    normalized = _normalize_zpl(zpl_data)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug(
            "zpl_normalized request_id=%s changed=%s before_len=%s after_len=%s",
            request_id,
            normalized != (zpl_data or ""),
            len(zpl_data or ""),
            len(normalized),
        )

    if resolved_backend == "tcp":
        result = _print_via_tcp(
            normalized,
            printer_host=printer_host,
            printer_port=printer_port,
            printer_timeout=printer_timeout,
            verify_tcp=verify_tcp,
            already_normalized=True,
            request_id=request_id,
        )
        return {"backend": "tcp", **result}

    if resolved_backend == "win32":
        result = _print_via_win32(normalized, printer_name=printer_name)
        return {
            "backend": "win32",
            **result,
            "printer_name": (printer_name or os.getenv("PRINTER_NAME")),
        }

    # auto
    os_name = platform.system().strip().lower()
    win32_error: Optional[Any] = None
    tcp_error: Optional[Any] = None

    if os_name == "windows":
        try:
            return _print_via_win32(normalized, printer_name=printer_name)
        except HTTPException as e:
            win32_error = e.detail

    effective_printer_host = (printer_host or os.getenv("PRINTER_HOST", "")).strip()
    if effective_printer_host:
        try:
            result = _print_via_tcp(
                normalized,
                printer_host=printer_host,
                printer_port=printer_port,
                printer_timeout=printer_timeout,
                verify_tcp=verify_tcp,
                already_normalized=True,
                request_id=request_id,
            )
            return {"backend": "tcp", **result}
        except HTTPException as e:
            tcp_error = e.detail

    raise HTTPException(
        status_code=500,
        detail=_auto_backend_diagnostics(
            os_name=os_name,
            has_printer_host=bool(effective_printer_host),
            win32_error=win32_error,
            tcp_error=tcp_error,
        ),
    )


@app.post("/print")
async def print_label(request: PrintRequest, http_request: Request):
    request_id = getattr(http_request.state, "request_id", None) or uuid.uuid4().hex
    return_diag_effective = (
        _env_flag("PRINT_SERVICE_RETURN_DIAGNOSTICS", default=False)
        if request.return_diagnostics is None
        else bool(request.return_diagnostics)
    )

    zpl_len = len(request.zpl_data or "")
    resolved_backend = _get_backend(request.backend)
    effective_host = (request.printer_host or os.getenv("PRINTER_HOST", "") or "").strip()
    effective_port = request.printer_port or (os.getenv("PRINTER_PORT") or "").strip() or None
    logger.info(
        "print_start request_id=%s backend=%s backend_override=%s verify_tcp=%s return_diag=%s zpl_len=%s host=%s port=%s",
        request_id,
        resolved_backend,
        request.backend,
        request.verify_tcp,
        return_diag_effective,
        zpl_len,
        _mask_host(effective_host),
        effective_port,
    )
    try:
        result = print_label_zpl(
            request.zpl_data,
            backend=request.backend,
            printer_host=request.printer_host,
            printer_port=request.printer_port,
            printer_name=request.printer_name,
            printer_timeout=request.printer_timeout,
            verify_tcp=request.verify_tcp,
            request_id=request_id,
        )
        if return_diag_effective:
            diag = {
                "request_id": request_id,
                "os": platform.system(),
                "env_printer_backend": os.getenv("PRINTER_BACKEND"),
                "env_printer_host_masked": _mask_host((os.getenv("PRINTER_HOST") or "").strip()),
                "env_printer_port": os.getenv("PRINTER_PORT"),
                "env_printer_timeout": os.getenv("PRINTER_TIMEOUT"),
                "printer_tcp_verify_env": _env_flag("PRINTER_TCP_VERIFY", default=False),
            }
            return {"diagnostics": diag, **result}
        return result
    except HTTPException as e:
        logger.error("print_failed request_id=%s detail=%s", request_id, e.detail)
        raise
    except Exception:
        logger.exception("print_unexpected request_id=%s", request_id)
        raise HTTPException(status_code=500, detail="Unexpected print error")


@app.get("/health")
async def health():
    return {"status": "ok", "backend": _get_backend()}


@app.get("/config")
async def config():
    backend = _get_backend()
    printer_host = (os.getenv("PRINTER_HOST", "") or "").strip()
    masked_host = _mask_host(printer_host)
    return {
        "backend": backend,
        "printer_host_masked": masked_host,
        "printer_port": os.getenv("PRINTER_PORT"),
        "printer_timeout": os.getenv("PRINTER_TIMEOUT"),
        "printer_tcp_verify": _env_flag("PRINTER_TCP_VERIFY", default=False),
        "return_diagnostics": _env_flag("PRINT_SERVICE_RETURN_DIAGNOSTICS", default=False),
        "log_level": os.getenv("PRINT_SERVICE_LOG_LEVEL") or os.getenv("LOG_LEVEL") or "INFO",
        "log_payload_snippet_bytes": _env_int("PRINT_SERVICE_LOG_PAYLOAD_SNIPPET_BYTES", default=0),
        "os": platform.system(),
    }
