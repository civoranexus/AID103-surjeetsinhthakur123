import json
import os
import requests

OFFLINE_FILE = "offline_results.json"
SERVER_SYNC_URL = "http://127.0.0.1:5000/sync"

def is_online(timeout=3):
    try:
        requests.get("https://www.google.com", timeout=timeout)
        return True
    except:
        return False


def save_offline_result(result):
    data = []
    if os.path.exists(OFFLINE_FILE):
        with open(OFFLINE_FILE, "r") as f:
            data = json.load(f)

    data.append(result)

    with open(OFFLINE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def sync_offline_results():
    if not os.path.exists(OFFLINE_FILE):
        return {"synced": 0}

    with open(OFFLINE_FILE, "r") as f:
        data = json.load(f)

    if not data:
        return {"synced": 0}

    try:
        res = requests.post(SERVER_SYNC_URL, json=data, timeout=10)
        if res.status_code == 200:
            os.remove(OFFLINE_FILE)
            return {"synced": len(data)}
    except:
        pass

    return {"synced": 0}
