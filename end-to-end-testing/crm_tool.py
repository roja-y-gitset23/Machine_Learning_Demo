import os
import requests
from dotenv import load_dotenv

load_dotenv()
CRM_URL = os.getenv("CRM_URL", "http://127.0.0.1:8000/crm")


def get_customer(name_or_id):
    """Look up a customer in the CRM. Returns a dict, or {'error': ...}."""
    try:
        r = requests.get(f"{CRM_URL}/customers/{name_or_id}", timeout=10)
        if r.status_code == 404:
            return {"error": "Customer not found"}
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        return {"error": f"CRM unavailable: {e}"}