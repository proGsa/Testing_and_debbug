import re
import base64
import requests

def get_last_2fa_code():
    messages = requests.get("http://localhost:8025/api/v2/messages").json()
    assert len(messages["items"]) > 0
    body = base64.b64decode(messages["items"][0]["Content"]["Body"]).decode("utf-8", errors="ignore")
    match = re.search(r"\b\d{6}\b", body)
    assert match, "2FA code not found in email"
    return match.group(0)
