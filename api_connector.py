import requests
import json

# رابط API Apps Script الخاص بك
API_URL = "https://script.google.com/macros/s/AKfycbwiHmypxMcHyrkR0bdALNtwjP6i3Ngnj55ZWW27YyXAjqMr_HybR8qt_mX1EWE6LMRDyQ/exec"

def send_request(action, data=None):
    """دالة عامة لإرسال الطلبات إلى Google Apps Script API"""
    if data is None:
        data = {}
    
    payload = {
        "action": action,
        "data": data
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status": "error", "message": f"HTTP Error: {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# دوال مساعدة جاهزة للاستخدام في الواجهات
def login_user(username, password):
    return send_request("login", {"username": username, "password": password})

def get_chart_of_accounts():
    return send_request("getChartOfAccounts")

def add_account(name, acc_type, parent_code, opening_balance, username):
    return send_request("addAccount", {
        "name": name,
        "type": acc_type,
        "parentCode": parent_code,
        "openingBalance": opening_balance,
        "username": username
    })

def add_transaction(date_str, entries, username):
    return send_request("addTransaction", {
        "date": date_str,
        "entries": entries,
        "username": username
    })

def upload_file_attachment(file_name, file_base64, mime_type):
    return send_request("uploadAttachment", {
        "fileName": file_name,
        "fileBase64": file_base64,
        "mimeType": mime_type
    })