import re
from colorama import Fore
from pdfminer.high_level import extract_text
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFEncryptionError

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

def extract_selected_information(file_path, password=None):
    """
    Extrai e-mails, URLs e metadados do PDF, usando a senha se necessário.
    """
    print(Fore.CYAN + "\nExtracting Emails, URLs, and Metadata...\n")

    emails_found = set()
    urls_found = set()
    operating_system = None
    metadata_fields = {}

    try:
        # Extrai texto usando a senha
        print(Fore.BLUE + "Extracting Text...")
        text = extract_text(file_path, password=password)  # Senha é passada aqui
        if text:
            # Busca por e-mails e URLs no texto
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

        # Extrai metadados usando a senha
        print(Fore.BLUE + "\nExtracting PDF Metadata...")
        with open(file_path, 'rb') as f:
            parser = PDFParser(f)
            document = PDFDocument(parser, password=password)
            if document.info:
                for metadata in document.info:
                    for key, value in metadata.items():
                        key_decoded = decode_with_fallback(key)
                        value_decoded = decode_with_fallback(value)

                        # Armazena todos os metadados encontrados
                        metadata_fields[key_decoded] = value_decoded

                        # Identificar sistema operacional no campo Producer
                        if "producer" in key_decoded.lower():
                            os_match = re.search(r'\((Windows|Linux|macOS|Ubuntu|Fedora|Android)\)', value_decoded, re.IGNORECASE)
                            if os_match:
                                operating_system = os_match.group(1)

        # Exibe todos os metadados coletados
        if metadata_fields:
            print(Fore.YELLOW + "\nMetadata Found:")
            for key, value in metadata_fields.items():
                print(Fore.BLUE + f"  {key}: {value}")

        # Exibe sistema operacional detectado no Producer
        if operating_system:
            print(Fore.YELLOW + f"\nOperating System Detected (via Producer): {operating_system}")
        else:
            print(Fore.RED + "\nNo Operating System detected in Producer metadata.")

    except PDFEncryptionError:
        print(Fore.RED + "Error: Incorrect password provided.")
    except Exception as e:
        print(Fore.RED + f"Error extracting information: {e}")
