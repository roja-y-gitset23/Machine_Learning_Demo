from unittest.mock import patch, MagicMock
import requests
import crm_tool
import order_tool


def fake_response(status=200, data=None):
    m = MagicMock()
    m.status_code = status
    m.json.return_value = data or {}
    if status >= 400:
        m.raise_for_status.side_effect = requests.HTTPError("error")
    return m


# ---------- CRM tool ----------
@patch("crm_tool.requests.get")
def test_crm_found(mock_get):
    mock_get.return_value = fake_response(200, {"id": 1, "name": "Rahul"})
    assert crm_tool.get_customer(1)["name"] == "Rahul"


@patch("crm_tool.requests.get")
def test_crm_not_found(mock_get):
    mock_get.return_value = fake_response(404)
    assert crm_tool.get_customer(999) == {"error": "Customer not found"}


@patch("crm_tool.requests.get", side_effect=requests.ConnectionError("down"))
def test_crm_service_down(mock_get):
    assert "unavailable" in crm_tool.get_customer(1)["error"]


# ---------- Order tool ----------
@patch("order_tool.requests.get")
def test_order_found(mock_get):
    mock_get.return_value = fake_response(200, {"order_id": 1001, "status": "Shipped"})
    assert order_tool.get_order_status(1001)["status"] == "Shipped"


@patch("order_tool.requests.get")
def test_order_not_found(mock_get):
    mock_get.return_value = fake_response(404)
    assert order_tool.get_order_status(5) == {"error": "Order not found"}


@patch("order_tool.requests.get", side_effect=requests.Timeout("slow"))
def test_order_timeout(mock_get):
    assert "unavailable" in order_tool.get_order_status(1001)["error"]