
import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# 建立 Google Sheets 連線
def get_sheet():
    # 讀取環境變數中儲存的 JSON 憑證
    creds_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
    if not creds_json:
        raise Exception("未提供 Google 憑證，請設定 GOOGLE_APPLICATION_CREDENTIALS_JSON")

    creds_dict = json.loads(creds_json)

    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(credentials)

    # 打開 Google Sheet（使用試算表 ID）
    sheet_id = "11YWT1tdkRBvtrs6gtX7MIYh5E8QaMK2lPo-6ZOM8TKA"
    spreadsheet = client.open_by_key(sheet_id)
    worksheet = spreadsheet.sheet1  # 預設第一個工作表
    return worksheet

# 寫入一列違規資料
def append_violation_record(location, category, description):
    worksheet = get_sheet()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [now, location, category, description, "未處理"]
    worksheet.append_row(row)
