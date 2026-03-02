#!/usr/bin/env python3
"""
保存 Microsoft Graph Token
在本地執行認證後，用此腳本保存 token
"""
from azure.identity import DeviceCodeCredential
import json
from pathlib import Path

CLIENT_ID = '59dce055-4648-4c77-bf42-66696043f2f3'
TENANT_ID = '78385e4e-091b-4f79-9187-a25935aaa90d'
SCOPES = 'User.Read Mail.Read Mail.Send Files.ReadWrite.All'

print('=' * 60)
print('Microsoft Graph Token 保存工具')
print('=' * 60)
print()

credential = DeviceCodeCredential(
    client_id=CLIENT_ID,
    tenant_id=TENANT_ID
)

print('正在獲取 token...')
print('如果瀏覽器沒有打開，請訪問：https://microsoft.com/devicelogin')
print('輸入畫面上的代碼，用 utest@tinote.onmicrosoft.com 登入')
print()

token = credential.get_token(SCOPES)

# 保存完整 token 資訊
token_data = {
    'graph_scopes': SCOPES,
    'access_token': token.token
}

token_file = Path(__file__).parent.parent / 'pri' / 'tokens.json'
token_file.parent.mkdir(parents=True, exist_ok=True)

with open(token_file, 'w', encoding='utf-8') as f:
    json.dump(token_data, f, indent=2)

print()
print('✓ Token 已保存到：', token_file)
print()
print('Token 前 50 字元：', token.token[:50], '...')
print()
print('下次執行 test_graph.py 將使用此 token，不需要重新認證！')
