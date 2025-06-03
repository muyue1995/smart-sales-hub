import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# 连接 Google Sheets
def connect_sheet(sheet_key: str, sheet_name: str = None):
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
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