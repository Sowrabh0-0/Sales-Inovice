import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_invoice_flow():
    """
    End-to-end invoice test:
    Customer -> Order -> Confirm -> Invoice
    """

    # -----------------------------
    # 1. CREATE CUSTOMER
    # -----------------------------
    customer_payload = {
        "name": "Invoice Test Customer",
        "email": f"invoice_test_{uuid.uuid4()}@example.com"
    }

    customer_res = client.post("/orders/customers", json=customer_payload)
    assert customer_res.status_code == 201
    customer_id = customer_res.json()["id"]

    # -----------------------------
    # 2. CREATE ORDER
    # -----------------------------
    order_payload = {
        "customer_id": customer_id,
        "items": [
            {
                "product_name": "Keyboard",
                "quantity": 2,
                "unit_price": 2000
            },
            {
                "product_name": "Monitor",
                "quantity": 1,
                "unit_price": 12000
            }
        ]
    }

    order_res = client.post("/orders", json=order_payload)
    assert order_res.status_code == 201

    order_data = order_res.json()
    order_id = order_data["id"]
    assert order_data["status"] == "CREATED"

    # -----------------------------
    # 3. CONFIRM ORDER
    # -----------------------------
    confirm_res = client.post(f"/orders/{order_id}/confirm")
    assert confirm_res.status_code == 200
    assert confirm_res.json()["status"] == "CONFIRMED"

    # -----------------------------
    # 4. CREATE INVOICE
    # -----------------------------
    invoice_res = client.post(f"/invoices/orders/{order_id}")
    assert invoice_res.status_code == 201

    invoice_data = invoice_res.json()

    assert invoice_data["order_id"] == order_id
    assert invoice_data["status"] == "UNPAID"
    assert invoice_data["subtotal"] > 0
    assert invoice_data["tax"] > 0
    assert invoice_data["total"] > invoice_data["subtotal"]

    invoice_id = invoice_data["id"]

    # -----------------------------
    # 5. FETCH INVOICE
    # -----------------------------
    get_invoice_res = client.get(f"/invoices/{invoice_id}")
    assert get_invoice_res.status_code == 200

    fetched_invoice = get_invoice_res.json()
    assert fetched_invoice["id"] == invoice_id
    assert fetched_invoice["order_id"] == order_id

    # -----------------------------
    # 6. DUPLICATE INVOICE SHOULD FAIL
    # -----------------------------
    duplicate_invoice_res = client.post(f"/invoices/orders/{order_id}")
    assert duplicate_invoice_res.status_code == 400
