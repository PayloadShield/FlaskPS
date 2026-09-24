"""Tests for Flask PayloadShield decorators."""

import base64
import json

from flask import Flask

from flask_payloadshield import PayloadShield, PayloadShieldEnc

PayloadShieldEnc.init({"Key": "0123456789abcdef0123456789abcdef"})
app = Flask(__name__)


@app.get("/encrypt-only")
@PayloadShield.encrypt("base64")
def encrypt_only():
    return {"message": "hello"}


@app.post("/decrypt-only")
@PayloadShield.decrypt("base64")
def decrypt_only(data: dict):
    return {"received": data}


@app.post("/crypt")
@PayloadShield.crypt("base64")
def crypt_both(data: dict):
    return {"echo": data}


client = app.test_client()


def _encode(payload: dict) -> str:
    return base64.b64encode(json.dumps(payload).encode("utf-8")).decode("utf-8")


def _decode(encoded: str) -> dict:
    return json.loads(base64.b64decode(encoded).decode("utf-8"))


def test_encrypt_only_wraps_response():
    response = client.get("/encrypt-only")
    assert response.status_code == 200
    assert _decode(response.json["encrypted"]) == {"message": "hello"}


def test_decrypt_only_injects_payload_into_view():
    payload = {"username": "admin", "password": "secret"}
    response = client.post("/decrypt-only", json={"encrypted": _encode(payload)})
    assert response.status_code == 200
    assert response.json == {"received": payload}


def test_crypt_round_trips_request_and_response():
    payload = {"name": "Alice"}
    response = client.post("/crypt", json={"encrypted": _encode(payload)})
    assert response.status_code == 200
    assert _decode(response.json["encrypted"]) == {"echo": payload}


def test_invalid_encrypted_request_returns_bad_request():
    response = client.post("/crypt", json={"encrypted": "invalid"})
    assert response.status_code == 400
    assert "error" in response.json
