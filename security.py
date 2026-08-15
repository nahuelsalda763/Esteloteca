from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128

password_hash = PasswordHash.recommended()

def generar_password_hash(
        password: str,
) -> str:
    return password_hash.hash(password)

def verificar_password(
        password: str,
        hash_guardado: str,
) -> bool:

    try:
        return password_hash.verify(
            password,
            hash_guardado,
        )
    except UnknownHashError:
        return False


def validar_password(
        password: str,
) -> str | None:
    if len(password) < PASSWORD_MIN_LENGTH:
        return (
            "La contraseña debe tener "
            f"al menos {PASSWORD_MIN_LENGTH} "
            "caracteres."
        )

    if password.isspace():
        return (
            "La contraseña no puede estar "
            "formada únicamente por espacios."
        )

    return None