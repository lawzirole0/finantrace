import json
import urllib.request
import urllib.error
from django.conf import settings

API_BASE = "https://api.paystack.co"

PLAN_CODES = {
    "startup": settings.PAYSTACK_STARTUP_PLAN_CODE,
    "growing": settings.PAYSTACK_GROWING_PLAN_CODE,
}

PLAN_AMOUNTS = {
    "startup": 500_00,
    "growing": 1000_00,
}


def _headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


def _post(path, data):
    req = urllib.request.Request(
        f"{API_BASE}{path}",
        data=json.dumps(data).encode(),
        headers=_headers(),
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return json.loads(body) if body else {"status": False, "message": str(e)}


def _get(path):
    req = urllib.request.Request(f"{API_BASE}{path}", headers=_headers())
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        return json.loads(body) if body else {"status": False, "message": str(e)}


def initialize_transaction(email: str, amount_kobo: int, plan_code: str = "", metadata: dict = None) -> dict:
    data = {
        "email": email,
        "amount": str(amount_kobo),
    }
    if plan_code:
        data["plan"] = plan_code
    if metadata:
        data["metadata"] = metadata
    return _post("/transaction/initialize", data)


def verify_transaction(reference: str) -> dict:
    return _get(f"/transaction/verify/{reference}")


def create_customer(email: str, first_name: str = "", last_name: str = "") -> dict:
    data = {"email": email}
    if first_name:
        data["first_name"] = first_name
    if last_name:
        data["last_name"] = last_name
    return _post("/customer", data)


def create_subscription(customer_code: str, plan_code: str) -> dict:
    return _post("/subscription", {
        "customer": customer_code,
        "plan": plan_code,
    })


def disable_subscription(subscription_code: str) -> dict:
    return _post("/subscription/disable", {
        "code": subscription_code,
        "token": "",
    })


def list_plans() -> dict:
    return _get("/plan")
