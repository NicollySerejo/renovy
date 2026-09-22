"""Notificacoes internas (in-app).

Estruturado para que canais externos (e-mail, WhatsApp, push, calendario)
possam ser plugados aqui no futuro sem alterar quem chama `notify()`.
"""
from sqlalchemy.orm import Session
from app import models


def notify(db: Session, user_id: str, mensagem: str) -> models.Notification:
    n = models.Notification(user_id=user_id, mensagem=mensagem)
    db.add(n)
    db.commit()
    db.refresh(n)
    # Ganchos futuros (nao implementados no MVP):
    # send_email(user, mensagem); send_whatsapp(user, mensagem); push(user, mensagem)
    return n
