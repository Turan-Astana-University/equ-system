from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import win32print

app = FastAPI()


class PrintRequest(BaseModel):
    zpl_data: str


def print_test_label(zpl_data):
    printer_name = "ZDesigner ZD220-203dpi ZPL"  # Укажите имя вашего принтера

    try:
        printers = [printer[2] for printer in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL)]
        if printer_name not in printers:
            raise Exception(f"Принтер '{printer_name}' не найден. Доступные принтеры: {printers}")

        printer = win32print.OpenPrinter(printer_name)
        try:
            job = win32print.StartDocPrinter(printer, 1, ("Test Print", None, "RAW"))
            win32print.StartPagePrinter(printer)
            bytes_written = win32print.WritePrinter(printer, zpl_data.encode('utf-8'))
            win32print.EndPagePrinter(printer)
            win32print.EndDocPrinter(printer)
            return {"message": "Этикетка успешно отправлена на печать!", "bytes_written": bytes_written}
        finally:
            win32print.ClosePrinter(printer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/print")
async def print_label(request: PrintRequest):
    return print_test_label(request.zpl_data)

