from typing import Any, Dict, List, Optional
from db import execute_returning_id, fetch_one, fetch_all
from services.notification_service import enqueue_email

def create_transaction(user_id: int, payload: Dict[str, Any], user_email: str) -> Dict[str, Any]:
    tx_id = execute_returning_id(
        """
        INSERT INTO transactions
        (id_transaccion, user_id, monto, moneda,
         origen_tipo, origen_id, destino_tipo, destino_id,
         status, error_code, error_message)
        VALUES
        (:id_transaccion, :user_id, :monto, :moneda,
         :origen_tipo, :origen_id, :destino_tipo, :destino_id,
         :status, :error_code, :error_message)
        """,
        {
            "id_transaccion": payload["id_transaccion"],
            "user_id": user_id,
            "monto": str(payload["monto"]),     
            "moneda": payload["moneda"],
            "origen_tipo": payload["origen_tipo"],
            "origen_id": payload["origen_id"],
            "destino_tipo": payload["destino_tipo"],
            "destino_id": payload["destino_id"],
            "status": payload["status"],
            "error_code": payload.get("error_code"),
            "error_message": payload.get("error_message"),
        },
    )

    if payload["status"] == "FAILED":
        subject = f"Alerta: Transacción fallida {payload['id_transaccion']}"
        body = (
            f"Tu transacción {payload['id_transaccion']} falló.\n"
            f"Monto: {payload['monto']} {payload['moneda']}\n"
            f"Origen: {payload['origen_tipo']} {payload['origen_id']}\n"
            f"Destino: {payload['destino_tipo']} {payload['destino_id']}\n"
            f"Error: {payload.get('error_code') or ''} {payload.get('error_message') or ''}\n"
        )
        enqueue_email(transaction_id=tx_id, to_email=user_email, subject=subject, body=body)

    return {"id": tx_id, "id_transaccion": payload["id_transaccion"], "status": payload["status"]}

def get_transaction_by_code(user_id: int, id_transaccion: str) -> Optional[Dict[str, Any]]:
    return fetch_one(
        """
        SELECT id_transaccion, monto, moneda, status, error_code, error_message, created_at
        FROM transactions
        WHERE user_id = :user_id AND id_transaccion = :id_transaccion
        """,
        {"user_id": user_id, "id_transaccion": id_transaccion},
    )

def list_transactions(user_id: int, limit: int, offset: int) -> Dict[str, Any]:
    items = fetch_all(
        """
        SELECT id_transaccion, monto, moneda, status, created_at
        FROM transactions
        WHERE user_id = :user_id
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
        """,
        {"user_id": user_id, "limit": limit, "offset": offset},
    )
    return {"items": items, "limit": limit, "offset": offset}
