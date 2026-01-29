import requests
import json
import time
from datetime import datetime, timezone

WEBHOOK_URL = "http://localhost:5000/webhook"

def send_event(event_type, payload):
    headers = {
        "Content-Type": "application/json",
        "X-GitHub-Event": event_type
    }
    try:
        response = requests.post(WEBHOOK_URL, json=payload, headers=headers)
        print(f"Sent {event_type}: Status {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Failed to send {event_type}: {e}")

def get_timestamp():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def simulate():
    print("Simulating Github Events...")

    # 1. PUSH Event
    push_payload = {
        "ref": "refs/heads/staging",
        "after": "c0d3hash12345",
        "pusher": {
            "name": "Travis"
        },
        "head_commit": {
            "id": "c0d3hash12345",
            "timestamp": get_timestamp()
        }
    }
    send_event("push", push_payload)
    time.sleep(2)

    # 2. PULL REQUEST Event (Opened)
    pr_payload = {
        "action": "opened",
        "pull_request": {
            "id": 101,
            "user": {
                "login": "Travis"
            },
            "head": {
                "ref": "staging"
            },
            "base": {
                "ref": "master"
            },
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    }
    send_event("pull_request", pr_payload)
    time.sleep(2)

    # 3. MERGE Event (PR Closed & Merged)
    merge_payload = {
        "action": "closed",
        "pull_request": {
            "id": 101,
            "merged": True,
            "user": {
                "login": "Travis"
            },
            "head": {
                "ref": "dev"
            },
            "base": {
                "ref": "master"
            },
            "created_at": get_timestamp(),
            "updated_at": get_timestamp()
        }
    }
    send_event("pull_request", merge_payload)

if __name__ == "__main__":
    simulate()
