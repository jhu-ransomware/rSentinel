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
    return hasher.hexdigest()  # Return the hexadecimal digest

def generate_combined_hash():
    """Generate a combined hash of all Python files in the directory."""
    combined_hasher = hashlib.sha256()
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_hash = hash_file(file_path)
                combined_hasher.update(file_hash.encode())  # Convert hexdigest back to bytes
    return combined_hasher.hexdigest()  # Return the hexadecimal digest

def sign_data(data):
    """Sign data using a private RSA key."""
    with open(private_key_path, 'rb') as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    # Convert hexdigest back to bytes for signing
    data_bytes = bytes.fromhex(data)

    signature = private_key.sign(
        data_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def compare_hash(received_hash, original_hash):
    return received_hash == original_hash

def verify_signature(data, signature):
    """Verify the signature using the public RSA key."""
    with open(public_key_path, 'rb') as key_file:
        public_key = serialization.load_pem_public_key(
            key_file.read(),
            backend=default_backend()
        )

    # Convert hexdigest back to bytes for verification
    data_bytes = bytes.fromhex(data)

    try:
        public_key.verify(
            signature,
            data_bytes,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        logger.info(f"Verification Succeeded")
        return True
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False

if __name__ == "__main__":
    # Generate and sign the combined hash
    combined_hash = generate_combined_hash()
    os.environ['COMBINED_HASH'] = combined_hash
    print(f"Combined Hash: {combined_hash}")

    # Sign the combined hash
    signature = sign_data(combined_hash)

    # Convert the signature to a hex string for display or storage
    signature_hex = signature.hex()
    print(f"Signature: {signature_hex}")

    # For verification, convert the hex string back to bytes
    signature_bytes = bytes.fromhex(signature_hex)

    # Recompute the combined hash on the other machine
    combined_hash = os.getenv('COMBINED_HASH')

    # Verify the signature
    is_valid = verify_signature(combined_hash, signature_bytes)
    print(f"Signature is valid: {is_valid}")
