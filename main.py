from fastapi import FastAPI
from presentation.api.accounts import router as accounts_router
from presentation.api.notifications import router as notifications_router
from presentation.api.statements import router as statements_router
from presentation.api.transfers import router as transfers_router

app = FastAPI(title="Simple Banking Application")

app.include_router(accounts_router, prefix="/accounts", tags=["Accounts"])
app.include_router(notifications_router, prefix="/notifications", tags=["Notifications"])
app.include_router(statements_router, prefix="/statements", tags=["Statements"])
app.include_router(transfers_router, prefix="/transfers", tags=["Transfers"])

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "ok"}