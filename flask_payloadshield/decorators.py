"""Flask decorators for automatic payload encryption and decryption."""

import inspect
from functools import wraps
from typing import Any, Callable

from flask import jsonify, request

from .config import PayloadShieldEnc
from .crypto import get_handler

def _replace_body_argument(
    func: Callable,
    args: tuple,
    kwargs: dict,
    original_body: Any,
    decrypted_data: Any,
) -> tuple[tuple, dict]:
    """Replace the body argument Flask passed to the decorated view."""
    updated_args = list(args)
    for index, value in enumerate(updated_args):
        if value == original_body:
            updated_args[index] = decrypted_data
            return tuple(updated_args), kwargs

    for key, value in kwargs.items():
        if value == original_body:
            kwargs[key] = decrypted_data
            return args, kwargs

    for parameter in inspect.signature(func).parameters.values():
        if parameter.name not in kwargs and parameter.kind in (
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
            inspect.Parameter.KEYWORD_ONLY,
        ):
            kwargs[parameter.name] = decrypted_data
            break
    return args, kwargs


def _wrap_encrypted(data: Any) -> dict:
    """Normalize a route's return value into a dict payload before encoding."""
    return data if isinstance(data, dict) else {"data": data}


def _call_func(func: Callable, *args, **kwargs) -> Any:
    """Call a synchronous Flask view and reject unsupported awaitables."""
    result = func(*args, **kwargs)
    if inspect.isawaitable(result):
        raise TypeError("Flask PayloadShield routes must be synchronous")
    return result


class PayloadShield:
    """
    Namespace of decorator factories for encrypting/decrypting Flask
    request and response payloads.

    Usage:
        PayloadShieldEnc.init({"Key": "..."})

        @app.get("/api/endpoint")
        @PayloadShield.encrypt("base64")
        def route(): ...

        @app.post("/api/endpoint")
        @PayloadShield.decrypt("base64")
        def route(data: dict): ...

        @app.post("/api/endpoint")
        @PayloadShield.crypt("base64")
        def route(data: dict): ...
    """

    @staticmethod
    def encrypt(encryption_type: str = "base64") -> Callable:
        """
        Decorator that encrypts the route's response payload only.

        The response is wrapped as ``{"encrypted": "<encoded-data>"}``.
        """
        handler = get_handler(encryption_type)

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                result = _call_func(func, *args, **kwargs)
                config = PayloadShieldEnc.get_config()
                encoded = handler.encode(_wrap_encrypted(result), config)
                return jsonify({"encrypted": encoded})

            return wrapper

        return decorator

    @staticmethod
    def decrypt(encryption_type: str = "base64") -> Callable:
        """
        Decorator that decrypts the incoming request payload only.

        Expects the request body to be ``{"encrypted": "<encoded-data>"}``.
        """
        handler = get_handler(encryption_type)

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                body = request.get_json(silent=True)
                if isinstance(body, dict) and "encrypted" in body:
                    config = PayloadShieldEnc.get_config()
                    try:
                        decrypted = handler.decode(body["encrypted"], config)
                    except Exception as e:
                        return jsonify(
                            {"error": f"Failed to decrypt request: {str(e)}"}
                        ), 400
                    args, kwargs = _replace_body_argument(
                        func, args, kwargs, body, decrypted
                    )

                return _call_func(func, *args, **kwargs)

            return wrapper

        return decorator

    @staticmethod
    def crypt(encryption_type: str = "base64") -> Callable:
        """Decrypt the request and encrypt the response using one handler."""
        handler = get_handler(encryption_type)

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                body = request.get_json(silent=True)
                if isinstance(body, dict) and "encrypted" in body:
                    config = PayloadShieldEnc.get_config()
                    try:
                        decrypted = handler.decode(body["encrypted"], config)
                    except Exception as e:
                        return jsonify(
                            {"error": f"Failed to decrypt request: {str(e)}"}
                        ), 400
                    args, kwargs = _replace_body_argument(
                        func, args, kwargs, body, decrypted
                    )

                result = _call_func(func, *args, **kwargs)
                config = PayloadShieldEnc.get_config()
                encoded = handler.encode(_wrap_encrypted(result), config)
                return jsonify({"encrypted": encoded})

            return wrapper

        return decorator

