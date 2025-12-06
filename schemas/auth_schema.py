from dataclasses import dataclass

class ValidationError(ValueError):
    pass

def _require_str(data, key: str) -> str:
    val = data.get(key)
    if not isinstance(val, str) or not val.strip():
        raise ValidationError(f"'{key}' es requerido y debe ser string.")
    return val.strip()

@dataclass(frozen=True)
class RegisterSchema:
    email: str
    password: str
    full_name: str

    @staticmethod
    def from_json(data: dict) -> "RegisterSchema":
        email = _require_str(data, "email").lower()
        password = _require_str(data, "password")
        full_name = data.get("full_name", "")
        if full_name is None:
            full_name = ""
        if not isinstance(full_name, str):
            raise ValidationError("'full_name' debe ser string.")
        full_name = full_name.strip()

        if "@" not in email or "." not in email:
            raise ValidationError("Email inválido.")
        if len(password) < 6:
            raise ValidationError("La contraseña debe tener al menos 6 caracteres.")

        return RegisterSchema(email=email, password=password, full_name=full_name)

@dataclass(frozen=True)
class LoginSchema:
    email: str
    password: str

    @staticmethod
    def from_json(data: dict) -> "LoginSchema":
        email = _require_str(data, "email").lower()
        password = _require_str(data, "password")

        if "@" not in email or "." not in email:
            raise ValidationError("Email inválido.")

        return LoginSchema(email=email, password=password)
