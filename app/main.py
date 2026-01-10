from fastapi import FastAPI
from app.database import engine, Base
from app.routers import orders, invoices, payments


app = FastAPI(
    title="Sales & Invoice Management API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {"status": "running"}



app.include_router(orders.router)
app.include_router(invoices.router)
app.include_router(payments.router)



if __name__ == "__main__":
    print("Use → uvicorn app.main:app --reload")
