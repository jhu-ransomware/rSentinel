import os
import random
import hashlib
from logconfig import get_logger
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
from reportlab.lib.pagesizes import letter
from docx import Document
import base64
import string
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import crypto_helper

logger = get_logger(__name__)


def generate_random_filename():
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))

def generate_random_text(length=100):
    printable_characters = string.ascii_letters + string.digits + string.punctuation + string.whitespace
    # Filter out characters that are not XML-compatible
    xml_compatible_characters = [char for char in printable_characters if char.isprintable()]
    text = ''.join(random.choice(xml_compatible_characters) for _ in range(length))

    # Replace characters that might interfere with PDF generation
    text = text.replace('<', ' ').replace('>', ' ')

    return text

def generate_pdf(file_path):
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()

    pdf_text = generate_random_text()  # Generate random text for the PDF
    pdf_paragraph = Paragraph(pdf_text, styles["Normal"])

    content = [pdf_paragraph, Spacer(1, 12)]  # Add a spacer for better formatting

    doc.build(content)
    return file_path, calculate_sha256(file_path)

def generate_docx(file_path, index):
    doc = Document()
    doc_text = generate_random_text()  # Generate random text for the DOCX
    doc.add_paragraph(doc_text)
    doc.save(file_path.format(index))
    return file_path.format(index), calculate_sha256(file_path.format(index))

def generate_random_location(locations):
    return random.choice(locations)

def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

def write_config_file(pdf_paths, docx_paths, pdf_hashes, docx_hashes):
    with open("config.txt", "w") as config_file:
        for i, pdf_path in enumerate(pdf_paths):
            config_file.write(f"PDF_PATH_{i}={pdf_path}\n")
        for i, docx_path in enumerate(docx_paths):
            config_file.write(f"DOCX_PATH_{i}={docx_path}\n")
        for i, pdf_hash in enumerate(pdf_hashes):
            config_file.write(f"PDF_HASH_{i}={pdf_hash}\n")
        for i, docx_hash in enumerate(docx_hashes):
            config_file.write(f"DOCX_HASH_{i}={docx_hash}\n")


def validate_files():
    config_dict = crypto_helper.decrypt_config_file()
    pdf_paths = [config_dict.get(f"PDF_PATH_{i}", "").strip() for i in range(4)]  # Assuming 4 PDF files
    pdf_hashes_expected = [config_dict.get(f"PDF_HASH_{i}") for i in range(4)]

    tampered_pdf_count = 0
    for i, pdf_path in enumerate(pdf_paths):
        if not pdf_path:
            logger.debug(f"PDF file {i} path is missing or empty in the configuration.")
            tampered_pdf_count += 1
        else:
            logger.debug(f"Checking PDF file {i} at path: {pdf_path}")
            logger.debug(f"Actual path {i}: '{pdf_path}'")

            if not os.path.exists(pdf_path):
                logger.debug(f"PDF file {i} does not exist at path: {pdf_path}")
                tampered_pdf_count += 1
            else:
                pdf_hash_actual = calculate_sha256(pdf_path)
                logger.debug(f"Calculated PDF hash for file {i}: {pdf_hash_actual}")
                logger.debug(f"Expected PDF hash for file {i}: {pdf_hashes_expected[i]}")

                if pdf_hash_actual.strip() != pdf_hashes_expected[i].strip():
                    logger.debug(f"PDF file {i} has been tampered with.")
                    tampered_pdf_count += 1

    docx_paths = [config_dict.get(f"DOCX_PATH_{i}", "").strip() for i in range(6)]  # Assuming 6 DOCX files
    docx_hashes_expected = [config_dict.get(f"DOCX_HASH_{i}") for i in range(6)]

    tampered_docx_count = 0
    for i, docx_path in enumerate(docx_paths):
        if not docx_path:
            logger.debug(f"DOCX file {i} path is missing or empty in the configuration.")
            tampered_docx_count += 1
        else:
            logger.debug(f"Checking DOCX file {i} at path: {docx_path}")
            logger.debug(f"Actual path {i}: '{docx_path}'")

            if not os.path.exists(docx_path):
                logger.debug(f"DOCX file {i} does not exist at path: {docx_path}")
                tampered_docx_count += 1
            else:
                docx_hash_actual = calculate_sha256(docx_path)
                logger.debug(f"Calculated DOCX hash for file {i}: {docx_hash_actual}")
                logger.debug(f"Expected DOCX hash for file {i}: {docx_hashes_expected[i]}")

                if docx_hash_actual.strip() != docx_hashes_expected[i].strip():
                    logger.debug(f"DOCX file {i} has been tampered with.")
                    tampered_docx_count += 1

    total_tampered_count = tampered_pdf_count + tampered_docx_count
    return total_tampered_count > 5





def execute_canary_logic():
    # Check if config.txt and keys.txt exist
    if os.path.exists("config.txt") and os.path.exists("keys.txt"):
        # Step 6: Decryption and Validation
        result = validate_files()

        if result:
            logger.debug("More than 5 files have been modified or tampered with.")
            return 1
        else:
            logger.debug("All files have not been modified or tampered with.")
            return 0
    elif os.path.exists("config.txt") or os.path.exists("keys.txt"):
        logger.info("Tampering detected. Both config.txt and keys.txt are required.")
        return 1
    else:
        # Step 1: File Generation
        pdf_filenames = [f"{generate_random_filename()}.pdf" for _ in range(4)]
        docx_filename = "{}_{}.docx".format(generate_random_filename(), "{}")

        # Specify the full path for file generation
        pdf_paths = [
            os.path.join(
                generate_random_location(["C:\\Users\\rSUser\\Downloads", "C:\\Users\\rSUser\\Desktop", "C:\\Users\\rSUser\\Documents"]),
                pdf_filename
            ) for pdf_filename in pdf_filenames
        ]

        docx_paths = [
            os.path.join(
                generate_random_location(["C:\\Users\\rSUser\\Downloads", "C:\\Users\\rSUser\\Desktop", "C:\\Users\\rSUser\\Documents"]),
                docx_filename.format(i)
            ) for i in range(6)  # Assuming 6 DOCX files
        ]

        for pdf_path in pdf_paths:
            generate_pdf(pdf_path)

        for i, docx_path in enumerate(docx_paths):
            generate_docx(docx_path, i)

        # Print the generated file paths
        logger.debug("Generated PDF Paths: %s", pdf_paths)
        logger.debug("Generated DOCX Paths: %s", docx_paths)

        # Step 2: Storage
        # No changes needed here, already using the generated paths

        # Print the final storage paths
        logger.debug("PDF Storage Paths: %s", pdf_paths)
        logger.debug("DOCX Storage Paths: %s", docx_paths)

        # Step 3: Hash Calculation
        pdf_hashes = [calculate_sha256(pdf_path) for pdf_path in pdf_paths]
        docx_hashes = [calculate_sha256(docx_path) for docx_path in docx_paths]

        # Step 4: Configuration File
        write_config_file(pdf_paths, docx_paths, pdf_hashes, docx_hashes)

        # Step 5: Encryption
        crypto_helper.encrypt_config_file()

        logger.debug("Files and configuration generated.")
        return 0



if __name__ == "__main__":
    result = execute_canary_logic()
