from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from uuid import UUID
from typing import Literal

router = APIRouter()

class NotificationSubscriptionRequest(BaseModel):
    account_id: UUID
    notify_type: Literal["email", "sms"]

# Placeholder for notification subscription (not fully implemented)
@router.post("/subscribe")
async def subscribe_to_notifications(request: NotificationSubscriptionRequest):
    return {"message": f"Subscribed {request.account_id} to {request.notify_type} notifications"}

@router.post("/unsubscribe")
async def unsubscribe_from_notifications(request: NotificationSubscriptionRequest):
    return {"message": f"Unsubscribed {request.account_id} from {request.notify_type} notifications"}