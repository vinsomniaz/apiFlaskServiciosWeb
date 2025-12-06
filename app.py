from flask import Flask, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

from config import settings
from utils.responses import build_response
from schemas.auth_schema import RegisterSchema, LoginSchema, ValidationError as AuthValidationError
from schemas.transaction_schema import TransactionSchema, ValidationError as TxValidationError

from services.auth_service import create_user, authenticate
from services.transaction_service import create_transaction, get_transaction_by_code, list_transactions
from services.notification_service import get_pending
from services.notification_service import list_all
import traceback


app = Flask(__name__)
CORS(app)

app.config["JWT_SECRET_KEY"] = settings.JWT_SECRET_KEY
jwt = JWTManager(app)

@app.get("/api/v1/health")
def health():
    return build_response(True, "ok", "ok"), 200

@app.post("/api/v1/auth/register")
def register():
    try:
        payload = request.get_json(force=True) or {}
        schema = RegisterSchema.from_json(payload)
        user = create_user(schema.email, schema.password, schema.full_name)
        return build_response(True, user, "Usuario creado"), 200
    except AuthValidationError as e:
        return build_response(False, None, str(e)), 400
    except ValueError as e:
        return build_response(False, None, str(e)), 409
    except Exception:
        return build_response(False, None, "Error interno"), 500

@app.post("/api/v1/auth/login")
def login():
    try:
        payload = request.get_json(force=True) or {}
        schema = LoginSchema.from_json(payload)

        user = authenticate(schema.email, schema.password)
        if not user:
            return build_response(False, None, "Credenciales inválidas"), 401

        token = create_access_token(
        identity=str(user["id"]),
            additional_claims={"email": user["email"]}
        )
        return build_response(True, {"access_token": token}, "OK"), 200
    except AuthValidationError as e:
        return build_response(False, None, str(e)), 400
    except Exception:
        return build_response(False, None, "Error interno"), 500

@app.post("/api/v1/transactions")
@jwt_required()
def post_transaction():
    try:
        from flask_jwt_extended import get_jwt, get_jwt_identity

        user_id = int(get_jwt_identity())
        claims = get_jwt()
        user_email = claims.get("email")
        if not user_email:
            return build_response(False, None, "Token sin email (claims)"), 401

        payload = request.get_json(silent=True) or {}
        tx = TransactionSchema.from_json(payload)

        tx_payload = {
            "id_transaccion": tx.id_transaccion,
            "monto": tx.monto,
            "moneda": tx.moneda,
            "origen_tipo": tx.origen_tipo,
            "origen_id": tx.origen_id,
            "destino_tipo": tx.destino_tipo,
            "destino_id": tx.destino_id,
            "status": tx.status,
            "error_code": tx.error_code,
            "error_message": tx.error_message,
        }

        created = create_transaction(user_id=user_id, payload=tx_payload, user_email=user_email)
        return build_response(True, created, "Transacción registrada"), 201

    except TxValidationError as e:
        return build_response(False, None, str(e)), 400

    except Exception as e:
        print("TX ERROR:", repr(e))
        traceback.print_exc()
        return build_response(False, None, f"Error interno: {type(e).__name__}"), 500

@app.get("/api/v1/transactions/<id_transaccion>")
@jwt_required()
def get_transaction(id_transaccion: str):
    user_id = int(get_jwt_identity())
    tx = get_transaction_by_code(user_id=user_id, id_transaccion=id_transaccion)
    if not tx:
        return build_response(False, None, "No encontrada"), 404
    return build_response(True, tx, "OK"), 200

@app.get("/api/v1/transactions")
@jwt_required()
def get_transactions():
    identity = get_jwt_identity()
    user_id = int(identity["id"])

    try:
        limit = int(request.args.get("limit", "20"))
        offset = int(request.args.get("offset", "0"))
        limit = max(1, min(limit, 100))
        offset = max(0, offset)
    except Exception:
        return build_response(False, None, "limit/offset inválidos"), 400

    data = list_transactions(user_id=user_id, limit=limit, offset=offset)
    return build_response(True, data, "OK"), 200

@app.get("/api/v1/notifications/pending")
@jwt_required()
def pending_notifications():
    return build_response(True, get_pending(limit=50), "OK"), 200

@app.get("/api/v1/notifications")
@jwt_required()
def notifications_all():
    return build_response(True, list_all(50), "OK"), 200

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5007, debug=True)
