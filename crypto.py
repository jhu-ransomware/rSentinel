from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
import os
import ipaddress
import constants

"""
generate private key
"""
def gen_pri_key():

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
    print(f"Private key for this node generated. Saved as {constants.pri_key} ")
    return private_key

"""
generate CSR
input: private_key
output: csr, if generated; None, if not
"""
def gen_CSR(private_key):
    print("Creating CSR...")
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # CSR info
        x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"California"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"c0conut"),
        x509.NameAttribute(NameOID.COMMON_NAME, u"10.0.0.5"),
    ])).add_extension(
        x509.SubjectAlternativeName([
            x509.IPAddress(ipaddress.IPv4Address(u"10.0.0.5"))
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())

    if isinstance(csr, x509.CertificateSigningRequest):
        print("CSR created.")
        return csr
    else:
        print("CSR creation failed.")
        return None