import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_payment_flow():
    """
    End-to-end payment test:
    Customer -> Order -> Confirm -> Invoice -> Partial Payment -> Full Payment
    """

    # -----------------------------
    # 1. CREATE CUSTOMER
    # -----------------------------
    customer_payload = {
        "name": "Payment Test Customer",
        "email": f"payment_test_{uuid.uuid4()}@example.com",
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
                "product_name": "Laptop",
                "quantity": 1,
                "unit_price": 50000,
            }
        ],
    }

    order_res = client.post("/orders", json=order_payload)
    assert order_res.status_code == 201
    order_id = order_res.json()["id"]

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

    invoice = invoice_res.json()
    invoice_id = invoice["id"]
    invoice_total = invoice["total"]
    assert invoice["status"] == "UNPAID"

    # -----------------------------
    # 5. PARTIAL PAYMENT
    # -----------------------------
    partial_payment_payload = {
        "invoice_id": invoice_id,
        "amount": invoice_total / 2,
        "payment_method": "CARD",
    }

    payment1_res = client.post("/payments", json=partial_payment_payload)
    assert payment1_res.status_code == 201

    # Invoice should now be PARTIALLY_PAID
    invoice_check = client.get(f"/invoices/{invoice_id}")
    assert invoice_check.status_code == 200
    assert invoice_check.json()["status"] == "PARTIALLY_PAID"

    # -----------------------------
    # 6. FINAL PAYMENT
    # -----------------------------
    remaining_amount = invoice_total - partial_payment_payload["amount"]

    final_payment_payload = {
        "invoice_id": invoice_id,
        "amount": remaining_amount,
        "payment_method": "BANK_TRANSFER",
    }

    payment2_res = client.post("/payments", json=final_payment_payload)
    assert payment2_res.status_code == 201

    # Invoice should now be PAID
    invoice_check = client.get(f"/invoices/{invoice_id}")
    assert invoice_check.status_code == 200
    assert invoice_check.json()["status"] == "PAID"

    # -----------------------------
    # 7. OVER-PAYMENT SHOULD FAIL
    # -----------------------------
    over_payment_payload = {
        "invoice_id": invoice_id,
        "amount": 1,
        "payment_method": "CASH",
    }

    overpay_res = client.post("/payments", json=over_payment_payload)
    assert overpay_res.status_code == 400

    # -----------------------------
    # 8. FETCH PAYMENTS
    # -----------------------------
    payments_res = client.get(f"/payments/invoice/{invoice_id}")
    assert payments_res.status_code == 200

    payments = payments_res.json()
    assert len(payments) == 2
