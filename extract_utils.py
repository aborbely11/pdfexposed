import re
import json
from colorama import Fore
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFEncryptionError

def decode_with_fallback(value):
    """
    Decodifica um valor de bytes usando uma lista de encodings comuns e remove caracteres nulos.
    """
    ENCODINGS = ['utf-8', 'latin-1', 'utf-16', 'utf-16le', 'utf-16be', 'ascii', 'cp1252']
    try:
        if isinstance(value, bytes):
            for encoding in ENCODINGS:
                try:
                    decoded_value = value.decode(encoding)
                    if "þÿ" in decoded_value:
                        return value.decode('utf-16').replace('\u0000', '').strip()
                    return decoded_value.replace('\u0000', '').strip()
                except (UnicodeDecodeError, AttributeError):
                    continue
        return value.replace('\u0000', '').strip()
    except Exception:
        return value

def extract_selected_information(file_path, password=None, silent=False):
    """
    Extrai e-mails, URLs, números de telefone, CPF, CNPJ e metadados do PDF.
    Se `silent=True`, não imprime a extração, apenas retorna os dados.
    """
    if not silent:
        print(Fore.CYAN + "\nExtracting Emails, URLs, Phone Numbers, CPF, CNPJ, and Metadata...\n")
    
    emails_found = set()
    urls_found = set()
    phone_numbers_found = set()
    cpf_found = set()
    cnpj_found = set()
    metadata_fields = {}
    operating_system = None
    
    try:
        text = extract_text(file_path, password=password)
        if text:
            emails_found.update(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
            urls_found.update(re.findall(r'https?://[^\s]+', text))
            phone_numbers_found.update(re.findall(r'\(?\d{2,3}\)?[-.\s]?\d{4,5}[-.\s]?\d{4}', text))
            cpf_found.update(re.findall(r'\b\d{3}\.\d{3}\.\d{3}-\d{2}\b', text))
            cnpj_found.update(re.findall(r'\b\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}\b', text))
        
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser, password=password)
            if document.info:
                for metadata in document.info:
                    for key, value in metadata.items():
                        key_decoded = decode_with_fallback(key)
                        value_decoded = decode_with_fallback(value)
                        metadata_fields[key_decoded] = value_decoded
        
        extracted_data = {
            "emails": list(emails_found),
            "urls": list(urls_found),
            "phone_numbers": list(phone_numbers_found),
            "cpf": list(cpf_found),
            "cnpj": list(cnpj_found),
            "metadata": metadata_fields,
            "operating_system": operating_system or "Not detected"
        }
        
        if not silent:
            print(Fore.YELLOW + "\nExtracted Information (JSON Format):")
            print(json.dumps(extracted_data, indent=4, ensure_ascii=False))
        
        return extracted_data
    
    except PDFEncryptionError:
        if not silent:
            print(Fore.RED + "Error: Incorrect password provided.")
        return {}
    except Exception as e:
        if not silent:
            print(Fore.RED + f"Error extracting information: {e}")
        return {}
