from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import os
import ipaddress
import constants
from logconfig import get_logger
import inspect

logger = get_logger(__name__)

"""
generate private key
"""
def gen_pri_key():

    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")

    if os.path.exists(constants.pri_key):
        os.remove(constants.pri_key)

    # Generate a private key for Node 1
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
    )
    # Write private key to file
    with open(constants.pri_key, 'wb') as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    logger.debug(f"Private key for this node generated. Saved as {constants.pri_key} ")
    return private_key

"""
generate CSR
input: private_key
output: csr, if generated; None, if not
"""
def gen_CSR(private_key):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # CSR info
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"c0conut"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"{}".format(constants.CRYPTO_LIB_COMMON_NAME)),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.IPAddress(ipaddress.IPv4Address(u"{}".format(constants.CRYPTO_LIB_COMMON_NAME)))
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    if isinstance(csr, x509.CertificateSigningRequest):
        logger.debug(f"{current_function_name} - CSR created.")
        #print_csr_info(csr)
        return csr
    else:
        logger.error(f"{current_function_name} - CSR creation failed.")
        return None

def print_csr_info(csr):

    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    
    logger.debug(f"{current_function_name} - CSR Information:")
    logger.debug(f"{current_function_name} - Subject:", csr.subject)
    for extension in csr.extensions:
        logger.debug(f"{current_function_name} - Extension:", extension.oid._name, extension.value)

def print_cert_info(cert_path):
    current_function_name = inspect.currentframe().f_globals["__name__"] + "." + inspect.currentframe().f_code.co_name
    logger.debug(f"Currently executing: {current_function_name}")
    
    # Load the certificate from the file
    with open(cert_path, "rb") as cert_file:
        cert_data = cert_file.read()
        cert = x509.load_pem_x509_certificate(cert_data, default_backend())

    # Print certificate information
    logger.debug(f"{current_function_name} - Certificate Information:")
    logger.debug(f"{current_function_name} - Issuer:", cert.issuer)
    logger.debug(f"{current_function_name} - Subject:", cert.subject)
    logger.debug(f"{current_function_name} - Valid From:", cert.not_valid_before)
    logger.debug(f"{current_function_name} - Valid To:", cert.not_valid_after)
    logger.debug(f"{current_function_name} - Serial Number:", cert.serial_number)

    for extension in cert.extensions:
        print("Extension:", extension.oid._name, extension.value)