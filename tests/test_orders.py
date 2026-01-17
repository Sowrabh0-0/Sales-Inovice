import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_full_order_flow():
    """
    End-to-end test:
    Customer -> Order -> Confirm Order
    """

    # -----------------------------
    # 1. CREATE CUSTOMER
    # -----------------------------
    customer_payload = {
        "name": "Test Customer",
        "email": f"testcustomer_{uuid.uuid4()}@example.com"
    }

    customer_res = client.post("/orders/customers", json=customer_payload)
    assert customer_res.status_code == 201

    customer_data = customer_res.json()
    assert "id" in customer_data
    assert customer_data["email"] == customer_payload["email"]

    customer_id = customer_data["id"]

    # -----------------------------
    # 2. CREATE ORDER
    # -----------------------------
    order_payload = {
        "customer_id": customer_id,
        "items": [
            {
                "product_name": "Laptop",
                "quantity": 2,
                "unit_price": 50000
            },
            {
                "product_name": "Mouse",
                "quantity": 1,
                "unit_price": 1500
            }
        ]
    }

    order_res = client.post("/orders", json=order_payload)
    assert order_res.status_code == 201

    order_data = order_res.json()
    assert order_data["status"] == "CREATED"
    assert len(order_data["items"]) == 2

    order_id = order_data["id"]

    # -----------------------------
    # 3. CONFIRM ORDER
    # -----------------------------
    confirm_res = client.post(f"/orders/{order_id}/confirm")
    assert confirm_res.status_code == 200

    confirm_data = confirm_res.json()
    assert confirm_data["status"] == "CONFIRMED"

    # -----------------------------
    # 4. INVALID CONFIRM (ALREADY CONFIRMED)
    # -----------------------------
    invalid_confirm_res = client.post(f"/orders/{order_id}/confirm")
    assert invalid_confirm_res.status_code == 400
