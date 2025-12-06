import time
import smtplib
from email.message import EmailMessage

from config import settings
from services.notification_service import get_pending, mark_sent, mark_failed, touch_attempt

def send_smtp(to_email: str, subject: str, body: str) -> None:
    if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise RuntimeError("SMTP no configurado. Define SMTP_HOST/SMTP_USER/SMTP_PASSWORD en .env")

    msg = EmailMessage()
    msg["From"] = settings.SMTP_FROM
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(msg)

def main():
    print("📨 Email worker corriendo... (Ctrl+C para salir)")
    while True:
        pending = get_pending(limit=20)
        if not pending:
            time.sleep(2)
            continue

        for n in pending:
            notif_id = n["id"]
            try:
                touch_attempt(notif_id)
                send_smtp(n["to_email"], n["subject"], n["body"])
                mark_sent(notif_id)
                print(f"✅ Enviado notif #{notif_id} -> {n['to_email']}")
            except Exception as e:
                mark_failed(notif_id, str(e))
                print(f"❌ Falló notif #{notif_id}: {e}")

        time.sleep(1)

if __name__ == "__main__":
    main()
