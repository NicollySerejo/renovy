from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import require_client
from app import models, schemas

router = APIRouter(prefix="/clients", tags=["clients"])


@router.get("/me", response_model=schemas.ClientMeOut)
def get_me(user: models.User = Depends(require_client)):
    return user


@router.get("/me/notifications", response_model=list[schemas.NotificationOut])
def my_notifications(
    user: models.User = Depends(require_client),
    db: Session = Depends(get_db),
):
    return (
        db.query(models.Notification)
        .filter(models.Notification.user_id == user.id)
        .order_by(models.Notification.created_at.desc())
        .limit(50)
        .all()
    )


@router.post("/me/notifications/{notification_id}/read")
def mark_notification_read(
    notification_id: str,
    user: models.User = Depends(require_client),
    db: Session = Depends(get_db),
):
    n = (
        db.query(models.Notification)
        .filter(models.Notification.id == notification_id, models.Notification.user_id == user.id)
        .first()
    )
    if n:
        n.lida = True
        db.commit()
    return {"ok": True}
