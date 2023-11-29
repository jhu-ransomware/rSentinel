import os
import constants
import crypto_helper
from logconfig import get_logger

logger = get_logger(__name__)

tracked_magic_numbers = {}

def get_magic_number(filename):
    with open(filename, 'rb') as f:
        header = f.read(4)
    
    # Check for PDF
    if header.startswith(b'%PDF'):
        return 'PDF'

    # Check for DOCX (and other ZIP-based file formats like XLSX, PPTX)
    if header.startswith(b'PK\x03\x04'):
        return 'DOCX'

    return None

def save_magic_numbers(files):
    for file in files:
        magic_number = get_magic_number(file)
        tracked_magic_numbers[file] = magic_number.hex()

def check_magic_numbers():
    global tracked_magic_numbers

    config_dict = crypto_helper.decrypt_config_file()
    pdf_paths = [config_dict.get(f"PDF_PATH_{i}", "").strip() for i in range(4)]  # Assuming 4 PDF files
    # pdf_paths = ["/Users/preethamnagesh8/Documents/JHU MSSI/Capstone Project/rSentinel/test/test.docx"]
    tampered_pdf_count = 0

    for i, pdf_path in enumerate(pdf_paths):
        if not pdf_path:
            logger.debug(f"PDF file {i} path is missing or empty in the configuration.")
            tampered_pdf_count += 1
        else:
            logger.debug(f"Checking PDF file {i} at path: {pdf_path}")

            if not os.path.exists(pdf_path):
                logger.debug(f"PDF file {i} does not exist at path: {pdf_path}")
                tampered_pdf_count += 1
            else:
                magic_number = get_magic_number(pdf_path)
                logger.debug(f"Magic number for PDF file {i}: {magic_number}")

                if magic_number != 'PDF':
                    logger.debug(f"PDF file {i} has been tampered with.")
                    tampered_pdf_count += 1

    
    docx_paths = [config_dict.get(f"DOCX_PATH_{i}", "").strip() for i in range(6)]  # Assuming 6 DOCX files

    tampered_docx_count = 0
    for i, docx_path in enumerate(docx_paths):
        if not docx_path:
            logger.debug(f"DOCX file {i} path is missing or empty in the configuration.")
            tampered_docx_count += 1
        else:
            logger.debug(f"Checking DOCX file {i} at path: {docx_path}")

            if not os.path.exists(docx_path):
                logger.debug(f"DOCX file {i} does not exist at path: {docx_path}")
                tampered_docx_count += 1
            else:
                magic_number = get_magic_number(docx_path)
                logger.debug(f"Magic number for DOC file {i}: {magic_number}")

                if magic_number != 'DOCX':
                    logger.debug(f"PDF file {i} has been tampered with.")
                    tampered_docx_count += 1

    total_tampered_count = tampered_pdf_count + tampered_docx_count
    return total_tampered_count > 5

if __name__ == '__main__':
    result = check_magic_numbers()
    if result:
        logger.debug("More than 50% of the files in the directory have changed file types.")
    else:
        logger.debug("Less than or equal to 50% of the files in the directory have changed file types.")
