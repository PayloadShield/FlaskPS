"""Flask example covering every built-in Flask Payload Shield handler."""

import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa, x25519
from flask import Flask

from flask_payloadshield import PayloadShield, PayloadShieldEnc, get_handler

BASE_DIR = Path(__file__).resolve().parent
app = Flask(__name__)
SYMMETRIC_KEY = "12345678901234567890123456789012"
ROUTE_PREFIX = {
    "base64": "base",
    "fernet": "fernet",
    "aes-gcm-256": "aes",
    "chacha20-poly1305": "chacha",
    "rsa-hybrid": "rsa",
    "ecdh-aes-gcm": "ecdh",
    "ecies": "ecies",
    "hpke": "hpke",
}
ALL_CRYPT_TYPES = list(ROUTE_PREFIX)


def _write_pem_pair_if_missing(private_path: Path, public_path: Path, private_key) -> None:
    if private_path.exists() and public_path.exists():
        return
    private_path.write_bytes(
        private_key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    public_path.write_bytes(
        private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
    )


RSA_PRIVATE = BASE_DIR / "private.pem"
RSA_PUBLIC = BASE_DIR / "public.pem"
EC_PRIVATE = BASE_DIR / "ec_private.pem"
EC_PUBLIC = BASE_DIR / "ec_public.pem"
HPKE_PRIVATE = BASE_DIR / "hpke_private.pem"
HPKE_PUBLIC = BASE_DIR / "hpke_public.pem"

_write_pem_pair_if_missing(RSA_PRIVATE, RSA_PUBLIC, rsa.generate_private_key(65537, 2048))
_write_pem_pair_if_missing(EC_PRIVATE, EC_PUBLIC, ec.generate_private_key(ec.SECP256R1()))
_write_pem_pair_if_missing(HPKE_PRIVATE, HPKE_PUBLIC, x25519.X25519PrivateKey.generate())

PayloadShieldEnc.init({
    "Key": SYMMETRIC_KEY,
    "PrivateKey": str(RSA_PRIVATE),
    "PublicKey": str(RSA_PUBLIC),
    "ECPrivateKey": str(EC_PRIVATE),
    "ECPublicKey": str(EC_PUBLIC),
    "HPKEPrivateKey": str(HPKE_PRIVATE),
    "HPKEPublicKey": str(HPKE_PUBLIC),
})


def _register_routes(crypt_type: str, prefix: str) -> None:
    @app.get(f"/{prefix}", endpoint=f"{prefix}_get")
    @PayloadShield.encrypt(crypt_type)
    def encrypted_response():
        return {"message": "Hello, Flask!"}

    @app.post(f"/{prefix}/dec", endpoint=f"{prefix}_decrypt")
    @PayloadShield.decrypt(crypt_type)
    def decrypted_request(data: dict):
        return data

    @app.post(f"/{prefix}/cry", endpoint=f"{prefix}_crypt")
    @PayloadShield.crypt(crypt_type)
    def encrypted_round_trip(data: dict):
        return data


for _crypt_type, _prefix in ROUTE_PREFIX.items():
    _register_routes(_crypt_type, _prefix)


@app.get("/health")
def health():
    return {"status": "ok"}


def print_postman_examples() -> None:
    sample = {"message": "hello", "id": 1}
    config = PayloadShieldEnc.get_config()
    print("\nPostman quick start: http://127.0.0.1:5000")
    for crypt_type, prefix in ROUTE_PREFIX.items():
        encoded = get_handler(crypt_type).encode(sample, config)
        print(f"{crypt_type}: POST /{prefix}/cry")
        print(json.dumps({"encrypted": encoded}))


if __name__ == "__main__":
    print_postman_examples()
    app.run(host="127.0.0.1", port=8000, debug=True)
