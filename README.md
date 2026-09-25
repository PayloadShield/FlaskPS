# Flask Payload Shield

Pluggable Flask decorators for encrypting and decrypting request and response
payloads.

## Installation

```bash
pip install flask-payloadshield
```

Project page: <https://pypi.org/project/flask-payloadshield/>

For local development:

```bash
git clone https://github.com/PayloadShield/FlaskPS.git
cd FlaskPS
python -m venv .venv

# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux/macOS
# source .venv/bin/activate

python -m pip install -e ".[dev]"
```

## Quick Start

```python
from flask import Flask
from flask_payloadshield import PayloadShield, PayloadShieldEnc

app = Flask(__name__)
PayloadShieldEnc.init({"Key": "12345678901234567890123456789012"})

@app.get("/data")
@PayloadShield.encrypt("aes-gcm-256")
def get_data():
    return {"message": "hello"}

@app.post("/process")
@PayloadShield.decrypt("aes-gcm-256")
def process_data(data: dict):
    return {"received": data}

@app.post("/secure")
@PayloadShield.crypt("aes-gcm-256")
def secure_endpoint(data: dict):
    return {"processed": data}

if __name__ == "__main__":
    app.run(debug=True)
```

Send encrypted requests using this envelope:

```json
{"encrypted": "<encoded payload>"}
```

The `decrypt` and `crypt` decorators inject the decrypted object into the
first route parameter, such as `data` above. Decryption errors return HTTP
400 with an `error` field.

## Built-in Handlers

| Name | Algorithm | Keys |
|---|---|---|
| `base64` | Base64 encoding | None; obfuscation only |
| `fernet` | Fernet | `Key` |
| `aes-gcm-256` | AES-256-GCM | `Key` resolving to 32 bytes |
| `chacha20-poly1305` | ChaCha20-Poly1305 | `Key` resolving to 32 bytes |
| `rsa-hybrid` | RSA-OAEP + AES-256-GCM | `PublicKey`, `PrivateKey` |
| `ecdh-aes-gcm` | ECDH P-256 + AES-256-GCM | `ECPublicKey`, `ECPrivateKey` |
| `ecies` | ECDH P-256 + AES-CTR + HMAC | `ECPublicKey`, `ECPrivateKey` |
| `hpke` | RFC 9180 HPKE with X25519 | `HPKEPublicKey`, `HPKEPrivateKey` |

PEM values may be raw key content or file paths. `PayloadShieldEnc.init()`
resets omitted keys to `None` and `get_config()` returns the current config.

## Example and Postman

```bash
cd examples
python main.py
```

The example runs on `http://127.0.0.1:5000`, generates missing RSA, EC, and
X25519 PEM files, and prints ready-to-paste Postman request bodies for every
handler at startup. Use `Ctrl+C` to stop it.

In another terminal, verify the app:

```bash
curl http://127.0.0.1:5000/health
curl http://127.0.0.1:5000/aes
```

## Development

```bash
pip install -e ".[dev]"
pytest
```

## Publishing

Set a PyPI API token and run the publishing script from the project root:

```bash
export PYPI_TOKEN="pypi-..."
bash publish.sh
```

The script builds and checks the package before uploading it to
<https://pypi.org/project/flask-payloadshield/>. The package version in
`pyproject.toml` must be incremented before publishing a new release.

## License

Apache-2.0 - See [LICENSE](LICENSE).

---

## 📞 Support

- **GitHub Issues**: https://github.com/PayloadShield/FlaskPS/issues
- **PyPI Page**: https://pypi.org/project/flask_payloadshield/
- **Author**: Ganesh Kandu <kanduganesh@gmail.com>