import gspread
import pandas as pd
import json
from google.oauth2.service_account import Credentials
import streamlit as st

# 通过 secrets 中的 GOOGLE_SERVICE_ACCOUNT 证书 JSON 配置链接 Google Sheets
def connect_sheet(sheet_key: str, sheet_name: str = None):
    service_account_info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(service_account_info, scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_key)

    if sheet_name:
        worksheet = sheet.worksheet(sheet_name)
    else:
        worksheet = sheet.sheet1

    return worksheet

# 读取为 dataframe
def read_sheet_as_df(sheet_key: str, sheet_name: str = None):
    ws = connect_sheet(sheet_key, sheet_name)
    data = ws.get_all_records()
    df = pd.DataFrame(data)
    return df

# 写入 dataframe（全部覆盖）
def write_df_to_sheet(sheet_key: str, df: pd.DataFrame, sheet_name: str = None):
    ws = connect_sheet(sheet_key, sheet_name)
    ws.clear()
    ws.update([df.columns.values.tolist()] + df.values.tolist())
