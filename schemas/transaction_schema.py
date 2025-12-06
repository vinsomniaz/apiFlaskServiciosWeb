from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Optional

class ValidationError(ValueError):
    pass

def _req(data: dict, key: str):
    if key not in data:
        raise ValidationError(f"'{key}' es requerido.")
    return data[key]

def _req_str(data: dict, key: str) -> str:
    v = _req(data, key)
    if not isinstance(v, str) or not v.strip():
        raise ValidationError(f"'{key}' debe ser string no vacío.")
    return v.strip()

def _req_obj(data: dict, key: str) -> dict:
    v = _req(data, key)
    if not isinstance(v, dict):
        raise ValidationError(f"'{key}' debe ser un objeto JSON.")
    return v

@dataclass(frozen=True)
class TransactionSchema:
    id_transaccion: str
    monto: Decimal
    moneda: str
    origen_tipo: str
    origen_id: str
    destino_tipo: str
    destino_id: str
    status: str
    error_code: Optional[str]
    error_message: Optional[str]

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "TransactionSchema":
        id_transaccion = _req_str(data, "id_transaccion")
        moneda = _req_str(data, "moneda").upper()
        if len(moneda) != 3:
            raise ValidationError("'moneda' debe tener 3 letras (ej: PEN, USD).")

        monto_val = _req(data, "monto")
        try:
            monto = Decimal(str(monto_val))
        except Exception:
            raise ValidationError("'monto' debe ser numérico.")
        if monto <= 0:
            raise ValidationError("'monto' debe ser mayor que 0.")

        origen = _req_obj(data, "origen")
        destino = _req_obj(data, "destino")

        origen_tipo = _req_str(origen, "tipo")
        origen_id = _req_str(origen, "id")
        destino_tipo = _req_str(destino, "tipo")
        destino_id = _req_str(destino, "id")

        status = _req_str(data, "status").upper()
        if status not in ("OK", "FAILED"):
            raise ValidationError("'status' debe ser 'OK' o 'FAILED'.")

        error_code = data.get("error_code")
        error_message = data.get("error_message")

        if error_code is not None and not isinstance(error_code, str):
            raise ValidationError("'error_code' debe ser string o null.")
        if error_message is not None and not isinstance(error_message, str):
            raise ValidationError("'error_message' debe ser string o null.")

        # Si es FAILED, al menos un error debe venir (recomendado)
        if status == "FAILED" and (not (error_code or "").strip()) and (not (error_message or "").strip()):
            raise ValidationError("Si 'status' es FAILED, envía 'error_code' o 'error_message'.")

        return TransactionSchema(
            id_transaccion=id_transaccion,
            monto=monto,
            moneda=moneda,
            origen_tipo=origen_tipo,
            origen_id=origen_id,
            destino_tipo=destino_tipo,
            destino_id=destino_id,
            status=status,
            error_code=(error_code.strip() if isinstance(error_code, str) else None),
            error_message=(error_message.strip() if isinstance(error_message, str) else None),
        )
