from typing import Any, Dict, List
from db import execute_returning_id, fetch_all, execute

def enqueue_email(transaction_id: int, to_email: str, subject: str, body: str) -> int:
    notif_id = execute_returning_id(
        """
        INSERT INTO email_notifications (transaction_id, to_email, subject, body, status, attempts)
        VALUES (:transaction_id, :to_email, :subject, :body, 'PENDING', 0)
        """,
        {"transaction_id": transaction_id, "to_email": to_email, "subject": subject, "body": body},
    )
    return notif_id

def get_pending(limit: int = 50) -> List[Dict[str, Any]]:
    return fetch_all(
        """
        SELECT id, transaction_id, to_email, subject, body, attempts
        FROM email_notifications
        WHERE status = 'PENDING'
        ORDER BY created_at ASC
        LIMIT :limit
        """,
        {"limit": limit},
    )

def mark_sent(notification_id: int) -> None:
    execute(
        """
        UPDATE email_notifications
        SET status='SENT', sent_at=NOW()
        WHERE id = :id
        """,
        {"id": notification_id},
    )

def mark_failed(notification_id: int, err: str) -> None:
    execute(
        """
        UPDATE email_notifications
        SET status='FAILED', last_error=:err, attempts=attempts+1
        WHERE id = :id
        """,
        {"id": notification_id, "err": (err or "")[:255]},
    )

def touch_attempt(notification_id: int) -> None:
    execute(
        "UPDATE email_notifications SET attempts=attempts+1 WHERE id=:id",
        {"id": notification_id},
    )

def list_all(limit: int = 50):
    return fetch_all(
        """
        SELECT id, transaction_id, to_email, subject, status, attempts, last_error, created_at, sent_at
        FROM email_notifications
        ORDER BY created_at DESC
        LIMIT :limit
        """,
        {"limit": limit},
    )