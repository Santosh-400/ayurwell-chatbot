import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()
API_KEY = os.getenv('GOOGLE_API_KEY')
if not API_KEY:
    print('NO_API_KEY')
    raise SystemExit('GOOGLE_API_KEY not set')

url = f'https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}'
print('REQUEST_URL:', url)
resp = requests.get(url, timeout=15)
print('STATUS:', resp.status_code)
try:
    data = resp.json()
    print(json.dumps(data, indent=2))
except Exception as e:
    print('JSON ERROR:', e)
    print(resp.text)
