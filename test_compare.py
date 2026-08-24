import urllib.request
import urllib.error
import json

req = urllib.request.Request(
    'http://127.0.0.1:8000/compare',
    data=json.dumps({"standard_ids": ["IS 10322 : Part 1 : 2014", "IS 10322 : Part 5 : Sec 3 : 2012"]}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
try:
    with urllib.request.urlopen(req) as response:
        print(response.read().decode('utf-8'))
except urllib.error.HTTPError as e:
    print(f"HTTPError: {e.code} - {e.reason}")
except urllib.error.URLError as e:
    print(f"URLError: {e.reason}")
