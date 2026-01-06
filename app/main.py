from fastapi import FastAPI
from app.database import engine, Base
# from app.routers import orders, invoices, payments   # your separated folders already exist


app = FastAPI(
    title="Sales & Invoice Management API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {"status": "running"}


# # -----------------------------
# # REGISTER ROUTERS
# # -----------------------------
# app.include_router(orders.router)
# app.include_router(invoices.router)
# app.include_router(payments.router)


# optional: allow script check
if __name__ == "__main__":
    print("Use → uvicorn app.main:app --reload")
