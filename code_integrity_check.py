import os
import hashlib
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from logconfig import get_logger

logger = get_logger(__name__)

directory_path = './'  # Replace with your directory path
private_key_path = 'private_key.pem'  # Replace with your private key file path
public_key_path = 'public_key.pem'

def hash_file(file_path):
    """Generate SHA-256 hash of a file."""
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        buf = f.read(4096)
        while buf:
            hasher.update(buf)
            buf = f.read(4096)
    return hasher.digest()

def generate_combined_hash():
    """Generate a combined hash of all Python files in the directory."""
    global directory_path
    combined_hasher = hashlib.sha256()
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                combined_hasher.update(hash_file(file_path))
    return combined_hasher.digest()

def sign_data(data):
    """Sign data using a private RSA key."""
    global private_key_path
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    signature = private_key.sign(
        data,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature


def verify_signature(data, signature):
    """Verify the signature using the public RSA key."""
    global public_key_path
    with open(public_key_path, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    try:
        public_key.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except Exception as e:
        return False

# Generate and sign the combined hash
combined_hash = generate_combined_hash()
print(f"Combined Hash: {combined_hash}")

signature = sign_data(combined_hash)

# Optionally, you can convert the signature to a hex string for easy display or storage
signature_hex = signature.hex()
print(f"Signature: {signature_hex}")

# Convert the hex string back to bytes
signature = bytes.fromhex(signature_hex)

signature_hex = signature  # Replace with the signature received

# Recompute the combined hash on the other machine
combined_hash = generate_combined_hash()

# Verify the signature
is_valid = verify_signature(combined_hash, signature)
print(f"Signature is valid: {is_valid}")
