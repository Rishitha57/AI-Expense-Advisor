import json
import urllib.request

base_url = 'http://127.0.0.1:8000'

payload = {
    'amount': 45.75,
    'currency': 'USD',
    'merchant': 'Whole Foods',
    'description': 'Groceries',
    'transaction_date': '2026-08-31T12:00:00Z',
    'source': 'manual',
}

req = urllib.request.Request(
    f'{base_url}/api/v1/transactions',
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
with urllib.request.urlopen(req) as resp:
    print('POST_STATUS', resp.status)
    print(resp.read().decode('utf-8'))

get_req = urllib.request.Request(f'{base_url}/api/v1/transactions', method='GET')
with urllib.request.urlopen(get_req) as resp:
    print('GET_STATUS', resp.status)
    print(resp.read().decode('utf-8'))
