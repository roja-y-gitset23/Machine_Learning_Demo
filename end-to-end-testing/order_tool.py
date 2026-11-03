import os
import requests
from dotenv import load_dotenv

load_dotenv()
ORDER_URL = os.getenv("ORDER_URL", "http://127.0.0.1:8000")


def get_order_status(order_id):
    """Look up an order. Returns a dict, or {'error': ...}."""
    try:
        r = requests.get(f"{ORDER_URL}/orders/{order_id}", timeout=10)
        if r.status_code == 404:
            return {"error": "Order not found"}
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": f"Order service unavailable: {e}"}