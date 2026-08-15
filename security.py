from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def generar_password_hash(
        password: str,
) -> str:
    return password_hash.hash(password)
