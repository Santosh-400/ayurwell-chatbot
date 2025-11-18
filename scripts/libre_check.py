import requests

url = 'https://libretranslate.de/translate'
payload = {'q': 'Hello, how are you?', 'source': 'en', 'target': 'kn', 'format': 'text'}
try:
    r = requests.post(url, json=payload, timeout=15)
    print('status', r.status_code)
    print('headers:', r.headers.get('Content-Type'))
    print('response (truncated):')
    print(r.text[:1000])
    try:
        print('\njson:', r.json())
    except Exception as e:
        print('\nno json:', e)
except Exception as e:
    print('request error', e)
