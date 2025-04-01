import os
import pandas as pd

def read_data_sheet(sheet_path: str = None):
    if not os.path.isfile(sheet_path):
        raise ValueError(f"Data File Not Found: got {sheet_path}")

    if sheet_path.endswith(".xlsx"):
        sheet = pd.read_excel(sheet_path, dtype=str, keep_default_na=False)
    elif sheet_path.endswith(".csv"):
        sheet = pd.read_csv(sheet_path, dtype=str, keep_default_na=False)
    else:
        raise ValueError("Unsupported file format. Only .xlsx and .csv are allowed.")
    data_inputs = sheet.to_dict(orient="records")

    if not data_inputs:
        raise ValueError(f"Invalid Data File: got {sheet_path}")

    return data_inputs

def convert_proxy_to_http(proxy: str) -> str | None:
    """
    Converts a proxy string in the format 'host:port:username:password'
    to an HTTP proxy string.
    """
    if proxy.startswith("http://") or proxy.startswith("https://"):
        return proxy
    try:
        if ":" not in proxy:
            return None

        if "@" in proxy:
            return "http://" + proxy
        host, port, username, password = proxy.split(":")

        http_proxy = f"http://{username}:{password}@{host}:{port}"
        return http_proxy
    except ValueError:
        return None