#!/usr/bin/env python3
"""Generate VAPID keys for Web Push notifications.

Usage:
    python scripts/generate_vapid_keys.py

This script generates a VAPID key pair and prints the public/private keys.
Add these to your .env file:
    VAPID_PUBLIC_KEY=<public_key>
    VAPID_PRIVATE_KEY=<private_key>

Note: You need pywebpush and cryptography installed:
    pip install pywebpush cryptography
"""

import sys
import base64
import os

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.backends import default_backend
except ImportError:
    print("Error: cryptography package not installed")
    print("Run: pip install cryptography")
    sys.exit(1)


def generate_vapid_keys():
    """Generate VAPID key pair for Web Push notifications."""
    # Generate EC key pair using P-256 curve
    private_key = ec.generate_private_key(ec.SECP256R1(), default_backend())
    public_key = private_key.public_key()
    
    # Serialize private key to bytes
    private_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    
    # Serialize public key to bytes
    public_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.X962,
        format=serialization.PublicFormat.UncompressedPoint
    )
    
    # Base64URL encode the keys (remove padding)
    private_key_b64 = base64.urlsafe_b64encode(private_bytes).decode('ascii').rstrip('=')
    public_key_b64 = base64.urlsafe_b64encode(public_bytes).decode('ascii').rstrip('=')
    
    return private_key_b64, public_key_b64


def main():
    print("=" * 70)
    print("VAPID Key Generator for CondoManager Web Push")
    print("=" * 70)
    print()
    
    print("Generating VAPID key pair...")
    print()
    
    private_key, public_key = generate_vapid_keys()
    
    print("Generated keys:")
    print("-" * 70)
    print()
    print("VAPID_PUBLIC_KEY:")
    print(public_key)
    print()
    print("VAPID_PRIVATE_KEY:")
    print(private_key)
    print()
    print("-" * 70)
    print()
    print("Add these to your .env file:")
    print()
    print("# Web Push Configuration")
    print(f'VAPID_PUBLIC_KEY="{public_key}"')
    print(f'VAPID_PRIVATE_KEY="{private_key}"')
    print('VAPID_CLAIMS_SUB="mailto:admin@condomanager.app"')
    print()
    print("=" * 70)
    print("IMPORTANT: Keep your private key secure! Never commit it to git.")
    print("=" * 70)


if __name__ == "__main__":
    main()
