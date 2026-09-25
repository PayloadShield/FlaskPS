"""Integration tests for every built-in Flask route."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "examples"))

from main import (  # noqa: E402
    ALL_CRYPT_TYPES,
    COMPYPS_VERSION,
    FLASKPS_VERSION,
    ROUTE_PREFIX,
    app,
)
from flask_payloadshield import PayloadShieldEnc, get_handler  # noqa: E402

FIXED_DATA = {"message": "Hello, Flask!"}
SECOND_DATA = {"user": "alice", "roles": ["admin", "editor"], "active": True}
_CONFIG_SNAPSHOT = dict(PayloadShieldEnc.get_config())


@pytest.fixture(autouse=True)
def reset_config():
    PayloadShieldEnc.init(_CONFIG_SNAPSHOT)
    yield


def test_all_crypt_types_round_trip():
    client = app.test_client()
    for crypt_type in ALL_CRYPT_TYPES:
        handler = get_handler(crypt_type)
        config = PayloadShieldEnc.get_config()
        prefix = ROUTE_PREFIX[crypt_type]

        response = client.get(f"/{prefix}")
        assert response.status_code == 200
        fixed = handler.decode(response.json["encrypted"], config)
        assert fixed == {
            "message": "Hello, PayloadShield!",
            "ComPyPS": COMPYPS_VERSION,
            "FLaskPS": FLASKPS_VERSION,
        }

        encrypted = handler.encode(SECOND_DATA, config)
        response = client.post(
            f"/{prefix}/cry", json={"encrypted": encrypted}
        )
        assert response.status_code == 200
        assert handler.decode(response.json["encrypted"], config) == SECOND_DATA
