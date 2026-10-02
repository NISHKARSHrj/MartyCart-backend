import os
import uuid
import requests

from dotenv import load_dotenv

load_dotenv()


def get_base_url():
    environment = os.getenv(
        "CASHFREE_ENVIRONMENT",
        "sandbox"
    ).lower()

    if environment == "production":
        return os.getenv("PRODUCTION_URL")

    return os.getenv("SANDBOX_URL")


def create_cashfree_order(
    order_id,
    amount,
    customer_id,
    customer_name,
    customer_email,
    customer_phone,
):
    client_id = os.getenv("CASHFREE_CLIENT_ID")
    client_secret = os.getenv("CASHFREE_CLIENT_SECRET")
    api_version = os.getenv(
        "CASHFREE_API_VERSION",
        "2025-01-01"
    )

    if not client_id or not client_secret:
        raise ValueError(
            "Cashfree credentials are not configured."
        )

    base_url = get_base_url()

    if not base_url:
        raise ValueError(
            "Cashfree API URL is not configured."
        )

    cashfree_order_id = (
        f"order_{order_id}_{uuid.uuid4().hex[:8]}"
    )

    payload = {
        "order_id": cashfree_order_id,
        "order_amount": float(amount),
        "order_currency": "INR",

        "customer_details": {
            "customer_id": str(customer_id),
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
        },
    }

    notify_url = os.getenv("CASHFREE_NOTIFY_URL")
    return_url = os.getenv("CASHFREE_RETURN_URL")

    order_meta = {}

    if notify_url:
        order_meta["notify_url"] = notify_url

    if return_url:
        order_meta["return_url"] = return_url

    if order_meta:
        payload["order_meta"] = order_meta

    headers = {
        "x-client-id": client_id,
        "x-client-secret": client_secret,
        "x-api-version": api_version,
        "Content-Type": "application/json",
        "Accept": "application/json",
        "x-request-id": str(uuid.uuid4()),
        "x-idempotency-key": str(uuid.uuid4()),
    }

    response = requests.post(
        f"{base_url}/orders",
        json=payload,
        headers=headers,
        timeout=30,
    )

    print("Cashfree Status:", response.status_code)
    print("Cashfree Response:", response.text)

    response.raise_for_status()

    return response.json()