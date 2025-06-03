import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import json

# 从 Streamlit secrets 加载 service account 信息
def get_credentials_from_secrets():
    info = json.loads(st.secrets["GOOGLE_SERVICE_ACCOUNT"])
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    return Credentials.from_service_account_info(info, scopes=scopes)

# 连接 Google Sheet
def connect_sheet(sheet_key: str, sheet_name: str = None):
    creds = get_credentials_from_secrets()
    client = gspread.authorize(creds)
    sheet = client.open_by_key(sheet_key)
    return sheet.worksheet(sheet_name) if sheet_name else sheet.sheet1

# 读取 Sheet 为 DataFrame
def read_sheet_as_df(sheet_key: str, sheet_name: str = None):
    ws = connect_sheet(sheet_key, sheet_name)
    data = ws.get_all_records()
    return pd.DataFrame(data)

# 将 DataFrame 写入 Sheet（全部覆盖）
def write_df_to_sheet(sheet_key: str, df: pd.DataFrame, sheet_name: str = None):
    ws = connect_sheet(sheet_key, sheet_name)
    ws.clear()
    ws.update([df.columns.tolist()] + df.values.tolist())
