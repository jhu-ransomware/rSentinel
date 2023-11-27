from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64
from logconfig import get_logger

logger = get_logger(__name__)

def encrypt_config_file():
    with open("config.txt", "rb") as config_file:
        config_data = config_file.read()
    key = get_random_bytes(32)
    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(config_data, AES.block_size))
    encoded_key = base64.b64encode(key).decode("utf-8")  # Encode the key in Base64
    with open("keys.txt", "w") as key_file:
        key_file.write(encoded_key)
    with open("config.txt", "wb") as config_file:
        config_file.write(cipher.iv + ciphertext)

def decrypt_config_file():
    with open("keys.txt", "r") as key_file:
        encoded_key = key_file.read()
        key = base64.b64decode(encoded_key.encode("utf-8"))  # Decode the Base64-encoded key

    with open("config.txt", "rb") as config_file:  # Open in binary mode
        data = config_file.read()
        # Find the index of the first occurrence of '\r\n' or '\n'
        index = data.find(b'\r\n') if b'\r\n' in data else data.find(b'\n')
        # Split the data into iv and ciphertext based on the index
        iv = data[:16]
        ciphertext = data[16:]

    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(ciphertext), AES.block_size)
    config_str = decrypted_data.decode("utf-8")
    config_lines = config_str.split("\n")
    # logger.info(f"The contents of the config file are: \n {config_str}")
    config_dict = {}
    for line in config_lines:
        if "=" in line:
            key, value = line.split("=")
            config_dict[key] = value

    return config_dict