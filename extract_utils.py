import re
from colorama import Fore
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument

def decode_with_fallback(value):
    """
    Decodifica o valor de bytes usando uma lista de encodings comuns.
    """
    ENCODINGS = ['utf-8', 'latin-1', 'utf-16', 'utf-16le', 'utf-16be', 'ascii', 'cp1252']
    for encoding in ENCODINGS:
        try:
            return value.decode(encoding)
        except (UnicodeDecodeError, AttributeError):
            continue
    return value

def extract_selected_information(file_path):
    """
    Extrai e-mails, URLs e metadados do PDF.
    """
    print(Fore.CYAN + "\nExtracting Emails, URLs, and Metadata...\n")

    emails_found = set()
    urls_found = set()

    try:
        # Extrai texto e busca por e-mails e URLs
        text = extract_text(file_path)
        emails_found.update(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text))
        urls_found.update(re.findall(r'https?://[^\s]+', text))

        # Exibe e-mails encontrados
        if emails_found:
            print(Fore.YELLOW + "\nE-mails Found:")
            for email in emails_found:
                print(Fore.GREEN + email)

        # Exibe URLs encontrados
        if urls_found:
            print(Fore.YELLOW + "\nURLs Found:")
            for url in urls_found:
                print(Fore.GREEN + url)

        # Extrai metadados do PDF
        print(Fore.CYAN + "\nExtracting PDF Metadata...")
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser)
            if document.info:
                for metadata in document.info:
                    for key, value in metadata.items():
                        key_decoded = decode_with_fallback(key)
                        value_decoded = decode_with_fallback(value)
                        print(Fore.BLUE + f"  {key_decoded}: {value_decoded}")

                        # Extrai informações específicas do metadado
                        if "author" in key_decoded.lower():
                            print(Fore.YELLOW + f"  Author: {value_decoded}")
                        if "creationdate" in key_decoded.lower():
                            print(Fore.YELLOW + f"  Creation Date: {value_decoded}")
                        if "moddate" in key_decoded.lower():
                            print(Fore.YELLOW + f"  Modification Date: {value_decoded}")
                        if "os" in key_decoded.lower():
                            print(Fore.YELLOW + f"  Operating System: {value_decoded}")

    except Exception as e:
        print(Fore.RED + f"Error extracting information: {e}")
