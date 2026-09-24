"""Flask Payload Shield encryption and request/response decorators."""

# Configuration
from .config import PayloadShieldEnc

# Decorators
from .decorators import PayloadShield

# Encryption handlers and utilities
from .crypto import (
    EncryptionHandler,
    Base64EncryptionHandler,
    FernetEncryptionHandler,
    AESGCM256EncryptionHandler,
    HybridRSAEncryptionHandler,
    ChaChaEncryptionHandler,
    ECDHAESGCMEncryptionHandler,
    ECIESEncryptionHandler,
    HPKEEncryptionHandler,
    register_handler,
    get_handler,
)

__version__ = "1.0.0"
__author__ = "Ganesh Kandu"

__all__ = [
    # Configuration
    "PayloadShieldEnc",
    # Decorators
    "PayloadShield",
    # Encryption handlers
    "EncryptionHandler",
    "Base64EncryptionHandler",
    "FernetEncryptionHandler",
    "AESGCM256EncryptionHandler",
    "HybridRSAEncryptionHandler",
    "ChaChaEncryptionHandler",
    "ECDHAESGCMEncryptionHandler",
    "ECIESEncryptionHandler",
    "HPKEEncryptionHandler",
    "register_handler",
    "get_handler",
]

