from openpyxl import load_workbook
from polars import DataFrame
import polars as pl


def read_headers(ws):
    last_main_header = None
    for col in ws.columns:
        if col[0].value is None and col[1].value is None:
            break
        elif col[0].value is not None:
            last_main_header = col[0].value

        headers = [
            header for header in [last_main_header, col[1].value] if header is not None
        ]
        yield " ".join(headers)


def convert_value(val):
    if val is None:
        return None
    elif isinstance(val, str):
        return val
    elif int(val) == val:
        return str(int(val))
    else:
        return str(val)


def read_bordered_column(ws, col):
    last_val = None
    for cell in next(ws.iter_cols(col, col, 3)):
        if cell.border.top.style is not None:
            last_val = convert_value(cell.value)
        yield last_val


def read_excel(path) -> DataFrame:
    wb = load_workbook(path, data_only=True)
    headers = read_headers(wb["IO-List"])
    data = {
        header: read_bordered_column(wb["IO-List"], index + 1)
        for index, header in enumerate(headers)
    }
    return DataFrame(data).filter(~pl.all_horizontal(pl.all().is_null()))
